# Git 遠程倉庫快速設定腳本
# 使用方式: .\scripts\setup_git_remote.ps1 -RepositoryUrl "https://github.com/wuchang/repo.git"

param(
    [Parameter(Mandatory=$true)]
    [string]$RepositoryUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$RemoteName = "origin"
)

Write-Host "=== Git 遠程倉庫設定 ===" -ForegroundColor Cyan

# 1. 檢查當前遠程倉庫
Write-Host "`n[1] 檢查當前遠程倉庫..." -ForegroundColor Yellow
$existingRemote = git remote get-url $RemoteName 2>$null
if ($existingRemote) {
    Write-Host "  發現現有遠程倉庫: $existingRemote" -ForegroundColor Yellow
    $replace = Read-Host "  是否要替換？ (Y/N)"
    if ($replace -eq 'Y' -or $replace -eq 'y') {
        git remote set-url $RemoteName $RepositoryUrl
        Write-Host "  ✓ 遠程倉庫已更新" -ForegroundColor Green
    } else {
        Write-Host "  保持現有設定" -ForegroundColor Gray
        exit 0
    }
} else {
    git remote add $RemoteName $RepositoryUrl
    Write-Host "  ✓ 遠程倉庫已設定: $RepositoryUrl" -ForegroundColor Green
}

# 2. 驗證遠程倉庫
Write-Host "`n[2] 驗證遠程倉庫..." -ForegroundColor Yellow
git remote -v

# 3. 測試連線（如果使用 HTTPS）
if ($RepositoryUrl -like "https://*") {
    Write-Host "`n[3] 測試連線..." -ForegroundColor Yellow
    Write-Host "  使用 HTTPS，需要 Personal Access Token" -ForegroundColor Cyan
    Write-Host "  執行 'git fetch origin' 來測試連線" -ForegroundColor Cyan
} else {
    Write-Host "`n[3] 測試連線..." -ForegroundColor Yellow
    Write-Host "  使用 SSH，確保 SSH 金鑰已添加到 Git 服務提供者" -ForegroundColor Cyan
}

Write-Host "`n=== 設定完成 ===" -ForegroundColor Green
Write-Host "`n下一步：" -ForegroundColor Yellow
Write-Host "  1. 如果使用 HTTPS，請在 GitHub/GitLab 建立 Personal Access Token" -ForegroundColor White
Write-Host "  2. 測試連線: git fetch origin" -ForegroundColor White
Write-Host "  3. 推送代碼: git push -u origin $(git branch --show-current)" -ForegroundColor White
