Param(
  [string]$OutDir = "backups"
)
$ErrorActionPreference = "Stop"
$root = (Get-Location).Path
$ts = Get-Date -Format "yyyyMMddHHmmss"
$paths = @(
  (Join-Path $root "wuchang_os"),
  (Join-Path $root "scripts"),
  (Join-Path $root "config"),
  (Join-Path $root "docker-compose.yml")
)
$dest = Join-Path $root (Join-Path $OutDir ("workspace_vm_package_" + $ts + ".zip"))
Compress-Archive -Path $paths -DestinationPath $dest -Force
Write-Output $dest

