# Deploy-WinVM-Agent.ps1
# Win-VM Environment Initialization Script

Write-Host "Starting initialization..." -ForegroundColor Cyan

# 1. Install Chocolatey
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}
else {
    Write-Host "Chocolatey is already installed." -ForegroundColor Green
}

# Refresh Environment Variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# 2. Install OpenSSH Server
Write-Host "Installing OpenSSH Server..." -ForegroundColor Yellow
choco install openssh -y --params="/SSHServerFeature"

# 3. Install Python
Write-Host "Installing Python..." -ForegroundColor Yellow
choco install python -y

# 4. Install Git
Write-Host "Installing Git..." -ForegroundColor Yellow
choco install git -y

# 5. Configure Firewall
Write-Host "Configuring Firewall (Allow Port 22)..." -ForegroundColor Yellow
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -ErrorAction SilentlyContinue

# 6. Start SSH Service
Write-Host "Starting SSH Service..." -ForegroundColor Yellow
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

Write-Host "Initialization Complete! Win-VM is ready." -ForegroundColor Green
Write-Host "You can now connect remotely." -ForegroundColor Cyan
