"""
五常 AI - Google Workspace 整合服務
支援 Drive、Gmail、Calendar 等服務的區域網路與雲端同步
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, List
import aiohttp
from datetime import datetime

# Google Workspace 配置
WORKSPACE_DOMAIN = os.getenv("WORKSPACE_DOMAIN", "wuchang.life")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")

# 本地同步目錄
WORKSPACE_SYNC_DIR = Path(r"c:\wuchang V5.1.0\workspace\google_workspace")
DRIVE_SYNC_DIR = WORKSPACE_SYNC_DIR / "drive"
GMAIL_BACKUP_DIR = WORKSPACE_SYNC_DIR / "gmail"
CALENDAR_SYNC_DIR = WORKSPACE_SYNC_DIR / "calendar"

# API 端點
GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_DRIVE_API = "https://www.googleapis.com/drive/v3"
GOOGLE_GMAIL_API = "https://www.googleapis.com/gmail/v1"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"


class GoogleWorkspaceClient:
    """Google Workspace 客戶端"""

    def __init__(self):
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self._session: Optional[aiohttp.ClientSession] = None

        # 確保目錄存在
        DRIVE_SYNC_DIR.mkdir(parents=True, exist_ok=True)
        GMAIL_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        CALENDAR_SYNC_DIR.mkdir(parents=True, exist_ok=True)

    async def get_session(self) -> aiohttp.ClientSession:
        """取得 HTTP session"""
        if self._session and not self._session.closed:
            return self._session

        self._session = aiohttp.ClientSession()
        return self._session

    async def refresh_access_token(self) -> bool:
        """刷新 access token"""
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REFRESH_TOKEN:
            print("❌ 缺少 Google OAuth 憑證")
            return False

        try:
            session = await self.get_session()
            data = {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": GOOGLE_REFRESH_TOKEN,
                "grant_type": "refresh_token"
            }

            async with session.post(GOOGLE_OAUTH_TOKEN_URL, data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.access_token = result.get("access_token")
                    expires_in = result.get("expires_in", 3600)
                    self.token_expires_at = datetime.now().timestamp() + expires_in
                    print(f"✅ Token 刷新成功，有效期 {expires_in} 秒")
                    return True
                else:
                    error = await resp.text()
                    print(f"❌ Token 刷新失敗: {error}")
                    return False
        except Exception as e:
            print(f"❌ Token 刷新異常: {e}")
            return False

    async def ensure_token(self):
        """確保 token 有效"""
        if not self.access_token or datetime.now().timestamp() >= self.token_expires_at - 300:
            await self.refresh_access_token()

    async def list_drive_files(self, folder_id: str = "root", page_size: int = 100) -> List[Dict]:
        """列出 Drive 文件"""
        await self.ensure_token()

        session = await self.get_session()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "pageSize": page_size,
            "fields": "files(id, name, mimeType, size, modifiedTime, webViewLink)"
        }

        try:
            url = f"{GOOGLE_DRIVE_API}/files"
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("files", [])
                else:
                    error = await resp.text()
                    print(f"❌ 列出文件失敗: {error}")
                    return []
        except Exception as e:
            print(f"❌ 列出文件異常: {e}")
            return []

    async def download_drive_file(self, file_id: str, save_path: Path) -> bool:
        """下載 Drive 文件"""
        await self.ensure_token()

        session = await self.get_session()
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            url = f"{GOOGLE_DRIVE_API}/files/{file_id}?alt=media"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(save_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(1024 * 1024):
                            f.write(chunk)
                    print(f"✅ 下載完成: {save_path.name}")
                    return True
                else:
                    error = await resp.text()
                    print(f"❌ 下載失敗: {error}")
                    return False
        except Exception as e:
            print(f"❌ 下載異常: {e}")
            return False

    async def sync_drive_folder(self, folder_id: str = "root", local_path: Path = DRIVE_SYNC_DIR):
        """同步 Drive 資料夾"""
        print(f"\n🔄 同步 Google Drive 資料夾...")
        files = await self.list_drive_files(folder_id)

        for file in files:
            file_name = file.get("name")
            file_id = file.get("id")
            mime_type = file.get("mimeType")

            # 跳過資料夾（可遞迴處理）
            if mime_type == "application/vnd.google-apps.folder":
                print(f"📁 資料夾: {file_name}")
                continue

            # 下載文件
            save_path = local_path / file_name
            if not save_path.exists():
                print(f"⬇️  下載: {file_name}")
                await self.download_drive_file(file_id, save_path)
            else:
                print(f"⏭️  跳過: {file_name} (已存在)")

    async def close(self):
        """關閉 session"""
        if self._session and not self._session.closed:
            await self._session.close()


class NetworkAutoConnect:
    """內外網自動連線服務"""

    def __init__(self):
        self.is_internal = False
        self.connection_mode = "unknown"

    def detect_network(self) -> str:
        """檢測當前網路環境"""
        import socket

        try:
            # 嘗試連線內網 IP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("192.168.50.249", 8766))
            sock.close()

            if result == 0:
                self.is_internal = True
                self.connection_mode = "internal"
                return "internal"
            else:
                self.is_internal = False
                self.connection_mode = "external"
                return "external"
        except:
            self.is_internal = False
            self.connection_mode = "external"
            return "external"

    def get_connection_config(self) -> Dict:
        """取得連線配置"""
        mode = self.detect_network()

        if mode == "internal":
            return {
                "mode": "internal",
                "server": "192.168.50.249",
                "port": 8766,
                "use_https": False,
                "description": "內網直連"
            }
        else:
            return {
                "mode": "external",
                "server": os.getenv("EXTERNAL_SERVER", "wuchang.life"),
                "port": int(os.getenv("EXTERNAL_PORT", "443")),
                "use_https": True,
                "description": "外網連線"
            }

    async def auto_connect_workspace(self) -> bool:
        """自動連線 Workspace"""
        config = self.get_connection_config()

        print(f"\n🌐 網路環境: {config['description']}")
        print(f"   模式: {config['mode']}")
        print(f"   伺服器: {config['server']}:{config['port']}")
        print(f"   HTTPS: {'是' if config['use_https'] else '否'}")

        # 設定環境變數供其他服務使用
        os.environ["SYNC_PEER"] = f"{'https' if config['use_https'] else 'http'}://{config['server']}:{config['port']}"
        os.environ["CONNECTION_MODE"] = config['mode']

        return True


async def main():
    """主函數"""
    print("="*60)
    print("  🏢 五常 AI - Google Workspace 整合")
    print("="*60)
    print()

    # 網路自動偵測
    connector = NetworkAutoConnect()
    await connector.auto_connect_workspace()

    print()

    # Google Workspace 客戶端
    if not GOOGLE_CLIENT_ID:
        print("⚠️  未配置 Google OAuth 憑證")
        print()
        print("請設定以下環境變數:")
        print("  GOOGLE_CLIENT_ID=你的客戶端ID")
        print("  GOOGLE_CLIENT_SECRET=你的客戶端密鑰")
        print("  GOOGLE_REFRESH_TOKEN=你的刷新令牌")
        print()
        print("取得憑證步驟:")
        print("  1. 前往 https://console.cloud.google.com/")
        print("  2. 創建專案並啟用 Drive/Gmail/Calendar API")
        print("  3. 創建 OAuth 2.0 憑證")
        print("  4. 取得 refresh_token")
        return

    client = GoogleWorkspaceClient()

    try:
        # 刷新 token
        if await client.refresh_access_token():
            print()
            print("請選擇操作:")
            print("  1. 同步 Google Drive")
            print("  2. 列出 Drive 文件")
            print("  3. 退出")
            print()

            choice = input("請選擇 (1-3): ").strip()

            if choice == "1":
                await client.sync_drive_folder()
            elif choice == "2":
                files = await client.list_drive_files()
                print()
                print(f"找到 {len(files)} 個文件:")
                for file in files:
                    print(
                        f"  📄 {file['name']} ({file.get('size', 'N/A')} bytes)")
    finally:
        await client.close()

    print()
    print("✅ 完成")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 已中斷")
