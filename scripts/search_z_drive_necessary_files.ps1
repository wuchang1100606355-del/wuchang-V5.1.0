# 從 Z_drive 搜尋必要檔案腳本
# 功能：搜尋 Z_drive 中的必要檔案並顯示

function Log-Message {
    param (
        [string]$Message,
        [string]$Level = "INFO"
    )
    $icons = @{
        "INFO" = "ℹ️"
        "OK" = "✅"
        "WARN" = "⚠️"
        "ERROR" = "❌"
        "PROGRESS" = "🔄"
    }
    $icon = $icons.($Level)
    Write-Host "$icon [$Level] $Message"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "從 Z_drive 搜尋必要檔案" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Z_drive
if (-not (Test-Path "Z:\")) {
    Log-Message "Z_drive 不存在" "ERROR"
    exit 1
}
Log-Message "Z_drive 存在" "OK"

Write-Host ""
Log-Message "搜尋必要檔案..." "PROGRESS"

# 定義必要檔案模式
$patterns = @{
    "credentials" = @("*.json", "*credentials*", "*token*", "*google*.json", "*sa*.json", "*.pem", "*.key")
    "configs" = @("*.env", "*config*.yml", "*config*.yaml", "*config*.json", "*docker-compose*.yml")
    "scripts" = @("*.py", "*.ps1", "*.sh", "*.bat")
    "modules" = @("*__manifest__.py", "*addons*")
    "docker" = @("*Dockerfile*", "*docker-compose*")
}

$foundFiles = @{
    "credentials" = @()
    "configs" = @()
    "scripts" = @()
    "modules" = @()
    "docker" = @()
}

# 搜尋檔案
foreach ($category in $patterns.Keys) {
    foreach ($pattern in $patterns[$category]) {
        try {
            $files = Get-ChildItem "Z:\" -Recurse -File -Filter $pattern -ErrorAction SilentlyContinue
            $foundFiles[$category] += $files
        } catch {
            # 忽略錯誤，繼續搜尋
        }
    }
}

# 顯示搜尋結果
Write-Host ""
Log-Message "搜尋結果：" "INFO"

$totalFound = 0
foreach ($category in $foundFiles.Keys) {
    $count = ($foundFiles[$category] | Measure-Object).Count
    $totalFound += $count
    if ($count -gt 0) {
        Log-Message "$category : $count 個檔案" "OK"
    }
}

Write-Host ""
Log-Message "總計找到 $totalFound 個可能相關的檔案" "INFO"

# 顯示詳細列表
Write-Host ""
Write-Host "詳細檔案列表：" -ForegroundColor Yellow
foreach ($category in $foundFiles.Keys) {
    $files = $foundFiles[$category] | Select-Object -Unique -First 10
    if ($files.Count -gt 0) {
        Write-Host ""
        Write-Host "### $category ($($files.Count) 個)" -ForegroundColor Cyan
        foreach ($file in $files) {
            $relativePath = $file.FullName.Replace("Z:\", "")
            Write-Host "  - $relativePath" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "搜尋完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Log-Message "如需同步檔案，請使用 Python 腳本或手動複製" "INFO"
