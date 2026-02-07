# 五常系統 - 部署與推送指南

## 📋 快速部署流程

### 1. 推送更新到伺服器

#### 方式一：使用環境變數（推薦）

在 PowerShell 中設定環境變數：

```powershell
# 設定伺服器健康檢查 URL
$env:WUCHANG_HEALTH_URL="https://wuchang.life/health"

# 設定推送目標資料夾（SMB 分享或掛載磁碟）
$env:WUCHANG_COPY_TO="\\SERVER\share\wuchang"
# 或使用掛載磁碟
# $env:WUCHANG_COPY_TO="Z:\wuchang"
```

然後執行推送：

```powershell
# 推送知識庫更新
python safe_sync_push.py --profile kb --actor "ops"

# 推送規則更新
python safe_sync_push.py --profile rules --actor "ops"

# 推送自動部署檔案
python deploy_auto_start.py --push-only
```

#### 方式二：使用命令列參數

```powershell
python safe_sync_push.py `
  --health-url "https://wuchang.life/health" `
  --copy-to "\\SERVER\share\wuchang" `
  --profile kb `
  --actor "ops"
```

#### 方式三：使用綜合部署腳本

```powershell
# 設定環境變數
$env:WUCHANG_HEALTH_URL="https://wuchang.life/health"
$env:WUCHANG_COPY_TO="\\SERVER\share\wuchang"

# 執行綜合部署（推送 + 設定開機自動啟動）
python deploy_auto_start.py
```

### 2. 設定開機自動啟動

#### 方式一：使用 PowerShell 腳本（需要管理員權限）

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

#### 方式二：使用 Python 部署腳本

```powershell
# 僅設定開機自動啟動（需要管理員權限）
python deploy_auto_start.py --setup-only
```

#### 方式三：手動設定任務計劃程序

1. 開啟「工作排程器」（Task Scheduler）
2. 建立基本工作
3. 設定觸發條件為「當電腦啟動時」
4. 設定動作為「啟動程式」
5. 選擇 `start_servers.bat` 作為程式
6. 設定工作目錄為專案根目錄

### 3. 驗證設定

#### 檢查任務是否已註冊

```powershell
Get-ScheduledTask -TaskName "五常系統-開機自動啟動服務器"
```

#### 檢查服務狀態

```powershell
python server_auto_deploy.py status
```

#### 手動測試任務

```powershell
Start-ScheduledTask -TaskName "五常系統-開機自動啟動服務器"
```

## 🔧 推送檔案說明

### 知識庫更新 (profile: kb)

預設推送檔案：
- `wuchang_community_knowledge_index.json`
- `wuchang_community_context_compact.md`

### 規則更新 (profile: rules)

預設推送檔案：
- `AGENT_CONSTITUTION.md`
- `RISK_ACTION_SOP.md`
- `risk_gate.py`
- `safe_sync_push.py`
- `api_community_data.py`

### 自動部署檔案

推送檔案：
- `start_servers.bat`
- `server_auto_deploy.py`
- `setup_auto_start.ps1`
- `remove_auto_start.ps1`
- `SERVER_AUTO_DEPLOY.md`

## 📝 環境變數說明

| 變數名稱 | 說明 | 範例 |
|---------|------|------|
| `WUCHANG_HEALTH_URL` | 伺服器健康檢查 URL | `https://wuchang.life/health` |
| `WUCHANG_COPY_TO` | 推送目標資料夾 | `\\SERVER\share\wuchang` |
| `WUCHANG_HUB_TOKEN` | Little J Hub Token | `your_token_here` |

## 🔍 故障排除

### 推送失敗

**問題：缺少環境變數**
- 解決：設定 `WUCHANG_HEALTH_URL` 和 `WUCHANG_COPY_TO`

**問題：伺服器無回應**
- 解決：檢查伺服器健康檢查端點是否正常運作
- 檢查：`curl https://wuchang.life/health`

**問題：權限不足**
- 解決：確認推送目標資料夾有寫入權限

### 開機自動啟動未生效

**問題：任務未註冊**
- 解決：以管理員身份執行 `setup_auto_start.ps1`

**問題：服務未啟動**
- 檢查：查看 `logs/server_startup_*.log`
- 檢查：確認 Python 路徑正確
- 檢查：確認必要檔案存在

**問題：端口已被佔用**
- 解決：使用 `python server_auto_deploy.py stop` 停止現有服務

## 📊 服務器資訊

### 本機中控台
- **端口**: 8788
- **網址**: http://127.0.0.1:8788/

### Little J Hub
- **端口**: 8799
- **網址**: http://127.0.0.1:8799/
- **必要環境變數**: `WUCHANG_HUB_TOKEN`

## 🆘 取得協助

如果遇到問題：

1. 檢查日誌檔案 (`logs/` 目錄)
2. 使用 `python server_auto_deploy.py status` 查看服務狀態
3. 查看任務計劃程序的執行歷史記錄
4. 確認所有必要檔案和目錄存在

---

**最後更新**: 2026-01-15
