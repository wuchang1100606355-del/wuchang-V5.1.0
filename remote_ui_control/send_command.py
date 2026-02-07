"""
五常 AI - 遠端命令發送工具
向 Server 傳送指令並獲取執行結果
"""

import asyncio
import os
import aiohttp
import json
from typing import Optional

# 配置
LOCAL_IP = "192.168.50.84"
SERVER_IP = "192.168.50.249"
SYNC_PORT = 8766
SYNC_SECRET = os.getenv("SYNC_SECRET", "wuchang-sync-secret")
SYNC_PEER = os.getenv("SYNC_PEER")  # 可覆蓋對端地址

# 預設命令清單
COMMON_COMMANDS = {
    "1": {
        "name": "檢查系統狀態",
        "command": "Get-ComputerInfo | Select-Object CsName, WindowsVersion, OsArchitecture",
        "shell": "powershell"
    },
    "2": {
        "name": "列出運行中的服務",
        "command": "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, DisplayName -First 10",
        "shell": "powershell"
    },
    "3": {
        "name": "檢查磁碟空間",
        "command": "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free",
        "shell": "powershell"
    },
    "4": {
        "name": "查看網路連線",
        "command": "Get-NetIPAddress -AddressFamily IPv4 | Select-Object IPAddress, InterfaceAlias",
        "shell": "powershell"
    },
    "5": {
        "name": "啟動同步服務",
        "command": "cd 'c:\\wuchang V5.1.0\\remote_ui_control'; .\\start_cloud_sync.ps1",
        "shell": "powershell"
    },
    "6": {
        "name": "檢查 Python 環境",
        "command": "python --version; pip list | Select-String 'aiohttp|streamlit|google'",
        "shell": "powershell"
    },
    "7": {
        "name": "查看最近日誌",
        "command": "Get-Content 'c:\\wuchang V5.1.0\\*.log' -Tail 20 -ErrorAction SilentlyContinue",
        "shell": "powershell"
    }
}


class CommandSender:
    """命令發送器"""

    def __init__(self, target: str = "server"):
        """
        初始化

        Args:
            target: "server" 或 "local" 或自定義 IP
        """
        if target == "server":
            self.target_ip = SERVER_IP
        elif target == "local":
            self.target_ip = LOCAL_IP
        else:
            self.target_ip = target

        self.base_url = SYNC_PEER if SYNC_PEER else f"http://{self.target_ip}:{SYNC_PORT}"
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        """取得 HTTP session"""
        if self._session and not self._session.closed:
            return self._session

        timeout = aiohttp.ClientTimeout(total=300)
        self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def check_connection(self) -> bool:
        """檢查連線"""
        try:
            session = await self.get_session()
            url = f"{self.base_url}/ping"
            headers = {"X-Sync-Token": SYNC_SECRET}

            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ 連線成功")
                    print(f"   對方角色: {data.get('role')}")
                    print(f"   時間: {data.get('time')}")
                    return True
        except Exception as e:
            print(f"❌ 連線失敗: {e}")
            return False

        return False

    async def send_command(self, command: str, shell: str = "powershell",
                           cwd: str = r"c:\wuchang V5.1.0") -> dict:
        """
        發送命令到遠端執行

        Args:
            command: 要執行的命令
            shell: powershell 或 cmd
            cwd: 工作目錄

        Returns:
            執行結果 {"status", "stdout", "stderr", "returncode"}
        """
        session = await self.get_session()
        url = f"{self.base_url}/execute"
        headers = {
            "X-Sync-Token": SYNC_SECRET,
            "Content-Type": "application/json"
        }
        data = {
            "command": command,
            "shell": shell,
            "cwd": cwd
        }

        try:
            print(f"\n📤 發送命令: {command}")
            print(f"   目標: {self.base_url}")
            print(f"   工作目錄: {cwd}")
            print(f"   Shell: {shell}")
            print()

            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print("✅ 命令執行完成")
                    return result
                else:
                    error = await resp.text()
                    print(f"❌ 執行失敗 ({resp.status}): {error}")
                    return {"status": "error", "error": error}

        except Exception as e:
            print(f"❌ 發送失敗: {e}")
            return {"status": "error", "error": str(e)}

    async def close(self):
        """關閉 session"""
        if self._session and not self._session.closed:
            await self._session.close()


async def interactive_mode():
    """互動模式"""
    print("="*60)
    print("  📡 五常 AI - 遠端命令發送工具")
    print("="*60)
    print()

    # 選擇目標
    print("請選擇目標:")
    print("  1. Server (192.168.50.249)")
    print("  2. 本機 (192.168.50.84)")
    print("  3. 自定義")
    print()

    choice = input("請輸入選項 (1-3): ").strip()

    if choice == "1":
        sender = CommandSender("server")
    elif choice == "2":
        sender = CommandSender("local")
    elif choice == "3":
        custom_ip = input("請輸入 IP 或 URL: ").strip()
        sender = CommandSender(custom_ip)
    else:
        print("無效選項")
        return

    # 檢查連線
    print()
    print("檢查連線...")
    if not await sender.check_connection():
        print("無法連線到目標，請檢查:")
        print("  1. 目標是否在線")
        print("  2. 防火牆是否開放 8766")
        print("  3. SYNC_SECRET 是否一致")
        await sender.close()
        return

    print()

    while True:
        print()
        print("="*60)
        print("  常用命令")
        print("="*60)

        for key, cmd in COMMON_COMMANDS.items():
            print(f"  {key}. {cmd['name']}")

        print()
        print("  0. 自定義命令")
        print("  q. 退出")
        print()

        choice = input("請選擇 (0-7, q): ").strip().lower()

        if choice == "q":
            break

        if choice == "0":
            # 自定義命令
            print()
            command = input("請輸入命令: ").strip()
            if not command:
                continue

            shell = input(
                "Shell (powershell/cmd) [powershell]: ").strip() or "powershell"
            cwd = input(f"工作目錄 [c:\\wuchang V5.1.0]: ").strip(
            ) or r"c:\wuchang V5.1.0"

            result = await sender.send_command(command, shell, cwd)

        elif choice in COMMON_COMMANDS:
            # 預設命令
            cmd = COMMON_COMMANDS[choice]
            print()
            print(f"執行: {cmd['name']}")
            confirm = input("確認執行? (y/n): ").strip().lower()

            if confirm != "y":
                continue

            result = await sender.send_command(
                cmd["command"],
                cmd.get("shell", "powershell"),
                cmd.get("cwd", r"c:\wuchang V5.1.0")
            )
        else:
            print("無效選項")
            continue

        # 顯示結果
        print()
        print("="*60)
        print("  執行結果")
        print("="*60)

        if result.get("status") == "ok":
            print(f"返回碼: {result.get('returncode', 'N/A')}")
            print()

            if result.get("stdout"):
                print("標準輸出:")
                print(result["stdout"])

            if result.get("stderr"):
                print()
                print("標準錯誤:")
                print(result["stderr"])
        else:
            print(f"錯誤: {result.get('error', '未知錯誤')}")

    await sender.close()
    print()
    print("👋 已退出")


async def main():
    """主函數"""
    import sys

    if len(sys.argv) > 1:
        # 命令行模式
        target = sys.argv[1] if len(sys.argv) > 1 else "server"
        command = sys.argv[2] if len(sys.argv) > 2 else ""

        if not command:
            print("用法: python send_command.py <target> <command>")
            print("  target: server / local / IP")
            print("  command: 要執行的命令")
            return

        sender = CommandSender(target)

        if await sender.check_connection():
            result = await sender.send_command(command)

            print()
            print("結果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        await sender.close()
    else:
        # 互動模式
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 已中斷")
