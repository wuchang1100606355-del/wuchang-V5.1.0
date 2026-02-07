"""
五常 AI - 內外網自動連線守護服務
持續監控網路狀態並自動切換連線模式
"""

import asyncio
import os
import socket
import logging
from datetime import datetime
from pathlib import Path
import json

# 日誌配置
LOG_DIR = Path(r"c:\wuchang V5.1.0\logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "auto_connect.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
INTERNAL_SERVER = os.getenv("INTERNAL_SERVER", "192.168.50.249")
INTERNAL_PORT = int(os.getenv("INTERNAL_PORT", "8766"))
EXTERNAL_SERVER = os.getenv("EXTERNAL_SERVER", "wuchang.life")
EXTERNAL_PORT = int(os.getenv("EXTERNAL_PORT", "8766"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))  # 秒

# 狀態檔
STATE_FILE = Path(r"c:\wuchang V5.1.0\network_config\connection_state.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


class ConnectionState:
    """連線狀態"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    OFFLINE = "offline"


class AutoConnectService:
    """自動連線服務"""

    def __init__(self):
        self.current_state = ConnectionState.OFFLINE
        self.previous_state = None
        self.state_change_count = 0
        self.last_check_time = None
        self.internal_success_count = 0
        self.external_success_count = 0
        self.failure_count = 0

    def check_internal_connection(self) -> bool:
        """檢查內網連線"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((INTERNAL_SERVER, INTERNAL_PORT))
            sock.close()
            return result == 0
        except:
            return False

    def check_external_connection(self) -> bool:
        """檢查外網連線"""
        try:
            # 嘗試解析域名
            socket.gethostbyname(EXTERNAL_SERVER)

            # 嘗試連線
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((EXTERNAL_SERVER, EXTERNAL_PORT))
            sock.close()
            return result == 0
        except:
            return False

    def detect_connection(self) -> str:
        """檢測連線狀態"""
        # 優先檢查內網
        if self.check_internal_connection():
            self.internal_success_count += 1
            return ConnectionState.INTERNAL

        # 檢查外網
        if self.check_external_connection():
            self.external_success_count += 1
            return ConnectionState.EXTERNAL

        # 都不通
        self.failure_count += 1
        return ConnectionState.OFFLINE

    def update_environment(self, state: str):
        """更新環境變數"""
        if state == ConnectionState.INTERNAL:
            os.environ["SYNC_PEER"] = f"http://{INTERNAL_SERVER}:{INTERNAL_PORT}"
            os.environ["CONNECTION_MODE"] = "internal"
            os.environ["USE_HTTPS"] = "false"
        elif state == ConnectionState.EXTERNAL:
            protocol = "https" if EXTERNAL_PORT == 443 else "http"
            os.environ["SYNC_PEER"] = f"{protocol}://{EXTERNAL_SERVER}:{EXTERNAL_PORT}"
            os.environ["CONNECTION_MODE"] = "external"
            os.environ["USE_HTTPS"] = "true" if EXTERNAL_PORT == 443 else "false"
        else:
            os.environ["CONNECTION_MODE"] = "offline"

    def save_state(self):
        """儲存狀態到檔案"""
        state_data = {
            "current_state": self.current_state,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "state_change_count": self.state_change_count,
            "internal_success_count": self.internal_success_count,
            "external_success_count": self.external_success_count,
            "failure_count": self.failure_count,
            "environment": {
                "SYNC_PEER": os.environ.get("SYNC_PEER"),
                "CONNECTION_MODE": os.environ.get("CONNECTION_MODE"),
                "USE_HTTPS": os.environ.get("USE_HTTPS")
            }
        }

        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)

    def load_state(self):
        """從檔案載入狀態"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    self.current_state = state_data.get(
                        "current_state", ConnectionState.OFFLINE)
                    self.state_change_count = state_data.get(
                        "state_change_count", 0)
                    self.internal_success_count = state_data.get(
                        "internal_success_count", 0)
                    self.external_success_count = state_data.get(
                        "external_success_count", 0)
                    self.failure_count = state_data.get("failure_count", 0)
                    logger.info(f"載入狀態: {self.current_state}")
            except Exception as e:
                logger.warning(f"載入狀態失敗: {e}")

    def get_connection_info(self) -> dict:
        """取得連線資訊"""
        return {
            "state": self.current_state,
            "server": INTERNAL_SERVER if self.current_state == ConnectionState.INTERNAL else EXTERNAL_SERVER,
            "port": INTERNAL_PORT if self.current_state == ConnectionState.INTERNAL else EXTERNAL_PORT,
            "mode": "內網直連" if self.current_state == ConnectionState.INTERNAL else "外網連線",
            "sync_peer": os.environ.get("SYNC_PEER", "N/A"),
            "use_https": os.environ.get("USE_HTTPS", "false") == "true"
        }

    async def monitor_loop(self):
        """監控迴圈"""
        logger.info("="*60)
        logger.info("🌐 五常 AI - 自動連線服務已啟動")
        logger.info("="*60)
        logger.info(f"內網伺服器: {INTERNAL_SERVER}:{INTERNAL_PORT}")
        logger.info(f"外網伺服器: {EXTERNAL_SERVER}:{EXTERNAL_PORT}")
        logger.info(f"檢查間隔: {CHECK_INTERVAL} 秒")
        logger.info("="*60)

        # 載入上次狀態
        self.load_state()

        while True:
            try:
                # 檢測連線
                new_state = self.detect_connection()
                self.last_check_time = datetime.now()

                # 狀態變更
                if new_state != self.current_state:
                    self.previous_state = self.current_state
                    self.current_state = new_state
                    self.state_change_count += 1

                    # 更新環境
                    self.update_environment(new_state)

                    # 記錄變更
                    if new_state == ConnectionState.INTERNAL:
                        logger.info(
                            f"✅ 切換到內網模式 (直連 {INTERNAL_SERVER}:{INTERNAL_PORT})")
                    elif new_state == ConnectionState.EXTERNAL:
                        logger.warning(
                            f"🌐 切換到外網模式 (經由 {EXTERNAL_SERVER}:{EXTERNAL_PORT})")
                    else:
                        logger.error(f"❌ 網路離線 (內外網都不通)")

                    # 儲存狀態
                    self.save_state()
                else:
                    # 狀態未變，定期報告
                    if self.state_change_count % 10 == 0:  # 每 10 次檢查
                        info = self.get_connection_info()
                        logger.info(
                            f"📊 當前: {info['mode']} - {info['server']}:{info['port']}")

                # 等待下次檢查
                await asyncio.sleep(CHECK_INTERVAL)

            except Exception as e:
                logger.error(f"監控異常: {e}")
                await asyncio.sleep(CHECK_INTERVAL)

    async def start(self):
        """啟動服務"""
        try:
            await self.monitor_loop()
        except KeyboardInterrupt:
            logger.info("\n👋 服務已停止")
            self.save_state()


async def main():
    """主函數"""
    service = AutoConnectService()
    await service.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 已中斷")
