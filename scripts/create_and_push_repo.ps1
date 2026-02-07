# 建立 GitHub 倉庫並推送代碼腳本

Write-Host "=== 建立 GitHub 倉庫並推送 ===" -ForegroundColor Cyan

# 檢查 GitHub CLI
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghInstalled) {
    Write-Host "`n[1] GitHub CLI 未安裝" -ForegroundColor Yellow
    Write-Host "  正在安裝 GitHub CLI..." -ForegroundColor Yellow
    winget install --id GitHub.cli --accept-package-agreements --accept-source-agreements
    Start-Sleep -Seconds 5
    
    # 重新整理環境變數
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    $ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $ghInstalled) {
        Write-Host "  ⚠ GitHub CLI 安裝失敗，請手動建立倉庫" -ForegroundColor Red
        Write-Host "`n手動建立步驟：" -ForegroundColor Yellow
        Write-Host "  1. 前往: https://github.com/new" -ForegroundColor White
        Write-Host "  2. 倉庫名稱: wuchang-os" -ForegroundColor White
        Write-Host "  3. 不要勾選 'Initialize with README'" -ForegroundColor White
        Write-Host "  4. 建立後執行: git push -u origin migration/ui-total-ai" -ForegroundColor White
        exit 1
    }
}

Write-Host "  ✓ GitHub CLI 已安裝" -ForegroundColor Green

# 檢查登入狀態
Write-Host "`n[2] 檢查 GitHub 登入狀態..." -ForegroundColor Yellow
$ghAuth = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ⚠ 未登入 GitHub" -ForegroundColor Yellow
    Write-Host "  請執行: gh auth login" -ForegroundColor Cyan
    Write-Host "`n或手動建立倉庫：" -ForegroundColor Yellow
    Write-Host "  1. 前往: https://github.com/new" -ForegroundColor White
    Write-Host "  2. 倉庫名稱: wuchang-os" -ForegroundColor White
    Write-Host "  3. 建立後執行: git push -u origin migration/ui-total-ai" -ForegroundColor White
    exit 1
}

Write-Host "  ✓ 已登入 GitHub" -ForegroundColor Green

# 建立倉庫
Write-Host "`n[3] 建立 GitHub 倉庫..." -ForegroundColor Yellow
$repoName = "wuchang-os"
$currentBranch = git branch --show-current

Write-Host "  倉庫名稱: $repoName" -ForegroundColor Cyan
Write-Host "  當前分支: $currentBranch" -ForegroundColor Cyan

# 建立私有倉庫
gh repo create $repoName --private --source=. --remote=origin --push 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  ✓ 倉庫已建立並推送成功！" -ForegroundColor Green
    Write-Host "`n倉庫 URL: https://github.com/wuchang/$repoName" -ForegroundColor Cyan
} else {
    Write-Host "`n  ⚠ 建立倉庫時發生錯誤" -ForegroundColor Yellow
    Write-Host "  可能原因：" -ForegroundColor Yellow
    Write-Host "    - 倉庫已存在" -ForegroundColor White
    Write-Host "    - 權限不足" -ForegroundColor White
    Write-Host "`n請手動建立倉庫：" -ForegroundColor Yellow
    Write-Host "  1. 前往: https://github.com/new" -ForegroundColor White
    Write-Host "  2. 倉庫名稱: $repoName" -ForegroundColor White
    Write-Host "  3. 建立後執行: git push -u origin $currentBranch" -ForegroundColor White
}
