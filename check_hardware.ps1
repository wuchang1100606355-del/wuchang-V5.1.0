Write-Host "=== 五常 POS 硬體檢測 ===" -ForegroundColor Cyan

# CPU
$cpu = Get-WmiObject -Class Win32_Processor
Write-Host "`nCPU: $($cpu.Name)" -ForegroundColor Yellow
Write-Host "核心數: $($cpu.NumberOfCores) / 邏輯處理器: $($cpu.NumberOfLogicalProcessors)"

# RAM
$ram = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
Write-Host "`nRAM: $ram GB" -ForegroundColor Yellow
if ($ram -ge 8) { 
    Write-Host "✅ 充足" -ForegroundColor Green 
} elseif ($ram -ge 4) { 
    Write-Host "⚠️ 勉強可用，建議升級至 8GB" -ForegroundColor Yellow 
} else { 
    Write-Host "❌ 不足，強烈建議升級" -ForegroundColor Red 
}

# 儲存
$disk = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3 -and $_.DeviceID -eq "C:"}
$diskSize = [math]::Round($disk.Size / 1GB, 2)
$diskFree = [math]::Round($disk.FreeSpace / 1GB, 2)
Write-Host "`n儲存: $diskSize GB (剩餘 $diskFree GB)" -ForegroundColor Yellow

# 判斷是否為 SSD
$diskModel = (Get-WmiObject -Class Win32_DiskDrive | Where-Object {$_.DeviceID -eq "\\.\PHYSICALDRIVE0"}).Model
Write-Host "硬碟型號: $diskModel"
if ($diskModel -match "SSD|NVMe|Solid") {
    Write-Host "✅ SSD 固態硬碟" -ForegroundColor Green
} else {
    Write-Host "⚠️ HDD 機械硬碟，建議升級為 SSD" -ForegroundColor Yellow
}

# 作業系統
$os = Get-WmiObject -Class Win32_OperatingSystem
Write-Host "`n作業系統: $($os.Caption)" -ForegroundColor Yellow
Write-Host "版本: $($os.Version)"

# 網路
$network = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
Write-Host "`n網路介面卡:" -ForegroundColor Yellow
$network | ForEach-Object { 
    Write-Host "  - $($_.Name): $($_.LinkSpeed)" 
}

# 電腦年齡估算
$bios = Get-WmiObject -Class Win32_BIOS
Write-Host "`nBIOS 日期: $($bios.ReleaseDate)" -ForegroundColor Yellow

# 綜合評估
Write-Host "`n=== 綜合評估 ===" -ForegroundColor Cyan

$score = 0
if ($ram -ge 8) { $score += 3 } elseif ($ram -ge 4) { $score += 1 }
if ($diskModel -match "SSD|NVMe") { $score += 3 } elseif ($diskSize -ge 128) { $score += 1 }
if ($cpu.NumberOfCores -ge 4) { $score += 2 } elseif ($cpu.NumberOfCores -ge 2) { $score += 1 }

if ($score -ge 7) {
    Write-Host "✅ 此電腦適合運行 Odoo POS" -ForegroundColor Green
    Write-Host "   可直接使用，效能良好" -ForegroundColor Green
} elseif ($score -ge 4) {
    Write-Host "⚠️ 此電腦勉強可用" -ForegroundColor Yellow
    Write-Host "   建議優化或小幅升級以獲得更好體驗" -ForegroundColor Yellow
} else {
    Write-Host "❌ 此電腦效能不足" -ForegroundColor Red
    Write-Host "   建議升級關鍵零件或考慮更換" -ForegroundColor Red
}

# 具體建議
Write-Host "`n=== 升級建議 ===" -ForegroundColor Cyan
$suggestions = @()
if ($ram -lt 8) { 
    $suggestions += "• RAM 升級至 8GB（約 1500-2500 元）" 
}
if ($diskModel -notmatch "SSD|NVMe") { 
    $suggestions += "• 更換為 128GB+ SSD（約 800-1500 元）- 效能提升最明顯" 
}
if ($diskFree -lt 20) { 
    $suggestions += "• 清理磁碟空間，建議保留至少 20GB" 
}
if ($cpu.NumberOfCores -lt 4) { 
    $suggestions += "• CPU 效能較弱，建議先測試實際使用情況" 
}

if ($suggestions.Count -eq 0) {
    Write-Host "✅ 無需升級，硬體已足夠" -ForegroundColor Green
} else {
    $suggestions | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
}

Write-Host "`n按任意鍵繼續..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
