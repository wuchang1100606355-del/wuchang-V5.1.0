# 將外接硬碟設定為虛擬記憶體（分頁檔案）
# 需要管理員權限執行

param(
    [Parameter(Mandatory=$false)]
    [string]$DriveLetter = "E",
    
    [Parameter(Mandatory=$false)]
    [int]$InitialSizeGB = 16,
    
    [Parameter(Mandatory=$false)]
    [int]$MaximumSizeGB = 32
)

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ 此腳本需要管理員權限！" -ForegroundColor Red
    Write-Host "請以管理員身份執行 PowerShell，然後重新執行此腳本" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "外接硬碟虛擬記憶體設定工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查目標磁碟
$targetDrive = Get-Volume -DriveLetter $DriveLetter -ErrorAction SilentlyContinue

if (-not $targetDrive) {
    Write-Host "❌ 找不到磁碟 $DriveLetter：" -ForegroundColor Red
    Write-Host "請確認外接硬碟已連接並有指定磁碟代號" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "可用磁碟：" -ForegroundColor Yellow
    Get-Volume | Where-Object {$_.DriveType -eq 'Removable' -or $_.DriveType -eq 'Fixed'} | ForEach-Object {
        Write-Host "  $($_.DriveLetter): - $($_.FileSystemLabel) ($([math]::Round($_.SizeRemaining / 1GB, 2)) GB 可用)" -ForegroundColor Gray
    }
    exit 1
}

$freeSpaceGB = [math]::Round($targetDrive.SizeRemaining / 1GB, 2)
$totalSpaceGB = [math]::Round($targetDrive.Size / 1GB, 2)

Write-Host "📊 目標磁碟資訊：" -ForegroundColor Yellow
Write-Host "  磁碟代號: $DriveLetter:" -ForegroundColor White
Write-Host "  標籤: $($targetDrive.FileSystemLabel)" -ForegroundColor White
Write-Host "  總容量: $totalSpaceGB GB" -ForegroundColor White
Write-Host "  可用空間: $freeSpaceGB GB" -ForegroundColor White
Write-Host "  檔案系統: $($targetDrive.FileSystemType)" -ForegroundColor White
Write-Host ""

if ($freeSpaceGB -lt $MaximumSizeGB) {
    Write-Host "⚠️  警告：可用空間不足！" -ForegroundColor Yellow
    Write-Host "  需要: $MaximumSizeGB GB" -ForegroundColor White
    Write-Host "  可用: $freeSpaceGB GB" -ForegroundColor White
    Write-Host "  建議調整最大大小設定" -ForegroundColor Yellow
    Write-Host ""
}

# 轉換為 MB
$initialSizeMB = $InitialSizeGB * 1024
$maximumSizeMB = $MaximumSizeGB * 1024

Write-Host "📋 設定參數：" -ForegroundColor Yellow
Write-Host "  初始大小: $InitialSizeGB GB ($initialSizeMB MB)" -ForegroundColor White
Write-Host "  最大大小: $MaximumSizeGB GB ($maximumSizeMB MB)" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  重要提醒：" -ForegroundColor Yellow
Write-Host "  1. 外接硬碟速度通常比系統 SSD 慢，效能影響更大" -ForegroundColor White
Write-Host "  2. 外接硬碟必須始終保持連接，否則系統可能不穩定" -ForegroundColor White
Write-Host "  3. 外接硬碟損壞會影響系統運作" -ForegroundColor White
Write-Host "  4. 建議僅作為臨時測試，長期仍應使用系統碟或升級實體記憶體" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "確認要在 $DriveLetter`: 設定虛擬記憶體? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔧 正在設定..." -ForegroundColor Yellow

# 取得當前分頁檔案設定
try {
    $currentPageFiles = Get-CimInstance -ClassName Win32_PageFileSetting
    
    Write-Host "📋 當前分頁檔案設定：" -ForegroundColor Cyan
    foreach ($pf in $currentPageFiles) {
        $pfName = $pf.Name
        Write-Host "  $pfName" -ForegroundColor Gray
        Write-Host "    初始大小: $($pf.InitialSize) MB" -ForegroundColor Gray
        Write-Host "    最大大小: $($pf.MaximumSize) MB" -ForegroundColor Gray
    }
    Write-Host ""
    
    # 刪除當前分頁檔案（會在下一次重啟時生效）
    Write-Host "🗑️  移除現有分頁檔案設定..." -ForegroundColor Yellow
    foreach ($pf in $currentPageFiles) {
        $pfName = $pf.Name.Replace('\', '').Replace(':', '')
        try {
            Remove-CimInstance -InputObject $pf -ErrorAction Stop
            Write-Host "  ✓ 已移除: $($pf.Name)" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️  無法移除 $($pf.Name): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    # 建立新的分頁檔案設定
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
    Write-Host "✅ 設定完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  重要：您需要重新啟動電腦才能使設定生效！" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 重新啟動後的驗證步驟：" -ForegroundColor Cyan
    Write-Host "  1. 重新啟動電腦" -ForegroundColor Gray
    Write-Host "  2. 執行以下指令確認：" -ForegroundColor Gray
    Write-Host "     Get-CimInstance -ClassName Win32_PageFileUsage | Select-Object Name, AllocatedBaseSize" -ForegroundColor White
    Write-Host "  3. 重新啟動 Ollama 容器：" -ForegroundColor Gray
    Write-Host "     docker restart wuchang-ollama-1" -ForegroundColor White
    Write-Host "  4. 測試運行 qwen2:7b 模型" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "❌ 執行失敗: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 替代方法（手動設定）：" -ForegroundColor Yellow
    Write-Host "  1. 開啟「系統內容」→「進階系統設定」" -ForegroundColor Gray
    Write-Host "  2. 點擊「效能」區域的「設定」按鈕" -ForegroundColor Gray
    Write-Host "  3. 選擇「進階」標籤" -ForegroundColor Gray
    Write-Host "  4. 點擊「變更」按鈕（虛擬記憶體區域）" -ForegroundColor Gray
    Write-Host "  5. 取消勾選「自動管理所有磁碟的分頁檔案大小」" -ForegroundColor Gray
    Write-Host "  6. 選擇 C: 磁碟，設定為「沒有分頁檔案」" -ForegroundColor Gray
    Write-Host "  7. 選擇 $DriveLetter`: 磁碟，設定「自訂大小」" -ForegroundColor Gray
    Write-Host "  8. 初始大小: $InitialSizeGB GB ($initialSizeMB MB)" -ForegroundColor White
    Write-Host "  9. 最大大小: $MaximumSizeGB GB ($maximumSizeMB MB)" -ForegroundColor White
    Write-Host "  10. 點擊「設定」→「確定」，重新啟動電腦" -ForegroundColor Gray
    exit 1
}
