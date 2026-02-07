Param(
  [string]$Root = (Get-Location).Path,
  [string]$OutDir = "backups",
  [string]$IndexDir = "logs\context_index"
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path (Join-Path $Root $OutDir) | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Root $IndexDir) | Out-Null
$ts = Get-Date -Format "yyyyMMddHHmmss"
$zipPath = Join-Path $Root ("backups/reading_context_" + $ts + ".zip")
$targets = @()
$mem = Join-Path $Root "memory_store"
if (Test-Path $mem) { $targets += $mem }
$logs = Join-Path $Root "logs"
if (Test-Path $logs) { $targets += $logs }
$cfg = Join-Path $Root "config"
if (Test-Path $cfg) { $targets += $cfg }
$addons = Join-Path $Root "wuchang_os\addons"
if (Test-Path $addons) { $targets += $addons }
$compose = Join-Path $Root "docker-compose.yml"
if (Test-Path $compose) { $targets += $compose }
$caddy = Join-Path $Root "wuchang_os\Caddyfile"
if (Test-Path $caddy) { $targets += $caddy }
Compress-Archive -Path $targets -DestinationPath $zipPath -Force
$files = @()
$include = @(
  "docker-compose.yml",
  "requirements.txt",
  "wuchang_os\Caddyfile",
  "config\*.conf",
  "scripts\*.ps1",
  "scripts\*.py",
  "wuchang_os\addons\**\*.py",
  "wuchang_os\addons\**\*.xml",
  "wuchang_os\addons\**\*.csv",
  "wuchang_os\addons\**\*.json",
  "wuchang_os\addons\**\__manifest__.py",
  "memory_store\**\*.json",
  "memory_store\**\*.md"
)
function Match-File($rel, $patterns) {
  foreach ($pat in $patterns) {
    $regex = '^' + [Regex]::Escape($pat).Replace('\\*\\*', '.*').Replace('\\*', '[^\\]*') + '$'
    if ($rel -match $regex) { return $true }
  }
  return $false
}
$all = Get-ChildItem -Path $Root -Recurse -File -ErrorAction SilentlyContinue
foreach ($f in $all) {
  $rel = $f.FullName.Replace($Root + '\\', '')
  if (-not (Match-File $rel $include)) { continue }
  try {
    $h = Get-FileHash -Algorithm SHA256 -LiteralPath $f.FullName
    $sample = ""
    try {
      $content = Get-Content -LiteralPath $f.FullName -TotalCount 10 -ErrorAction SilentlyContinue
      $sample = ("" + ($content -join "`n"))
      if ($sample.Length -gt 600) { $sample = $sample.Substring(0,600) }
    } catch {}
    $files += [pscustomobject]@{
      path = $rel
      size = $f.Length
      sha256 = $h.Hash
      head = $sample
    }
  } catch {}
}
$json = $files | ConvertTo-Json -Depth 4
$out = Join-Path $Root ("logs/context_index/" + $ts + ".json")
Set-Content -LiteralPath $out -Value $json -Encoding UTF8
Write-Output ("context_index: " + $out)
