Param(
  [switch]$InitBaseline,
  [string]$Root = (Get-Location).Path,
  [string]$BaselinePath = "config\integrity_manifest.json",
  [string]$ReportDir = "logs\integrity"
)
$ErrorActionPreference = "Stop"

function Write-Log($msg) {
  $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] " + $msg
  Add-Content -Path (Join-Path $Root "automation.log") -Value $line
}

function Get-RelPath($full) {
  $p = Resolve-Path -LiteralPath $full
  $rp = $p.Path.Replace('/', '\')
  $r = $rp.Replace($Root + '\', '')
  return $r
}

$defaultInclude = @(
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
  "wuchang_os\addons\**\__manifest__.py"
)
$defaultExclude = @(
  ".git\**",
  "node_modules\**",
  "backups\**",
  "downloads\**",
  "memory_store\**",
  ".trae\**"
)

function Match-File($rel, $patterns) {
  foreach ($pat in $patterns) {
    $regex = '^' + [Regex]::Escape($pat).Replace('\*\*', '.*').Replace('\*', '[^\\]*') + '$'
    if ($rel -match $regex) { return $true }
  }
  return $false
}

function Collect-Files($root, $include, $exclude) {
  $all = Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue
  $out = New-Object System.Collections.Generic.List[System.IO.FileInfo]
  foreach ($f in $all) {
    $rel = Get-RelPath $f.FullName
    if (Match-File $rel $exclude) { continue }
    if (Match-File $rel $include) { $out.Add($f) }
  }
  return $out
}

function Hash-File($path) {
  $h = Get-FileHash -Algorithm SHA256 -LiteralPath $path
  return $h.Hash.ToLower()
}

function Ensure-Dir($p) {
  $dir = Split-Path -Parent $p
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}

# Load or initialize manifest
$manifest = $null
$rules = @{
  include = $defaultInclude
  exclude = $defaultExclude
}

if ($InitBaseline -or -not (Test-Path (Join-Path $Root $BaselinePath))) {
  $files = Collect-Files $Root $rules.include $rules.exclude
  $items = @()
  foreach ($f in $files) {
    $items += @{
      path  = Get-RelPath $f.FullName
      sha256 = Hash-File $f.FullName
      size = $f.Length
    }
  }
  $manifest = @{
    version = 1
    created_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    rules = $rules
    files = $items
  }
  $baselineAbs = Join-Path $Root $BaselinePath
  Ensure-Dir $baselineAbs
  ($manifest | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $baselineAbs -Encoding UTF8
  Write-Log "Integrity baseline created at $BaselinePath with $($items.Count) files."
  Write-Output "Baseline created: $BaselinePath"
  exit 0
} else {
  $baselineAbs = Join-Path $Root $BaselinePath
  $manifest = Get-Content -LiteralPath $baselineAbs -Raw | ConvertFrom-Json
  if ($manifest.rules -and $manifest.rules.include) { $rules.include = @($manifest.rules.include) }
  if ($manifest.rules -and $manifest.rules.exclude) { $rules.exclude = @($manifest.rules.exclude) }
}

# Verify current files against baseline
$current = Collect-Files $Root $rules.include $rules.exclude
$baselineMap = @{}
foreach ($b in $manifest.files) { $baselineMap[$b.path] = $b }

$report = @{
  date = (Get-Date -Format "yyyy-MM-dd")
  time = (Get-Date -Format "HH:mm:ss")
  summary = @{
    ok = 0; mismatch = 0; new = 0; missing = 0; total = 0
  }
  items = @()
}

$seen = New-Object System.Collections.Generic.HashSet[string]
foreach ($f in $current) {
  $rel = Get-RelPath $f.FullName
  $seen.Add($rel) | Out-Null
  $sha = Hash-File $f.FullName
  if ($baselineMap.ContainsKey($rel)) {
    $expected = $baselineMap[$rel].sha256
    if ($sha -eq $expected) {
      $report.items += @{ path = $rel; status = "ok"; sha256 = $sha }
      $report.summary.ok++
    } else {
      $report.items += @{ path = $rel; status = "mismatch"; sha256 = $sha; expected = $expected }
      $report.summary.mismatch++
    }
  } else {
    $report.items += @{ path = $rel; status = "new"; sha256 = $sha }
    $report.summary.new++
  }
}

foreach ($k in $baselineMap.Keys) {
  if (-not $seen.Contains($k)) {
    $report.items += @{ path = $k; status = "missing"; expected = $baselineMap[$k].sha256 }
    $report.summary.missing++
  }
}

$report.summary.total = $report.items.Count

$reportPath = Join-Path $Root (Join-Path $ReportDir ((Get-Date -Format "yyyyMMdd") + ".json"))
Ensure-Dir $reportPath
($report | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $reportPath -Encoding UTF8

$statusMsg = "Integrity check: ok=$($report.summary.ok), mismatch=$($report.summary.mismatch), new=$($report.summary.new), missing=$($report.summary.missing)"
Write-Log $statusMsg

$workLogCsv = Join-Path $Root "logs\work_log.csv"
Ensure-Dir $workLogCsv
if (-not (Test-Path $workLogCsv)) {
  Set-Content -LiteralPath $workLogCsv -Value "date,time,actor,task,result,details" -Encoding UTF8
}
$result = if ($report.summary.mismatch -gt 0 -or $report.summary.missing -gt 0) { "MISMATCH DETECTED" } else { "OK" }
$details = "ok=$($report.summary.ok); mismatch=$($report.summary.mismatch); new=$($report.summary.new); missing=$($report.summary.missing)"
# Use ASCII-safe labels to avoid codepage parsing issues
Add-Content -LiteralPath $workLogCsv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", "daily_integrity_check", $result, $details)

Write-Output $statusMsg
