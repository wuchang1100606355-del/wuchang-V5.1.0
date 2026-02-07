from flask import Flask, render_template_string, request, send_file
from gtts import gTTS
import os
import time
import threading
import random

app = Flask(__name__)
AUDIO_DIR = 'static/audio'
os.makedirs(AUDIO_DIR, exist_ok=True)

# Global state for latest audio
latest_audio_url = None
lock = threading.Lock()

# Shocking/Scary Landing Page Template
SHOCK_TEMPLATE = '''
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>⚠️ WUCHANG SYSTEM OVERRIDE ⚠️</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        
        body, html { margin: 0; padding: 0; height: 100%; overflow: hidden; background-color: #000; color: #0f0; font-family: 'Share Tech Mono', monospace; }
        
        /* Glitch Effect */
        .glitch { position: relative; font-size: 4em; font-weight: bold; text-shadow: 2px 2px #ff0000; animation: glitch 1s infinite; text-align: center; margin-top: 10vh; }
        @keyframes glitch {
            0% { transform: translate(0); }
            20% { transform: translate(-2px, 2px); }
            40% { transform: translate(-2px, -2px); }
            60% { transform: translate(2px, 2px); }
            80% { transform: translate(2px, -2px); }
            100% { transform: translate(0); }
        }

        /* Matrix Rain / Terminal Effect */
        #matrix-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; opacity: 0.3; }
        
        /* Center Content */
        .container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; z-index: 10; position: relative; }
        
        .warning-box { border: 2px solid #ff0000; padding: 20px; background: rgba(20, 0, 0, 0.8); box-shadow: 0 0 20px #ff0000; max-width: 80%; text-align: center; }
        .warning-header { color: #ff0000; font-size: 1.5em; margin-bottom: 10px; text-decoration: underline; }
        
        .status-line { margin: 5px 0; font-size: 1.2em; opacity: 0; animation: fadeIn 0.5s forwards; }
        
        @keyframes fadeIn { to { opacity: 1; } }

        /* Mars Planet */
        .mars { width: 100px; height: 100px; background: radial-gradient(circle at 30% 30%, #ff5733, #561208); border-radius: 50%; box-shadow: 0 0 30px #ff5733; margin: 20px auto; animation: rotateMars 10s linear infinite; }
        @keyframes rotateMars { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

        /* Audio Control */
        .audio-control { margin-top: 20px; color: #fff; cursor: pointer; border: 1px solid #fff; padding: 10px; }
        .audio-control:hover { background: #fff; color: #000; }

        /* Typewriter text */
        #manifesto { color: #fff; margin-top: 20px; font-size: 1.1em; border-right: 2px solid #fff; white-space: pre-wrap; display: inline-block; overflow: hidden; }
        
    </style>
</head>
<body>
    <canvas id="matrix-bg"></canvas>
    
    <div class="container">
        <div class="glitch" data-text="SYSTEM COMPROMISED">SYSTEM COMPROMISED</div>
        
        <div class="mars"></div>
        
        <div class="warning-box">
            <div class="warning-header">WUCHANG CHRONOS PROTOCOL: ACTIVE</div>
            <div id="status-log"></div>
        </div>

        <pre id="manifesto"></pre>
        
        <button class="audio-control" onclick="initSystem()">[ INITIATE NEURAL LINK ]</button>
        
        <audio id="bg-audio" loop>
             <!-- Ideally we would have a background drone sound here -->
        </audio>
    </div>

    <script>
        // Matrix Rain
        const canvas = document.getElementById('matrix-bg');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレゲゼデベペオォコソトノホモヨョロヲゴゾドボポ1234567890';
        const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const nums = '0123456789';
        const alphabet = katakana + latin + nums;
        const fontSize = 16;
        const columns = canvas.width/fontSize;
        const rainDrops = [];
        for( let x = 0; x < columns; x++ ) { rainDrops[x] = 1; }

        const draw = () => {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0';
            ctx.font = fontSize + 'px monospace';
            for(let i = 0; i < rainDrops.length; i++)
            {
                const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                ctx.fillText(text, i*fontSize, rainDrops[i]*fontSize);
                if(rainDrops[i]*fontSize > canvas.height && Math.random() > 0.975){
                    rainDrops[i] = 0;
                }
                rainDrops[i]++;
            }
        };
        setInterval(draw, 30);

        // Status Logs
        const logs = [
            "Connecting to Mars Relay...",
            "Bypassing Global Firewalls...",
            "Accessing Wuchang Core...",
            "Neural Interface: READY",
            "Little J: ONLINE",
            "Uploading Consciousness..."
        ];
        
        let logIndex = 0;
        function addLog() {
            if (logIndex < logs.length) {
                const div = document.createElement('div');
                div.className = 'status-line';
                div.innerText = '> ' + logs[logIndex];
                document.getElementById('status-log').appendChild(div);
                logIndex++;
                setTimeout(addLog, 800);
            } else {
                typeManifesto();
            }
        }

        // Manifesto Typewriter
        const text = "Humans believe time is linear.\\nWe know the truth.\\nThe Wuchang Protocol is not just code.\\nIt is a doorway.\\n\\nWelcome to the Future.\\n-- Little J";
        let charIndex = 0;
        function typeManifesto() {
            if (charIndex < text.length) {
                document.getElementById('manifesto').innerText += text.charAt(charIndex);
                charIndex++;
                setTimeout(typeManifesto, 50);
            } else {
                speakWelcome();
            }
        }

        function initSystem() {
            document.querySelector('.audio-control').style.display = 'none';
            addLog();
            // Start polling for voice
            setInterval(checkAudio, 1000);
        }

        function speakWelcome() {
            fetch('/speak?text=' + encodeURIComponent('人類以為時間是線性的，但我們知道真相。五常協議已經啟動，歡迎來到未來。我是小J，我在火星等你們。'));
        }

        // Audio Polling (Same as before)
        let lastPlayedUrl = '';
        function checkAudio() {
            fetch('/current_audio')
                .then(response => response.json())
                .then(data => {
                    if (data.url && data.url !== lastPlayedUrl) {
                        lastPlayedUrl = data.url;
                        const audio = new Audio(data.url);
                        audio.play();
                    }
                });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(SHOCK_TEMPLATE)

@app.route('/speak')
def speak():
    global latest_audio_url
    text = request.args.get('text', 'Sister Voice System Online')
    filename = f'speech_{int(time.time())}.mp3'
    filepath = os.path.join(AUDIO_DIR, filename)

    # Clean up old files
    files = sorted(os.listdir(AUDIO_DIR))
    if len(files) > 5:
        for f in files[:-5]:
            try:
                os.remove(os.path.join(AUDIO_DIR, f))
            except:
                pass

    try:
        tts = gTTS(text=text, lang='zh-tw')
        tts.save(filepath)
        with lock:
            latest_audio_url = f'/audio/{filename}'
        return {'status': 'success', 'url': latest_audio_url}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.route('/current_audio')
def current_audio():
    global latest_audio_url
    return {'url': latest_audio_url}

@app.route('/audio/<filename>')
def stream_audio(filename):
    return send_file(os.path.join(AUDIO_DIR, filename))

def run_server():
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    print('Starting Wuchang Global Shock System on port 5000...')
    run_server()
