param (
    [string]$BackupName
)

$rollbackDir = "Rollback_Points"
if (-not (Test-Path $rollbackDir)) {
    Write-Error "找不到 Rollback_Points 目錄！"
    exit 1
}

if ([string]::IsNullOrEmpty($BackupName)) {
    Write-Host "可用備份："
    Get-ChildItem $rollbackDir | Sort-Object CreationTime -Descending | Select-Object Name, CreationTime
    Write-Warning "請指定備份名稱 (例如：Backup_20260204_XXXXXX)"
    exit
}

$sourceDir = Join-Path $rollbackDir $BackupName
if (-not (Test-Path $sourceDir)) {
    Write-Error "找不到備份：$sourceDir"
    exit 1
}

Write-Host "正在從 $BackupName 還原..." -ForegroundColor Cyan

# 1. 還原根目錄檔案
$rootFiles = @("docker-compose.yml", "Caddyfile")
foreach ($file in $rootFiles) {
    $src = Join-Path $sourceDir $file
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination . -Force
        Write-Host "已還原：$file (至根目錄)" -ForegroundColor Green
    }
}

# 2. 還原模組 (wuchang_core)
if (Test-Path "$sourceDir\wuchang_core") {
    $dest = "wuchang_os\addons\wuchang_core"
    if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
    Copy-Item -Path "$sourceDir\wuchang_core" -Destination "wuchang_os\addons" -Recurse -Force
    Write-Host "已還原：wuchang_core (至 wuchang_os\addons)" -ForegroundColor Green
}

# 3. 還原工具庫
if (Test-Path "$sourceDir\wuchang_tools_library") {
    Copy-Item -Path "$sourceDir\wuchang_tools_library" -Destination . -Recurse -Force
    Write-Host "已還原：wuchang_tools_library" -ForegroundColor Green
}

Write-Host "還原完成！請記得重啟 Docker 服務以套用變更。" -ForegroundColor Yellow
Write-Host "建議指令：docker-compose up -d --force-recreate" -ForegroundColor Gray
