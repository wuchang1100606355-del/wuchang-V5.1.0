# Git 認證設定腳本
# 協助設定 Git 認證方式

Write-Host "=== Git 認證設定 ===" -ForegroundColor Cyan

# 1. 檢查當前 Git 配置
Write-Host "`n[1] 檢查當前 Git 配置..." -ForegroundColor Yellow
git config --global --list

# 2. 設定認證方式選項
Write-Host "`n[2] 選擇認證方式：" -ForegroundColor Yellow
Write-Host "  A. HTTPS (使用 Personal Access Token)" -ForegroundColor Green
Write-Host "  B. SSH (使用 SSH 金鑰)" -ForegroundColor Green
Write-Host "  C. Windows 認證管理器 (已設定)" -ForegroundColor Green

# 3. 檢查是否有 SSH 金鑰
Write-Host "`n[3] 檢查 SSH 金鑰..." -ForegroundColor Yellow
if (Test-Path "$env:USERPROFILE\.ssh\id_rsa.pub") {
    Write-Host "  找到 SSH 公鑰：" -ForegroundColor Green
    Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"
} else {
    Write-Host "  未找到 SSH 金鑰" -ForegroundColor Yellow
    $create = Read-Host "  是否要建立新的 SSH 金鑰？ (Y/N)"
    if ($create -eq 'Y' -or $create -eq 'y') {
        ssh-keygen -t rsa -b 4096 -C "admin@wuchang.life"
        Write-Host "  SSH 金鑰已建立！請將公鑰添加到 Git 服務提供者。" -ForegroundColor Green
    }
}

# 4. 設定遠程倉庫（如果需要）
Write-Host "`n[4] 遠程倉庫設定" -ForegroundColor Yellow
$hasRemote = git remote -v
if (-not $hasRemote) {
    Write-Host "  目前沒有設定遠程倉庫" -ForegroundColor Yellow
    $setupRemote = Read-Host "  是否要設定遠程倉庫？ (Y/N)"
    if ($setupRemote -eq 'Y' -or $setupRemote -eq 'y') {
        $remoteUrl = Read-Host "  請輸入遠程倉庫 URL (例如: https://github.com/username/repo.git)"
        if ($remoteUrl) {
            git remote add origin $remoteUrl
            Write-Host "  遠程倉庫已設定為: $remoteUrl" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  當前遠程倉庫：" -ForegroundColor Green
    git remote -v
}

Write-Host "`n=== 設定完成 ===" -ForegroundColor Cyan
Write-Host "`n提示：" -ForegroundColor Yellow
Write-Host "  - 使用 HTTPS: git push 時會提示輸入用戶名和密碼/Token" -ForegroundColor White
Write-Host "  - 使用 SSH: 確保已將 SSH 公鑰添加到 Git 服務提供者" -ForegroundColor White
Write-Host "  - Windows 認證管理器會自動儲存認證資訊" -ForegroundColor White
