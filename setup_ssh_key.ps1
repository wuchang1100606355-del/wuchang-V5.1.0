#!/usr/bin/env pwsh
<#
.SYNOPSIS
    設定 SSH 免密碼登入
.DESCRIPTION
    產生 SSH key pair 並複製到伺服器，實現免密碼登入
#>

param(
    [string]$ServerIP = "192.168.50.84",
    [string]$ServerUser = "wuchang",
    [string]$KeyType = "ed25519"
)

$colors = @{ ok = "Green"; warn = "Yellow"; err = "Red"; info = "Cyan"; header = "Magenta" }
function H($t) { Write-Host "`n$('═'*70)" -f $colors.header; Write-Host "  $t" -f $colors.header; Write-Host $('═'*70) -f $colors.header }
function OK($m) { Write-Host "  [OK]   $m" -f $colors.ok }
function WW($m) { Write-Host "  [WARN] $m" -f $colors.warn }
function EE($m) { Write-Host "  [ERR]  $m" -f $colors.err }
function II($m) { Write-Host "  [INFO] $m" -f $colors.info }

H "SSH 免密碼登入設定"

$sshDir = "$env:USERPROFILE\.ssh"
$keyPath = "$sshDir\id_$KeyType"
$pubKeyPath = "$keyPath.pub"

# 檢查 SSH 目錄
if (-not (Test-Path $sshDir)) {
    II "建立 SSH 目錄: $sshDir"
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
}

# 檢查是否已有 key
if (Test-Path $keyPath) {
    WW "SSH key 已存在: $keyPath"
    $response = Read-Host "是否使用現有 key? (Y/n)"
    if ($response -eq "n" -or $response -eq "N") {
        $keyPath = "$sshDir\id_${KeyType}_wuchang"
        $pubKeyPath = "$keyPath.pub"
        II "將建立新的 key: $keyPath"
    } else {
        OK "使用現有 key"
    }
}

# 產生新 key（如果需要）
if (-not (Test-Path $keyPath)) {
    H "產生 SSH Key Pair"
    II "使用 $KeyType 加密演算法"
    
    try {
        ssh-keygen -t $KeyType -f $keyPath -N '""' -C "$env:USERNAME@$env:COMPUTERNAME-wuchang"
        if ($LASTEXITCODE -eq 0) {
            OK "SSH key 產生成功"
            OK "私鑰: $keyPath"
            OK "公鑰: $pubKeyPath"
        } else {
            EE "SSH key 產生失敗"
            exit 1
        }
    } catch {
        EE "錯誤: $_"
        exit 1
    }
}

# 讀取公鑰
if (-not (Test-Path $pubKeyPath)) {
    EE "找不到公鑰檔案: $pubKeyPath"
    exit 1
}

$pubKey = Get-Content $pubKeyPath -Raw
II "公鑰內容:"
Write-Host "  $($pubKey.Trim())" -f $colors.info

# 測試伺服器連線
H "測試伺服器連線"
II "連接到 $ServerUser@$ServerIP ..."

$testResult = Test-NetConnection -ComputerName $ServerIP -Port 22 -WarningAction SilentlyContinue
if (-not $testResult.TcpTestSucceeded) {
    EE "無法連接到伺服器 port 22"
    II "請確認:"
    Write-Host "  1. 伺服器 IP 正確: $ServerIP" -f $colors.info
    Write-Host "  2. SSH 服務運行中" -f $colors.info
    Write-Host "  3. 防火牆允許 port 22" -f $colors.info
    exit 1
}
OK "伺服器 port 22 可連接"

# 複製公鑰到伺服器
H "複製公鑰到伺服器"

Write-Host "`n選擇方式:" -f $colors.info
Write-Host "  1. 自動複製 (需輸入密碼一次)" -f $colors.info
Write-Host "  2. 手動複製 (顯示指令讓你自己執行)" -f $colors.info
$method = Read-Host "`n請選擇 (1/2)"

if ($method -eq "1") {
    II "使用 ssh-copy-id 或手動方式..."
    
    # 檢查是否有 ssh-copy-id (通常 Windows 沒有)
    $hasSshCopyId = Get-Command ssh-copy-id -ErrorAction SilentlyContinue
    
    if ($hasSshCopyId) {
        II "執行: ssh-copy-id -i $pubKeyPath $ServerUser@$ServerIP"
        ssh-copy-id -i $pubKeyPath "$ServerUser@$ServerIP"
    } else {
        II "Windows 沒有 ssh-copy-id，使用替代方式..."
        II "需要輸入伺服器密碼一次"
        
        $escapedKey = $pubKey.Replace('"', '\"')
        $cmd = "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo `"$escapedKey`" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'Key added successfully'"
        
        Write-Host "`n執行指令..." -f $colors.info
        ssh "$ServerUser@$ServerIP" $cmd
        
        if ($LASTEXITCODE -eq 0) {
            OK "公鑰已成功複製到伺服器"
        } else {
            EE "複製失敗，錯誤碼: $LASTEXITCODE"
            II "請嘗試手動方式 (選項 2)"
            exit 1
        }
    }
} else {
    H "手動複製指令"
    Write-Host "`n請依序執行以下指令:" -f $colors.warn
    Write-Host ""
    Write-Host "1. 複製這段公鑰 (按 Enter 後會自動複製到剪貼簿):" -f $colors.info
    Write-Host ""
    Write-Host $pubKey.Trim() -f $colors.header
    Write-Host ""
    Read-Host "按 Enter 複製到剪貼簿"
    Set-Clipboard -Value $pubKey.Trim()
    OK "已複製到剪貼簿"
    
    Write-Host "`n2. 登入伺服器:" -f $colors.info
    Write-Host "   ssh $ServerUser@$ServerIP" -f $colors.header
    
    Write-Host "`n3. 在伺服器執行:" -f $colors.info
    Write-Host "   mkdir -p ~/.ssh" -f $colors.header
    Write-Host "   chmod 700 ~/.ssh" -f $colors.header
    Write-Host "   nano ~/.ssh/authorized_keys  # 或用 vi" -f $colors.header
    
    Write-Host "`n4. 貼上剛才的公鑰 (Ctrl+Shift+V)，存檔離開" -f $colors.info
    
    Write-Host "`n5. 設定權限:" -f $colors.info
    Write-Host "   chmod 600 ~/.ssh/authorized_keys" -f $colors.header
    
    Write-Host "`n6. 登出後測試:" -f $colors.info
    Write-Host "   exit" -f $colors.header
    Write-Host "   ssh $ServerUser@$ServerIP" -f $colors.header
    
    Write-Host ""
    Read-Host "完成後按 Enter 繼續測試"
}

# 測試免密碼登入
H "測試免密碼登入"
II "測試連線..."

$testCmd = "echo 'SSH login successful'"
$result = ssh -o BatchMode=yes -o ConnectTimeout=5 "$ServerUser@$ServerIP" $testCmd 2>&1

if ($result -match "successful") {
    OK "免密碼登入設定成功！"
    Write-Host ""
    Write-Host "  測試指令: ssh $ServerUser@$ServerIP" -f $colors.ok
    Write-Host "  比對腳本: pwsh -File .\compare_ui_files.ps1" -f $colors.ok
} else {
    EE "免密碼登入測試失敗"
    II "可能原因:"
    Write-Host "  1. 公鑰尚未正確加入 ~/.ssh/authorized_keys" -f $colors.info
    Write-Host "  2. 檔案權限不正確 (需 600)" -f $colors.info
    Write-Host "  3. SSH 設定不允許 key 認證" -f $colors.info
    Write-Host ""
    II "除錯步驟:"
    Write-Host "  ssh -v $ServerUser@$ServerIP  # 看詳細錯誤" -f $colors.info
    Write-Host "  # 在伺服器檢查:" -f $colors.info
    Write-Host "  ls -la ~/.ssh/authorized_keys  # 應為 -rw-------" -f $colors.info
    Write-Host "  cat /etc/ssh/sshd_config | grep PubkeyAuthentication  # 應為 yes" -f $colors.info
}

Write-Host ""
