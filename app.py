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

    # Subject-Specific Methodologies
    subject_rules = {
        "Advanced Mathematics": """
            - Show explicit algebraic transformations, integration steps, matrix operations, or ODE solutions.
            - State any theorems or identities used (e.g., L'Hôpital's Rule, Trigonometric Identities).
        """,
        "Physics & Mechanics": """
            - List 'Given Data' with units and 'Unknown Variables' explicitly.
            - State applicable physical laws (e.g., Newton's Laws, Energy Conservation, Kirchhoff's Laws).
            - Include physical SI units in intermediate and final steps.
        """,
        "Advanced Statistics": """
            - Explicitly state H_0 and H_1 hypotheses.
            - Show test statistics, degrees of freedom, critical values, or p-values.
        """,
        "Engineering Sciences": """
            - Break down circuit analysis, state variables, or thermodynamic relations.
        """,
        "Physical Chemistry": """
            - Show balanced equations, stoichiometry, equilibrium constants (K_c, K_p), or thermodynamics.
        """,
        "Computer Science": """
            - Show formal proof steps, induction logic, or Big-O complexity analysis.
        """
    }

    chosen_rule = subject_rules.get(subject, subject_rules["Advanced Mathematics"])

    prompt = f"""
    You are an expert tutor in {subject} tailored for {level} academic level.
    Explanation Mode: {mode}
    Layout Preference: {layout}
    User Manual Text Correction: "{corrected_text}"

    SUBJECT-SPECIFIC METHODOLOGY:
    {chosen_rule}

    MULTI-QUESTION & FORMATTING INSTRUCTIONS:
    1. MULTI-QUESTION DETECTION: Scan the entire document/image for ALL distinct questions or numbered items (e.g., Question 1, Question 2, 1.1, 1.2, etc.). Solve EVERY question in order from top to bottom.
    2. HEADER FORMATTING: Start each question with a styled HTML header:
       <span class="question-header">[QUESTION NUMBER AND PROMPT HERE]</span>

    3. WORKING OUT FORMATTING:
       - Output line-by-line working out centered using LaTeX display math delimiters:
         <div class="math-step">\\[ ... \\]</div>
       - CRITICAL SQUARE ROOT FORMATTING: ALWAYS wrap square root expressions cleanly inside \\sqrt{{...}} with full group brackets.

    4. FINAL ANSWER FORMATTING:
       - Place the final evaluated answer for EACH question inside a boxed container:
         <div class="final-boxed-answer">\\[ ... \\]</div>

    5. GRAPH DETECTION:
       - If the problem involves functions, parabolas, integration area, or 3D surfaces, append a valid JSON block at the very end of your response inside ```json_graph ... ``` tags with Plotly trace data to render the plot.
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
