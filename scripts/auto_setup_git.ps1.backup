# 自動 Git 設定腳本
# 協助完成所有 Git 設定步驟

Write-Host "=== 自動 Git 設定 ===" -ForegroundColor Cyan

# 1. 確認當前配置
Write-Host "`n[1] 確認 Git 配置..." -ForegroundColor Yellow
$userName = git config --global user.name
$userEmail = git config --global user.email
Write-Host "  用戶名稱: $userName" -ForegroundColor Green
Write-Host "  電子郵件: $userEmail" -ForegroundColor Green

if (-not $userName -or -not $userEmail) {
    Write-Host "  ⚠ Git 用戶資訊未設定，正在設定..." -ForegroundColor Yellow
    git config --global user.name "wuchang"
    git config --global user.email "admin@wuchang.life"
    Write-Host "  ✓ 已設定用戶資訊" -ForegroundColor Green
}

# 2. 設定認證管理器
Write-Host "`n[2] 設定認證管理器..." -ForegroundColor Yellow
$credentialHelper = git config --global credential.helper
if (-not $credentialHelper) {
    git config --global credential.helper manager-core
    Write-Host "  ✓ 已設定認證管理器" -ForegroundColor Green
} else {
    Write-Host "  ✓ 認證管理器已設定: $credentialHelper" -ForegroundColor Green
}

# 3. 檢查遠程倉庫
Write-Host "`n[3] 檢查遠程倉庫..." -ForegroundColor Yellow
$remotes = git remote -v
if ($remotes) {
    Write-Host "  遠程倉庫已設定：" -ForegroundColor Green
    $remotes | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
} else {
    Write-Host "  ⚠ 尚未設定遠程倉庫" -ForegroundColor Yellow
    
    # 提供常見的倉庫名稱建議
    $suggestedRepos = @(
        "wuchang-os",
        "wuchang-v5.1.0",
        "wuchang-community-os",
        "wuchang-system"
    )
    
    Write-Host "`n  建議的倉庫名稱：" -ForegroundColor Cyan
    for ($i = 0; $i -lt $suggestedRepos.Count; $i++) {
        Write-Host "    $($i+1). $($suggestedRepos[$i])" -ForegroundColor White
    }
    
    Write-Host "`n  請選擇以下方式之一：" -ForegroundColor Yellow
    Write-Host "    A. 提供現有倉庫 URL" -ForegroundColor White
    Write-Host "    B. 建立新 GitHub 倉庫（需要 GitHub CLI 或手動建立）" -ForegroundColor White
    Write-Host "    C. 稍後設定" -ForegroundColor White
}

# 4. 檢查 GitHub CLI
Write-Host "`n[4] 檢查 GitHub CLI..." -ForegroundColor Yellow
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if ($ghInstalled) {
    Write-Host "  ✓ GitHub CLI 已安裝" -ForegroundColor Green
    $ghAuth = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ GitHub CLI 已登入" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ GitHub CLI 未登入" -ForegroundColor Yellow
        Write-Host "    執行 'gh auth login' 來登入" -ForegroundColor Cyan
    }
} else {
    Write-Host "  ⚠ GitHub CLI 未安裝" -ForegroundColor Yellow
    Write-Host "    可以執行 'winget install GitHub.cli' 來安裝" -ForegroundColor Cyan
}

# 5. 顯示當前分支和狀態
Write-Host "`n[5] 當前狀態..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
Write-Host "  當前分支: $currentBranch" -ForegroundColor Green

$status = git status --short
$stagedFiles = ($status | Select-String "^[AM]").Count
$unstagedFiles = ($status | Select-String "^[?]").Count
Write-Host "  已暫存檔案: $stagedFiles" -ForegroundColor Cyan
Write-Host "  未追蹤檔案: $unstagedFiles" -ForegroundColor Cyan

# 6. 提供下一步指引
Write-Host "`n=== 設定摘要 ===" -ForegroundColor Cyan
Write-Host "  ✓ 用戶資訊: $userName <$userEmail>" -ForegroundColor Green
Write-Host "  ✓ 認證管理器: 已設定" -ForegroundColor Green
Write-Host "  $(if ($remotes) { '✓' } else { '⚠' }) 遠程倉庫: $(if ($remotes) { '已設定' } else { '未設定' })" -ForegroundColor $(if ($remotes) { 'Green' } else { 'Yellow' })
Write-Host "  $(if ($ghInstalled) { '✓' } else { '⚠' }) GitHub CLI: $(if ($ghInstalled) { '已安裝' } else { '未安裝' })" -ForegroundColor $(if ($ghInstalled) { 'Green' } else { 'Yellow' })

Write-Host "`n=== 下一步操作 ===" -ForegroundColor Cyan
if (-not $remotes) {
    Write-Host "  1. 設定遠程倉庫：" -ForegroundColor Yellow
    Write-Host "     .\scripts\setup_git_remote.ps1 -RepositoryUrl 'https://github.com/wuchang/repo-name.git'" -ForegroundColor Gray
    Write-Host "`n  2. 或使用 GitHub CLI 建立新倉庫：" -ForegroundColor Yellow
    Write-Host "     gh repo create wuchang-os --private --source=. --remote=origin --push" -ForegroundColor Gray
} else {
    Write-Host "  1. 測試連線：" -ForegroundColor Yellow
    Write-Host "     git fetch origin" -ForegroundColor Gray
    Write-Host "`n  2. 推送代碼：" -ForegroundColor Yellow
    Write-Host "     git push -u origin $currentBranch" -ForegroundColor Gray
}

Write-Host "`n=== 設定完成 ===" -ForegroundColor Green
