Param(
  [string]$Root = (Get-Location).Path,
  [string]$CloudBase,
  [string]$Subdir = "wuchang\offload"
)
$ErrorActionPreference = "Stop"

function Write-Log($msg) {
  $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] " + $msg
  try { Add-Content -Path (Join-Path $Root "automation.log") -Value $line } catch {}
}

function Find-CloudBase() {
  if ($CloudBase -and (Test-Path -LiteralPath $CloudBase)) { return $CloudBase }
  $cands = @(
    "G:\\My Drive", "X:\\My Drive", "Z:\\My Drive", "T:\\My Drive",
    (Join-Path $env:USERPROFILE "My Drive"),
    (Join-Path $env:USERPROFILE "Google Drive"),
    "G:\\"
  )
  foreach ($c in $cands) { if (Test-Path -LiteralPath $c) { return $c } }
  return $null
}

$base = Find-CloudBase
if (-not $base) {
  $stage = Join-Path $env:USERPROFILE "Desktop\upload_wuchang"
  New-Item -ItemType Directory -Force -Path $stage | Out-Null
  $dest = $stage
  Write-Log ("Cloud base not found. Staging to: " + $stage)
} else {
  $dest = Join-Path $base $Subdir
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Write-Log ("Cloud base: " + $base + " dest: " + $dest)
}

$toCopy = New-Object System.Collections.Generic.List[string]
function Add-IfExists($pattern) {
  try {
    $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    foreach ($f in $files) { $toCopy.Add($f.FullName) }
  } catch {}
}

Add-IfExists (Join-Path $Root "backups/workspace_vm_package_*.zip")
Add-IfExists (Join-Path $Root "backups/reading_context_*.zip")
Add-IfExists (Join-Path $Root "backups/offload/*.sha256")
Add-IfExists (Join-Path $Root "backups/odoo-*_*.tgz")

$copied = @()
foreach ($src in $toCopy) {
  try {
    $name = Split-Path -Leaf $src
    $dst = Join-Path $dest $name
    Copy-Item -LiteralPath $src -Destination $dst -Force
    $copied += $dst
  } catch {
    Write-Log ("Copy failed: " + $src + " -> " + $dest + " : " + $_.Exception.Message)
  }
}

if ($copied.Count -gt 0) {
  Write-Log ("Cloud sync OK: " + ($copied -join "; "))
  $workLogCsv = Join-Path $Root "logs\work_log.csv"
  if (-not (Test-Path $workLogCsv)) { Set-Content -LiteralPath $workLogCsv -Value "date,time,actor,task,result,details" -Encoding UTF8 }
  Add-Content -LiteralPath $workLogCsv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", "cloud_sync", "OK", ("copied=" + $copied.Count))
}

Write-Output ($copied -join "`n")
