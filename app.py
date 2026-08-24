import os
import json
import re
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from PIL import Image


# ============================================================
# STEM VISION AI — FLASK BACKEND
# ============================================================

app = Flask(__name__)

# Allow requests from your frontend
CORS(
    app,
    resources={
        r"/*": {
            "origins": "*"
        }
    }
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

# Read Gemini API key from environment variable
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("WARNING: GEMINI_API_KEY environment variable is not set.")
    client = None
else:
    client = genai.Client(api_key=API_KEY)


# IMPORTANT:
# gemini-2.5-pro is no longer available for new users.
# Use the model specified by the API error.
MODEL_NAME = "gemini-3.1-pro-preview"


# ============================================================
# HOME / HEALTH CHECK
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return "STEM Vision Backend Running!"


@app.route("/health", methods=["GET"])
def health():
    """
    Simple endpoint to check whether the backend is alive.
    """
    return jsonify({
        "status": "ok",
        "service": "STEM Vision Backend",
        "gemini_configured": bool(API_KEY),
        "model": MODEL_NAME
    })


# ============================================================
# PROCESS IMAGE
# ============================================================

@app.route("/process-image", methods=["POST"])
def process_image():

    # --------------------------------------------------------
    # Check API key
    # --------------------------------------------------------

    if not API_KEY or client is None:
        return jsonify({
            "extracted_text": "Configuration Error",
            "solution_steps": [
                """
                <div class="question-header">NOTICE</div>
                <p style="color:#c91818; font-size:18px;">
                    GEMINI_API_KEY is not configured on the server.
                    Please add your Gemini API key to the environment variables.
                </p>
                """
            ],
            "graph_data": None
        }), 200


    # --------------------------------------------------------
    # Read frontend parameters
    # --------------------------------------------------------

    subject = request.form.get(
        "subject",
        "Advanced Mathematics"
    )

    level = request.form.get(
        "level",
        "Undergraduate"
    )

    mode = request.form.get(
        "mode",
        "Full Working"
    )

    layout = request.form.get(
        "layout",
        "Block-by-Block"
    )

    corrected_text = request.form.get(
        "corrected_text",
        ""
    )


    # --------------------------------------------------------
    # Prepare Gemini contents
    # --------------------------------------------------------

    contents = []


    # --------------------------------------------------------
    # Read uploaded image
    # --------------------------------------------------------

    if (
        "file" in request.files
        and request.files["file"].filename != ""
    ):

        file = request.files["file"]

        try:

            img = Image.open(file.stream)

            # Convert unusual image modes into RGB/RGBA
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            contents.append(img)

        except Exception as image_error:

            print(
                "Image processing error:",
                str(image_error)
            )

            return jsonify({
                "extracted_text": "Image Error",
                "solution_steps": [
                    """
                    <div class="question-header">
                        NOTICE
                    </div>

                    <p style="color:#c91818; font-size:18px;">
                        The uploaded image could not be processed.
                        Please upload a clear JPG, JPEG, PNG, or WEBP image.
                    </p>
                    """
                ],
                "graph_data": None
            }), 200


    # --------------------------------------------------------
    # Mathematical AI prompt
    # --------------------------------------------------------

    prompt = f"""
You are STEM Vision AI, an expert mathematics tutor.

Your job is to analyze the uploaded mathematical question,
equation, graph, diagram, worksheet, textbook page, or
mathematics problem and provide a highly accurate solution.

SUBJECT:
{subject}

ACADEMIC LEVEL:
{level}

EXPLANATION MODE:
{mode}

LAYOUT PREFERENCE:
{layout}

USER MANUAL TEXT CORRECTION:
"{corrected_text}"


============================================================
CORE INSTRUCTIONS
============================================================

1. Carefully inspect the uploaded image.

2. Identify the exact mathematical question.

3. Do not invent information that is not visible in the image.

4. If part of the question is unclear, state exactly what
   portion is unclear instead of guessing.

5. Solve the problem step by step.

6. Show all important algebraic transformations.

7. Explain why each major mathematical step is performed.

8. Check the final answer before presenting it.

9. If there are multiple parts such as (a), (b), (c), solve
   each part separately.

10. Preserve mathematical notation accurately.


============================================================
FORMATTING RULES
============================================================

The frontend uses MathJax.

Follow these rules carefully.


QUESTION:

The first line must contain the extracted question:

<div class="question-header">
[EXACT QUESTION OR MAIN EQUATION]
</div>


IMPORTANT:

Do not put LaTeX HTML tags inside math delimiters.

Correct:

<div class="question-header">
Find x if \\(2x+5=15\\).
</div>

Incorrect:

\\[
<div>2x+5=15</div>
\\]


============================================================
LATEX RULES
============================================================

Use:

\\[
...
\\]

for standalone mathematical equations.

Use:

\\(
...
\\)

for inline mathematics.

Always use complete LaTeX groups for square roots.

Correct:

\\sqrt{{x+4}}

Correct:

\\sqrt{{x^2+5x+6}}

Do not create malformed square-root expressions.


============================================================
STEP-BY-STEP WORKING
============================================================

Every important mathematical step should be wrapped like this:

<div class="math-step">
\\[
MATHEMATICAL STEP
\\]
</div>


For example:

<div class="math-step">
\\[
2x+5=15
\\]
</div>

<div class="math-step">
\\[
2x=15-5
\\]
</div>

<div class="math-step">
\\[
2x=10
\\]
</div>

<div class="math-step">
\\[
x=5
\\]
</div>


============================================================
EXPLANATIONS
============================================================

After important mathematical steps, provide a short,
clear explanation.

For example:

<p>
Subtract 5 from both sides to isolate the term containing x.
</p>


Do not make explanations unnecessarily complicated.

The goal is to make mathematics easy for learners.


============================================================
FINAL ANSWER
============================================================

The final answer MUST be placed inside:

<div class="final-boxed-answer">
\\[
FINAL ANSWER
\\]
</div>


If the answer contains multiple values, you may use:

<div class="final-boxed-answer">
\\[
x=5,\\quad y=3
\\]
</div>


============================================================
GRAPH DETECTION
============================================================

If the question involves any of the following:

- Functions
- Quadratic functions
- Parabolas
- Straight lines
- Trigonometric graphs
- Integration areas
- Differentiation graphs
- Coordinate geometry
- 3D surfaces
- Curves
- Statistical graphs
- Any mathematical graph

then generate Plotly-compatible graph data.


IMPORTANT:

The graph data MUST be placed at the VERY END of the response.

Use exactly:

```json_graph
{{
    "data": [],
    "layout": {{}}
}}
