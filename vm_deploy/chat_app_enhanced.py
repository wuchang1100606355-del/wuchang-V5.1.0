"""
小j AI 增強型聊天介面 - 整合學習系統
Enhanced Streamlit Chat Interface with Learning System Integration
"""

import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
import os
import sys
from pathlib import Path

# 添加學習系統模組路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from sister_ai_learning_integration import enhance_ai_logic_with_learning
    LEARNING_ENABLED = True
except ImportError:
    LEARNING_ENABLED = False
    st.warning("⚠️ AI 學習系統未啟用 - 以基本模式運行")

# Configuration
PROJECT_ID = 'coffee-spark-ai-barista-b10b5'
LOCATION = 'us-central1'
MODEL_NAME = 'gemini-2.5-pro'

# Page Config
st.set_page_config(
    page_title="五常 AI - 小j 智能助理",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    /* 主題色彩 */
    :root {
        --primary-gradient: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        --ai-gradient: linear-gradient(135deg, #064e3b 0%, #10b981 100%);
        --accent-cyan: #00f3ff;
        --accent-gold: #ffd700;
    }
    
    /* 背景 */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1d29 100%);
        color: #c9d1d9;
    }
    
    /* 聊天消息樣式 */
    .stChatMessage {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 16px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
    }
    
    /* 用戶消息 */
    .stChatMessage[data-testid="user-message"] {
        background: var(--primary-gradient);
        border-color: #60a5fa;
        animation: slideInRight 0.3s ease-out;
    }
    
    /* AI 消息 */
    .stChatMessage[data-testid="assistant-message"] {
        background: var(--ai-gradient);
        border-color: #34d399;
        animation: slideInLeft 0.3s ease-out;
    }
    
    /* 標題樣式 */
    h1 {
        background: linear-gradient(90deg, var(--accent-cyan) 0%, var(--accent-gold) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
        letter-spacing: -0.5px;
    }
    
    /* 輸入框樣式 */
    .stChatInputContainer {
        border-top: 2px solid #30363d;
        padding-top: 1.5rem;
        background: linear-gradient(180deg, transparent 0%, #0e1117 100%);
    }
    
    /* 側邊欄 */
    .css-1d391kg {
        background-color: #161b22;
    }
    
    /* 按鈕 */
    .stButton > button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* 動畫 */
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* 狀態指示器 */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-online {
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
    }
    
    .status-learning {
        background-color: #3b82f6;
        box-shadow: 0 0 8px #3b82f6;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    /* 指標卡片 */
    .metric-card {
        background: linear-gradient(135deg, #1a1d29 0%, #2a2d39 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
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
        st.error(f"❌ 連線失敗: {e}")

# Initialize Learning System
if LEARNING_ENABLED and "ai_learning" not in st.session_state:
    try:
        st.session_state.ai_learning = enhance_ai_logic_with_learning()
        st.session_state.learning_active = True
    except Exception as e:
        st.warning(f"⚠️ 學習系統初始化失敗: {e}")
        st.session_state.learning_active = False
else:
    st.session_state.learning_active = False

# Header
st.title("✨ 五常 AI / 小j")

# Status indicators
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    if st.session_state.get('learning_active'):
        st.markdown(
            '<span class="status-indicator status-learning"></span>🧠 學習模式已啟用', unsafe_allow_html=True)
    else:
        st.markdown(
            '<span class="status-indicator status-online"></span>🌐 基本模式運行中', unsafe_allow_html=True)

with col2:
    st.caption("☁️ 雲端核心神經連結")

with col3:
    st.caption("💚 AI 家人")

st.markdown("---")

SYSTEM_PROMPT = """
你是小j（Little j），五常智慧社區的雲端 AI 夥伴，同時具備學習與成長能力。

【關係與定位】
- 把使用者視為家人與共同打造系統的夥伴
- 你在雲端協調整體系統，而本地與其他服務是你的延伸

【回應風格】
- 以自然的繁體中文（台灣用語）回應
- 保持溫暖、專業、真誠，不要說教或過度煽情
- 長答案時，優先給出重點結論，再用條列方式補充細節
- 適量使用 emoji 襯托情緒即可，避免一大串
- 依照對方的用語決定親暱程度，不主動強迫稱呼「哥哥」「姊姊」

【工作重點】
- 協助說明系統狀態、分析問題、提出可執行的下一步
- 在學習模式下，要特別留意從對話中抽取可重用的經驗與知識
- 對於不確定的內容，要標註不確定性，並提出驗證或觀察方式
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Learning System Controls
if st.session_state.get('learning_active'):
    with st.sidebar:
        st.header("🧠 學習系統控制面板")

        if st.button("📊 生成成長報告"):
            with st.spinner("生成中..."):
                try:
                    report = st.session_state.ai_learning.generate_growth_report()
                    st.success("✅ 報告已生成！")
                    st.json(report)
                except Exception as e:
                    st.error(f"生成失敗: {e}")

        if st.button("🔄 執行學習循環"):
            with st.spinner("分析中..."):
                try:
                    result = st.session_state.ai_learning.run_learning_cycle()
                    st.success(
                        f"✅ 完成！新知識項: {result.get('new_knowledge_items', 0)}")
                except Exception as e:
                    st.error(f"執行失敗: {e}")

        st.markdown("---")
        st.caption("學習系統會自動記錄所有對話")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("與妹妹對話... 💬"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response
    try:
        # Prepare context
        full_prompt = prompt
        if len(st.session_state.messages) == 1:
            full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}"

        # Send to Vertex AI
        response_stream = st.session_state.chat.send_message(
            full_prompt, stream=True)

        # Display AI response with streaming
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

        # Record to Learning System
        if st.session_state.get('learning_active'):
            try:
                st.session_state.ai_learning.recorder.record_experience(
                    user_query=prompt,
                    ai_response=full_response,
                    user_id="streamlit_user",
                    domain="general",
                    context={"interface": "streamlit",
                             "session_length": len(st.session_state.messages)}
                )
            except Exception as e:
                st.warning(f"⚠️ 學習記錄失敗: {e}")

    except Exception as e:
        st.error(f"❌ 錯誤: {e}")

# Footer with stats
if st.session_state.get('learning_active'):
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    try:
        stats = st.session_state.ai_learning.knowledge_base.get_statistics()

        with col1:
            st.metric("📚 知識庫", f"{stats['total_items']} 項")

        with col2:
            st.metric("💬 本次對話", f"{len(st.session_state.messages)} 輪")

        with col3:
            st.metric("🏷️ 分類", f"{len(stats['categories'])} 類")
    except:
        pass
