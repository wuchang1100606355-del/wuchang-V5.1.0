"""
五常 AI - Server 端 UI 控制客戶端
Server 主動連線機制 - Server 端 (192.168.50.249)

Server 主動連線到本機 (192.168.50.84)，發送 UI 操作指令
"""

import asyncio
import websockets
import json
import logging
import hmac
import hashlib
import time
from datetime import datetime
import os

# 配置
LOCAL_CLIENT_IP = "192.168.50.84"  # 本機 IP
LOCAL_CLIENT_PORT = 8765
SERVER_IP = "192.168.50.249"  # 本 Server IP
SHARED_SECRET = os.getenv("WUCHANG_SECRET", "wuchang-ui-secret-2026")
RECONNECT_INTERVAL = 5  # 重連間隔（秒）

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UIControlClient:
    """Server 端 UI 控制客戶端"""

    def __init__(self):
        self.websocket = None
        self.connected = False
        self.command_queue = asyncio.Queue()

    def generate_token(self) -> tuple:
        """生成認證 Token"""
        timestamp = str(time.time())
        token = hmac.new(
            SHARED_SECRET.encode(),
            f"{SERVER_IP}:{timestamp}".encode(),
            hashlib.sha256
        ).hexdigest()
        return token, timestamp

    async def connect(self) -> bool:
        """連線到本機 UI 控制服務"""
        try:
            uri = f"ws://{LOCAL_CLIENT_IP}:{LOCAL_CLIENT_PORT}"
            logger.info(f"🔌 嘗試連線到: {uri}")

            self.websocket = await websockets.connect(
                uri,
                ping_interval=30,
                ping_timeout=10
            )

            # 發送認證
            token, timestamp = self.generate_token()
            auth_msg = {
                "token": token,
                "timestamp": timestamp,
                "server_ip": SERVER_IP
            }

            await self.websocket.send(json.dumps(auth_msg))

            # 等待認證響應
            response = await asyncio.wait_for(self.websocket.recv(), timeout=10)
            auth_result = json.loads(response)

            if auth_result.get("status") == "success":
                self.connected = True
                logger.info(f"✅ 已成功連線到本機: {LOCAL_CLIENT_IP}")
                return True
            else:
                logger.error(f"❌ 認證失敗: {auth_result.get('message')}")
                return False

        except asyncio.TimeoutError:
            logger.error("認證超時")
            return False
        except Exception as e:
            logger.error(f"連線失敗: {e}")
            return False

    async def send_command(self, cmd_type: str, payload: dict = None) -> dict:
        """發送 UI 操作指令"""
        if not self.connected or not self.websocket:
            return {"status": "error", "message": "未連線"}

        try:
            command = {
                "type": cmd_type,
                "payload": payload or {},
                "timestamp": datetime.now().isoformat()
            }

            await self.websocket.send(json.dumps(command))

            # 等待響應
            response = await asyncio.wait_for(self.websocket.recv(), timeout=30)
            return json.loads(response)

        except asyncio.TimeoutError:
            logger.error("指令執行超時")
            return {"status": "error", "message": "超時"}
        except Exception as e:
            logger.error(f"發送指令錯誤: {e}")
            self.connected = False
            return {"status": "error", "message": str(e)}

    async def open_odoo_ui(self):
        """打開本機 Odoo UI"""
        logger.info("📋 請求打開 Odoo UI...")
        result = await self.send_command("open_odoo")
        logger.info(f"結果: {result}")
        return result

    async def open_ai_ui(self):
        """打開本機 AI Assistant UI"""
        logger.info("🤖 請求打開 AI Assistant UI...")
        result = await self.send_command("open_ai")
        logger.info(f"結果: {result}")
        return result

    async def open_browser(self, url: str):
        """打開指定 URL"""
        logger.info(f"🌐 請求打開 URL: {url}")
        result = await self.send_command("open_browser", {"url": url})
        logger.info(f"結果: {result}")
        return result

    async def execute_script(self, script: str):
        """在本機執行腳本"""
        logger.info(f"⚙️ 請求執行腳本...")
        result = await self.send_command("execute_script", {"script": script})
        logger.info(f"結果: {result}")
        return result

    async def get_client_status(self):
        """獲取本機狀態"""
        logger.info("📊 請求本機狀態...")
        result = await self.send_command("get_status")
        logger.info(f"狀態: {result}")
        return result

    async def refresh_ui(self):
        """刷新本機 UI"""
        logger.info("🔄 請求刷新 UI...")
        result = await self.send_command("refresh_ui")
        logger.info(f"結果: {result}")
        return result

    async def maintain_connection(self):
        """維護連線（自動重連）"""
        while True:
            if not self.connected:
                logger.info("🔄 嘗試重新連線...")
                success = await self.connect()
                if not success:
                    logger.warning(f"重連失敗，{RECONNECT_INTERVAL} 秒後重試")
                    await asyncio.sleep(RECONNECT_INTERVAL)
                    continue

            # 處理指令佇列
            try:
                # 可以在這裡加入定時任務
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"維護連線錯誤: {e}")
                self.connected = False

    async def close(self):
        """關閉連線"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("連線已關閉")


# ============================================
# 命令行界面（用於測試和手動控制）
# ============================================

async def interactive_mode():
    """互動模式"""
    client = UIControlClient()

    # 連線
    if not await client.connect():
        logger.error("無法連線到本機，請確認本機 UI 控制服務已啟動")
        return

    print("\n" + "="*50)
    print("🎮 五常 AI - Server 端 UI 控制面板")
    print("="*50)
    print("\n可用指令:")
    print("  1. open_odoo    - 打開 Odoo UI")
    print("  2. open_ai      - 打開 AI Assistant UI")
    print("  3. open_url     - 打開指定 URL")
    print("  4. status       - 獲取本機狀態")
    print("  5. refresh      - 刷新 UI")
    print("  6. exec         - 執行腳本")
    print("  q. quit         - 退出")
    print("="*50 + "\n")

    try:
        while True:
            cmd = input("請輸入指令 (1-6/q): ").strip().lower()

            if cmd in ['q', 'quit', 'exit']:
                break
            elif cmd in ['1', 'open_odoo']:
                await client.open_odoo_ui()
            elif cmd in ['2', 'open_ai']:
                await client.open_ai_ui()
            elif cmd in ['3', 'open_url']:
                url = input("請輸入 URL: ").strip()
                await client.open_browser(url)
            elif cmd in ['4', 'status']:
                await client.get_client_status()
            elif cmd in ['5', 'refresh']:
                await client.refresh_ui()
            elif cmd in ['6', 'exec']:
                script = input("請輸入要執行的腳本: ").strip()
                await client.execute_script(script)
            else:
                print("❌ 未知指令")

            print()

    except KeyboardInterrupt:
        print("\n\n👋 再見！")
    finally:
        await client.close()


async def main():
    """主函數"""
    import sys

    if len(sys.argv) > 1:
        # 命令行模式
        client = UIControlClient()
        if not await client.connect():
            logger.error("連線失敗")
            return

        cmd = sys.argv[1]
        if cmd == "open_odoo":
            await client.open_odoo_ui()
        elif cmd == "open_ai":
            await client.open_ai_ui()
        elif cmd == "status":
            await client.get_client_status()
        elif cmd == "refresh":
            await client.refresh_ui()
        else:
            logger.error(f"未知指令: {cmd}")

        await client.close()
    else:
        # 互動模式
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
