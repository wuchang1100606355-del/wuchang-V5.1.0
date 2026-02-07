# SSH Authorized Keys 設定腳本
# 設定 SSH 公鑰認證

param(
    [Parameter(Mandatory=$true)]
    [string]$SSHKey,
    
    [Parameter(Mandatory=$false)]
    [string]$SSHDir = "$env:USERPROFILE\.ssh",
    
    [Parameter(Mandatory=$false)]
    [string]$AuthorizedKeysFile = "$env:USERPROFILE\.ssh\authorized_keys"
)

Write-Host "=== SSH Authorized Keys 設定 ===" -ForegroundColor Cyan

# 1. 建立 .ssh 目錄（如果不存在）
Write-Host "`n[1] 建立 .ssh 目錄..." -ForegroundColor Yellow
if (-not (Test-Path $SSHDir)) {
    New-Item -ItemType Directory -Path $SSHDir -Force | Out-Null
    Write-Host "  ✓ 已建立: $SSHDir" -ForegroundColor Green
} else {
    Write-Host "  ✓ 已存在: $SSHDir" -ForegroundColor Green
}

# 2. 設定目錄權限（Windows 等效於 chmod 700）
Write-Host "`n[2] 設定目錄權限..." -ForegroundColor Yellow
try {
    # Windows 上設定目錄權限（移除繼承，只給當前使用者）
    icacls $SSHDir /inheritance:r /grant "${env:USERNAME}:(OI)(CI)F" 2>&1 | Out-Null
    Write-Host "  ✓ 已設定目錄權限: $SSHDir" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ 設定目錄權限失敗: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3. 檢查並添加 SSH 公鑰
Write-Host "`n[3] 檢查並添加 SSH 公鑰..." -ForegroundColor Yellow
Write-Host "  SSH 公鑰: $SSHKey" -ForegroundColor Cyan

# 建立 authorized_keys 檔案（如果不存在）
if (-not (Test-Path $AuthorizedKeysFile)) {
    New-Item -ItemType File -Path $AuthorizedKeysFile -Force | Out-Null
    Write-Host "  ✓ 已建立: $AuthorizedKeysFile" -ForegroundColor Green
}

# 讀取現有內容
$content = if (Test-Path $AuthorizedKeysFile) {
    Get-Content $AuthorizedKeysFile -Raw
} else {
    ""
}

# 檢查是否已存在（使用正則表達式轉義）
$escapedKey = [regex]::Escape($SSHKey)
if ($content -notmatch $escapedKey) {
    # 添加新行（如果檔案不為空）
    if ($content -and -not $content.EndsWith("`n")) {
        Add-Content -Path $AuthorizedKeysFile -Value ""
    }
    Add-Content -Path $AuthorizedKeysFile -Value $SSHKey
    Write-Host "  ✓ 已添加 SSH 公鑰到 authorized_keys" -ForegroundColor Green
} else {
    Write-Host "  ✓ SSH 公鑰已存在於 authorized_keys" -ForegroundColor Green
}

# 4. 設定 authorized_keys 檔案權限（Windows 等效於 chmod 600）
Write-Host "`n[4] 設定檔案權限..." -ForegroundColor Yellow
try {
    # Windows 上設定檔案權限（移除繼承，只給當前使用者讀取權限）
    icacls $AuthorizedKeysFile /inheritance:r /grant "${env:USERNAME}:(R)" 2>&1 | Out-Null
    Write-Host "  ✓ 已設定檔案權限: $AuthorizedKeysFile" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ 設定檔案權限失敗: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 5. 顯示結果
Write-Host "`n[5] 設定結果..." -ForegroundColor Yellow
Write-Host "  SSH 目錄: $SSHDir" -ForegroundColor Cyan
Write-Host "  Authorized Keys 檔案: $AuthorizedKeysFile" -ForegroundColor Cyan

if (Test-Path $AuthorizedKeysFile) {
    $keyCount = (Get-Content $AuthorizedKeysFile | Where-Object { $_.Trim() -ne "" }).Count
    Write-Host "  已授權的公鑰數量: $keyCount" -ForegroundColor Cyan
}

Write-Host "`n=== 設定完成 ===" -ForegroundColor Green

# 6. 顯示使用說明
Write-Host "`n使用說明：" -ForegroundColor Yellow
Write-Host "  1. 確保 OpenSSH 服務已啟動" -ForegroundColor White
Write-Host "  2. 確認 SSH 服務配置正確" -ForegroundColor White
Write-Host "  3. 從對應的私鑰可以使用此公鑰登入" -ForegroundColor White

Write-Host "`n檢查 SSH 服務狀態：" -ForegroundColor Yellow
Write-Host "  Get-Service sshd" -ForegroundColor Cyan

Write-Host "`n啟動 SSH 服務（如果需要）：" -ForegroundColor Yellow
Write-Host "  Start-Service sshd" -ForegroundColor Cyan
