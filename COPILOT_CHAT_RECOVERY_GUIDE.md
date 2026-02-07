# GitHub Copilot 聊天歷史恢復指南

## 問題描述

對話內容突然消失，無法訪問之前的聊天歷史。

## 根本原因分析

VS Code 中的 Copilot Chat 歷史默認存儲在本地，以下情況可能導致丟失：

1. **VS Code 本地存儲清除**

    - 緩存清理
    - 暫存檔案刪除
    - 配置重置

2. **擴展問題**

    - Copilot Chat 擴展更新/重裝
    - 擴展數據損壞

3. **系統問題**
    - 不完整的會話關閉
    - 存儲區域權限問題

## 恢復步驟

### 1️⃣ 檢查本地存儲位置

```powershell
# Windows用戶
$copilotPath = "$env:APPDATA\Code\User\globalStorage\github.copilot-chat"
if (Test-Path $copilotPath) {
    Get-ChildItem -Path $copilotPath -Recurse
} else {
    Write-Host "未找到Copilot Chat數據目錄"
}
```

### 2️⃣ 啟用聊天歷史持久化

添加以下配置到`.vscode/settings.json`：

```json
{
    "github.copilot.chat.localeOverride": "zh-tw",
    "github.copilot.chat.enabled": true,
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000
}
```

### 3️⃣ 建立聊天歷史備份機制

創建自動備份系統，監控 Copilot Chat 目錄：

```python
# backup_copilot_chat.py
import os
import json
import shutil
from datetime import datetime

def backup_copilot_chat():
    copilot_path = os.path.expandvars(
        r"$APPDATA\Code\User\globalStorage\github.copilot-chat"
    )

    if os.path.exists(copilot_path):
        backup_dir = "memory_store/copilot_backups"
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"copilot_chat_{timestamp}")

        shutil.copytree(copilot_path, backup_path)
        print(f"✅ 備份完成: {backup_path}")

if __name__ == "__main__":
    backup_copilot_chat()
```

### 4️⃣ 關閉 VS Code 並清理快取（謹慎操作）

```powershell
# 1. 關閉所有VS Code進程
Get-Process code -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. 清理插件快取（可選）
$extensionPath = "$env:USERPROFILE\.vscode\extensions"
# 不要刪除，只是為了重新初始化

# 3. 重新開啟VS Code
code "C:\wuchang V5.1.0"
```

### 5️⃣ 重新初始化 Copilot

-   打開 VS Code
-   按 `Ctrl + Shift + P`
-   搜尋 "Copilot: Reset"
-   重新登入 GitHub 帳戶

## ⚠️ 預防措施

### 設置定期備份任務

```powershell
# 創建計劃任務，每天備份Copilot Chat
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\wuchang V5.1.0\backup_copilot_chat.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "BackupCopilotChat"
```

### 監控存儲狀況

實現一個監控腳本檢查：

-   Copilot Chat 目錄大小
-   最後修改時間
-   存儲可用空間

## 🔄 替代方案：集中化聊天歷史管理

創建一個自定義的聊天歷史追蹤系統，將所有對話保存到項目的`memory_store`：

```python
# chat_history_manager.py
import json
import os
from datetime import datetime

class ChatHistoryManager:
    def __init__(self):
        self.history_dir = "memory_store/chat_history"
        os.makedirs(self.history_dir, exist_ok=True)

    def save_conversation(self, topic: str, messages: list):
        """保存對話內容"""
        filename = f"{self.history_dir}/{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'topic': topic,
                'timestamp': datetime.now().isoformat(),
                'messages': messages
            }, f, ensure_ascii=False, indent=2)
        return filename

    def list_conversations(self):
        """列出所有對話"""
        return os.listdir(self.history_dir)

    def load_conversation(self, filename: str):
        """加載對話歷史"""
        with open(f"{self.history_dir}/{filename}", 'r', encoding='utf-8') as f:
            return json.load(f)
```

## 📞 聯繫支持

如果問題持續，請檢查：

-   VS Code 版本：`code --version`
-   Copilot Chat 擴展版本：擴展面板檢查
-   GitHub 認證狀態：`GitHub Copilot: Sign Out` 後重新登入

---

**最後更新**：2026 年 1 月 10 日  
**系統**：Wuchang V5.1.0  
**狀態**：正常運作
