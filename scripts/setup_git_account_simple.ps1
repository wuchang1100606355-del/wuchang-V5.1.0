# 新 Git 帳號快速設定腳本
# 使用方式: .\scripts\setup_git_account_simple.ps1 -Username "your-username" -Email "your-email" -Service "GitHub"

param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    
    [Parameter(Mandatory=$true)]
    [string]$Email,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("GitHub", "GitLab", "Bitbucket", "Other")]
    [string]$Service = "GitHub",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("HTTPS", "SSH")]
    [string]$AuthMethod = "HTTPS",
    
    [Parameter(Mandatory=$false)]
    [string]$RemoteUrl = ""
)

Write-Host "=== 新 Git 帳號設定 ===" -ForegroundColor Cyan

# 1. 設定 Git 用戶資訊
Write-Host "`n[1] 設定 Git 用戶資訊..." -ForegroundColor Yellow
git config --global user.name $Username
git config --global user.email $Email
Write-Host "  ✓ 用戶名稱: $Username" -ForegroundColor Green
Write-Host "  ✓ 電子郵件: $Email" -ForegroundColor Green

# 2. 設定認證方式
if ($AuthMethod -eq "SSH") {
    Write-Host "`n[2] 設定 SSH 認證..." -ForegroundColor Yellow
    
    # 生成 SSH 金鑰
    $sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa_$Username"
    if (-not (Test-Path "$sshKeyPath")) {
        Write-Host "  正在生成新的 SSH 金鑰..." -ForegroundColor Yellow
        ssh-keygen -t rsa -b 4096 -C $Email -f $sshKeyPath -N '""' -q
        Write-Host "  ✓ SSH 金鑰已生成" -ForegroundColor Green
    } else {
        Write-Host "  SSH 金鑰已存在" -ForegroundColor Green
    }
    
    # 設定 SSH config
    $sshConfigPath = "$env:USERPROFILE\.ssh\config"
    $hostName = switch ($Service) {
        "GitHub" { "github.com" }
        "GitLab" { "gitlab.com" }
        "Bitbucket" { "bitbucket.org" }
        default { "github.com" }
    }
    
    $hostAlias = "$($Service.ToLower())-$Username"
    $sshConfigEntry = @"

Host $hostAlias
    HostName $hostName
    User git
    IdentityFile $sshKeyPath
"@
    
    # 檢查是否已存在
    $configContent = if (Test-Path $sshConfigPath) { Get-Content $sshConfigPath -Raw } else { "" }
    if ($configContent -notmatch "Host $hostAlias") {
        Add-Content -Path $sshConfigPath -Value $sshConfigEntry
        Write-Host "  ✓ SSH config 已更新" -ForegroundColor Green
    }
    
    # 顯示公鑰
    Write-Host "`n[3] SSH 公鑰（請複製並添加到 $Service）：" -ForegroundColor Yellow
    Write-Host "  檔案位置: ${sshKeyPath}.pub" -ForegroundColor Cyan
    Write-Host "`n公鑰內容：" -ForegroundColor Yellow
    Get-Content "${sshKeyPath}.pub"
    
} else {
    Write-Host "`n[2] HTTPS 認證設定" -ForegroundColor Yellow
    Write-Host "  請在 $Service 建立 Personal Access Token" -ForegroundColor Cyan
    Write-Host "  推送時使用 Token 作為密碼" -ForegroundColor Cyan
}

# 3. 設定遠程倉庫
if ($RemoteUrl) {
    Write-Host "`n[3] 設定遠程倉庫..." -ForegroundColor Yellow
    
    # 檢查是否已有 origin
    $existingRemote = git remote get-url origin 2>$null
    if ($existingRemote) {
        git remote set-url origin $RemoteUrl
        Write-Host "  ✓ 遠程倉庫已更新為: $RemoteUrl" -ForegroundColor Green
    } else {
        git remote add origin $RemoteUrl
        Write-Host "  ✓ 遠程倉庫已設定為: $RemoteUrl" -ForegroundColor Green
    }
}

# 4. 顯示配置摘要
Write-Host "`n=== 設定摘要 ===" -ForegroundColor Cyan
Write-Host "  用戶名稱: $Username" -ForegroundColor White
Write-Host "  電子郵件: $Email" -ForegroundColor White
Write-Host "  Git 服務: $Service" -ForegroundColor White
Write-Host "  認證方式: $AuthMethod" -ForegroundColor White
if ($RemoteUrl) {
    Write-Host "  遠程倉庫: $RemoteUrl" -ForegroundColor White
}

Write-Host "`n=== 設定完成 ===" -ForegroundColor Green
