Param(
  [string]$Source,
  [string]$Name,
  [string]$OutDir = "backups\offload",
  [string]$Root = (Get-Location).Path
)
$ErrorActionPreference = "Stop"
if (-not $Source) { Write-Output "error: Source required"; exit 1 }
if (-not $Name) { $Name = Split-Path -Leaf $Source }
$srcAbs = Join-Path $Root $Source
if (-not (Test-Path -LiteralPath $srcAbs)) { Write-Output ("skip: " + $srcAbs + " not found"); exit 0 }
$outAbs = Join-Path $Root $OutDir
New-Item -ItemType Directory -Force -Path $outAbs | Out-Null
$ts = Get-Date -Format "yyyyMMddHHmmss"
$zipPath = $null
try {
  $zipPath = Join-Path $outAbs ($Name + "_" + $ts + ".zip")
  Compress-Archive -Path $srcAbs -DestinationPath $zipPath -Force
  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zipPath).Hash.ToLower()
  Set-Content -LiteralPath ($zipPath + ".sha256") -Value $hash -Encoding ASCII
} catch {
  $zipPath = Join-Path $outAbs ($Name + "_hashes.sha256")
  Remove-Item -LiteralPath $zipPath -Force -ErrorAction SilentlyContinue
  $files = Get-ChildItem -Path $srcAbs -Recurse -File -ErrorAction SilentlyContinue
  foreach ($f in $files) {
    try {
      $h = Get-FileHash -Algorithm SHA256 -LiteralPath $f.FullName
      Add-Content -Path $zipPath -Value ($h.Hash.ToLower() + "  " + ($f.FullName.Substring($srcAbs.Length).TrimStart('\')))
    } catch {}
  }
}
Remove-Item -LiteralPath $srcAbs -Recurse -Force
Write-Output $zipPath
