"""
五常 AI - 智能資料夾同步服務
雙方雲端可見時自動同步，採用最優策略避免衝突

特性：
- 雙向連通性檢測
- 增量同步（只傳輸變更）
- 衝突解決策略
- 錯誤恢復機制
- 斷點續傳
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import hashlib
import os
import shutil
import aiofiles
import socket
import aiohttp
from aiohttp import web
import psutil

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置
LOCAL_IP = "192.168.50.84"
SERVER_IP = "192.168.50.249"
SYNC_PORT = 8766  # 同步服務端口

# 同步資料夾配置
SYNC_FOLDERS = [
    {
        "name": "workspace",
        "local_path": r"c:\wuchang V5.1.0\workspace",
        "priority": 0,
        "exclude": ["__pycache__", "*.pyc", ".venv", "*.log", "node_modules", ".git"]
    },
    {
        "name": "remote_ui_control",
        "local_path": r"c:\wuchang V5.1.0\remote_ui_control",
        "priority": 1,
        "exclude": ["__pycache__", "*.pyc", ".env", "*.log"]
    },
    {
        "name": "wuchang_os_addons",
        "local_path": r"c:\wuchang V5.1.0\wuchang_os\addons",
        "priority": 2,
        "exclude": ["__pycache__", "*.pyc", "*.swp"]
    },
    {
        "name": "scripts",
        "local_path": r"c:\wuchang V5.1.0\scripts",
        "priority": 3,
        "exclude": ["__pycache__", "*.pyc"]
    }
]

# 同步策略
# newest, manual, local_wins, remote_wins
SYNC_STRATEGY = os.getenv("SYNC_STRATEGY", "newest")
MAX_FILE_SIZE = int(os.getenv("MAX_SYNC_FILE_SIZE",
                    str(50 * 1024 * 1024)))  # 50MB
CHUNK_SIZE = 1024 * 1024  # 1MB chunks
SYNC_SECRET = os.getenv("SYNC_SECRET", "wuchang-sync-secret")
SYNC_BIND_HOST = os.getenv("SYNC_BIND_HOST", "0.0.0.0")
# 直接指定對端 base，例如 https://a.b.com:8766
SYNC_PEER_OVERRIDE = os.getenv("SYNC_PEER")
FORCE_ROLE = os.getenv("SYNC_ROLE")  # local / server 覆蓋自動偵測


class FileInfo:
    """文件資訊"""

    def __init__(self, path: Path, base_path: Path):
        self.path = path
        self.relative_path = path.relative_to(base_path)
        self.size = path.stat().st_size if path.exists() else 0
        self.mtime = path.stat().st_mtime if path.exists() else 0
        self.hash = None

    def calculate_hash(self) -> str:
        """計算文件 hash"""
        if not self.path.exists():
            return ""

        if self.hash:
            return self.hash

        hasher = hashlib.md5()
        with open(self.path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        self.hash = hasher.hexdigest()
        return self.hash

    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "path": str(self.relative_path),
            "size": self.size,
            "mtime": self.mtime,
            "hash": self.calculate_hash() if self.size < MAX_FILE_SIZE else "too_large"
        }


class CloudSyncService:
    """雲端同步服務"""

    def __init__(self):
        self.is_local = self._detect_role()
        self.peer_ip = SERVER_IP if self.is_local else LOCAL_IP
        self.peer_available = False
        self.sync_folders = SYNC_FOLDERS
        self._session: aiohttp.ClientSession | None = None
        self._server: aiohttp.web.AppRunner | None = None
        self._server_task: asyncio.Task | None = None

    def _detect_role(self) -> bool:
        """檢測當前角色（本機 or Server）"""
        if FORCE_ROLE:
            return FORCE_ROLE.lower() == "local"
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            # 檢查是否有 192.168.50.84 的網卡
            import psutil
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        if addr.address.startswith("192.168.50.84"):
                            return True

            return False
        except:
            return False

    async def _get_session(self) -> aiohttp.ClientSession:
        """取得可重用的 HTTP session"""
        if self._session and not self._session.closed:
            return self._session

        timeout = aiohttp.ClientTimeout(total=300)
        self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    # ============================
    # 服務端 (aiohttp) - 提供 RPC
    # ============================

    async def start_server(self):
        """啟動同步 RPC 服務"""
        app = web.Application(middlewares=[self._auth_middleware])
        app.add_routes([
            web.get('/ping', self._handle_ping),
            web.get('/files', self._handle_list_files),
            web.get('/download', self._handle_download_file),
            web.post('/upload', self._handle_upload_file),
            web.post('/execute', self._handle_execute_command),
        ])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, SYNC_BIND_HOST, SYNC_PORT)
        await site.start()
        self._server = runner
        logger.info(f"🚀 同步 RPC 服務已啟動，監聽 {SYNC_PORT}")

    @web.middleware
    async def _auth_middleware(self, request, handler):
        token = request.headers.get("X-Sync-Token")
        if token != SYNC_SECRET:
            return web.json_response({"error": "unauthorized"}, status=401)
        return await handler(request)

    async def _handle_ping(self, request: web.Request):
        return web.json_response({
            "role": "local" if self.is_local else "server",
            "folders": [cfg["name"] for cfg in self.sync_folders],
            "time": datetime.utcnow().isoformat()
        })

    async def _handle_list_files(self, request: web.Request):
        folder_name = request.query.get("folder")
        folder_config = next(
            (f for f in self.sync_folders if f["name"] == folder_name), None)
        if not folder_config:
            return web.json_response({"error": "folder_not_found"}, status=404)

        files = await self.scan_folder(folder_config)
        data = {path: fi.to_dict() for path, fi in files.items()}
        return web.json_response({"files": data})

    async def _handle_download_file(self, request: web.Request):
        folder_name = request.query.get("folder")
        rel_path = request.query.get("path")
        folder_config = next(
            (f for f in self.sync_folders if f["name"] == folder_name), None)
        if not folder_config or not rel_path:
            return web.json_response({"error": "invalid_params"}, status=400)

        base_path = Path(folder_config["local_path"])
        abs_path = base_path / rel_path
        if not abs_path.exists() or not abs_path.is_file():
            return web.json_response({"error": "file_not_found"}, status=404)

        headers = {
            "Content-Length": str(abs_path.stat().st_size),
            "X-File-MTime": str(abs_path.stat().st_mtime)
        }

        resp = web.StreamResponse(status=200, headers=headers)
        await resp.prepare(request)

        async with aiofiles.open(abs_path, 'rb') as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)
                if not chunk:
                    break
                await resp.write(chunk)

        await resp.write_eof()
        return resp

    async def _handle_upload_file(self, request: web.Request):
        folder_name = request.query.get("folder")
        rel_path = request.query.get("path")
        mtime = float(request.query.get("mtime", "0"))
        folder_config = next(
            (f for f in self.sync_folders if f["name"] == folder_name), None)
        if not folder_config or not rel_path:
            return web.json_response({"error": "invalid_params"}, status=400)

        base_path = Path(folder_config["local_path"])
        abs_path = base_path / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(abs_path, 'wb') as f:
            while True:
                chunk = await request.content.read(CHUNK_SIZE)
                if not chunk:
                    break
                await f.write(chunk)

        if mtime:
            os.utime(abs_path, times=(mtime, mtime))

        return web.json_response({"status": "ok"})

    async def _handle_execute_command(self, request: web.Request):
        """執行遠端命令"""
        try:
            data = await request.json()
            command = data.get("command")
            shell = data.get("shell", "powershell")
            cwd = data.get("cwd", r"c:\wuchang V5.1.0")

            if not command:
                return web.json_response({"error": "command required"}, status=400)

            logger.info(f"📥 收到遠端命令: {command}")

            # 執行命令
            import subprocess
            if shell == "powershell":
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    capture_output=True,
                    text=True,
                    cwd=cwd,
                    timeout=300
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=cwd,
                    timeout=300
                )

            return web.json_response({
                "status": "ok",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            })
        except subprocess.TimeoutExpired:
            return web.json_response({"error": "command timeout"}, status=408)
        except Exception as e:
            logger.error(f"❌ 命令執行失敗: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def check_peer_availability(self) -> bool:
        """檢查對方是否可達"""
        try:
            session = await self._get_session()
            url = f"{self._peer_base}/ping"
            headers = {"X-Sync-Token": SYNC_SECRET}
            async with session.get(url, headers=headers, timeout=3) as resp:
                if resp.status == 200:
                    self.peer_available = True
                    logger.info(f"✅ 對方可達: {self.peer_ip}")
                    return True
        except Exception:
            pass

        self.peer_available = False
        logger.warning(f"⚠️  對方不可達: {self.peer_ip}")
        return False

    async def scan_folder(self, folder_config: dict) -> Dict[str, FileInfo]:
        """掃描資料夾獲取文件清單"""
        base_path = Path(folder_config["local_path"])
        if not base_path.exists():
            logger.warning(f"資料夾不存在: {base_path}")
            return {}

        exclude_patterns = folder_config.get("exclude", [])
        files = {}

        logger.info(f"掃描資料夾: {base_path}")

        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                # 檢查排除規則
                relative = file_path.relative_to(base_path)
                if self._should_exclude(relative, exclude_patterns):
                    continue

                # 檢查文件大小
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    logger.warning(
                        f"文件過大，跳過: {relative} ({file_path.stat().st_size / 1024 / 1024:.1f}MB)")
                    continue

                file_info = FileInfo(file_path, base_path)
                files[str(relative)] = file_info

        logger.info(f"找到 {len(files)} 個文件")
        return files

    def _should_exclude(self, path: Path, patterns: List[str]) -> bool:
        """檢查是否應該排除"""
        path_str = str(path).replace("\\", "/")

        for pattern in patterns:
            if pattern.startswith("*."):
                # 文件副檔名匹配
                if path_str.endswith(pattern[1:]):
                    return True
            elif "*" in pattern:
                # 通配符匹配（簡單實現）
                import fnmatch
                if fnmatch.fnmatch(path_str, pattern):
                    return True
            else:
                # 目錄名匹配
                if pattern in path_str.split("/"):
                    return True

        return False

    def compare_files(self, local_files: Dict[str, FileInfo],
                      remote_files: Dict[str, dict]) -> Dict[str, str]:
        """
        比較文件差異

        返回: {文件路徑: 操作}
        操作: "upload", "download", "skip", "conflict"
        """
        actions = {}

        # 本地有，遠端沒有 -> 上傳
        for path, local_info in local_files.items():
            if path not in remote_files:
                actions[path] = "upload"

        # 遠端有，本地沒有 -> 下載
        for path, remote_info in remote_files.items():
            if path not in local_files:
                actions[path] = "download"

        # 雙方都有 -> 比較
        for path in set(local_files.keys()) & set(remote_files.keys()):
            local_info = local_files[path]
            remote_info = remote_files[path]

            # Hash 相同 -> 跳過
            if local_info.calculate_hash() == remote_info.get("hash"):
                actions[path] = "skip"
                continue

            # 根據策略決定
            if SYNC_STRATEGY == "newest":
                # 選擇最新的
                if local_info.mtime > remote_info.get("mtime", 0):
                    actions[path] = "upload"
                elif local_info.mtime < remote_info.get("mtime", 0):
                    actions[path] = "download"
                else:
                    actions[path] = "conflict"

            elif SYNC_STRATEGY == "local_wins":
                actions[path] = "upload"

            elif SYNC_STRATEGY == "remote_wins":
                actions[path] = "download"

            else:  # manual
                actions[path] = "conflict"

        return actions

    # ============================
    # 與對端的 HTTP RPC 客戶端
    # ============================

    @property
    def _peer_base(self) -> str:
        if SYNC_PEER_OVERRIDE:
            return SYNC_PEER_OVERRIDE.rstrip('/')
        return f"http://{self.peer_ip}:{SYNC_PORT}"

    async def fetch_remote_files(self, folder_config: dict) -> Dict[str, dict]:
        """從對端取得文件清單"""
        session = await self._get_session()
        params = {"folder": folder_config["name"]}
        headers = {"X-Sync-Token": SYNC_SECRET}
        url = f"{self._peer_base}/files"
        try:
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status != 200:
                    logger.error(f"對端文件清單失敗 {resp.status}")
                    return {}
                data = await resp.json()
                return data.get("files", {})
        except Exception as e:
            logger.error(f"取得對端文件清單失敗: {e}")
            return {}

    async def download_file(self, folder_config: dict, rel_path: str, remote_meta: dict):
        """從對端下載文件"""
        session = await self._get_session()
        params = {"folder": folder_config["name"], "path": rel_path}
        headers = {"X-Sync-Token": SYNC_SECRET}
        url = f"{self._peer_base}/download"
        base_path = Path(folder_config["local_path"])
        target_path = base_path / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(f"下載失敗 {rel_path}, status={resp.status}")

            async with aiofiles.open(target_path, 'wb') as f:
                async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                    await f.write(chunk)

        mtime = remote_meta.get("mtime")
        if mtime:
            os.utime(target_path, times=(mtime, mtime))

    async def upload_file(self, folder_config: dict, rel_path: str, local_info: FileInfo):
        """上傳文件到對端"""
        session = await self._get_session()
        params = {
            "folder": folder_config["name"],
            "path": rel_path,
            "mtime": str(local_info.mtime)
        }
        headers = {"X-Sync-Token": SYNC_SECRET}
        url = f"{self._peer_base}/upload"

        async def file_iter():
            async with aiofiles.open(local_info.path, 'rb') as f:
                while True:
                    chunk = await f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield chunk

        async with session.post(url, params=params, headers=headers, data=file_iter()) as resp:
            if resp.status != 200:
                raise RuntimeError(f"上傳失敗 {rel_path}, status={resp.status}")

    def print_sync_plan(self, folder_name: str, actions: Dict[str, str]):
        """顯示同步計劃"""
        upload_count = sum(1 for a in actions.values() if a == "upload")
        download_count = sum(1 for a in actions.values() if a == "download")
        skip_count = sum(1 for a in actions.values() if a == "skip")
        conflict_count = sum(1 for a in actions.values() if a == "conflict")

        logger.info(f"\n{'='*60}")
        logger.info(f"同步計劃: {folder_name}")
        logger.info(f"{'='*60}")
        logger.info(f"⬆️  上傳: {upload_count} 個文件")
        logger.info(f"⬇️  下載: {download_count} 個文件")
        logger.info(f"⏭️  跳過: {skip_count} 個文件")
        logger.info(f"⚠️  衝突: {conflict_count} 個文件")

        if conflict_count > 0:
            logger.warning("\n⚠️  衝突文件:")
            for path, action in actions.items():
                if action == "conflict":
                    logger.warning(f"  - {path}")

    async def sync_folder(self, folder_config: dict, dry_run: bool = False) -> Dict[str, any]:
        """
        同步單個資料夾

        Args:
            folder_config: 資料夾配置
            dry_run: 只顯示計劃，不實際執行

        Returns:
            同步結果統計
        """
        folder_name = folder_config["name"]
        logger.info(f"\n🔄 開始同步資料夾: {folder_name}")

        # 掃描本地文件
        local_files = await self.scan_folder(folder_config)

        # 獲取遠端文件清單
        remote_files = await self.fetch_remote_files(folder_config)

        # 比較差異
        actions = self.compare_files(local_files, remote_files)

        # 顯示計劃
        self.print_sync_plan(folder_name, actions)

        if dry_run:
            logger.info("🔍 試運行模式，不執行實際同步")
            return {
                "folder": folder_name,
                "actions": len(actions),
                "dry_run": True
            }

        # 執行同步
        results = {
            "folder": folder_name,
            "uploaded": 0,
            "downloaded": 0,
            "skipped": 0,
            "conflicts": 0,
            "errors": 0
        }

        for path, action in actions.items():
            try:
                if action == "upload":
                    await self.upload_file(folder_config, path, local_info=local_files[path])
                    results["uploaded"] += 1
                elif action == "download":
                    await self.download_file(folder_config, path, remote_meta=remote_files[path])
                    results["downloaded"] += 1
                elif action == "skip":
                    results["skipped"] += 1
                elif action == "conflict":
                    results["conflicts"] += 1
            except Exception as e:
                logger.error(f"❌ 同步失敗 {path}: {e}")
                results["errors"] += 1

        return results

    async def sync_all(self, dry_run: bool = False) -> List[Dict]:
        """同步所有資料夾"""
        # 檢查雲端連通性
        if not await self.check_peer_availability():
            logger.error("❌ 對方不可達，無法同步")
            return []

        logger.info(f"\n{'='*60}")
        logger.info(f"🌐 雙方雲端可見，開始同步")
        logger.info(f"{'='*60}")
        logger.info(f"本機: {LOCAL_IP if self.is_local else SERVER_IP}")
        logger.info(f"對方: {self.peer_ip}")
        logger.info(f"策略: {SYNC_STRATEGY}")
        logger.info(f"{'='*60}\n")

        # 按優先級排序
        sorted_folders = sorted(
            self.sync_folders, key=lambda x: x.get("priority", 999))

        results = []
        for folder_config in sorted_folders:
            result = await self.sync_folder(folder_config, dry_run)
            results.append(result)

        # 顯示總結
        self.print_summary(results)

        return results

    def print_summary(self, results: List[Dict]):
        """顯示同步總結"""
        total_uploaded = sum(r.get("uploaded", 0) for r in results)
        total_downloaded = sum(r.get("downloaded", 0) for r in results)
        total_skipped = sum(r.get("skipped", 0) for r in results)
        total_conflicts = sum(r.get("conflicts", 0) for r in results)
        total_errors = sum(r.get("errors", 0) for r in results)

        logger.info(f"\n{'='*60}")
        logger.info("📊 同步總結")
        logger.info(f"{'='*60}")
        logger.info(f"⬆️  總上傳: {total_uploaded}")
        logger.info(f"⬇️  總下載: {total_downloaded}")
        logger.info(f"⏭️  總跳過: {total_skipped}")
        logger.info(f"⚠️  總衝突: {total_conflicts}")
        logger.info(f"❌ 總錯誤: {total_errors}")
        logger.info(f"{'='*60}\n")

        if total_errors == 0 and total_conflicts == 0:
            logger.info("✅ 同步完成，無錯誤！")
        elif total_conflicts > 0:
            logger.warning("⚠️  存在衝突，請手動解決")
        else:
            logger.error("❌ 同步過程中出現錯誤")


# ============================================
# 命令行界面
# ============================================

async def main():
    """主函數"""
    import sys

    service = CloudSyncService()

    # 啟動 RPC 服務，確保對端可連
    await service.start_server()

    print("="*60)
    print("  🌐 五常 AI - 雲端智能同步服務")
    print("="*60)
    print()

    # 檢查連通性
    print("檢查雲端連通性...")
    is_available = await service.check_peer_availability()
    
    if is_available:
        print(f"✅ 雙方雲端可見")
        print(f"   本機角色: {'本機 (84)' if service.is_local else 'Server (249)'}")
        print(f"   對方地址: {service.peer_ip}")
    else:
        print(f"❌ 對方不可達: {service.peer_ip}")
        if "--passive" not in sys.argv:
            print(f"   無法進行同步")
            return

    print()

    # 選擇模式
    if "--auto" in sys.argv:
        # 自動模式
        print("🚀 自動同步模式")
        await service.sync_all(dry_run=False)
    elif "--dry-run" in sys.argv:
        # 試運行模式
        print("🔍 試運行模式（只顯示計劃）")
        await service.sync_all(dry_run=True)
    elif "--passive" in sys.argv:
        # 被動模式 (Server Directed)
        print("🛡️ 被動模式啟動 (Server Directed)")
        print("   等待伺服器指令與同步請求...")
        print("   按 Ctrl+C 停止")
        while True:
            await asyncio.sleep(3600)
    else:
        # 互動模式
        print("請選擇操作:")
        print("  1. 試運行（只查看同步計劃）")
        print("  2. 執行同步")
        print("  3. 退出")
        print()

        choice = input("請輸入選項 (1-3): ").strip()

        if choice == "1":
            await service.sync_all(dry_run=True)
        elif choice == "2":
            confirm = input("\n確認要執行同步嗎？(y/n): ").strip().lower()
            if confirm == 'y':
                await service.sync_all(dry_run=False)
            else:
                print("已取消")
        else:
            print("已退出")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 已中斷")
