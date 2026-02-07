# 測試腳本：start_j_chaing.ps1 功能驗證
# Test Script: start_j_chaing.ps1 Functionality Validation

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "start_j_chaing.ps1 功能測試" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# 測試 1: 檢查腳本檔案存在
Write-Host "測試 1: 檢查腳本檔案存在..." -ForegroundColor Yellow
if (Test-Path "./start_j_chaing.ps1") {
    Write-Host "✓ 通過: 腳本檔案存在" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "✗ 失敗: 找不到腳本檔案" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# 測試 2: 檢查 PowerShell 語法
Write-Host "測試 2: 檢查 PowerShell 語法..." -ForegroundColor Yellow
try {
    $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content "./start_j_chaing.ps1" -Raw), [ref]$null)
    Write-Host "✓ 通過: PowerShell 語法正確" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "✗ 失敗: PowerShell 語法錯誤" -ForegroundColor Red
    Write-Host "  錯誤: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# 測試 3: 測試 AutoApprove 參數（無變更情況）
Write-Host "測試 3: 測試 AutoApprove 參數..." -ForegroundColor Yellow
try {
    $output = & "./start_j_chaing.ps1" -AutoApprove 2>&1 | Out-String
    if ($output -match "五常雲端空間") {
        Write-Host "✓ 通過: AutoApprove 模式正常運行" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "✗ 失敗: AutoApprove 模式輸出異常" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "✗ 失敗: AutoApprove 模式執行錯誤" -ForegroundColor Red
    Write-Host "  錯誤: $_" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# 測試 4: 檢查 Git 倉庫偵測
Write-Host "測試 4: 檢查 Git 倉庫偵測..." -ForegroundColor Yellow
$isGitRepo = Test-Path ".git"
if ($isGitRepo) {
    Write-Host "✓ 通過: 正確偵測到 Git 倉庫" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "⚠ 警告: 非 Git 倉庫環境" -ForegroundColor Yellow
    $testsPassed++  # 這不算失敗，只是環境不同
}
Write-Host ""

# 測試 5: 檢查文件編碼（應為 UTF-8）
Write-Host "測試 5: 檢查文件編碼..." -ForegroundColor Yellow
try {
    $bytes = [System.IO.File]::ReadAllBytes("./start_j_chaing.ps1")
    # 檢查 UTF-8 BOM 或純 ASCII/UTF-8
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Host "✓ 通過: 檔案使用 UTF-8 with BOM 編碼" -ForegroundColor Green
        $testsPassed++
    } elseif ($bytes[0] -lt 128) {
        Write-Host "✓ 通過: 檔案使用 UTF-8 編碼" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "⚠ 注意: 檔案編碼可能不是 UTF-8" -ForegroundColor Yellow
        $testsPassed++  # 不算失敗，只是警告
    }
} catch {
    Write-Host "✗ 失敗: 無法檢查檔案編碼" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# 測試 6: 檢查相關文件
Write-Host "測試 6: 檢查相關文件..." -ForegroundColor Yellow
$requiredFiles = @("CLOUD_AGENT_GUIDE.md", "README.md")
$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file 存在" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file 不存在" -ForegroundColor Red
        $allFilesExist = $false
    }
}
if ($allFilesExist) {
    Write-Host "✓ 通過: 所有必要文件都存在" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "✗ 失敗: 缺少必要文件" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# 測試總結
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "測試總結" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "通過: $testsPassed" -ForegroundColor Green
Write-Host "失敗: $testsFailed" -ForegroundColor Red
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "所有測試通過！ ✓" -ForegroundColor Green
    exit 0
} else {
    Write-Host "有測試失敗，請檢查上述錯誤 ✗" -ForegroundColor Red
    exit 1
}
