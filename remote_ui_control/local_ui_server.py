"""
五常 AI - 本機 UI 控制服務端
Server 主動連線機制 - 本機端

本機監聽 WebSocket 連線，接收來自 Server (192.168.50.249) 的 UI 操作指令
"""

import asyncio
import websockets
import json
import logging
import hmac
import hashlib
import time
from datetime import datetime
from pathlib import Path
import subprocess
import os

# 配置
LOCAL_WS_HOST = "0.0.0.0"  # 監聽所有網卡
LOCAL_WS_PORT = 8765
SERVER_IP = "192.168.50.249"
SHARED_SECRET = os.getenv("WUCHANG_SECRET", "wuchang-ui-secret-2026")

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UIControlServer:
    """本機 UI 控制服務"""

    def __init__(self):
        self.connected_clients = set()
        self.session_tokens = {}

    def verify_token(self, token: str, timestamp: str) -> bool:
        """驗證來自 Server 的認證 Token"""
        try:
            # 時間戳檢查（防止重放攻擊，5分鐘有效期）
            token_time = float(timestamp)
            current_time = time.time()
            if abs(current_time - token_time) > 300:
                logger.warning(f"Token 過期: {current_time - token_time} 秒")
                return False

            # HMAC 驗證
            expected_token = hmac.new(
                SHARED_SECRET.encode(),
                f"{SERVER_IP}:{timestamp}".encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(token, expected_token)
        except Exception as e:
            logger.error(f"Token 驗證錯誤: {e}")
            return False

    async def handle_ui_command(self, command: dict) -> dict:
        """處理 UI 操作指令"""
        cmd_type = command.get("type")
        payload = command.get("payload", {})

        logger.info(f"收到指令: {cmd_type}")

        try:
            if cmd_type == "open_browser":
                # 打開瀏覽器
                url = payload.get("url", "http://localhost:8069")
                result = self.open_browser(url)
                return {"status": "success", "result": result}

            elif cmd_type == "open_odoo":
                # 打開 Odoo UI
                result = self.open_browser("http://localhost:8069")
                return {"status": "success", "result": result}

            elif cmd_type == "open_ai":
                # 打開 AI Assistant UI
                result = self.open_browser("http://localhost:8080")
                return {"status": "success", "result": result}

            elif cmd_type == "execute_script":
                # 執行腳本
                script = payload.get("script")
                result = await self.execute_script(script)
                return {"status": "success", "result": result}

            elif cmd_type == "get_status":
                # 獲取系統狀態
                status = self.get_system_status()
                return {"status": "success", "data": status}

            elif cmd_type == "refresh_ui":
                # 刷新 UI（發送 F5）
                result = self.refresh_browser()
                return {"status": "success", "result": result}

            else:
                return {"status": "error", "message": f"未知指令: {cmd_type}"}

        except Exception as e:
            logger.error(f"指令執行錯誤: {e}")
            return {"status": "error", "message": str(e)}

    def open_browser(self, url: str) -> str:
        """打開瀏覽器"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(url)
            else:  # Linux/Mac
                subprocess.run(['xdg-open', url], check=True)
            return f"已打開: {url}"
        except Exception as e:
            logger.error(f"打開瀏覽器失敗: {e}")
            return f"錯誤: {str(e)}"

    async def execute_script(self, script: str) -> str:
        """執行 PowerShell 腳本"""
        try:
            if os.name == 'nt':  # Windows
                proc = await asyncio.create_subprocess_shell(
                    f'powershell -Command "{script}"',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:  # Linux
                proc = await asyncio.create_subprocess_shell(
                    script,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                return stdout.decode('utf-8', errors='ignore')
            else:
                return f"錯誤: {stderr.decode('utf-8', errors='ignore')}"
        except Exception as e:
            return f"執行失敗: {str(e)}"

    def refresh_browser(self) -> str:
        """發送 F5 刷新瀏覽器"""
        try:
            if os.name == 'nt':  # Windows
                import pyautogui
                pyautogui.press('f5')
                return "已發送 F5 刷新"
            else:
                return "Linux 環境需要額外配置"
        except Exception as e:
            return f"刷新失敗: {str(e)}"

    def get_system_status(self) -> dict:
        """獲取系統狀態"""
        return {
            "timestamp": datetime.now().isoformat(),
            "hostname": os.getenv("COMPUTERNAME", "unknown"),
            "platform": os.name,
            "connected_clients": len(self.connected_clients),
            "services": {
                "odoo": self.check_service_port(8069),
                "ai_assistant": self.check_service_port(8080),
                "kuma": self.check_service_port(3001)
            }
        }

    def check_service_port(self, port: int) -> bool:
        """檢查端口是否開啟"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False

    async def handle_client(self, websocket, path):
        """處理客戶端連線"""
        client_addr = websocket.remote_address
        logger.info(f"新連線來自: {client_addr}")

        try:
            # 等待認證
            auth_msg = await asyncio.wait_for(websocket.recv(), timeout=10)
            auth_data = json.loads(auth_msg)

            # 驗證 Token
            token = auth_data.get("token")
            timestamp = auth_data.get("timestamp")

            if not self.verify_token(token, timestamp):
                await websocket.send(json.dumps({
                    "type": "auth_response",
                    "status": "failed",
                    "message": "認證失敗"
                }))
                await websocket.close()
                return

            # 認證成功
            self.connected_clients.add(websocket)
            await websocket.send(json.dumps({
                "type": "auth_response",
                "status": "success",
                "message": "認證成功，已建立連線"
            }))

            logger.info(f"✅ Server {client_addr} 認證成功")

            # 處理指令
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self.handle_ui_command(data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 解析錯誤: {e}")
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": "無效的 JSON 格式"
                    }))
                except Exception as e:
                    logger.error(f"處理訊息錯誤: {e}")
                    await websocket.send(json.dumps({
                        "status": "error",
                        "message": str(e)
                    }))

        except asyncio.TimeoutError:
            logger.warning(f"認證超時: {client_addr}")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"連線關閉: {client_addr}")
        except Exception as e:
            logger.error(f"處理客戶端錯誤: {e}")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"客戶端已斷開: {client_addr}")

    async def start(self):
        """啟動服務"""
        logger.info(f"🚀 本機 UI 控制服務啟動")
        logger.info(f"📡 監聽: {LOCAL_WS_HOST}:{LOCAL_WS_PORT}")
        logger.info(f"🔐 允許來自: {SERVER_IP}")

        async with websockets.serve(
            self.handle_client,
            LOCAL_WS_HOST,
            LOCAL_WS_PORT,
            ping_interval=30,
            ping_timeout=10
        ):
            await asyncio.Future()  # 永久運行


async def main():
    """主函數"""
    server = UIControlServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("服務已停止")
    except Exception as e:
        logger.error(f"服務錯誤: {e}")


if __name__ == "__main__":
    asyncio.run(main())
