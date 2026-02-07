# Rebuild Odoo Environment (Safe Mode)
$ErrorActionPreference = "Stop"
$OdooPath = "C:\Users\o0930\odoo"
$VenvPath = "$OdooPath\venv"

Write-Host "Step 1: Checking Odoo Source..."
if (-not (Test-Path "$OdooPath\odoo-bin")) {
    if (Test-Path $OdooPath) {
        $files = Get-ChildItem -Path $OdooPath -Force
        if ($files.Count -eq 0) {
             Write-Host "Directory exists but is empty. Cloning..."
             git clone --depth 1 -b 17.0 https://github.com/odoo/odoo.git $OdooPath
        } else {
             Write-Host "Directory exists and is not empty. Attempting git pull..."
             Push-Location $OdooPath
             try {
                git pull
             } catch {
                Write-Warning "Git pull failed. Assuming directory might be corrupted or not a git repo."
                Write-Warning "Please manually clear C:\Users\o0930\odoo if this fails."
             }
             Pop-Location
        }
    } else {
        Write-Host "Cloning Odoo 17..."
        git clone --depth 1 -b 17.0 https://github.com/odoo/odoo.git $OdooPath
    }
} else {
    Write-Host "Odoo source found at $OdooPath"
}

Write-Host "Step 2: Recreating venv..."
# Use --clear to overwrite existing venv safely without Remove-Item
& "python" -m venv $VenvPath --clear

Write-Host "Step 3: Installing Dependencies..."
$pip = "$VenvPath\Scripts\pip.exe"

# Validate pip exists
if (-not (Test-Path $pip)) {
    Write-Error "Pip not found at $pip after venv creation!"
}

& $pip install --upgrade pip
# Install basic requirements from Odoo source
& $pip install -r "$OdooPath\requirements.txt"
# Install user requested packages and binary fixes
& $pip install reportlab polib decorator docutils html2text num2words xlwt xlsxwriter python-stdnum manifest-file
& $pip install psycopg2-binary libsass pypdf pillow gevent greenlet lxml werkzeug==2.2.2

Write-Host "Step 4: Verifying Installation..."
$python = "$VenvPath\Scripts\python.exe"
$odoo_bin = "$OdooPath\odoo-bin"
$config = "C:\wuchang V5.0.0\config\odoo.conf"

if (Test-Path $odoo_bin) {
    Write-Host "Odoo binary found."
    Write-Host "You can start Odoo with:"
    Write-Host "& `"$python`" `"$odoo_bin`" -c `"$config`""
} else {
    Write-Error "Odoo binary still missing!"
}
