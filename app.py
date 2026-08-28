import os
import json
import re
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load variables from a local .env file if present
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Pull key directly from environment variables (No raw strings in code!)
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

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}]
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
