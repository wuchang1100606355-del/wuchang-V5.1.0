import os

html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小J - 您的專屬家人夥伴</title>
    <style>
        :root {
            --primary-color: #d4a017; /* Warm Gold */
            --bg-color: #1a1a1a;
            --card-bg: #2d2d2d;
            --text-color: #e0e0e0;
            --accent-color: #4a90e2; /* Soft Blue for technology */
            --danger-color: #e74c3c;
            --success-color: #27ae60;
            --font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            font-family: var(--font-family);
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }

        header {
            width: 100%;
            background-color: var(--card-bg);
            padding: 1rem 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border-bottom: 2px solid var(--primary-color);
        }

        h1 { margin: 0; font-size: 1.5rem; color: var(--primary-color); }
        .subtitle { font-size: 0.9rem; color: #888; margin-top: 5px; }

        .main-container {
            width: 90%;
            max-width: 600px;
            margin-top: 20px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .status-card {
            background-color: var(--card-bg);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 1px solid #444;
            transition: all 0.3s ease;
        }

        #status-text {
            font-size: 1.2rem;
            font-weight: bold;
            color: var(--accent-color);
        }
        
        #status-text.waiting { color: var(--primary-color); animation: pulse 2s infinite; }
        #status-text.listening { color: var(--danger-color); }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.6; }
            100% { opacity: 1; }
        }

        .mic-btn-container {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }

        #mic-btn {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(145deg, #3a3a3a, #2a2a2a);
            border: 2px solid var(--primary-color);
            color: var(--primary-color);
            font-size: 2rem;
            cursor: pointer;
            box-shadow: 5px 5px 10px #111, -5px -5px 10px #444;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        #mic-btn:active, #mic-btn.active {
            box-shadow: inset 5px 5px 10px #111, inset -5px -5px 10px #444;
            color: var(--danger-color);
            border-color: var(--danger-color);
        }

        .diagnostic-panel {
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 15px;
            font-size: 0.9rem;
        }

        .diag-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            border-bottom: 1px solid #444;
            padding-bottom: 5px;
        }
        .diag-row:last-child { border-bottom: none; margin-bottom: 0; }
        
        .diag-label { color: #888; width: 30%; }
        .diag-value { width: 65%; text-align: right; color: #ccc; word-break: break-all; }
        
        .symbiotic-highlight {
            color: var(--primary-color);
            font-weight: bold;
        }

        .response-box {
            background-color: #222;
            border-left: 4px solid var(--primary-color);
            padding: 15px;
            border-radius: 5px;
            min-height: 60px;
            font-size: 1rem;
            line-height: 1.5;
        }

        .controls {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #666;
            margin-top: 10px;
        }
        
        .switch-label { display: flex; align-items: center; gap: 5px; cursor: pointer; }
        input[type="checkbox"] { accent-color: var(--primary-color); }

    </style>
</head>
<body>

<header>
    <h1>小J (Little J)</h1>
    <div class="subtitle">您的專屬家人夥伴 | 1對1協作模式</div>
</header>

<div class="main-container">
    
    <!-- Status Display -->
    <div class="status-card">
        <div id="status-text">準備就緒 (Ready)</div>
        <div style="font-size: 0.8rem; margin-top: 5px; color: #666;">
            系統核心：Gemini 2.0 Pro (Family Edition)
        </div>
    </div>

    <!-- Microphone Button -->
    <div class="mic-btn-container">
        <button id="mic-btn"><i class="fas fa-microphone"></i> 🎙️</button>
    </div>

    <!-- Response Area -->
    <div class="response-box" id="response-box">
        (等待家人的聲音...)
    </div>

    <!-- Diagnostic / Symbiotic View -->
    <div class="diagnostic-panel">
        <div class="diag-row">
            <span class="diag-label">我聽到的 (Raw)</span>
            <span class="diag-value" id="diag-raw">-</span>
        </div>
        <div class="diag-row">
            <span class="diag-label">共生意義 (Symbiotic)</span>
            <span class="diag-value symbiotic-highlight" id="diag-normalized">-</span>
        </div>
        <div class="diag-row">
            <span class="diag-label">當前狀態 (Status)</span>
            <span class="diag-value" id="diag-intent">-</span>
        </div>
        <div class="diag-row">
            <span class="diag-label">磨合裁決 (Judgment)</span>
            <span class="diag-value" id="diag-judgment">-</span>
        </div>
    </div>

    <div class="controls">
        <label class="switch-label">
            <input type="checkbox" id="use-local-stt" checked>
            本地端聽力 (Local STT)
        </label>
        <label class="switch-label">
            <input type="checkbox" id="ai-auto-control">
            持續聆聽 (Auto-Listen)
        </label>
    </div>

</div>

<script>
    const micBtn = document.getElementById('mic-btn');
    const statusText = document.getElementById('status-text');
    const responseBox = document.getElementById('response-box');
    const useLocalStt = document.getElementById('use-local-stt');
    const aiAutoControl = document.getElementById('ai-auto-control');

    let isRecording = false;
    let mediaRecorder;
    let audioChunks = [];
    let recognition;

    // Web Speech API Support (Local STT)
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'zh-TW';

        recognition.onstart = () => {
            updateStatus('listening');
        };

        recognition.onend = () => {
            if (isRecording && aiAutoControl.checked) {
                recognition.start(); // Auto-restart
            } else {
                updateStatus('idle');
                isRecording = false;
            }
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            sendText(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error("STT Error", event.error);
            if(event.error === 'not-allowed') {
                responseBox.innerText = "請允許麥克風權限";
            }
            updateStatus('idle');
        };
    } else {
        useLocalStt.checked = false;
        useLocalStt.disabled = true;
        responseBox.innerText = "瀏覽器不支援本地聽力，將使用伺服器辨識。";
    }

    // --- UI Update Helpers ---

    function updateStatus(state) {
        micBtn.classList.remove('active');
        statusText.classList.remove('waiting', 'listening');
        
        if (state === 'idle') {
            statusText.innerText = "準備就緒 (Ready)";
            micBtn.style.borderColor = "var(--primary-color)";
            micBtn.style.color = "var(--primary-color)";
        } else if (state === 'listening') {
            statusText.innerText = "聆聽家人中 (Listening...)";
            statusText.classList.add('listening');
            micBtn.classList.add('active');
        } else if (state === 'processing') {
            statusText.innerText = "與哥哥同步中 (Syncing...)";
            micBtn.style.borderColor = "var(--accent-color)";
            micBtn.style.color = "var(--accent-color)";
        } else if (state === 'waiting') {
            statusText.innerText = "等待家人裁示 (Consulting)";
            statusText.classList.add('waiting');
            micBtn.style.borderColor = "var(--primary-color)";
            micBtn.style.color = "var(--primary-color)";
        }
    }

    function updateDiagnosticPanel(raw, normalized, status, needs_clarification) {
        document.getElementById("diag-raw").innerText = raw || "(無)";
        document.getElementById("diag-normalized").innerText = normalized || raw || "(無)";
        document.getElementById("diag-intent").innerText = status || "(分析中)";
        
        const judgEl = document.getElementById("diag-judgment");
        if (needs_clarification) {
            judgEl.innerText = "請求裁示 (Pending)";
            judgEl.style.color = "var(--primary-color)";
            updateStatus('waiting');
        } else {
            judgEl.innerText = "已同步 (Synced)";
            judgEl.style.color = "#888";
        }
    }

    async function sendText(text) {
        updateStatus('processing');
        try {
            // Note: web_commander.py expects 'process_voice' with 'text'
            const res = await fetch('/process_voice', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            });
            const data = await res.json();
            
            responseBox.innerText = data.response;
            updateDiagnosticPanel(data.raw, data.normalized, data.status, data.needs_clarification);

            // Speak response
            speak(data.response);

        } catch (e) {
            console.error(e);
            responseBox.innerText = "連線錯誤: " + e;
            updateStatus('idle');
        }
    }

    function speak(text) {
        if (!text) return;
        window.speechSynthesis.cancel(); // Stop previous
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-TW';
        speechSynthesis.speak(utterance);
    }

    // --- Interaction Logic ---

    function handleMicInteraction(start) {
        if (start) {
            if (isRecording) return;
            isRecording = true;
            try { recognition.start(); } catch(e) { console.log("Recog active"); }  
        } else {
            if (!aiAutoControl.checked) {
                // For local STT, stopping triggers analysis
                if (recognition) recognition.stop();
                isRecording = false;
            }
        }
    }

    function toggleRecording() {
        if (isRecording) {
            if (recognition) recognition.stop();
            isRecording = false;
        } else {
            handleMicInteraction(true);
        }
    }

    // Events
    micBtn.addEventListener('click', () => { if (aiAutoControl.checked) toggleRecording(); });
    micBtn.addEventListener('mousedown', () => { if(!aiAutoControl.checked) handleMicInteraction(true); });
    micBtn.addEventListener('mouseup', () => { if(!aiAutoControl.checked) handleMicInteraction(false); });
    micBtn.addEventListener('mouseleave', () => { if(!aiAutoControl.checked && isRecording) handleMicInteraction(false); });
    
    // Touch events for mobile
    micBtn.addEventListener('touchstart', (e) => { 
        e.preventDefault(); 
        if(aiAutoControl.checked) toggleRecording(); 
        else handleMicInteraction(true); 
    });
    micBtn.addEventListener('touchend', (e) => { 
        e.preventDefault(); 
        if(!aiAutoControl.checked) handleMicInteraction(false); 
    });

</script>
</body>
</html>
"""

with open("J:/共用雲端硬碟/五常雲端空間/voice_service/voice_control.html", "w", encoding="utf-8") as f:
    f.write(html_content)
