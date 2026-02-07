# Deploy-Win-Odoo-Native.ps1
# Automates Odoo 17.0 installation on Windows VM
# Requirements: Admin Privileges

$ErrorActionPreference = "Stop"
$toolsDir = "C:\tools"
$odooDir = "$HOME\odoo"
$projectDir = "$HOME\wuchang_project"
$venvDir = "$odooDir\venv"

function Write-Log {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

# 1. Check Admin
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator!"
    exit 1
}

Write-Log "Starting Odoo Native Installation..." "Green"

# 2. Install System Dependencies via Chocolatey
Write-Log "Installing System Dependencies..."
$chocoPackages = @(
    @{Name = "postgresql15"; Params = "/Password:odoo /Port:5432" },
    @{Name = "wkhtmltopdf"; Params = "" },
    @{Name = "nodejs-lts"; Params = "" },
    @{Name = "git"; Params = "" },
    @{Name = "microsoft-visual-cpp-build-tools"; Params = "" } 
)

foreach ($pkg in $chocoPackages) {
    if (-not (Get-Command $pkg.Name -ErrorAction SilentlyContinue)) {
        Write-Log "Installing $($pkg.Name)..."
        choco install $pkg.Name -y --params $pkg.Params
    }
    else {
        Write-Log "$($pkg.Name) is already installed." "Yellow"
    }
}

# 3. Configure PostgreSQL
Write-Log "Configuring PostgreSQL..."
$pgBin = "C:\Program Files\PostgreSQL\15\bin"
if (Test-Path $pgBin) {
    $env:Path += ";$pgBin"
    # Create user 'odoo' if not exists
    try {
        & "$pgBin\createuser.exe" -U postgres -w -d -R -S odoo
        Write-Log "Created postgres user 'odoo'." "Green"
    }
    catch {
        Write-Log "User 'odoo' might already exist or DB not ready." "Yellow"
    }
    # Set password for 'odoo' just in case
    & "$pgBin\psql.exe" -U postgres -c "ALTER USER odoo WITH PASSWORD 'odoo';"
}
else {
    Write-Log "PostgreSQL bin not found. Please check installation." "Red"
}

# 4. Clone Odoo 17
if (-not (Test-Path $odooDir)) {
    Write-Log "Cloning Odoo 17.0..."
    git clone https://github.com/odoo/odoo.git --depth 1 --branch 17.0 $odooDir
}
else {
    Write-Log "Odoo directory exists. Skipping clone." "Yellow"
}

# 5. Setup Python Environment
Write-Log "Setting up Python Virtual Environment..."
if (-not (Test-Path $venvDir)) {
    python -m venv $venvDir
}

# Upgrade pip
& "$venvDir\Scripts\python.exe" -m pip install --upgrade pip

Write-Log "Pinning wheel/setuptools for compatibility..."
& "$venvDir\Scripts\pip.exe" install "wheel==0.43.0" "setuptools<75" --upgrade

# Install Odoo Requirements
Write-Log "Installing Python Requirements (this may take a while)..."
# We need to filter psycopg2 to psycopg2-binary for easier Windows install
$reqFile = "$odooDir\requirements.txt"
$reqContent = Get-Content $reqFile
$reqContent = $reqContent -replace "psycopg2", "psycopg2-binary"
# Remove python-ldap and gevent on windows if they fail easily, but let's try
# For Windows, we might need specific wheels. 
# Let's try standard install first, but psycopg2-binary is a must.
$reqContent | Set-Content "$odooDir\requirements_win.txt"

try {
    # Force psycopg2-binary to use binary only to avoid compilation
    & "$venvDir\Scripts\pip.exe" install psycopg2-binary --only-binary=:all:
    & "$venvDir\Scripts\pip.exe" install -r "$odooDir\requirements_win.txt" --prefer-binary
    # Ensure HTTP stack present
    & "$venvDir\Scripts\pip.exe" install requests urllib3 idna charset-normalizer certifi --upgrade
}
catch {
    Write-Log "Pip install had errors. You might need to install some wheels manually." "Red"
}

# Install rtlcss
Write-Log "Installing rtlcss..."
# Ensure npm is in PATH (Chocolatey installs to Program Files)
$env:Path += ";C:\Program Files\nodejs"
if (Get-Command npm -ErrorAction SilentlyContinue) {
    npm install -g rtlcss
}
else {
    Write-Log "npm not found. Skipping rtlcss installation." "Yellow"
}

# 6. Create Configuration File
Write-Log "Creating Odoo Configuration..."
$addonsPath = "$odooDir\addons,$projectDir\wuchang_os\addons"
$confContent = @"
[options]
admin_passwd = odoo
addons_path = $addonsPath
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
http_port = 8069
"@
$confPath = "$projectDir\config\odoo_win.conf"
$confDir = Split-Path -Parent $confPath
if (-not (Test-Path $confDir)) {
    New-Item -ItemType Directory -Path $confDir -Force | Out-Null
}
Set-Content $confPath -Value $confContent

# 7. Create Startup Script
Write-Log "Creating Startup Script..."
$desktopDir = [Environment]::GetFolderPath("Desktop")
$startPath = Join-Path $desktopDir "Start-Odoo.cmd"
$startScript = @"
@echo off
cd /d "$projectDir"
call "$venvDir\Scripts\activate.bat"
python "$odooDir\odoo-bin" -c "$projectDir\config\odoo_win.conf"
pause
"@
Set-Content $startPath -Value $startScript

Write-Log "Installation Complete!" "Green"
Write-Log "You can start Odoo using the shortcut on your Desktop: Start-Odoo.cmd" "Cyan"
