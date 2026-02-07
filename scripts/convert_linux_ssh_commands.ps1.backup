# Linux/Unix SSH 命令轉換為 PowerShell
# 將常見的 Linux SSH 設定命令轉換為 Windows PowerShell 等效命令

Write-Host "=== Linux/Unix SSH 命令轉換為 PowerShell ===" -ForegroundColor Cyan

Write-Host "`n常見的 Linux/Unix SSH 設定命令及其 PowerShell 等效命令：" -ForegroundColor Yellow

$examples = @(
    @{
        Linux = "mkdir -p ~/.ssh"
        PowerShell = "New-Item -ItemType Directory -Path `$env:USERPROFILE\.ssh -Force"
        Description = "建立 .ssh 目錄"
    },
    @{
        Linux = "chmod 700 ~/.ssh"
        PowerShell = "icacls `$env:USERPROFILE\.ssh /inheritance:r /grant `"${env:USERNAME}:(OI)(CI)F`""
        Description = "設定目錄權限（700 = 只有使用者可讀寫執行）"
    },
    @{
        Linux = "grep -qxF 'key' ~/.ssh/authorized_keys || echo 'key' >> ~/.ssh/authorized_keys"
        PowerShell = "`$key = 'key' ; `$file = `$env:USERPROFILE\.ssh\authorized_keys ; `$content = if (Test-Path `$file) { Get-Content `$file -Raw } else { '' } ; if (`$content -notmatch [regex]::Escape(`$key)) { Add-Content -Path `$file -Value `$key }"
        Description = "檢查並添加 SSH 公鑰（如果不存在）"
    },
    @{
        Linux = "chmod 600 ~/.ssh/authorized_keys"
        PowerShell = "icacls `$env:USERPROFILE\.ssh\authorized_keys /inheritance:r /grant `"${env:USERNAME}:(R)`""
        Description = "設定檔案權限（600 = 只有使用者可讀寫）"
    }
)

foreach ($example in $examples) {
    Write-Host "`n$($example.Description):" -ForegroundColor Cyan
    Write-Host "  Linux/Unix: $($example.Linux)" -ForegroundColor Yellow
    Write-Host "  PowerShell: $($example.PowerShell)" -ForegroundColor Green
}

Write-Host "`n`n完整的 SSH 公鑰設定腳本：" -ForegroundColor Yellow
Write-Host "  .\scripts\setup_ssh_authorized_key.ps1 -SSHKey 'your-ssh-public-key'" -ForegroundColor Cyan

Write-Host "`n=== 轉換完成 ===" -ForegroundColor Green
