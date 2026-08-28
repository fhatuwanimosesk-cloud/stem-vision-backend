import os
import json
import re
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL_NAME = "deepseek/deepseek-r1:free"


@app.route('/')
def home():
    return "STEM Vision Backend Running!"


@app.route('/process-image', methods=['POST', 'OPTIONS'])
def process_image():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    if not OPENROUTER_API_KEY:
        return jsonify({
            'extracted_text': 'Configuration Error',
            'solution_steps': ["<div class='question-header'>NOTICE</div><p style='color:#c91818; font-size:18px;'>OPENROUTER_API_KEY environment variable is missing on server.</p>"],
            'graph_data': None
        }), 200

    subject = request.form.get('subject', 'Advanced Mathematics')
    level = request.form.get('level', 'Undergraduate')
    mode = request.form.get('mode', 'Full Working')
    layout = request.form.get('layout', 'Block-by-Block')
    corrected_text = request.form.get('corrected_text', '')

    file_data_url = None
    if 'file' in request.files and request.files['file'].filename != '':
        uploaded_file = request.files['file']
        mime_type = uploaded_file.mimetype or "image/png"
        encoded_string = base64.b64encode(uploaded_file.read()).decode('utf-8')
        file_data_url = f"data:{mime_type};base64,{encoded_string}"

    prompt = f"""You are an expert tutor in {subject} tailored for {level} academic level.
Explanation Mode: {mode}
Layout Preference: {layout}
User Text Input/Correction: "{corrected_text}"

Solve the mathematical problem step-by-step.

CRITICAL FORMATTING RULES TO PREVENT MATHJAX RENDER OVERLAP:
1. First line: Extract and write the exact question statement in red bold text:
   <div class="question-header">[EXACT QUESTION PROMPT / MAIN EQUATION HERE]</div>

2. Standard LaTeX formatting:
   - Use \\\\[... \\\\] for standalone block equations.
   - Use \\\\(... \\\\) for inline math equations inside text.

3. Line-by-line working out:
   Wrap each intermediate math step inside:
   <div class="math-step">\\\\[... \\\\]</div>

4. Final line: Output the final evaluated answer inside a boxed container:
   <div class="final-boxed-answer">\\\\[... \\\\]</div>

5. GRAPH DETECTION:
   If the problem involves functions, parabolas, or curves, append a valid JSON block at the very end inside ```json_graph ... ``` tags with Plotly trace data.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://stem-vision-backend.onrender.com",
        "X-Title": "STEM Vision AI Helper"
    }

    if file_data_url:
        message_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": file_data_url}}
        ]
    else:
        message_content = prompt

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": message_content}]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45
        )

        if response.status_code != 200:
            return jsonify({
                'extracted_text': 'API Error',
                'solution_steps': [f"<div class='question-header'>NOTICE</div><p style='color:#c91818; font-size:18px;'>OpenRouter API Status {response.status_code}: {response.text}</p>"],
                'graph_data': None
            }), 200

        result = response.json()
        response_text = result['choices'][0]['message']['content']

    except Exception as e:
        return jsonify({
            'extracted_text': 'Processing Error',
            'solution_steps': [f"<div class='question-header'>NOTICE</div><p style='color:#c91818; font-size:18px;'>Connection Error: {str(e)}</p>"],
            'graph_data': None
        }), 200

    graph_data = None
    graph_match = re.search(r'```json_graph\s*(.*?)\s*```', response_text, re.DOTALL)
    if graph_match:
        try:
            graph_data = json.loads(graph_match.group(1))
            response_text = re.sub(r'```json_graph\s*.*?\s*```', '', response_text, flags=re.DOTALL)
        except Exception:
            graph_data = None

    return jsonify({
        'extracted_text': 'Processed via OpenRouter Free AI',
        'solution_steps': [response_text],
        'graph_data': graph_data
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
