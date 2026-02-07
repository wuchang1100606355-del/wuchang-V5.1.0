# 環境變數設定指引

## 方式一：互動式 PowerShell 腳本（推薦）

在 **互動式 PowerShell 視窗**中執行：

```powershell
cd "C:\wuchang V5.1.0\wuchang-V5.1.0"
.\setup_file_sync_env.ps1
```

腳本會提示您輸入：
- **伺服器健康檢查 URL**：例如 `https://wuchang.life/health`
- **伺服器接收資料夾路徑**：例如 `\\SERVER\share\wuchang`
- **Hub URL**（選填）
- **Hub Token**（選填）

### 永久設定

如需永久設定（寫入系統環境變數），使用 `-Persistent` 參數：

```powershell
.\setup_file_sync_env.ps1 -Persistent
```

## 方式二：使用參數直接設定

如果您知道所有值，可以直接使用參數：

```powershell
.\setup_file_sync_env.ps1 `
  -HealthUrl "https://wuchang.life/health" `
  -CopyTo "\\SERVER\share\wuchang" `
  -HubUrl "https://hub.wuchang.life" `
  -HubToken "your_token" `
  -Persistent
```

## 方式三：使用 Python 腳本

### 查看環境變數狀態

```bash
python setup_env_vars.py status
```

### 設定單一環境變數

```bash
# 當前會話
python setup_env_vars.py set --var WUCHANG_HEALTH_URL --value "https://wuchang.life/health"

# 永久設定
python setup_env_vars.py set --var WUCHANG_COPY_TO --value "\\SERVER\share\wuchang" --persistent
```

### 生成設定檔模板

```bash
# 生成 PowerShell 設定檔
python setup_env_vars.py generate --format ps1 --output env_vars.ps1

# 生成 JSON 設定檔
python setup_env_vars.py generate --format json --output env_vars.json
```

## 方式四：手動設定（當前會話）

在 PowerShell 中：

```powershell
$env:WUCHANG_HEALTH_URL = "https://wuchang.life/health"
$env:WUCHANG_COPY_TO = "\\SERVER\share\wuchang"
$env:WUCHANG_HUB_URL = "https://hub.wuchang.life"
$env:WUCHANG_HUB_TOKEN = "your_token"
```

## 方式五：永久設定（系統環境變數）

### Windows GUI

1. 開啟「系統內容」→「進階」→「環境變數」
2. 在「使用者變數」中新增或編輯：
   - `WUCHANG_HEALTH_URL` = `https://wuchang.life/health`
   - `WUCHANG_COPY_TO` = `\\SERVER\share\wuchang`
   - `WUCHANG_HUB_URL` = `https://hub.wuchang.life`
   - `WUCHANG_HUB_TOKEN` = `your_token`

### PowerShell（管理員權限）

```powershell
[System.Environment]::SetEnvironmentVariable("WUCHANG_HEALTH_URL", "https://wuchang.life/health", [System.EnvironmentVariableTarget]::User)
[System.Environment]::SetEnvironmentVariable("WUCHANG_COPY_TO", "\\SERVER\share\wuchang", [System.EnvironmentVariableTarget]::User)
```

## 驗證設定

設定完成後，驗證環境變數：

```bash
# 使用 Python 腳本
python setup_env_vars.py status

# 或直接檢查
python -c "import os; print('WUCHANG_HEALTH_URL:', os.getenv('WUCHANG_HEALTH_URL', '未設定')); print('WUCHANG_COPY_TO:', os.getenv('WUCHANG_COPY_TO', '未設定'))"
```

## 重要提示

1. **當前會話設定**：只在當前 PowerShell 視窗中有效，關閉視窗後失效
2. **永久設定**：需要重新啟動終端機或重新登入才能生效
3. **路徑格式**：
   - SMB 路徑：`\\SERVER\share\wuchang`
   - 本地路徑：`C:\wuchang\server`
   - URL：`https://wuchang.life/health`

## 下一步

設定完成後，可以執行：

```bash
# 檢查伺服器連接
python check_server_connection.py

# 比對檔案
python file_compare_sync.py --profile kb

# 執行雙向擇優同步
python sync_all_profiles.py
```
