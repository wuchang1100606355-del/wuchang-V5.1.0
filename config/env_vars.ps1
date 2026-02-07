# 五常系統環境變數設定檔
# 使用方式: .\env_vars.ps1
# 或: Get-Content env_vars.ps1 | Invoke-Expression

# 伺服器健康檢查 URL
# $env:WUCHANG_HEALTH_URL = "https://wuchang.life/health"

# 伺服器接收資料夾路徑（SMB/掛載磁碟）
# $env:WUCHANG_COPY_TO = "\\SERVER\share\wuchang"

# Little J Hub 服務器 URL
# $env:WUCHANG_HUB_URL = "https://hub.wuchang.life"

# Little J Hub 認證 Token
# $env:WUCHANG_HUB_TOKEN = "your_token_here"

# 系統資料庫目錄
# $env:WUCHANG_SYSTEM_DB_DIR = "C:\wuchang\db"

# 工作空間輸出目錄
# $env:WUCHANG_WORKSPACE_OUTDIR = "C:\wuchang\output"

# 個資輸出目錄
# $env:WUCHANG_PII_OUTDIR = "C:\wuchang\pii"

# 是否啟用個資處理功能
# $env:WUCHANG_PII_ENABLED = "true"

# 個資儲存裝置 ID
# $env:WUCHANG_PII_STORAGE_DEVICE = "usb_001"
