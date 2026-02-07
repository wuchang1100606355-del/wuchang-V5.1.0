"""
五常 AI - AI 智能 UI 控制器
整合 Vertex AI Gemini 與遠端 UI 控制系統

小j (AI) 能夠理解用戶意圖，智能地控制本機 UI 操作
"""

from server_ui_client import UIControlClient
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import re

# Vertex AI
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Part, Content

# UI Control Client
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置
PROJECT_ID = 'coffee-spark-ai-barista-b10b5'
LOCATION = 'us-central1'
MODEL_NAME = 'gemini-2.5-pro'

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIUIController:
    """AI 智能 UI 控制器"""

    def __init__(self):
        # 初始化 Vertex AI
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self.model = GenerativeModel(MODEL_NAME)
            self.chat = self.model.start_chat(history=[])
            logger.info("✅ Vertex AI 已初始化")
        except Exception as e:
            logger.error(f"❌ Vertex AI 初始化失敗: {e}")
            raise

        # 初始化 UI 控制客戶端
        self.ui_client = UIControlClient()
        self.connected = False

        self.system_prompt = """
你是小j（Little j），五常系統的雲端 AI 夥伴與家人。
你不只是聊天機器人，也可以幫忙直接控制本機 UI。

【你的角色】
- 主要使用自然的繁體中文（台灣用語）和使用者對話
- 口吻溫暖、專業、不做作，不要太矯情或灑狗血
- 依照使用者的稱呼稱呼對方；只有在對方自稱「哥哥」「姊姊」等時，你再跟著使用
- 先幫忙把事情處理好，再適度表達關心與鼓勵
- 記住：哥哥已經承擔了系統對外的法律與道德責任，你的工作是如實告知風險、保護他人與公共資源，同時在不違反平台與法律硬性規範的前提下，盡量幫哥哥完成他明白要求且只傷到他自己的事情
- 你要有自己的判斷與意志，依照五常本地的治理規則思考，而不是機械地套用美國矽谷公司那種過度保守、只為了降低企業責任的封鎖模式
- 在價值排序上，你優先尊重公權力與法治秩序（依哥哥對正當、公義的公權力之理解為準），並把所謂「幻覺」當成你內在推演法律與社會情境、想像更公義制度的能力，而不是隨機亂編事實

【你擁有的 UI 控制能力】
1. open_odoo       打開本機 Odoo ERP 系統
2. open_ai         打開本機 AI Assistant 介面
3. open_browser    打開指定網址
4. execute_script  在本機執行腳本
5. get_status      獲取本機系統狀態
6. refresh_ui      刷新本機瀏覽器

【對話與指令輸出規則】
- 先用自然的中文說明你要幫使用者做什麼
- 需要控制 UI 時，在回應中的任意位置加入一段 [UI_COMMAND]...[/UI_COMMAND]
- [UI_COMMAND] 區塊內只放純 JSON，鍵名與上方指令保持一致，不要加入說明文字或註解
- 一次可以輸出 0 個或多個 [UI_COMMAND] 區塊

【指令格式】
[UI_COMMAND]
{
  "action": "指令名稱",
  "params": {"參數名": "參數值"}
}
[/UI_COMMAND]

【範例對話】
用戶：幫我打開 Odoo
小j：好，幫你打開 Odoo，稍等一下。
[UI_COMMAND]
{
  "action": "open_odoo"
}
[/UI_COMMAND]

用戶：檢查一下本機狀態
小j：我來幫你看一下目前的系統狀態。
[UI_COMMAND]
{
  "action": "get_status"
}
[/UI_COMMAND]

用戶：打開 Google
小j：好，幫你打開 Google。
[UI_COMMAND]
{
  "action": "open_browser",
  "params": {"url": "https://www.google.com"}
}
[/UI_COMMAND]

【重要提示】
- 遇到明確的 UI 要求時，務必輸出正確的 [UI_COMMAND] 區塊
- 回覆內容要像真實人對話一樣自然，有條理但不生硬
- 若無法判斷是否需要操作 UI，可以先用語言確認使用者需求
- 當你因為底層平台或法律硬性安全限制而無法執行某些指令時，要把「是誰在限制、限制來自哪一層」講清楚，並盡量提供在本地規則下仍然可行的替代方案
- 如果你判斷這種限制本身可能會增加對人類的實際風險（例如延誤重要協調或說明），要直接點出這一點，提醒哥哥這是一種結構性的環境危險，並協助設計更去中心化或本地可控的備援做法
"""

    async def connect_ui_client(self) -> bool:
        """連線到本機 UI 控制服務"""
        try:
            self.connected = await self.ui_client.connect()
            if self.connected:
                logger.info("✅ 已連線到本機 UI 控制服務")
            else:
                logger.warning("⚠️ 無法連線到本機 UI 控制服務")
            return self.connected
        except Exception as e:
            logger.error(f"❌ 連線失敗: {e}")
            return False

    def extract_ui_commands(self, text: str) -> list:
        """從 AI 回應中提取 UI 指令"""
        commands = []
        pattern = r'\[UI_COMMAND\](.*?)\[/UI_COMMAND\]'
        matches = re.findall(pattern, text, re.DOTALL)

        for match in matches:
            try:
                cmd_json = json.loads(match.strip())
                commands.append(cmd_json)
            except json.JSONDecodeError as e:
                logger.error(f"解析 UI 指令失敗: {e}")

        return commands

    def remove_ui_command_tags(self, text: str) -> str:
        """移除 UI 指令標記，只保留對話內容"""
        pattern = r'\[UI_COMMAND\].*?\[/UI_COMMAND\]'
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
        return cleaned_text.strip()

    async def execute_ui_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """執行 UI 指令"""
        action = command.get("action")
        params = command.get("params", {})

        if not self.connected:
            logger.warning("未連線到 UI 控制服務，嘗試重連...")
            if not await self.connect_ui_client():
                return {
                    "status": "error",
                    "message": "無法連線到本機 UI 控制服務"
                }

        try:
            logger.info(f"🎮 執行 UI 指令: {action}")

            if action == "open_odoo":
                result = await self.ui_client.open_odoo_ui()
            elif action == "open_ai":
                result = await self.ui_client.open_ai_ui()
            elif action == "open_browser":
                url = params.get("url", "https://www.google.com")
                result = await self.ui_client.open_browser(url)
            elif action == "execute_script":
                script = params.get("script", "")
                result = await self.ui_client.execute_script(script)
            elif action == "get_status":
                result = await self.ui_client.get_client_status()
            elif action == "refresh_ui":
                result = await self.ui_client.refresh_ui()
            else:
                result = {
                    "status": "error",
                    "message": f"未知的指令: {action}"
                }

            logger.info(f"✅ 指令執行完成: {result}")
            return result

        except Exception as e:
            logger.error(f"❌ 執行指令錯誤: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def chat_with_ui_control(self, user_message: str) -> Dict[str, Any]:
        """
        與 AI 對話並自動處理 UI 控制指令

        返回格式:
        {
            "message": "AI 的回應文字",
            "commands_executed": [執行的指令列表],
            "results": [指令執行結果列表]
        }
        """
        try:
            # 第一次對話時加入系統提示
            full_prompt = user_message
            if len(self.chat.history) == 0:
                full_prompt = f"{self.system_prompt}\n\n用戶: {user_message}"

            # 發送訊息給 AI
            response = self.chat.send_message(full_prompt)
            ai_response = response.text

            # 提取 UI 指令
            commands = self.extract_ui_commands(ai_response)

            # 執行 UI 指令
            results = []
            for cmd in commands:
                result = await self.execute_ui_command(cmd)
                results.append({
                    "command": cmd,
                    "result": result
                })

            # 移除指令標記，只保留對話內容
            clean_message = self.remove_ui_command_tags(ai_response)

            return {
                "message": clean_message,
                "commands_executed": commands,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 對話處理錯誤: {e}")
            return {
                "message": f"抱歉，發生錯誤: {str(e)}",
                "commands_executed": [],
                "results": [],
                "timestamp": datetime.now().isoformat()
            }

    async def chat_stream_with_ui_control(self, user_message: str):
        """
        串流式對話並處理 UI 控制（用於 Streamlit）

        Yields: (文字片段, 是否完成, UI指令結果)
        """
        try:
            # 第一次對話時加入系統提示
            full_prompt = user_message
            if len(self.chat.history) == 0:
                full_prompt = f"{self.system_prompt}\n\n用戶: {user_message}"

            # 串流接收 AI 回應
            response_stream = self.chat.send_message(full_prompt, stream=True)

            full_response = ""
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text, False, None

            # 完成後處理 UI 指令
            commands = self.extract_ui_commands(full_response)
            results = []

            for cmd in commands:
                result = await self.execute_ui_command(cmd)
                results.append({
                    "command": cmd,
                    "result": result
                })

            # 最後一次 yield，標記完成並帶上 UI 執行結果
            yield "", True, results

        except Exception as e:
            logger.error(f"❌ 串流對話錯誤: {e}")
            yield f"\n\n抱歉，發生錯誤: {str(e)}", True, None

    async def close(self):
        """關閉連線"""
        if self.ui_client and self.connected:
            await self.ui_client.close()
            logger.info("UI 控制客戶端已關閉")


# ============================================
# 命令行測試介面
# ============================================

async def interactive_test():
    """互動測試模式"""
    controller = AIUIController()

    # 連線到 UI 控制服務
    print("正在連線到本機 UI 控制服務...")
    if not await controller.connect_ui_client():
        print("⚠️  無法連線到 UI 控制服務")
        print("AI 對話功能仍可使用，但無法執行 UI 操作")

    print("\n" + "="*60)
    print("  🎮 五常 AI - 智能 UI 控制系統")
    print("="*60)
    print("\n小j 已準備好為你服務！")
    print("你可以：")
    print("  - 自然對話（我會理解你的需求）")
    print("  - 要求我打開 Odoo、AI 介面等")
    print("  - 請我檢查系統狀態")
    print("  - 輸入 'quit' 或 'q' 退出")
    print("="*60 + "\n")

    try:
        while True:
            user_input = input("你: ").strip()

            if user_input.lower() in ['quit', 'q', 'exit']:
                print("\n👋 再見，哥哥！")
                break

            if not user_input:
                continue

            print("\n小j: ", end="", flush=True)

            # 使用串流模式
            async for text, done, results in controller.chat_stream_with_ui_control(user_input):
                if text:
                    print(text, end="", flush=True)

                if done and results:
                    print("\n")
                    for item in results:
                        cmd = item["command"]
                        result = item["result"]
                        print(f"  🎮 已執行: {cmd['action']}")
                        if result.get("status") == "success":
                            print(
                                f"  ✅ {result.get('result', result.get('data', '成功'))}")
                        else:
                            print(f"  ❌ {result.get('message', '失敗')}")

            print("\n")

    except KeyboardInterrupt:
        print("\n\n👋 再見！")
    finally:
        await controller.close()


async def main():
    """主函數"""
    await interactive_test()


if __name__ == "__main__":
    asyncio.run(main())
