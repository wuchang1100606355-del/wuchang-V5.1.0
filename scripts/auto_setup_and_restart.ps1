# 自動設定外接硬碟為虛擬記憶體並重啟電腦
# 需要管理員權限執行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "自動設定虛擬記憶體並重啟" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ 此腳本需要管理員權限！" -ForegroundColor Red
    Write-Host ""
    Write-Host "請以管理員身份執行以下指令：" -ForegroundColor Yellow
    Write-Host "  Start-Process powershell -Verb RunAs -ArgumentList `"-File '$PWD\scripts\auto_setup_and_restart.ps1'`"" -ForegroundColor White
    Write-Host ""
    exit 1
}

$DriveLetter = "E"
$InitialSizeGB = 16
$MaximumSizeGB = 32

# 檢查目標磁碟
Write-Host "📊 檢查目標磁碟..." -ForegroundColor Yellow
$targetDrive = Get-Volume -DriveLetter $DriveLetter -ErrorAction SilentlyContinue

if (-not $targetDrive) {
    Write-Host "❌ 找不到磁碟 $DriveLetter：" -ForegroundColor Red
    exit 1
}

$freeSpaceGB = [math]::Round($targetDrive.SizeRemaining / 1GB, 2)
Write-Host "✓ 找到磁碟 $DriveLetter`: ($freeSpaceGB GB 可用)" -ForegroundColor Green
Write-Host ""

# 轉換為 MB
$initialSizeMB = $InitialSizeGB * 1024
$maximumSizeMB = $MaximumSizeGB * 1024

Write-Host "📋 設定參數：" -ForegroundColor Yellow
Write-Host "  目標磁碟: $DriveLetter`:" -ForegroundColor White
Write-Host "  初始大小: $InitialSizeGB GB ($initialSizeMB MB)" -ForegroundColor White
Write-Host "  最大大小: $MaximumSizeGB GB ($maximumSizeMB MB)" -ForegroundColor White
Write-Host ""

# 刪除現有分頁檔案
Write-Host "🗑️  移除現有分頁檔案設定..." -ForegroundColor Yellow
$currentPageFiles = Get-CimInstance -ClassName Win32_PageFileSetting -ErrorAction SilentlyContinue
if ($currentPageFiles) {
    foreach ($pf in $currentPageFiles) {
        try {
            Remove-CimInstance -InputObject $pf -ErrorAction Stop
            Write-Host "  ✓ 已移除: $($pf.Name)" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️  無法移除 $($pf.Name): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ℹ️  沒有找到現有分頁檔案設定" -ForegroundColor Gray
}

# 建立新的分頁檔案
Write-Host ""
Write-Host "➕ 建立新的分頁檔案設定..." -ForegroundColor Yellow
$pageFileSetting = @{
    Name = "$DriveLetter`:\pagefile.sys"
    InitialSize = $initialSizeMB
    MaximumSize = $maximumSizeMB
}

try {
    New-CimInstance -ClassName Win32_PageFileSetting -Property $pageFileSetting -ErrorAction Stop
    Write-Host "  ✓ 已在 $DriveLetter`:\ 建立分頁檔案設定" -ForegroundColor Green
    Write-Host "    初始大小: $InitialSizeGB GB" -ForegroundColor Gray
    Write-Host "    最大大小: $MaximumSizeGB GB" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ 建立失敗: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  請手動設定虛擬記憶體" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 虛擬記憶體設定完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 確認重啟
Write-Host "⚠️  系統將在 30 秒後重新啟動..." -ForegroundColor Yellow
Write-Host "  按 Ctrl+C 可以取消" -ForegroundColor Gray
Write-Host ""

$countdown = 30
for ($i = $countdown; $i -gt 0; $i--) {
    Write-Host "`r重新啟動倒數: $i 秒    " -NoNewline -ForegroundColor Cyan
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host ""
Write-Host "🔄 正在重新啟動電腦..." -ForegroundColor Yellow

# 重新啟動電腦
Restart-Computer -Force
