# 完整 Git 設定腳本
# 協助完成 Git 倉庫設定和初始化

Write-Host "=== 完整 Git 設定 ===" -ForegroundColor Cyan

# 1. 檢查當前配置
Write-Host "`n[1] 檢查當前 Git 配置..." -ForegroundColor Yellow
$currentUser = git config --global user.name
$currentEmail = git config --global user.email
Write-Host "  用戶名稱: $currentUser" -ForegroundColor Green
Write-Host "  電子郵件: $currentEmail" -ForegroundColor Green

# 2. 檢查遠程倉庫
Write-Host "`n[2] 檢查遠程倉庫..." -ForegroundColor Yellow
$remotes = git remote -v
if ($remotes) {
    Write-Host "  當前遠程倉庫：" -ForegroundColor Green
    $remotes | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
} else {
    Write-Host "  尚未設定遠程倉庫" -ForegroundColor Yellow
}

# 3. 檢查當前分支和狀態
Write-Host "`n[3] 檢查當前分支和狀態..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
Write-Host "  當前分支: $currentBranch" -ForegroundColor Green

$status = git status --short
$stagedCount = ($status | Select-String "^[AM]").Count
$unstagedCount = ($status | Select-String "^[?]").Count
Write-Host "  已暫存檔案: $stagedCount" -ForegroundColor Cyan
Write-Host "  未追蹤檔案: $unstagedCount" -ForegroundColor Cyan

# 4. 設定遠程倉庫（如果需要）
if (-not $remotes) {
    Write-Host "`n[4] 設定遠程倉庫..." -ForegroundColor Yellow
    Write-Host "  請選擇以下選項：" -ForegroundColor Cyan
    Write-Host "  1. 使用 GitHub" -ForegroundColor White
    Write-Host "  2. 使用 GitLab" -ForegroundColor White
    Write-Host "  3. 使用其他 Git 服務" -ForegroundColor White
    Write-Host "  4. 稍後設定" -ForegroundColor White
    
    # 提供常見的 GitHub 倉庫 URL 範例
    Write-Host "`n  GitHub 倉庫 URL 格式：" -ForegroundColor Yellow
    Write-Host "    HTTPS: https://github.com/username/repository.git" -ForegroundColor Gray
    Write-Host "    SSH:   git@github.com:username/repository.git" -ForegroundColor Gray
}

# 5. 認證檢查
Write-Host "`n[5] 認證設定檢查..." -ForegroundColor Yellow
$credentialHelper = git config --global credential.helper
if ($credentialHelper) {
    Write-Host "  ✓ 認證管理器: $credentialHelper" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 未設定認證管理器" -ForegroundColor Yellow
    git config --global credential.helper manager-core
    Write-Host "  ✓ 已設定認證管理器" -ForegroundColor Green
}

# 6. 提供下一步指引
Write-Host "`n=== 設定摘要 ===" -ForegroundColor Cyan
Write-Host "  用戶名稱: $currentUser" -ForegroundColor White
Write-Host "  電子郵件: $currentEmail" -ForegroundColor White
Write-Host "  當前分支: $currentBranch" -ForegroundColor White
Write-Host "  遠程倉庫: $(if ($remotes) { '已設定' } else { '未設定' })" -ForegroundColor White

Write-Host "`n=== 下一步操作 ===" -ForegroundColor Cyan
if (-not $remotes) {
    Write-Host "  1. 設定遠程倉庫：" -ForegroundColor Yellow
    Write-Host "     git remote add origin <repository-url>" -ForegroundColor Gray
} else {
    Write-Host "  1. 遠程倉庫已設定，可以開始推送：" -ForegroundColor Yellow
    Write-Host "     git push -u origin $currentBranch" -ForegroundColor Gray
}

Write-Host "  2. 如果使用 HTTPS，請在 GitHub/GitLab 建立 Personal Access Token" -ForegroundColor Yellow
Write-Host "  3. 推送時使用 Token 作為密碼" -ForegroundColor Yellow

Write-Host "`n=== 設定完成 ===" -ForegroundColor Green
