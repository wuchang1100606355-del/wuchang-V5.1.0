Param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectID,
    
    [string]$Zone = "us-central1-a",
    [string]$Region = "us-central1",
    [ValidateSet('system', 'ui')]
    [string]$Role = 'system',
    [string]$VmName = "",
    [string]$IpName = "",
    [switch]$IncludeData = $false,
    [switch]$SkipVmCreate = $false
)

$ErrorActionPreference = "Stop"

# 0. Configure Role Defaults
if ($Role -eq 'system') {
    if (-not $VmName) { $VmName = "vm-system-odoo" }
    if (-not $IpName) { $IpName = "ip-system-odoo" }
    $MachineType = "e2-standard-8" # Consider reducing to e2-standard-4 if cost is concern
    $BootDiskSize = "200GB"
}
else {
    if (-not $VmName) { $VmName = "vm-ui-ai-hub" }
    if (-not $IpName) { $IpName = "ip-ui-ai-hub" }
    $MachineType = "e2-standard-8"
    $BootDiskSize = "150GB"
}

Write-Host "Deployment Config: Role=$Role, VM=$VmName, IP=$IpName, Zone=$Zone" -ForegroundColor Magenta

# 1. Config Project
Write-Host "Setting gcloud project to $ProjectID..." -ForegroundColor Cyan
gcloud config set project $ProjectID

# 2. Check/Create IP
$sysIp = ""
if (-not $SkipVmCreate) {
    Write-Host "Checking IP Address $IpName..." -ForegroundColor Cyan
    $exists = gcloud compute addresses list --filter="name=('$IpName')" --format="get(name)"
    if (-not $exists) { 
        Write-Host "Creating static IP $IpName..." -ForegroundColor Yellow
        gcloud compute addresses create $IpName --region=$Region 
    }
    $sysIp = gcloud compute addresses describe $IpName --region=$Region --format='get(address)'
    Write-Host "Target IP: $sysIp" -ForegroundColor Green
}

# 3. Create VM
if (-not $SkipVmCreate) {
    Write-Host "Checking VM $VmName..." -ForegroundColor Cyan
    $vmExists = gcloud compute instances list --filter="name=('$VmName')" --format="get(name)"
    if (-not $vmExists) {
        Write-Host "Creating VM $VmName..." -ForegroundColor Yellow
        gcloud compute instances create $VmName `
            --zone=$Zone `
            --machine-type=$MachineType `
            --image-family=ubuntu-2204-lts `
            --image-project=ubuntu-os-cloud `
            --boot-disk-size=$BootDiskSize `
            --tags=http-server, https-server `
            --address=$sysIp `
            --metadata=startup-script='#!/bin/bash 
         apt-get update -y 
         apt-get install -y ca-certificates curl gnupg lsb-release docker-compose-plugin unzip 
         curl -fsSL https://get.docker.com | sh 
         systemctl enable docker 
         mkdir -p /opt/wuchang 
         '
         
        Write-Host "VM creating... Waiting 60s for startup..." -ForegroundColor Yellow
        Start-Sleep -Seconds 60
    }
    else {
        Write-Host "VM $VmName already exists." -ForegroundColor Green
        # Get IP if not set
        if (-not $sysIp) {
            $sysIp = gcloud compute instances describe $VmName --zone=$Zone --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
        }
    }
}

# 4. Prepare Zip
$zipPath = "$env:TEMP\wuchang_project.zip"
Write-Host "Preparing deployment package to $zipPath..." -ForegroundColor Cyan
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

# Select items to zip
$includes = @(
    "wuchang_os",
    "scripts",
    "config",
    "docker-compose.yml",
    "Dockerfile",
    "package.json"
)

if ($IncludeData) {
    $includes += "migration_pack"
    $includes += "memory_store"
    Write-Host "Including data directories (migration_pack, memory_store)..." -ForegroundColor Magenta
}
else {
    Write-Host "Skipping data directories (use -IncludeData to include)." -ForegroundColor Gray
}

# Create temp dir for clean zipping
$tempDir = Join-Path $env:TEMP "wuchang_deploy_$(Get-Random)"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
foreach ($item in $includes) {
    if (Test-Path $item) {
        Copy-Item -Path $item -Destination $tempDir -Recurse -Force
    }
}

Write-Host "Zipping files..." -ForegroundColor Cyan
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force
Remove-Item $tempDir -Recurse -Force

# 5. Upload
Write-Host "Uploading package to VM..." -ForegroundColor Cyan
gcloud compute scp $zipPath "$VmName`:~/wuchang_project.zip" --zone=$Zone

# 6. Deploy
Write-Host "Executing remote deployment..." -ForegroundColor Cyan
$profile = if ($Role -eq 'ui') { 'ui' } else { 'system' }
$remoteCmd = "mkdir -p ~/app && mv ~/wuchang_project.zip ~/app/ && cd ~/app && unzip -o wuchang_project.zip && docker compose --profile $profile up -d --build"
Write-Host "Deploying with profile: $profile" -ForegroundColor Cyan

gcloud compute ssh $VmName --zone=$Zone --command "$remoteCmd"

# 7. Post-flight Check
Write-Host "Deployment command sent. Waiting 30s for services to stabilize..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

Write-Host "Running Pre-flight/Sanity Checks against $sysIp..." -ForegroundColor Cyan
$localTestScript = ".\scripts\sanity_deploy_tests.ps1"
if (Test-Path $localTestScript) {
    Invoke-Expression "& '$localTestScript' -BaseUrl 'http://$sysIp'"
}
else {
    Write-Host "Warning: Sanity test script not found at $localTestScript" -ForegroundColor Yellow
}

Write-Host "Done! Access your instance at http://$sysIp" -ForegroundColor Green
