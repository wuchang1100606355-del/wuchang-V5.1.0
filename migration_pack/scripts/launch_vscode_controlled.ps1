Param(
  [string]$Root = (Get-Location).Path,
  [string]$User = "o0930"
)
$ErrorActionPreference = "Stop"
$codeDir = "C:\Users\$User\AppData\Local\Programs\Microsoft VS Code"
$codeExe = Join-Path $codeDir "Code.exe"
if (-not (Test-Path $codeExe)) { $codeExe = "code" }
$userData = Join-Path $Root "vscode_user"
$extDir = Join-Path $Root "vscode_ext"
if (-not (Test-Path $userData)) { New-Item -ItemType Directory -Path $userData -Force | Out-Null }
if (-not (Test-Path $extDir)) { New-Item -ItemType Directory -Path $extDir -Force | Out-Null }
$workspace = Join-Path $Root "wuchang.code-workspace"
$args = @()
$args += ("--user-data-dir=" + $userData)
$args += ("--extensions-dir=" + $extDir)
if (Test-Path $workspace) { $args += $workspace } else { $args += $Root }
Start-Process -FilePath $codeExe -ArgumentList $args
Write-Output ("vscode_controlled_launch: " + $codeExe)

