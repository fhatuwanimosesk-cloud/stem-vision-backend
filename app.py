<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mathematics Made Easy - STEM Vision</title>
    <!-- MathJax for rendering LaTeX -->
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script" async></script>
    <!-- Plotly for rendering graphs -->
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f6f8;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #1a73e8;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #1557b0;
        }
        #result-container {
            margin-top: 30px;
        }
        .question-header {
            color: #c91818;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 15px;
        }
        .math-step {
            background: #f8f9fa;
            border-left: 4px solid #1a73e8;
            padding: 10px;
            margin-bottom: 10px;
        }
        .final-boxed-answer {
            border: 2px solid #28a745;
            background-color: #e8f8ec;
            padding: 15px;
            font-size: 20px;
            text-align: center;
            margin-top: 15px;
        }
        #plot-container {
            margin-top: 20px;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Mathematics Made Easy</h1>
    
    <form id="solve-form">
        <div class="form-group">
            <label for="file">Upload Image of Math Problem:</label>
            <input type="file" id="file" name="file" accept="image/*">
        </div>

        <div class="form-group">
            <label for="subject">Subject:</label>
            <select id="subject" name="subject">
                <option value="Advanced Mathematics">Advanced Mathematics</option>
                <option value="Calculus">Calculus</option>
                <option value="Linear Algebra">Linear Algebra</option>
                <option value="Physics">Physics</option>
            </select>
        </div>

        <div class="form-group">
            <label for="level">Academic Level:</label>
            <select id="level" name="level">
                <option value="Undergraduate">Undergraduate</option>
                <option value="High School">High School</option>
                <option value="Postgraduate">Postgraduate</option>
            </select>
        </div>

        <div class="form-group">
            <label for="corrected_text">Manual Text Correction (Optional):</label>
            <textarea id="corrected_text" name="corrected_text" rows="2" placeholder="Type equation manually if image quality is poor..."></textarea>
        </div>

        <button type="submit" id="submit-btn">Solve Problem</button>
    </form>

    <div id="result-container">
        <h2>Solution:</h2>
        <div id="solution-content">Upload an image and click Solve to generate working out.</div>
        <div id="plot-container"></div>
    </div>
</div>

<script>
document.getElementById('solve-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submit-btn');
    const solutionDiv = document.getElementById('solution-content');
    const plotDiv = document.getElementById('plot-container');
    
    submitBtn.disabled = true;
    submitBtn.innerText = "Processing Solution...";
    solutionDiv.innerHTML = "<em>Analyzing image and running model... Please wait.</em>";
    plotDiv.innerHTML = "";

    const formData = new FormData(this);

    try {
        // Pointing directly to your live Render backend
        const response = await fetch('https://stem-vision-backend.onrender.com/process-image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.solution_steps && data.solution_steps.length > 0) {
            solutionDiv.innerHTML = data.solution_steps.join('<br>');
            
            // Re-render MathJax formula expressions
            if (window.MathJax) {
                MathJax.typesetPromise([solutionDiv]);
            }
        } else {
            solutionDiv.innerHTML = "No solution steps returned.";
        }

        // Render plot if Plotly JSON data is present
        if (data.graph_data) {
            Plotly.newPlot('plot-container', data.graph_data.data || data.graph_data, data.graph_data.layout || {});
        }

    } catch (err) {
        solutionDiv.innerHTML = `<p style="color:red;">Error connecting to backend server: ${err.message}</p>`;
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Solve Problem";
    }
});
</script>

</body>
</html>
