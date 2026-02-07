Write-Host "=== Wuchang System VM Deployment Helper ===" -ForegroundColor Cyan
Write-Host "Preparing to deploy system to VM: vm-system-us (35.222.14.0)" -ForegroundColor Yellow

# 1. Compress Source Code
 = "wuchang_os"
 = "wuchang_deploy.zip"
if (Test-Path ) { Remove-Item  }

Write-Host "Compressing ..."
Compress-Archive -Path  -DestinationPath 

Write-Host "Compression Complete: " -ForegroundColor Green

# 2. Instructions
Write-Host "
=== Deployment Instructions ===" -ForegroundColor Cyan
Write-Host "Please execute the following command in your terminal (where your SSH key is available):"
Write-Host "scp -i [YOUR_KEY_PATH]  nic0@35.222.14.0:~/" -ForegroundColor White -BackgroundColor DarkBlue

Write-Host "
Then SSH into the VM and run:"
Write-Host "ssh -i [YOUR_KEY_PATH] nic0@35.222.14.0" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "unzip wuchang_deploy.zip -d wuchang_os"
Write-Host "cd wuchang_os"
Write-Host "pip install -r requirements.txt"
Write-Host "./odoo-bin -c odoo.conf"

Write-Host "
=== System Enhanced with Vertex AI ===" -ForegroundColor Magenta
Write-Host "Vertex AI Mode: ENABLED"
Write-Host "GPU Status: Using Google Cloud Vertex AI (Remote GPU/TPU)"
