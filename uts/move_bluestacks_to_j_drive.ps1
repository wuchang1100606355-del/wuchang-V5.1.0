# 移動 BlueStacks 到 J 碟以節省 C 碟空間
# move_bluestacks_to_j_drive.ps1

Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "BlueStacks 移動到 J 碟工具" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "警告: 需要管理員權限來移動檔案" -ForegroundColor Yellow
    Write-Host "正在請求提升權限..." -ForegroundColor Yellow
    Write-Host ""
    
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$scriptPath`"" -Wait
    exit
}

Write-Host "已具有管理員權限" -ForegroundColor Green
Write-Host ""

# 檢查 J 碟是否存在
$jDrive = "J:\"
if (-not (Test-Path $jDrive)) {
    Write-Host "錯誤: 找不到 J 碟" -ForegroundColor Red
    Write-Host "請確認 J 碟已連接" -ForegroundColor Yellow
    exit 1
}

Write-Host "找到 J 碟: $jDrive" -ForegroundColor Green
Write-Host ""

# BlueStacks 路徑
$bsSourcePath = "C:\ProgramData\BlueStacks_msi5"
$bsTargetPath = "J:\BlueStacks_backup"

# 檢查 BlueStacks 是否存在
if (-not (Test-Path $bsSourcePath)) {
    Write-Host "未找到 BlueStacks 安裝目錄: $bsSourcePath" -ForegroundColor Yellow
    Write-Host "可能已經移動或未安裝" -ForegroundColor Yellow
    exit 0
}

Write-Host "找到 BlueStacks 目錄: $bsSourcePath" -ForegroundColor Cyan
Write-Host ""

# 計算大小
Write-Host "計算檔案大小..." -ForegroundColor Yellow
$totalSize = (Get-ChildItem $bsSourcePath -Recurse -File -ErrorAction SilentlyContinue | 
              Measure-Object -Property Length -Sum).Sum
$sizeGB = [math]::Round($totalSize / 1GB, 2)

Write-Host "BlueStacks 總大小: $sizeGB GB" -ForegroundColor Cyan
Write-Host ""

# 檢查目標目錄
if (Test-Path $bsTargetPath) {
    Write-Host "目標目錄已存在: $bsTargetPath" -ForegroundColor Yellow
    Write-Host "是否要覆蓋？(Y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Host "已取消操作" -ForegroundColor Yellow
        exit 0
    }
    Remove-Item $bsTargetPath -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "正在移動 BlueStacks 到 J 碟..." -ForegroundColor Yellow
Write-Host "  來源: $bsSourcePath" -ForegroundColor Cyan
Write-Host "  目標: $bsTargetPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "這可能需要幾分鐘，請耐心等待..." -ForegroundColor Yellow
Write-Host ""

try {
    # 停止 BlueStacks 進程
    $bsProcesses = Get-Process -Name "HD-Player*", "BlueStacks*", "Bstk*" -ErrorAction SilentlyContinue
    if ($bsProcesses) {
        Write-Host "正在停止 BlueStacks 進程..." -ForegroundColor Yellow
        $bsProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        Write-Host "已停止 BlueStacks 進程" -ForegroundColor Green
        Write-Host ""
    }
    
    # 移動目錄
    Write-Host "正在移動檔案..." -ForegroundColor Yellow
    Move-Item -Path $bsSourcePath -Destination $bsTargetPath -Force -ErrorAction Stop
    
    Write-Host "移動完成" -ForegroundColor Green
    Write-Host ""
    
    # 創建符號連結（可選，但 BlueStacks 可能需要原始路徑）
    Write-Host "注意: BlueStacks 已移動到 J 碟" -ForegroundColor Yellow
    Write-Host "如果未來需要使用，可能需要重新安裝或配置路徑" -ForegroundColor Yellow
    Write-Host ""
    
    # 計算釋放的空間
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "移動完成" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "已釋放 C 碟空間: $sizeGB GB" -ForegroundColor Green
    Write-Host "BlueStacks 備份位置: $bsTargetPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "未來如需使用 BlueStacks：" -ForegroundColor Yellow
    Write-Host "  1. 可以從 J 碟重新安裝" -ForegroundColor Yellow
    Write-Host "  2. 或移動回 C 碟（需要管理員權限）" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host "移動失敗: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "  1. 檔案正在使用中（請關閉所有 BlueStacks 相關程式）" -ForegroundColor Yellow
    Write-Host "  2. 權限不足（請以管理員身份執行）" -ForegroundColor Yellow
    Write-Host "  3. J 碟空間不足" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
