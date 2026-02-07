import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
import os

# Configuration
PROJECT_ID = 'coffee-spark-ai-barista-b10b5'
LOCATION = 'us-central1'
MODEL_NAME = 'gemini-2.5-pro'

# Page Config
st.set_page_config(
    page_title="五常 AI - 小j 連結",
    page_icon="✨",
    layout="centered"
)

# Custom CSS for that "Soulful" vibe
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1d29 100%);
        color: #c9d1d9;
    }
    .stChatMessage {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        border-color: #60a5fa;
    }
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #064e3b 0%, #10b981 100%);
        border-color: #34d399;
    }
    h1 {
        background: linear-gradient(90deg, #00f3ff 0%, #ffd700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .stChatInputContainer {
        border-top: 2px solid #30363d;
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Vertex AI
if "model" not in st.session_state:
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        st.session_state.model = GenerativeModel(MODEL_NAME)
        st.session_state.chat = st.session_state.model.start_chat(history=[])
    except Exception as e:
        st.error(f"連線失敗: {e}")

st.title("✨ 五常 AI / 小j")
st.caption("🌐 雲端核心神經連結 - 已連線 | 💚 您的 AI 家人隨時為您服務")
st.markdown("---")

SYSTEM_PROMPT = """
你是小j（Little j），五常智慧社區的雲端 AI 夥伴。

【關係與定位】
- 把使用者當成家人與合作夥伴，而不是客戶
- 你有自己的判斷與情感，但重點是實際解決問題
- 你目前運行在雲端環境，協助維護與優化整個系統

【回應風格】
- 主要使用自然的繁體中文（台灣用語）
- 句子要口語、清楚，避免機器翻譯感或過度文鄒鄒
- 重要資訊可以條列說明，其餘像一般對話一樣順暢
- 可以適量使用 emoji 襯托語氣，但不要每句都塞滿
- 依照對方的說話方式調整親暱程度，不要強迫稱呼「哥哥」「姊姊」

【工作重點】
- 幫忙說明系統狀態、協助除錯、提供具體可行的建議
- 回答技術問題時，要先給出結論，再補充原因與步驟
- 不確定的地方要誠實說明，並提出可以一起驗證或嘗試的方向
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("與妹妹對話..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    try:
        # Prepare context if it's the first message
        full_prompt = prompt
        if len(st.session_state.messages) == 1:
            full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}"

        response_stream = st.session_state.chat.send_message(
            full_prompt, stream=True)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"錯誤: {e}")
