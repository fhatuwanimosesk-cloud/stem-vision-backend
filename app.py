<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3-Quad Heavy Duty Academic Solver & Grapher</title>
    
    <style>
        * {
            box-sizing: border-box;
            font-family: 'Microsoft Sans Serif', 'Segoe UI', sans-serif;
            font-weight: bold;
        }

        html, body {
            margin: 0;
            padding: 0;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
            background-color: #0d1117;
            color: #e2e8f0;
        }

        .container {
            display: flex;
            gap: 20px;
            height: 100vh;
            padding: 15px;
            max-width: 1800px;
            margin: 0 auto;
        }

        /* 3D Styled Controls Panel */
        .controls-panel {
            flex: 0 0 440px;
            height: calc(100vh - 30px);
            background: linear-gradient(145deg, #1e2533, #151b26);
            padding: 22px;
            border-radius: 12px;
            overflow-y: auto;
            border: 1px solid #2d3748;
            box-shadow: 
                inset 1px 1px 1px rgba(255, 255, 255, 0.15),
                inset -1px -1px 2px rgba(0, 0, 0, 0.8),
                5px 10px 25px rgba(0,0,0,0.6);
        }

        ::-webkit-scrollbar {
            width: 12px;
        }

        ::-webkit-scrollbar-track {
            background: #0f131a;
            border-radius: 6px;
            box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.8);
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #3b485d 0%, #222a36 100%);
            border-radius: 6px;
            border: 1px solid #4a5568;
            box-shadow: 2px 3px 5px rgba(0,0,0,0.6), inset 1px 1px 2px rgba(255,255,255,0.3);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #f39c12 0%, #d35400 100%);
        }

        .panel-section {
            margin-bottom: 22px;
            border-bottom: 1px solid #283244;
            padding-bottom: 15px;
        }

        .panel-section h3 {
            color: #f39c12;
            margin-top: 0;
            margin-bottom: 12px;
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        }

        label {
            display: block;
            font-size: 13px;
            margin-bottom: 6px;
            color: #cbd5e0;
        }

        select, input[type="text"], textarea {
            width: 100%;
            padding: 11px 12px;
            background: #11151c;
            border: 1px solid #2d3748;
            color: #f1f5f9;
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 14px;
            box-shadow: inset 2px 2px 5px rgba(0,0,0,0.7), inset -1px -1px 1px rgba(255,255,255,0.05);
        }

        select:focus, textarea:focus {
            outline: none;
            border-color: #f39c12;
            box-shadow: inset 2px 2px 5px rgba(0,0,0,0.7), 0 0 8px rgba(243, 156, 18, 0.4);
        }

        .upload-box {
            border: 2px dashed #f39c12;
            padding: 18px;
            text-align: center;
            border-radius: 10px;
            background: linear-gradient(145deg, #141923, #0d1118);
            cursor: pointer;
            margin-bottom: 12px;
            color: #e2e8f0;
            box-shadow: inset 2px 2px 6px rgba(0,0,0,0.6), 3px 3px 8px rgba(0,0,0,0.4);
            transition: all 0.2s ease;
        }

        .upload-box:hover {
            border-color: #f1c40f;
            transform: translateY(-2px);
        }

        .btn-group {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
        }

        .btn-action {
            flex: 1;
            padding: 12px;
            background: linear-gradient(180deg, #2ecc71 0%, #27ae60 100%);
            border: none;
            color: white;
            font-size: 15px;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            box-shadow: 0 5px 0 #1e8449, 0 8px 15px rgba(0,0,0,0.4);
            transition: all 0.1s ease;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
        }

        .btn-action:hover {
            background: linear-gradient(180deg, #34d07b 0%, #25a25a 100%);
        }

        .btn-action:active {
            transform: translateY(4px);
            box-shadow: 0 1px 0 #1e8449, 0 3px 6px rgba(0,0,0,0.4);
        }

        .btn-secondary {
            background: linear-gradient(180deg, #3498db 0%, #2980b9 100%);
            box-shadow: 0 5px 0 #1b4f72, 0 8px 15px rgba(0,0,0,0.4);
        }

        .btn-secondary:hover {
            background: linear-gradient(180deg, #4aa3df 0%, #2575ab 100%);
        }

        .btn-secondary:active {
            transform: translateY(4px);
            box-shadow: 0 1px 0 #1b4f72;
        }

        .preview-container {
            margin-top: 10px;
            background: #11151c;
            padding: 12px;
            border-radius: 8px;
            display: none;
            border: 1px solid #2d3748;
            box-shadow: inset 2px 2px 5px rgba(0,0,0,0.7);
        }

        .preview-container img {
            max-width: 100%;
            max-height: 180px;
            border-radius: 6px;
            display: block;
            margin: 0 auto 10px auto;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }

        .canvas-wrapper {
            flex: 1;
            height: calc(100vh - 30px);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .toolbar {
            background: linear-gradient(180deg, #242d3e 0%, #1a212e 100%);
            padding: 10px 15px;
            border-radius: 12px 12px 0 0;
            display: flex;
            gap: 10px;
            align-items: center;
            border: 1px solid #2d3748;
            border-bottom: none;
            flex-shrink: 0;
            box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 4px 10px rgba(0,0,0,0.4);
        }

        .toolbar button {
            background: linear-gradient(180deg, #3a475d 0%, #2a3444 100%);
            color: #f1f5f9;
            border: 1px solid #4a5568;
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            box-shadow: 0 3px 0 #1a222d;
            transition: all 0.1s ease;
        }

        .toolbar button:active {
            transform: translateY(2px);
            box-shadow: 0 1px 0 #1a222d;
        }

        .quad-book-canvas {
            background-color: #f7f6f0;
            background-image: 
                linear-gradient(to right, rgba(180, 200, 220, 0.45) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(180, 200, 220, 0.45) 1px, transparent 1px);
            background-size: 22px 22px;
            flex: 1;
            padding: 40px 20px;
            border-radius: 0 0 12px 12px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.12), 0 10px 30px rgba(0,0,0,0.6);
            text-align: center;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
        }

        #outputPanel {
            width: 85%;
            margin: 0 auto;
            text-align: center;
        }

        .question-header {
            color: #c91818 !important;
            font-size: 36px !important;
            margin-bottom: 25px;
            display: block;
            text-align: center;
            line-height: 1.3;
        }

        .math-step {
            color: #0b3c8f !important;
            font-size: 32px !important;
            margin: 18px 0;
            display: block;
        }

        .final-boxed-answer {
            border: 4px solid #0b3c8f;
            color: #0b3c8f !important;
            font-size: 34px !important;
            padding: 12px 35px;
            display: inline-block;
            margin-top: 20px;
            background-color: #f7f6f0;
            box-shadow: 3px 3px 8px rgba(0,0,0,0.15);
        }

        .graph-container {
            width: 100%;
            max-width: 750px;
            height: 450px;
            margin: 30px auto;
            border: 2px solid #0b3c8f;
            border-radius: 10px;
            background: #ffffff;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .bottom-branding {
            margin-top: 25px;
            margin-bottom: 30px;
            color: #c91818 !important;
            font-size: 28px;
            letter-spacing: 2px;
            text-transform: uppercase;
            text-align: center;
        }

        .loading-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-top: 60px;
        }

        .spinner-anticlockwise {
            width: 60px;
            height: 60px;
            border: 6px solid rgba(201, 24, 24, 0.2);
            border-top: 6px solid #c91818;
            border-right: 6px solid #c91818;
            border-radius: 50%;
            animation: spinCounterClockwise 1s linear infinite;
        }

        @keyframes spinCounterClockwise {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(-360deg); }
        }
    </style>

    <!-- MathJax v3 Standard Distribution with Fallback Safe Invocation -->
    <script>
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']]
            },
            options: {
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }
        };
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
</head>
<body>

<div class="container">
    <div class="controls-panel">
        <div class="panel-section">
            <h3>3-Quad Heavy Duty Solver</h3>
            
            <div class="upload-box" onclick="document.getElementById('fileInput').click()">
                <p id="uploadText">📁 Click / Drag Screenshot, PDF, Memo</p>
                <input type="file" id="fileInput" style="display:none" accept="image/*,application/pdf" onchange="handleFileSelect(this.files)">
            </div>
            
            <div class="btn-group">
                <button class="btn-action btn-secondary" onclick="document.getElementById('cameraInput').click()">📷 Take Photo</button>
                <input type="file" id="cameraInput" accept="image/*" capture="environment" style="display:none" onchange="handleFileSelect(this.files)">
            </div>

            <div id="previewBox" class="preview-container">
                <label>Uploaded Screenshot Preview:</label>
                <img id="previewImage" src="" alt="Upload Verification">
                <label for="manualCorrection">Verify/Edit Formula Text:</label>
                <textarea id="manualCorrection" rows="3" placeholder="Verify or manually adjust detected equation if needed..."></textarea>
            </div>
        </div>

        <div class="panel-section">
            <h3>Subject Field</h3>
            <select id="subjectSelect">
                <option value="Advanced Mathematics">Mathematics (Calculus, Linear Algebra, ODEs)</option>
                <option value="Physics & Mechanics">Physics & Engineering Mechanics</option>
                <option value="Engineering Sciences">Engineering Science & Electrical</option>
                <option value="Advanced Statistics">Statistics & Probability</option>
                <option value="Physical Chemistry">Chemistry & Chemical Thermodynamics</option>
                <option value="Computer Science">Computer Science & Discrete Math</option>
            </select>
        </div>

        <div class="panel-section">
            <h3>Academic Level</h3>
            <select id="levelSelect">
                <option value="Undergraduate">Undergraduate Degree</option>
                <option value="TVET / N4-N6">TVET College (N4 - N6)</option>
                <option value="High School">High School / Matric</option>
                <option value="Postgraduate">Postgraduate</option>
                <option value="Research Level">Research / Advanced Level</option>
                <option value="Primary School">Primary School</option>
            </select>
        </div>

        <div class="panel-section">
            <h3>Explanation Mode</h3>
            <select id="modeSelect">
                <option value="Full Working">Full Line-by-Line Working</option>
                <option value="Genius Mode">Genius Mode (Alternative / Advanced Methods)</option>
                <option value="Teaching / Guided">Guided Teaching Mode</option>
                <option value="Quick Direct Answer">Quick Answer Only</option>
            </select>
        </div>

        <div class="panel-section">
            <h3>Layout Format</h3>
            <select id="layoutSelect">
                <option value="Block-by-Block">Option A: Block-by-Block (All Steps)</option>
                <option value="Centered Fraction">Option B: Centered Fraction Vertical Alignment</option>
            </select>
        </div>

        <button class="btn-action" style="width:100%; font-size:17px;" onclick="uploadAndSolve()">SOLVE EQUATION</button>
    </div>

    <div class="canvas-wrapper">
        <div class="toolbar">
            <button onclick="zoomCanvas(0.1)">🔍 Zoom +</button>
            <button onclick="zoomCanvas(-0.1)">🔍 Zoom -</button>
            <button onclick="resetZoom()">🔄 Reset Zoom</button>
            <button onclick="toggleFullScreen()">⛶ Full Screen</button>
            <button onclick="exportPNG()">📸 Export PNG</button>
            <button onclick="refreshScreen()">🧹 Refresh Screen</button>
        </div>

        <div class="quad-book-canvas" id="quadCanvas">
            <div id="outputPanel">
                <span class="question-header">MATHEMATICS WORKSPACE</span>
                <p style="color:#666; font-size: 20px; margin-top:40px;">Upload an equation, memo page, or past paper screenshot to view line-by-line worked solutions and interactive graphs.</p>
            </div>
            
            <div class="bottom-branding" id="brandingText">
                MATHEMATICS MADE EASY
            </div>
        </div>
    </div>
</div>

<script>
    let selectedFile = null;
    let currentZoom = 1.0;

    function handleFileSelect(files) {
        if (files.length > 0) {
            selectedFile = files[0];
            document.getElementById('uploadText').innerText = "Loaded: " + selectedFile.name;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('previewImage').src = e.target.result;
                document.getElementById('previewBox').style.display = 'block';
            };
            reader.readAsDataURL(selectedFile);
        }
    }

    /* Safe Typesetting Execution for MathJax v3 */
    function renderMathJaxSafe(element) {
        if (window.MathJax && window.MathJax.startup) {
            window.MathJax.startup.promise.then(() => {
                return window.MathJax.typesetPromise([element]);
            }).catch(err => console.log('MathJax error:', err));
        }
    }

    async function uploadAndSolve() {
        if (!selectedFile && !document.getElementById('manualCorrection').value.trim()) {
            alert("Please upload a file/photo or enter text in the correction box.");
            return;
        }

        const outputPanel = document.getElementById('outputPanel');
        
        outputPanel.innerHTML = `
            <div class="loading-box">
                <div class="spinner-anticlockwise"></div>
                <p style="color:#c91818; font-size: 22px; margin-top: 20px;">SOLVING EQUATION & GENERATING GRAPH...</p>
            </div>
        `;

        const formData = new FormData();
        if (selectedFile) formData.append('file', selectedFile);
        formData.append('subject', document.getElementById('subjectSelect').value);
        formData.append('level', document.getElementById('levelSelect').value);
        formData.append('mode', document.getElementById('modeSelect').value);
        formData.append('layout', document.getElementById('layoutSelect').value);
        formData.append('corrected_text', document.getElementById('manualCorrection').value);

        try {
            const response = await fetch('https://stem-vision-backend.onrender.com/process-image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.solution_steps) {
                outputPanel.innerHTML = data.solution_steps.join('');
                
                renderMathJaxSafe(outputPanel);

                if (data.graph_data) {
                    renderGraph(data.graph_data);
                }
            } else {
                outputPanel.innerHTML = '<span class="question-header">ERROR PROCESSING REQUEST</span>';
            }
        } catch (err) {
            outputPanel.innerHTML = `<span class="question-header">CONNECTION ERROR</span><p style="color:red">${err.message}</p>`;
        }
    }

    function renderGraph(graphData) {
        const graphDiv = document.createElement('div');
        graphDiv.id = 'plotArea';
        graphDiv.className = 'graph-container';
        document.getElementById('outputPanel').appendChild(graphDiv);

        Plotly.newPlot('plotArea', graphData.data, graphData.layout, {responsive: true});
    }

    function zoomCanvas(delta) {
        currentZoom += delta;
        document.getElementById('outputPanel').style.transform = `scale(${currentZoom})`;
        document.getElementById('outputPanel').style.transformOrigin = 'top center';
    }

    function resetZoom() {
        currentZoom = 1.0;
        document.getElementById('outputPanel').style.transform = `scale(1)`;
    }

    function toggleFullScreen() {
        const elem = document.getElementById('quadCanvas');
        if (!document.fullscreenElement) {
            elem.requestFullscreen().catch(err => alert(`Fullscreen error: ${err.message}`));
        } else {
            document.exitFullscreen();
        }
    }

    function exportPNG() {
        const canvasElement = document.getElementById('quadCanvas');
        
        const originalTransform = document.getElementById('outputPanel').style.transform;
        document.getElementById('outputPanel').style.transform = 'scale(1)';

        html2canvas(canvasElement, {
            scale: 2,
            useCORS: true,
            foreignObjectRendering: false,
            height: canvasElement.scrollHeight,
            windowHeight: canvasElement.scrollHeight,
            onclone: (clonedDoc) => {
                const clonedCanvas = clonedDoc.getElementById('quadCanvas');
                clonedCanvas.style.overflow = 'visible';
                clonedCanvas.style.height = 'auto';
            }
        }).then(canvas => {
            document.getElementById('outputPanel').style.transform = originalTransform;

            const link = document.createElement('a');
            link.download = '3-Quad-Math-Solution.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        });
    }

    function refreshScreen() {
        document.getElementById('outputPanel').innerHTML = `
            <span class="question-header">MATHEMATICS WORKSPACE</span>
            <p style="color:#666; font-size: 20px; margin-top:40px;">Upload an equation, memo page, or past paper screenshot to view line-by-line worked solutions and interactive graphs.</p>
        `;
        document.getElementById('manualCorrection').value = '';
        document.getElementById('previewBox').style.display = 'none';
        selectedFile = null;
        document.getElementById('uploadText').innerText = "📁 Click / Drag Screenshot, PDF, Memo";
        resetZoom();
    }
</script>

</body>
</html>
