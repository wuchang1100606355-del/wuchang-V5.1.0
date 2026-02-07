param(
    [string]$Password = "Qwerty926",
    [string]$ServerIP = "192.168.50.249",
    [string]$ServerUser = "wuchang"
)

Write-Host "`n=== Auto SSH Key Setup ===" -ForegroundColor Cyan

# Get public key
$pubKeyFile = "$env:USERPROFILE\.ssh\id_ed25519.pub"
if (-not (Test-Path $pubKeyFile)) {
    Write-Host "[ERROR] Public key not found: $pubKeyFile" -ForegroundColor Red
    exit 1
}

$pubKey = (Get-Content $pubKeyFile).Trim()
Write-Host "[INFO] Public Key: $($pubKey.Substring(0,50))..." -ForegroundColor Gray

# Create script to deploy key
$deployCmd = @"
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '$pubKey' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo 'KEY_INSTALLED'
"@

# Use password to execute command
Write-Host "[INFO] Deploying SSH key to $ServerUser@$ServerIP..." -ForegroundColor Yellow

$tempScript = [System.IO.Path]::GetTempFileName()
$deployCmd | Out-File -FilePath $tempScript -Encoding ASCII

try {
    $result = Get-Content $tempScript | ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=yes "$ServerUser@$ServerIP" "bash -s" 2>&1
    
    if ($result -match "KEY_INSTALLED") {
        Write-Host "[OK] SSH Key installed successfully!" -ForegroundColor Green
        
        # Test passwordless login
        Write-Host "`n[INFO] Testing passwordless login..." -ForegroundColor Yellow
        $testResult = ssh -o BatchMode=yes -o ConnectTimeout=5 "$ServerUser@$ServerIP" "echo 'SSH_OK'; hostname; whoami" 2>&1
        
        if ($testResult -match "SSH_OK") {
            Write-Host "[OK] Passwordless SSH working!" -ForegroundColor Green
            Write-Host "Server: $testResult" -ForegroundColor Gray
        } else {
            Write-Host "[WARN] SSH key deployed but test failed" -ForegroundColor Yellow
            Write-Host $testResult -ForegroundColor Gray
        }
    } else {
        Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
        Write-Host $result -ForegroundColor Gray
    }
} finally {
    Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
}
