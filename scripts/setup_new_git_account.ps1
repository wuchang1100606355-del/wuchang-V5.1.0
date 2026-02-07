# 新 Git 帳號設定腳本
# 協助設定新的 Git 帳號和認證

Write-Host "=== 新 Git 帳號設定 ===" -ForegroundColor Cyan

# 1. 收集新帳號資訊
Write-Host "`n[1] 請輸入新 Git 帳號資訊：" -ForegroundColor Yellow

$gitService = Read-Host "  Git 服務 (GitHub/GitLab/Bitbucket/其他)"
$newUsername = Read-Host "  用戶名稱"
$newEmail = Read-Host "  電子郵件"

# 2. 設定 Git 用戶資訊
Write-Host "`n[2] 設定 Git 用戶資訊..." -ForegroundColor Yellow
git config --global user.name $newUsername
git config --global user.email $newEmail
Write-Host "  ✓ 用戶名稱: $newUsername" -ForegroundColor Green
Write-Host "  ✓ 電子郵件: $newEmail" -ForegroundColor Green

# 3. 選擇認證方式
Write-Host "`n[3] 選擇認證方式：" -ForegroundColor Yellow
Write-Host "  1. HTTPS (使用 Personal Access Token)" -ForegroundColor Cyan
Write-Host "  2. SSH (使用 SSH 金鑰)" -ForegroundColor Cyan
$authChoice = Read-Host "  請選擇 (1 或 2)"

if ($authChoice -eq "2") {
    # SSH 方式
    Write-Host "`n[4] 設定 SSH 認證..." -ForegroundColor Yellow
    
    # 檢查是否已有 SSH 金鑰
    $sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa_$newUsername"
    if (-not (Test-Path "$sshKeyPath")) {
        Write-Host "  正在生成新的 SSH 金鑰..." -ForegroundColor Yellow
        ssh-keygen -t rsa -b 4096 -C $newEmail -f $sshKeyPath -N '""'
        Write-Host "  ✓ SSH 金鑰已生成: $sshKeyPath" -ForegroundColor Green
    } else {
        Write-Host "  SSH 金鑰已存在: $sshKeyPath" -ForegroundColor Green
    }
    
    # 顯示公鑰
    Write-Host "`n[5] 請將以下 SSH 公鑰添加到 $gitService：" -ForegroundColor Yellow
    Write-Host "  公鑰位置: ${sshKeyPath}.pub" -ForegroundColor Cyan
    Write-Host "`n公鑰內容：" -ForegroundColor Yellow
    Get-Content "${sshKeyPath}.pub"
    
    # 設定 SSH config
    $sshConfigPath = "$env:USERPROFILE\.ssh\config"
    $hostName = switch ($gitService.ToLower()) {
        "github" { "github.com" }
        "gitlab" { "gitlab.com" }
        "bitbucket" { "bitbucket.org" }
        default { Read-Host "  請輸入 Git 服務主機名稱" }
    }
    
    $sshConfigEntry = @"

Host $gitService-$newUsername
    HostName $hostName
    User git
    IdentityFile $sshKeyPath
"@
    
    Add-Content -Path $sshConfigPath -Value $sshConfigEntry -ErrorAction SilentlyContinue
    Write-Host "`n  ✓ SSH config 已更新" -ForegroundColor Green
    
} else {
    # HTTPS 方式
    Write-Host "`n[4] HTTPS 認證設定" -ForegroundColor Yellow
    Write-Host "  使用 Personal Access Token 進行認證" -ForegroundColor Cyan
    Write-Host "  請在 $gitService 建立 Personal Access Token" -ForegroundColor Yellow
    Write-Host "  推送時使用 Token 作為密碼" -ForegroundColor Yellow
}

# 4. 設定遠程倉庫
Write-Host "`n[5] 遠程倉庫設定" -ForegroundColor Yellow
$setupRemote = Read-Host "  是否要設定遠程倉庫？ (Y/N)"
if ($setupRemote -eq 'Y' -or $setupRemote -eq 'y') {
    if ($authChoice -eq "2") {
        # SSH URL
        $repoName = Read-Host "  請輸入倉庫名稱 (例如: username/repo)"
        $remoteUrl = "git@$gitService-$newUsername`:$repoName.git"
    } else {
        # HTTPS URL
        $remoteUrl = Read-Host "  請輸入遠程倉庫 URL (例如: https://github.com/username/repo.git)"
    }
    
    # 檢查是否已有 origin
    $existingRemote = git remote get-url origin 2>$null
    if ($existingRemote) {
        $replace = Read-Host "  已存在 origin ($existingRemote)，是否要替換？ (Y/N)"
        if ($replace -eq 'Y' -or $replace -eq 'y') {
            git remote set-url origin $remoteUrl
            Write-Host "  ✓ 遠程倉庫已更新為: $remoteUrl" -ForegroundColor Green
        }
    } else {
        git remote add origin $remoteUrl
        Write-Host "  ✓ 遠程倉庫已設定為: $remoteUrl" -ForegroundColor Green
    }
}

# 5. 顯示配置摘要
Write-Host "`n=== 設定摘要 ===" -ForegroundColor Cyan
Write-Host "  用戶名稱: $newUsername" -ForegroundColor White
Write-Host "  電子郵件: $newEmail" -ForegroundColor White
Write-Host "  Git 服務: $gitService" -ForegroundColor White
Write-Host "  認證方式: $(if ($authChoice -eq '2') { 'SSH' } else { 'HTTPS' })" -ForegroundColor White

Write-Host "`n=== 設定完成 ===" -ForegroundColor Green
Write-Host "`n下一步：" -ForegroundColor Yellow
if ($authChoice -eq "2") {
    Write-Host "  1. 將 SSH 公鑰添加到 $gitService 帳號設定中" -ForegroundColor White
    Write-Host "  2. 測試連線: ssh -T git@$gitService-$newUsername" -ForegroundColor White
} else {
    Write-Host "  1. 在 $gitService 建立 Personal Access Token" -ForegroundColor White
    Write-Host "  2. 推送時使用 Token 作為密碼" -ForegroundColor White
}
Write-Host "  3. 測試推送: git push -u origin $(git branch --show-current)" -ForegroundColor White
