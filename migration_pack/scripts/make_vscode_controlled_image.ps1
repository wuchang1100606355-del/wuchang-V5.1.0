Param(
  [string]$User = "o0930",
  [string]$OutDir = "backups"
)
$ErrorActionPreference = "Stop"
$root = (Get-Location).Path
$ts = Get-Date -Format "yyyyMMddHHmmss"
$codeDir = "C:\Users\$User\AppData\Local\Programs\Microsoft VS Code"
$launcher = Join-Path $root "scripts\launch_vscode_controlled.ps1"
$workspace = Join-Path $root "wuchang.code-workspace"
$userDataDir = Join-Path $root "vscode_user"
if (-not (Test-Path $launcher)) { Write-Error "Launcher missing: $launcher" }
if (-not (Test-Path $workspace)) { Write-Error "Workspace missing: $workspace" }
if (-not (Test-Path $userDataDir)) { Write-Error "UserData missing: $userDataDir" }
$dest = Join-Path $root (Join-Path $OutDir ("vscode_controlled_image_" + $ts + ".zip"))
$targets = @()
if (Test-Path $codeDir) { $targets += $codeDir }
$targets += $launcher
$targets += $workspace
$targets += $userDataDir
Compress-Archive -Path $targets -DestinationPath $dest -Force
Write-Output $dest

