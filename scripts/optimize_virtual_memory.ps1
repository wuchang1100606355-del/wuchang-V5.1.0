# 虛擬記憶體優化腳本
# 增加虛擬記憶體以支援大型 LLM 模型

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "虛擬記憶體優化工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查當前記憶體狀態
Write-Host "📊 當前系統記憶體狀態：" -ForegroundColor Yellow
Write-Host ""

$os = Get-CimInstance -ClassName Win32_OperatingSystem
$totalRAM = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeRAM = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$totalVirtual = [math]::Round($os.TotalVirtualMemorySize / 1MB, 2)
$freeVirtual = [math]::Round($os.FreeVirtualMemory / 1MB, 2)

Write-Host "實體記憶體：" -ForegroundColor Gray
Write-Host "  總計: $totalRAM GB" -ForegroundColor White
Write-Host "  可用: $freeRAM GB" -ForegroundColor White
Write-Host ""
Write-Host "虛擬記憶體：" -ForegroundColor Gray
Write-Host "  總計: $totalVirtual GB" -ForegroundColor White
Write-Host "  可用: $freeVirtual GB" -ForegroundColor White
Write-Host ""

# 檢查分頁檔案
Write-Host "📋 分頁檔案設定：" -ForegroundColor Yellow
$pageFiles = Get-CimInstance -ClassName Win32_PageFileUsage
if ($pageFiles) {
    foreach ($pf in $pageFiles) {
        $allocated = [math]::Round($pf.AllocatedBaseSize / 1MB, 2)
        $current = [math]::Round($pf.CurrentUsage / 1MB, 2)
        Write-Host "  檔案: $($pf.Name)" -ForegroundColor White
        Write-Host "  已分配: $allocated GB" -ForegroundColor White
        Write-Host "  目前使用: $current GB" -ForegroundColor White
    }
} else {
    Write-Host "  ⚠️ 未找到分頁檔案" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⚠️  重要提醒：" -ForegroundColor Yellow
Write-Host "  1. 使用硬碟作為虛擬記憶體會大幅降低效能" -ForegroundColor White
Write-Host "  2. qwen2:7b 模型運行會非常慢（可能比正常慢 10-100 倍）" -ForegroundColor White
Write-Host "  3. 建議僅作為臨時測試使用，長期仍需升級實體記憶體" -ForegroundColor White
Write-Host ""

# 計算建議的虛擬記憶體大小
$recommendedVirtual = [math]::Round($totalRAM * 1.5, 0)  # 實體記憶體的 1.5 倍
Write-Host "💡 建議的虛擬記憶體大小：" -ForegroundColor Cyan
Write-Host "  最小: $totalRAM GB (與實體記憶體相同)" -ForegroundColor White
Write-Host "  推薦: $recommendedVirtual GB (實體記憶體的 1.5 倍)" -ForegroundColor White
Write-Host "  理想: $([math]::Round($totalRAM * 2, 0)) GB (實體記憶體的 2 倍，用於大型模型)" -ForegroundColor White
Write-Host ""

Write-Host "📝 如何調整虛擬記憶體（需管理員權限）：" -ForegroundColor Yellow
Write-Host "  1. 開啟「系統內容」→「進階系統設定」" -ForegroundColor Gray
Write-Host "  2. 點擊「效能」區域的「設定」按鈕" -ForegroundColor Gray
Write-Host "  3. 選擇「進階」標籤" -ForegroundColor Gray
Write-Host "  4. 點擊「變更」按鈕（虛擬記憶體區域）" -ForegroundColor Gray
Write-Host "  5. 取消勾選「自動管理所有磁碟的分頁檔案大小」" -ForegroundColor Gray
Write-Host "  6. 選擇系統磁碟，設定「自訂大小」" -ForegroundColor Gray
Write-Host "  7. 初始大小建議: $recommendedVirtual GB" -ForegroundColor White
Write-Host "  8. 最大大小建議: $([math]::Round($totalRAM * 2, 0)) GB" -ForegroundColor White
Write-Host "  9. 點擊「設定」→「確定」，重新啟動電腦" -ForegroundColor Gray
Write-Host ""

Write-Host "🔧 快速指令（PowerShell，需管理員權限）：" -ForegroundColor Yellow
Write-Host ""
Write-Host "# 建立調整腳本..." -ForegroundColor Gray
Write-Host ""

# 建立調整指令範例
$adjustScript = @"
# 調整虛擬記憶體（需要管理員權限）
# 注意：此操作需要重新啟動電腦

`$computerSystem = Get-CimInstance -ClassName Win32_ComputerSystem
`$pageFile = Get-CimInstance -ClassName Win32_PageFileSetting -Filter "Name='C:\\\\pagefile.sys'"

if (-not `$pageFile) {
    Write-Host "未找到分頁檔案，需要手動建立" -ForegroundColor Yellow
    exit
}

# 設定建議大小（GB）
`$initialSize = $recommendedVirtual * 1024  # 轉換為 MB
`$maximumSize = $([math]::Round($totalRAM * 2, 0)) * 1024  # 轉換為 MB

Write-Host "設定虛擬記憶體大小：" -ForegroundColor Cyan
Write-Host "  初始大小: `$initialSize MB (~$recommendedVirtual GB)" -ForegroundColor White
Write-Host "  最大大小: `$maximumSize MB (~$([math]::Round($totalRAM * 2, 0)) GB)" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  此操作需要重新啟動電腦才能生效" -ForegroundColor Yellow
"@

$adjustScript | Out-File -FilePath "scripts\adjust_virtual_memory_example.ps1" -Encoding UTF8
Write-Host "✓ 已建立調整範例腳本: scripts\adjust_virtual_memory_example.ps1" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ 記憶體狀態檢查完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "💡 建議：" -ForegroundColor Cyan
Write-Host "  如果當前可用虛擬記憶體 ($freeVirtual GB) 已經足夠，可以直接測試運行模型" -ForegroundColor White
Write-Host "  如果需要增加，請按照上述步驟調整，然後重新啟動電腦" -ForegroundColor White
Write-Host ""
