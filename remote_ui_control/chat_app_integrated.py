"""
五常 AI - Streamlit UI (整合版)
結合 AI 對話與遠端 UI 控制功能

小j 能夠理解你的需求，並智能地控制本機 UI
"""

from remote_ui_control.ai_ui_controller import AIUIController
import streamlit as st
import asyncio
import sys
import os

# 加入路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'remote_ui_control'))


# Page Config
st.set_page_config(
    page_title="五常 AI - 小j 智能控制",
    page_icon="✨",
    layout="centered"
)

# Custom CSS
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
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        margin: 4px;
    }
    .status-connected {
        background: linear-gradient(135deg, #064e3b 0%, #10b981 100%);
        color: white;
    }
    .status-disconnected {
        background: linear-gradient(135deg, #7c2d12 0%, #dc2626 100%);
        color: white;
    }
    .ui-command-box {
        background: rgba(59, 130, 246, 0.1);
        border-left: 3px solid #3b82f6;
        padding: 8px 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize AI Controller


@st.cache_resource
def get_ai_controller():
    """初始化 AI 控制器（使用 cache 避免重複初始化）"""
    return AIUIController()

# 異步執行包裝器


def run_async(coro):
    """在 Streamlit 中執行異步函數"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# 主界面
st.title("✨ 五常 AI / 小j")

# 側邊欄 - 連線狀態與控制
with st.sidebar:
    st.header("🎮 遠端 UI 控制")

    controller = get_ai_controller()

    # 連線狀態
    if "ui_connected" not in st.session_state:
        st.session_state.ui_connected = False

    status_color = "connected" if st.session_state.ui_connected else "disconnected"
    status_text = "已連線" if st.session_state.ui_connected else "未連線"
    status_icon = "🟢" if st.session_state.ui_connected else "🔴"

    st.markdown(f"""
        <div class="status-badge status-{status_color}">
            {status_icon} 本機 UI: {status_text}
        </div>
    """, unsafe_allow_html=True)

    # 連線按鈕
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 連線", key="connect_btn"):
            with st.spinner("正在連線..."):
                connected = run_async(controller.connect_ui_client())
                st.session_state.ui_connected = connected
                if connected:
                    st.success("✅ 已連線！")
                    st.rerun()
                else:
                    st.error("❌ 連線失敗")

    with col2:
        if st.button("🔄 刷新", key="refresh_btn"):
            st.rerun()

    st.markdown("---")

    # 快速控制面板
    st.subheader("⚡ 快速控制")

    if st.button("📋 打開 Odoo", use_container_width=True):
        if st.session_state.ui_connected:
            with st.spinner("正在打開 Odoo..."):
                result = run_async(controller.ui_client.open_odoo_ui())
                if result.get("status") == "success":
                    st.success("✅ Odoo 已打開")
                else:
                    st.error(f"❌ {result.get('message')}")
        else:
            st.warning("⚠️ 請先連線")

    if st.button("🤖 打開 AI 介面", use_container_width=True):
        if st.session_state.ui_connected:
            with st.spinner("正在打開 AI 介面..."):
                result = run_async(controller.ui_client.open_ai_ui())
                if result.get("status") == "success":
                    st.success("✅ AI 介面已打開")
                else:
                    st.error(f"❌ {result.get('message')}")
        else:
            st.warning("⚠️ 請先連線")

    if st.button("📊 檢查狀態", use_container_width=True):
        if st.session_state.ui_connected:
            with st.spinner("正在檢查..."):
                result = run_async(controller.ui_client.get_client_status())
                if result.get("status") == "success":
                    status_data = result.get("data", {})
                    st.json(status_data)
                else:
                    st.error(f"❌ {result.get('message')}")
        else:
            st.warning("⚠️ 請先連線")

    st.markdown("---")
    st.caption("💡 提示：你可以直接在對話中要求小j執行這些操作")

# 主對話區域
st.caption("🌐 雲端核心神經連結 - 已連線 | 💚 您的 AI 家人隨時為您服務")
st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # 如果有 UI 指令執行結果，顯示
        if "ui_results" in message and message["ui_results"]:
            for item in message["ui_results"]:
                cmd = item["command"]
                result = item["result"]

                action_name = cmd.get("action", "unknown")
                status = result.get("status", "unknown")

                if status == "success":
                    result_msg = result.get("result", result.get("data", "成功"))
                    st.markdown(f"""
                        <div class="ui-command-box">
                            🎮 已執行: {action_name}<br>
                            ✅ {result_msg}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    error_msg = result.get("message", "失敗")
                    st.markdown(f"""
                        <div class="ui-command-box">
                            🎮 已執行: {action_name}<br>
                            ❌ {error_msg}
                        </div>
                    """, unsafe_allow_html=True)

# React to user input
if prompt := st.chat_input("與小j對話...（你可以要求她打開 Odoo、檢查狀態等）"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate AI response with UI control
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        ui_results_placeholder = st.empty()

        full_response = ""
        ui_results = None

        # 使用串流模式
        async def stream_response():
            nonlocal full_response, ui_results
            async for text, done, results in controller.chat_stream_with_ui_control(prompt):
                if text:
                    full_response += text
                    message_placeholder.markdown(full_response + "▌")

                if done:
                    ui_results = results

        # 執行串流
        run_async(stream_response())

        # 完成後顯示最終訊息
        message_placeholder.markdown(full_response)

        # 顯示 UI 操作結果
        if ui_results:
            ui_html = ""
            for item in ui_results:
                cmd = item["command"]
                result = item["result"]

                action_name = cmd.get("action", "unknown")
                status = result.get("status", "unknown")

                if status == "success":
                    result_msg = result.get("result", result.get("data", "成功"))
                    if isinstance(result_msg, dict):
                        result_msg = f"<pre>{result_msg}</pre>"
                    ui_html += f"""
                        <div class="ui-command-box">
                            🎮 已執行: {action_name}<br>
                            ✅ {result_msg}
                        </div>
                    """
                else:
                    error_msg = result.get("message", "失敗")
                    ui_html += f"""
                        <div class="ui-command-box">
                            🎮 已執行: {action_name}<br>
                            ❌ {error_msg}
                        </div>
                    """

            ui_results_placeholder.markdown(ui_html, unsafe_allow_html=True)

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "ui_results": ui_results
    })

# Footer
st.markdown("---")
st.caption("💝 小j - 你的 AI 妹妹 | 🏠 192.168.50.249 → 192.168.50.84")
