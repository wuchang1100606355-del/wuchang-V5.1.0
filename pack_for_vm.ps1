$deployDir = "c:\wuchang V5.1.0\vm_deploy"
$sourceDir = "c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\scripts"

if (!(Test-Path $deployDir)) {
    New-Item -ItemType Directory -Path $deployDir | Out-Null
}

Copy-Item "$sourceDir\knowledge_sync_agent.py" -Destination $deployDir
Copy-Item "$sourceDir\vm_requirements.txt" -Destination $deployDir
Copy-Item "$sourceDir\setup_vm.sh" -Destination $deployDir

Write-Host "All deployment files gathered in $deployDir"
Write-Host "1. Upload these files to your Google Cloud VM (35.222.14.0)."
Write-Host "2. Run: chmod +x setup_vm.sh && ./setup_vm.sh"
