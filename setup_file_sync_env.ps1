# 設定檔案比對與同步環境變數
# 
# 使用方式：
#   .\setup_file_sync_env.ps1
#   或
#   .\setup_file_sync_env.ps1 -HealthUrl "https://wuchang.life/health" -CopyTo "\\SERVER\share\wuchang"

param(
    [string]$HealthUrl = "",
    [string]$CopyTo = "",
    [string]$HubUrl = "",
    [string]$HubToken = "",
    [switch]$Persistent  # 是否永久設定（寫入系統環境變數）
)

Write-Host "========================================"
Write-Host "五常系統 - 檔案比對同步環境變數設定"
Write-Host "========================================"
Write-Host ""

# 讀取現有環境變數（若未提供參數）
if (-not $HealthUrl) {
    $HealthUrl = $env:WUCHANG_HEALTH_URL
}
if (-not $CopyTo) {
    $CopyTo = $env:WUCHANG_COPY_TO
}
if (-not $HubUrl) {
    $HubUrl = $env:WUCHANG_HUB_URL
}
if (-not $HubToken) {
    $HubToken = $env:WUCHANG_HUB_TOKEN
}

# 互動式輸入（若仍未設定）
if (-not $HealthUrl) {
    $HealthUrl = Read-Host "請輸入伺服器健康檢查 URL (例如: https://wuchang.life/health)"
}
if (-not $CopyTo) {
    $CopyTo = Read-Host "請輸入伺服器接收資料夾路徑 (例如: \\SERVER\share\wuchang)"
}
if (-not $HubUrl) {
    $input = Read-Host "請輸入 Hub URL (選填，按 Enter 跳過)"
    if ($input) {
        $HubUrl = $input
    }
}
if (-not $HubToken -and $HubUrl) {
    $input = Read-Host "請輸入 Hub Token (選填，按 Enter 跳過)"
    if ($input) {
        $HubToken = $input
    }
}

# 設定環境變數（當前會話）
Write-Host ""
Write-Host "設定當前會話環境變數..."
$env:WUCHANG_HEALTH_URL = $HealthUrl
$env:WUCHANG_COPY_TO = $CopyTo

if ($HubUrl) {
    $env:WUCHANG_HUB_URL = $HubUrl
}
if ($HubToken) {
    $env:WUCHANG_HUB_TOKEN = $HubToken
}

Write-Host "[OK] WUCHANG_HEALTH_URL = $HealthUrl"
Write-Host "[OK] WUCHANG_COPY_TO = $CopyTo"
if ($HubUrl) {
    Write-Host "[OK] WUCHANG_HUB_URL = $HubUrl"
}
if ($HubToken) {
    Write-Host "[OK] WUCHANG_HUB_TOKEN = *** (已隱藏)"
}

# 永久設定（寫入系統環境變數）
if ($Persistent) {
    Write-Host ""
    Write-Host "設定永久環境變數（需要管理員權限）..."
    
    try {
        [System.Environment]::SetEnvironmentVariable("WUCHANG_HEALTH_URL", $HealthUrl, [System.EnvironmentVariableTarget]::User)
        [System.Environment]::SetEnvironmentVariable("WUCHANG_COPY_TO", $CopyTo, [System.EnvironmentVariableTarget]::User)
        
        if ($HubUrl) {
            [System.Environment]::SetEnvironmentVariable("WUCHANG_HUB_URL", $HubUrl, [System.EnvironmentVariableTarget]::User)
        }
        if ($HubToken) {
            [System.Environment]::SetEnvironmentVariable("WUCHANG_HUB_TOKEN", $HubToken, [System.EnvironmentVariableTarget]::User)
        }
        
        Write-Host "[OK] 永久環境變數設定完成"
        Write-Host "[提示] 請重新啟動終端機或重新登入以生效"
    } catch {
        Write-Host "[錯誤] 無法設定永久環境變數: $_" -ForegroundColor Red
        Write-Host "[提示] 請以管理員權限執行此腳本"
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "環境變數設定完成"
Write-Host "========================================"
Write-Host ""
Write-Host "使用方式："
Write-Host "  1. 比對檔案："
Write-Host "     python file_compare_sync.py --profile kb"
Write-Host "  2. 比對並同步："
Write-Host "     python file_compare_sync.py --profile kb --sync"
Write-Host "  3. 檢查連接狀態："
Write-Host "     python check_server_connection.py"
Write-Host ""
