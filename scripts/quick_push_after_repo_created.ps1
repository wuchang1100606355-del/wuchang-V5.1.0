# 快速推送腳本（在 GitHub 倉庫建立後使用）

Write-Host "=== 快速推送代碼 ===" -ForegroundColor Cyan

# 檢查遠程倉庫
Write-Host "`n[1] 檢查遠程倉庫..." -ForegroundColor Yellow
$remoteUrl = git remote get-url origin 2>$null
if ($remoteUrl) {
    Write-Host "  遠程倉庫: $remoteUrl" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 未設定遠程倉庫" -ForegroundColor Yellow
    Write-Host "  請先執行: git remote add origin https://github.com/wuchang/wuchang-os.git" -ForegroundColor Cyan
    exit 1
}

# 檢查是否有未推送的提交
Write-Host "`n[2] 檢查本地提交..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
$unpushedCommits = git log origin/$currentBranch..HEAD --oneline 2>$null

if ($unpushedCommits) {
    Write-Host "  找到未推送的提交：" -ForegroundColor Green
    $unpushedCommits | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
} else {
    Write-Host "  所有提交已推送" -ForegroundColor Green
}

# 推送代碼
Write-Host "`n[3] 推送代碼到 GitHub..." -ForegroundColor Yellow
Write-Host "  分支: $currentBranch" -ForegroundColor Cyan
Write-Host "  遠程: origin" -ForegroundColor Cyan
Write-Host "`n  提示：" -ForegroundColor Yellow
Write-Host "    - Username: wuchang" -ForegroundColor White
Write-Host "    - Password: <貼上 Personal Access Token>" -ForegroundColor White
Write-Host "`n  正在推送..." -ForegroundColor Yellow

git push -u origin $currentBranch

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  ✓ 推送成功！" -ForegroundColor Green
    Write-Host "`n倉庫 URL: https://github.com/wuchang/wuchang-os" -ForegroundColor Cyan
} else {
    Write-Host "`n  ⚠ 推送失敗" -ForegroundColor Yellow
    Write-Host "`n可能原因：" -ForegroundColor Yellow
    Write-Host "  1. GitHub 倉庫尚未建立" -ForegroundColor White
    Write-Host "  2. Personal Access Token 無效或過期" -ForegroundColor White
    Write-Host "  3. Token 權限不足（需要 repo 權限）" -ForegroundColor White
    Write-Host "`n解決方法：" -ForegroundColor Yellow
    Write-Host "  1. 確認 GitHub 倉庫已建立: https://github.com/wuchang/wuchang-os" -ForegroundColor White
    Write-Host "  2. 建立新的 Personal Access Token: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "  3. 確保 Token 有 'repo' 權限" -ForegroundColor White
}
