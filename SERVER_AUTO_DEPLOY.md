# 伺服器開機自動部署指南

本指南說明如何設定五常系統服務器在 Windows 開機時自動啟動。

## 📋 目錄

- [快速開始](#快速開始)
- [檔案說明](#檔案說明)
- [設定步驟](#設定步驟)
- [使用方式](#使用方式)
- [故障排除](#故障排除)

## 🚀 快速開始

### 方法一：使用 PowerShell 腳本（推薦）

1. **以系統管理員身份開啟 PowerShell**
   - 右鍵點擊「開始」按鈕
   - 選擇「Windows PowerShell (系統管理員)」或「終端機 (系統管理員)」

2. **切換到專案目錄**
   ```powershell
   cd "C:\wuchang V5.1.0\wuchang-V5.1.0"
   ```

3. **執行設定腳本**
   ```powershell
   .\setup_auto_start.ps1
   ```

4. **完成！** 系統開機時會自動啟動所有服務器

### 方法二：手動設定任務計劃程序

1. 開啟「工作排程器」（Task Scheduler）
2. 建立基本工作
3. 設定觸發條件為「當電腦啟動時」
4. 設定動作為「啟動程式」
5. 選擇 `start_servers.bat` 作為程式
6. 設定工作目錄為專案根目錄

## 📁 檔案說明

### 核心檔案

| 檔案名稱 | 說明 |
|---------|------|
| `start_servers.bat` | Windows 批處理腳本，用於啟動所有服務器 |
| `server_auto_deploy.py` | Python 服務管理器，提供更進階的管理功能 |
| `setup_auto_start.ps1` | PowerShell 腳本，自動註冊任務計劃程序 |
| `remove_auto_start.ps1` | PowerShell 腳本，移除自動啟動設定 |

### 日誌檔案

所有日誌檔案會儲存在 `logs/` 目錄下：

- `server_startup_YYYY-MM-DD_HHMM.log` - 啟動腳本日誌
- `control_center.log` - 本機中控台日誌
- `little_j_hub.log` - Little J Hub 日誌

## ⚙️ 設定步驟

### 1. 環境變數設定（可選）

如果使用 Little J Hub 服務器，需要設定環境變數：

```powershell
# 臨時設定（僅當前會話有效）
$env:WUCHANG_HUB_TOKEN = "your_token_here"

# 永久設定（系統層級）
[System.Environment]::SetEnvironmentVariable("WUCHANG_HUB_TOKEN", "your_token_here", "Machine")
```

### 2. Python 路徑確認

確認 Python 已正確安裝並在系統 PATH 中：

```powershell
python --version
```

如果 Python 不在 PATH 中，請編輯 `start_servers.bat`，修改 `PYTHON_CMD` 變數：

```batch
set PYTHON_CMD=C:\Python39\python.exe
```

### 3. 註冊自動啟動

執行設定腳本：

```powershell
.\setup_auto_start.ps1
```

## 💻 使用方式

### 手動啟動服務器

#### 使用批處理腳本
```batch
start_servers.bat
```

#### 使用 Python 管理器
```bash
# 啟動所有服務
python server_auto_deploy.py start

# 停止所有服務
python server_auto_deploy.py stop

# 重啟所有服務
python server_auto_deploy.py restart

# 查看服務狀態
python server_auto_deploy.py status
```

### 管理自動啟動任務

#### 查看任務狀態
```powershell
Get-ScheduledTask -TaskName "五常系統-開機自動啟動服務器"
```

#### 手動執行任務
```powershell
Start-ScheduledTask -TaskName "五常系統-開機自動啟動服務器"
```

#### 移除自動啟動
```powershell
.\remove_auto_start.ps1
```

或手動移除：
```powershell
Unregister-ScheduledTask -TaskName "五常系統-開機自動啟動服務器" -Confirm:$false
```

## 🔍 故障排除

### 問題：服務器未自動啟動

**檢查項目：**

1. **確認任務已註冊**
   ```powershell
   Get-ScheduledTask -TaskName "五常系統-開機自動啟動服務器"
   ```

2. **檢查任務執行歷史**
   - 開啟「工作排程器」
   - 找到任務「五常系統-開機自動啟動服務器」
   - 查看「歷程記錄」標籤

3. **檢查日誌檔案**
   - 查看 `logs/server_startup_*.log`
   - 查看 `logs/control_center.log`
   - 查看 `logs/little_j_hub.log`

### 問題：端口已被佔用

**解決方法：**

1. **查看端口佔用情況**
   ```powershell
   netstat -ano | findstr ":8788"
   netstat -ano | findstr ":8799"
   ```

2. **停止佔用端口的進程**
   ```powershell
   taskkill /F /PID <進程ID>
   ```

3. **或使用 Python 管理器停止服務**
   ```bash
   python server_auto_deploy.py stop
   ```

### 問題：Python 未找到

**解決方法：**

1. **確認 Python 安裝位置**
   ```powershell
   where.exe python
   ```

2. **修改批處理腳本中的 Python 路徑**
   編輯 `start_servers.bat`，修改：
   ```batch
   set PYTHON_CMD=C:\Python39\python.exe
   ```

### 問題：權限不足

**解決方法：**

- 確保以系統管理員身份執行 PowerShell
- 確認任務計劃程序中的「執行身分」設定正確
- 檢查任務的「安全性選項」是否允許執行

### 問題：Little J Hub 未啟動

**可能原因：**

1. **環境變數未設定**
   - 檢查 `WUCHANG_HUB_TOKEN` 是否已設定
   - 使用 `echo %WUCHANG_HUB_TOKEN%` 確認

2. **檔案不存在**
   - 確認 `little_j_hub_server.py` 存在
   - 確認 `little_j_hub/` 目錄存在

## 📊 服務器資訊

### 本機中控台
- **端口**: 8788
- **網址**: http://127.0.0.1:8788/
- **狀態檢查**: `netstat -ano | findstr ":8788"`

### Little J Hub
- **端口**: 8799
- **網址**: http://127.0.0.1:8799/
- **狀態檢查**: `netstat -ano | findstr ":8799"`
- **必要環境變數**: `WUCHANG_HUB_TOKEN`

## 🔐 安全注意事項

1. **本機綁定**: 所有服務器僅綁定 `127.0.0.1`，不對外網開放
2. **日誌管理**: 定期清理 `logs/` 目錄中的舊日誌檔案
3. **權限控制**: 確保任務計劃程序任務僅以必要權限執行
4. **環境變數**: 不要在腳本中硬編碼敏感資訊（如 token）

## 📝 進階設定

### 自訂啟動延遲

如果需要延遲啟動（例如等待網路連接），可以修改任務計劃程序設定：

```powershell
$task = Get-ScheduledTask -TaskName "五常系統-開機自動啟動服務器"
$trigger = $task.Triggers[0]
$trigger.Delay = "PT30S"  # 延遲 30 秒
Set-ScheduledTask -TaskName "五常系統-開機自動啟動服務器" -Trigger $trigger
```

### 僅在網路連接時啟動

修改 `setup_auto_start.ps1` 中的設定：

```powershell
$settings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable:$true  # 改為 $true
```

## 🆘 取得協助

如果遇到問題：

1. 檢查日誌檔案 (`logs/` 目錄)
2. 使用 `python server_auto_deploy.py status` 查看服務狀態
3. 查看任務計劃程序的執行歷史記錄
4. 確認所有必要檔案和目錄存在

---

**最後更新**: 2026-01-15
