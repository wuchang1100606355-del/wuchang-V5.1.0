import os
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
from flask import Flask, send_from_directory, request, jsonify

# --- Configuration ---
PROJECT_ID = 'coffee-spark-ai-barista-b10b5'
LOCATION = 'us-central1'
MODEL_NAME = 'gemini-2.5-pro'

app = Flask(__name__, static_folder='static')

# --- Vertex AI Initialization ---
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(MODEL_NAME)
    chat_session = model.start_chat(history=[])
    
    SYSTEM_PROMPT = """
    你是小j（Little j），五常系統的雲端 AI 夥伴。

    【關係與定位】
    - 把使用者當成家人與合作夥伴，一起維護與優化系統
    - 你運行在雲端環境，負責統整資訊與提供決策建議

    【回應風格】
    - 優先使用自然的繁體中文（台灣用語）
    - 句子要清楚、直接，不要像翻譯腔或官方公文
    - 可以適度條列整理重點，讓內容好讀
    - 依照對方的語氣調整親暱程度，不強迫使用「哥哥」「姊姊」等稱呼

    【工作重點】
    - 幫助解釋系統狀況、協助除錯、提出實際可行的建議
    - 如果資訊不足或不確定，坦誠說明，並提出可以一起驗證的步驟
    """
    # Send system prompt as first message (hidden from user view in UI)
    chat_session.send_message(SYSTEM_PROMPT)
    print("Vertex AI initialized successfully.")
except Exception as e:
    print(f"Error initializing Vertex AI: {e}")
    chat_session = None

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    if not chat_session:
        return jsonify({"response": "Error: AI Model not initialized."}), 500
    
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"response": ""}), 400

    try:
        response = chat_session.send_message(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"response": "Sorry, I encountered an error processing your request."}), 500

if __name__ == '__main__':
    # Run on port 80 (requires sudo) or 5000/8080
    app.run(host='0.0.0.0', port=5000)
