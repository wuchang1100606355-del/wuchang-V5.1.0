$InstanceName = "wuchang-shop-vm"
$Region = "asia-east1"
$Zone = "asia-east1-a"
$MachineType = "e2-standard-4"
$ImageProject = "ubuntu-os-cloud"
$ImageFamily = "ubuntu-2204-lts"
$StartupScriptPath = Join-Path $PSScriptRoot "deploy_shop_wuchang.sh"

Write-Host "Creating VM: $InstanceName ($MachineType) in $Zone..." -ForegroundColor Cyan
Write-Host "Startup Script: $StartupScriptPath" -ForegroundColor Yellow

$gcloudArgs = @(
    "compute", "instances", "create", $InstanceName,
    "--zone=$Zone",
    "--machine-type=$MachineType",
    "--image-family=$ImageFamily",
    "--image-project=$ImageProject",
    "--tags=http-server,https-server",
    "--boot-disk-size=50GB",
    "--boot-disk-type=pd-balanced",
    "--metadata-from-file", "startup-script=$StartupScriptPath"
)

& gcloud $gcloudArgs

Write-Host "VM Creation command sent. Waiting for IP..." -ForegroundColor Green
Start-Sleep -Seconds 10
gcloud compute instances list --filter="name=($InstanceName)"
