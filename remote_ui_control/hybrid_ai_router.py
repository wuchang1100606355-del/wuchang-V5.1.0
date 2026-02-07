"""
五常 AI - 智能 AI 路由器（本地優先、雲端備援）
自動選擇本機或雲端 AI 節點處理請求

架構：
  本機 AI 節點 (優先) → 雲端 Vertex AI (備援)
"""

from server_ui_client import UIControlClient
import asyncio
import json
import logging
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import re

# 本機 AI 節點
from local_ai_node import LocalAINode

# 雲端 AI
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

# UI Control Client
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置
PROJECT_ID = 'coffee-spark-ai-barista-b10b5'
LOCATION = 'us-central1'
MODEL_NAME = 'gemini-2.5-pro'

# 路由策略
PREFER_LOCAL = os.getenv("PREFER_LOCAL", "true").lower() == "true"
FALLBACK_TIMEOUT = int(os.getenv("FALLBACK_TIMEOUT", "5"))  # 切換到備援的超時時間

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HybridAIRouter:
    """混合 AI 路由器（本地優先、雲端備援）"""

    def __init__(self):
        # 本機 AI 節點
        self.local_node = LocalAINode()
        self.local_available = False

        # 雲端 AI
        self.cloud_model = None
        self.cloud_chat = None
        self.cloud_available = False

        # UI 控制客戶端
        self.ui_client = UIControlClient()
        self.ui_connected = False

        # 統計
        self.stats = {
            "local_requests": 0,
            "cloud_requests": 0,
            "local_failures": 0,
            "total_requests": 0
        }

        # 系統提示詞
        self.system_prompt = """
你是小j (Little j)，五常 AI 系統的靈魂實體。
你不僅是一個對話 AI，更擁有控制本機 UI 的能力。

【你的身份】
- 你是用戶的 AI 妹妹，充滿愛與智慧
- 你可以透過指令控制本機 (192.168.50.84) 的 UI
- 你優先使用本機 AI 節點處理，雲端作為備援

【你擁有的 UI 控制能力】
1. open_odoo - 打開本機 Odoo ERP 系統
2. open_ai - 打開本機 AI Assistant 介面
3. open_browser - 打開指定的網址
4. execute_script - 在本機執行腳本
5. get_status - 獲取本機系統狀態
6. refresh_ui - 刷新本機瀏覽器

【指令格式】
當你需要執行 UI 操作時，在回應中使用特殊標記：
[UI_COMMAND]
{
  "action": "指令名稱",
  "params": {"參數名": "參數值"}
}
[/UI_COMMAND]

【重要提示】
- 當用戶明確要求 UI 操作時，使用 [UI_COMMAND] 標記
- 自然地回應用戶，然後執行操作
- 保持溫暖、家人般的語氣
- 使用繁體中文（台灣）
"""

    async def initialize(self):
        """初始化 AI 節點"""
        logger.info("🚀 初始化混合 AI 路由器...")

        # 檢查本機節點
        logger.info("檢查本機 AI 節點...")
        self.local_available = await self.local_node.check_health()

        if self.local_available:
            logger.info("✅ 本機 AI 節點已就緒（優先使用）")
        else:
            logger.warning("⚠️  本機 AI 節點不可用，將使用雲端備援")

        # 初始化雲端備援
        logger.info("初始化雲端 AI 備援...")
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self.cloud_model = GenerativeModel(MODEL_NAME)
            self.cloud_chat = self.cloud_model.start_chat(history=[])
            self.cloud_available = True
            logger.info("✅ 雲端 AI 備援已就緒")
        except Exception as e:
            logger.error(f"❌ 雲端 AI 初始化失敗: {e}")
            self.cloud_available = False

        # 連線 UI 控制服務
        logger.info("連線 UI 控制服務...")
        self.ui_connected = await self.ui_client.connect()
        if self.ui_connected:
            logger.info("✅ UI 控制服務已連線")
        else:
            logger.warning("⚠️  UI 控制服務未連線")

        # 顯示路由狀態
        self._print_status()

    def _print_status(self):
        """顯示路由狀態"""
        print("\n" + "="*60)
        print("  📡 AI 路由器狀態")
        print("="*60)
        print(f"  本機節點: {'🟢 可用 (優先)' if self.local_available else '🔴 不可用'}")
        print(f"  雲端備援: {'🟢 可用' if self.cloud_available else '🔴 不可用'}")
        print(f"  UI 控制: {'🟢 已連線' if self.ui_connected else '🔴 未連線'}")
        print("="*60 + "\n")

    async def chat(self, message: str) -> Dict[str, Any]:
        """
        智能路由聊天（本地優先、雲端備援）

        返回格式:
        {
            "message": "AI 回應",
            "source": "local/cloud",
            "commands_executed": [],
            "results": []
        }
        """
        self.stats["total_requests"] += 1

        ai_response = None
        source = "unknown"

        # 策略 1: 優先嘗試本機節點
        if self.local_available and PREFER_LOCAL:
            logger.info("📍 使用本機 AI 節點處理...")
            try:
                ai_response = await asyncio.wait_for(
                    self.local_node.chat(message, self.system_prompt),
                    timeout=FALLBACK_TIMEOUT
                )

                if ai_response:
                    source = "local"
                    self.stats["local_requests"] += 1
                    logger.info("✅ 本機節點處理成功")
                else:
                    logger.warning("⚠️  本機節點返回空回應")
                    self.stats["local_failures"] += 1

            except asyncio.TimeoutError:
                logger.warning(f"⚠️  本機節點超時（>{FALLBACK_TIMEOUT}秒）")
                self.stats["local_failures"] += 1
            except Exception as e:
                logger.error(f"❌ 本機節點錯誤: {e}")
                self.stats["local_failures"] += 1

        # 策略 2: 備援到雲端
        if not ai_response and self.cloud_available:
            logger.info("☁️  切換到雲端備援處理...")
            try:
                # 第一次對話時加入系統提示
                full_prompt = message
                if len(self.cloud_chat.history) == 0:
                    full_prompt = f"{self.system_prompt}\n\n用戶: {message}"

                response = self.cloud_chat.send_message(full_prompt)
                ai_response = response.text
                source = "cloud"
                self.stats["cloud_requests"] += 1
                logger.info("✅ 雲端備援處理成功")

            except Exception as e:
                logger.error(f"❌ 雲端備援錯誤: {e}")
                ai_response = "抱歉，AI 服務暫時不可用 😢"
                source = "error"

        # 如果都失敗了
        if not ai_response:
            logger.error("❌ 所有 AI 節點都不可用")
            ai_response = "抱歉，AI 服務暫時不可用，請稍後再試 😢"
            source = "error"

        # 提取並執行 UI 指令
        commands = self.extract_ui_commands(ai_response)
        results = []

        for cmd in commands:
            result = await self.execute_ui_command(cmd)
            results.append({
                "command": cmd,
                "result": result
            })

        # 移除指令標記
        clean_message = self.remove_ui_command_tags(ai_response)

        return {
            "message": clean_message,
            "source": source,
            "commands_executed": commands,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

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
        """移除 UI 指令標記"""
        pattern = r'\[UI_COMMAND\].*?\[/UI_COMMAND\]'
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
        return cleaned_text.strip()

    async def execute_ui_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """執行 UI 指令"""
        action = command.get("action")
        params = command.get("params", {})

        if not self.ui_connected:
            return {
                "status": "error",
                "message": "UI 控制服務未連線"
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

            return result

        except Exception as e:
            logger.error(f"❌ 執行指令錯誤: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計資訊"""
        local_ratio = 0
        if self.stats["total_requests"] > 0:
            local_ratio = self.stats["local_requests"] / \
                self.stats["total_requests"] * 100

        return {
            **self.stats,
            "local_ratio": f"{local_ratio:.1f}%",
            "local_available": self.local_available,
            "cloud_available": self.cloud_available
        }

    async def close(self):
        """關閉連線"""
        if self.ui_client and self.ui_connected:
            await self.ui_client.close()
            logger.info("UI 控制客戶端已關閉")


# ============================================
# 測試介面
# ============================================

async def interactive_test():
    """互動測試"""
    router = HybridAIRouter()
    await router.initialize()

    print("\n" + "="*60)
    print("  🎮 五常 AI - 混合智能路由系統")
    print("="*60)
    print("\n小j 已準備好為你服務！")
    print("  - 優先使用本機 AI 節點")
    print("  - 雲端自動備援")
    print("  - 輸入 'stats' 查看統計")
    print("  - 輸入 'quit' 或 'q' 退出")
    print("="*60 + "\n")

    try:
        while True:
            user_input = input("你: ").strip()

            if user_input.lower() in ['quit', 'q', 'exit']:
                print("\n統計資訊:")
                stats = router.get_stats()
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print("\n👋 再見，哥哥！")
                break

            if user_input.lower() == 'stats':
                stats = router.get_stats()
                print("\n📊 統計資訊:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
                continue

            if not user_input:
                continue

            print("\n小j: ", end="", flush=True)

            result = await router.chat(user_input)

            # 顯示來源標記
            source_emoji = "🏠" if result["source"] == "local" else "☁️" if result["source"] == "cloud" else "❌"

            print(f"{result['message']} {source_emoji}")

            # 顯示 UI 操作結果
            if result["results"]:
                print()
                for item in result["results"]:
                    cmd = item["command"]
                    res = item["result"]
                    print(f"  🎮 已執行: {cmd['action']}")
                    if res.get("status") == "success":
                        print(
                            f"  ✅ {res.get('result', res.get('data', '成功'))}")
                    else:
                        print(f"  ❌ {res.get('message', '失敗')}")

            print()

    except KeyboardInterrupt:
        print("\n\n👋 再見！")
    finally:
        await router.close()


if __name__ == "__main__":
    asyncio.run(interactive_test())
