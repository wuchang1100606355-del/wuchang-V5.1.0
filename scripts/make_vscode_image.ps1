Param(
  [string]$User = "o0930",
  [string]$OutDir = "backups"
)
$ErrorActionPreference = "Stop"
$root = (Get-Location).Path
$ts = Get-Date -Format "yyyyMMddHHmmss"
$lnk = "C:\Users\$User\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code\Visual Studio Code.lnk"
$bin = "C:\Users\$User\AppData\Local\Programs\Microsoft VS Code"
$dest = Join-Path $root (Join-Path $OutDir ("vscode_image_" + $ts + ".zip"))
$targets = @()
if (Test-Path $lnk) { $targets += $lnk }
if (Test-Path $bin) { $targets += $bin }
if ($targets.Count -eq 0) {
  Write-Error "No VS Code files found for user '$User'"
}
Compress-Archive -Path $targets -DestinationPath $dest -Force
Write-Output $dest

