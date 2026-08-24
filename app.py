import os
import json
import re
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Fetch API Key securely from the cloud server environment
API_KEY = os.environ.get("API_KEY")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = 'gemini-3.6-flash'

@app.route('/')
def home():
    return "STEM Vision Backend Running!"

@app.route('/process-image', methods=['POST'])
def process_image():
    subject = request.form.get('subject', 'Advanced Mathematics')
    level = request.form.get('level', 'Undergraduate')
    mode = request.form.get('mode', 'Full Working')
    layout = request.form.get('layout', 'Block-by-Block')
    corrected_text = request.form.get('corrected_text', '')

    contents = []

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        try:
            img = Image.open(file.stream)
            contents.append(img)
        except Exception:
            pass

    prompt = f"""
    You are an expert tutor in {subject} tailored for {level} academic level.
    Explanation Mode: {mode}
    Layout Preference: {layout}
    User Manual Text Correction: "{corrected_text}"

    Analyze the input equation/document page and output a pure line-by-line mathematical solution.
    
    CRITICAL SQUARE ROOT FORMATTING:
    - ALWAYS wrap square root expressions cleanly inside \\sqrt{{...}} with full group brackets so the radical bar spans across all terms inside.

    Format requirements:
    1. First line: Extract and write the exact statement/prompt from the image in red bold text:
       <span class="question-header">[EXACT QUESTION PROMPT / MAIN EQUATION HERE]</span>

    2. Output intermediate line-by-line working out centered as raw LaTeX wrapped in display math delimiters:
       <div class="math-step">\\[ ... \\]</div>

    3. Final line: Output final evaluated answer inside a wide boxed container:
       <div class="final-boxed-answer">\\[ ... \\]</div>

    4. GRAPH DETECTION:
       If the problem involves functions, parabolas, integration area, or 3D surfaces, append a valid JSON block at the very end of your response inside ```json_graph ... ``` tags with Plotly trace data to render the plot.
    """

    contents.append(prompt)

    response_text = None
    last_error = None

    # Retry loop to gracefully handle rate-limit spikes
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents
            )
            response_text = response.text
            break
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                time.sleep(3)  # Wait 3 seconds before retrying
            else:
                break

    if not response_text:
        if "429" in str(last_error) or "RESOURCE_EXHAUSTED" in str(last_error):
            user_msg = "Free tier request quota exceeded. Please wait 30–60 seconds before clicking Solve again."
        else:
            user_msg = last_error

        return jsonify({
            'extracted_text': 'Processing Error',
            'solution_steps': [f"<span class='question-header'>NOTICE</span><p style='color:#c91818; font-size:18px;'>{user_msg}</p>"],
            'graph_data': None
        }), 200

    graph_data = None

    # Extract Graph JSON if generated
    graph_match = re.search(r'```json_graph\s*(.*?)\s*```', response_text, re.DOTALL)
    if graph_match:
        try:
            graph_data = json.loads(graph_match.group(1))
            response_text = re.sub(r'```json_graph\s*.*?\s*```', '', response_text, flags=re.DOTALL)
        except Exception:
            graph_data = None

    return jsonify({
        'extracted_text': 'Processed via Vision AI',
        'solution_steps': [response_text],
        'graph_data': graph_data
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)