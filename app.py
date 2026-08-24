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

# Read key strictly from environment variable
API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

# Using Gemini Pro for heavy reasoning & complex math tasks
MODEL_NAME = 'gemini-2.5-pro'

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

    Analyze the input equation/document page and output a step-by-step mathematical solution.

    CRITICAL FORMATTING RULES TO PREVENT MATHJAX RENDER OVERLAP:
    1. First line: Extract and write the exact question statement from the image in red bold text:
       <div class="question-header">[EXACT QUESTION PROMPT / MAIN EQUATION HERE]</div>

    2. Standard LaTeX formatting:
       - Use \\[ ... \\] for standalone block equations.
       - Use \\( ... \\) for inline math equations inside text.
       - NEVER nest HTML tags inside LaTeX math delimiters (\\[ or \\().
       - ALWAYS wrap square root expressions cleanly inside \\sqrt{{...}} with full group brackets.

    3. Line-by-line working out:
       Wrap each intermediate math step inside:
       <div class="math-step">\\[ ... \\]</div>

    4. Final line: Output the final evaluated answer inside a boxed container:
       <div class="final-boxed-answer">\\[ ... \\]</div>

    5. GRAPH DETECTION:
       If the problem involves functions, parabolas, integration area, or 3D surfaces, append a valid JSON block at the very end of your response inside ```json_graph ... ``` tags with Plotly trace data to render the plot.
    """

    contents.append(prompt)

    response_text = None
    last_error = None

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
                time.sleep(3)
            else:
                break

    if not response_text:
        if "429" in str(last_error) or "RESOURCE_EXHAUSTED" in str(last_error):
            user_msg = "Free tier request quota exceeded. Please wait 30–60 seconds before clicking Solve again."
        else:
            user_msg = last_error

        return jsonify({
            'extracted_text': 'Processing Error',
            'solution_steps': [f"<div class='question-header'>NOTICE</div><p style='color:#c91818; font-size:18px;'>{user_msg}</p>"],
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
        'extracted_text': 'Processed via Vision AI',
        'solution_steps': [response_text],
        'graph_data': graph_data
    })

if __name__ == '__main__':
    print("STEM AI Vision Backend Running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
