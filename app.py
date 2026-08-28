import os
import json
import re
import time
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from anthropic import Anthropic

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Correct Anthropic Model Identifier
MODEL_NAME = 'claude-3-5-sonnet-20241022'


@app.route('/')
def home():
    return "STEM Vision Backend Running!"


@app.route('/process-image', methods=['POST', 'OPTIONS'])
def process_image():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({
            'extracted_text': 'Configuration Error',
            'solution_steps': ["<div class='question-header'>NOTICE</div><p style='color:#c91818; font-size:18px;'>ANTHROPIC_API_KEY environment variable is missing on server.</p>"],
            'graph_data': None
        }), 200

    try:
        client = Anthropic(api_key=api_key)
    except Exception as e:
        return jsonify({
            'extracted_text': 'Initialization Error',
            'solution_steps': [f"<div class='question-header'>NOTICE</div><p style='color:#c91818; font-size:18px;'>{str(e)}</p>"],
            'graph_data': None
        }), 200

    subject = request.form.get('subject', 'Advanced Mathematics')
    level = request.form.get('level', 'Undergraduate')
    mode = request.form.get('mode', 'Full Working')
    layout = request.form.get('layout', 'Block-by-Block')
    corrected_text = request.form.get('corrected_text', '')

    media_block = None
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        try:
            file_bytes = file.read()
            mime_type = file.mimetype or "image/jpeg"
            
            # Format block appropriately for Image vs Document (PDF)
            if mime_type == "application/pdf":
                media_block = {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": base64.standard_b64encode(file_bytes).decode("utf-8"),
                    },
                }
            else:
                media_block = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": base64.standard_b64encode(file_bytes).decode("utf-8"),
                    },
                }
        except Exception as e:
            print(f"File processing error: {e}")

    prompt = f"""You are an expert tutor in {subject} tailored for {level} academic level.
Explanation Mode: {mode}
Layout Preference: {layout}
User Manual Text Correction: "{corrected_text}"

Analyze the input equation/document page and output a step-by-step mathematical solution.

CRITICAL FORMATTING RULES TO PREVENT MATHJAX RENDER OVERLAP:
1. First line: Extract and write the exact question statement from the input in red bold text:
   <div class="question-header">[EXACT QUESTION PROMPT / MAIN EQUATION HERE]</div>

2. Standard LaTeX formatting:
   - Use \\\\[ ... \\\\] for standalone block equations.
   - Use \\\\( ... \\\\) for inline math equations inside text.
   - NEVER nest HTML tags inside LaTeX math delimiters (\\\\[ or \\\\().
   - ALWAYS wrap square root expressions cleanly inside \\\\sqrt{{...}} with full group brackets.

3. Line-by-line working out:
   Wrap each intermediate math step inside:
   <div class="math-step">\\\\[ ... \\\\]</div>

4. Final line: Output the final evaluated answer inside a boxed container:
   <div class="final-boxed-answer">\\\\[ ... \\\\]</div>

5. GRAPH DETECTION:
   If the problem involves functions, parabolas, integration area, or 3D surfaces, append a valid JSON block at the very end of your response inside ```json_graph ... ``` tags containing valid Plotly JSON object structure with "data" array and "layout" object.
"""

    content = ([media_block] if media_block else []) + [{"type": "text", "text": prompt}]

    response_text = None
    last_error = None

    for attempt in range(3):
        try:
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=3000,
                messages=[{"role": "user", "content": content}],
            )
            response_text = "".join(b.text for b in message.content if b.type == "text")
            break
        except Exception as e:
            last_error = str(e)
            print(f"Attempt {attempt + 1} failed: {last_error}")
            if "429" in last_error or "rate_limit" in last_error.lower() or "overloaded" in last_error.lower():
                time.sleep(5 * (attempt + 1))
            else:
                break

    if not response_text:
        return jsonify({
            'extracted_text': 'Processing Error',
            'solution_steps': [f"<div class='question-header'>NOTICE</div><p style='color:#c91818; font-size:18px;'>{last_error}</p>"],
            'graph_data': None
        }), 200

    graph_data = None
    graph_match = re.search(r'```json_graph\s*(.*?)\s*```', response_text, re.DOTALL)
    if graph_match:
        try:
            graph_data = json.loads(graph_match.group(1))
            response_text = re.sub(r'```json_graph\s*.*?\s*```', '', response_text, flags=re.DOTALL)
        except Exception as e:
            print(f"JSON graph parsing error: {e}")
            graph_data = None

    return jsonify({
        'extracted_text': 'Processed via Vision AI',
        'solution_steps': [response_text],
        'graph_data': graph_data
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"STEM AI Vision Backend Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
