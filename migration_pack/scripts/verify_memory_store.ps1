Param(
  [switch]$InitBaseline,
  [string]$Root = (Get-Location).Path,
  [string]$BaselinePath = "config\\memory_manifest.json",
  [string]$ReportDir = "logs\\memory"
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

function Ensure-Dir($p) {
  $dir = Split-Path -Parent $p
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}

function Hash-File($path) {
  $h = Get-FileHash -Algorithm SHA256 -LiteralPath $path
  return $h.Hash.ToLower()
}

$targetDir = Join-Path $Root "memory_store"
if (-not (Test-Path $targetDir)) {
  Write-Log "Memory store not found: memory_store"
  Write-Output "Memory store missing"
  exit 0
}

function Collect-Files($dir) {
  return Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue
}

$manifest = $null
if ($InitBaseline -or -not (Test-Path (Join-Path $Root $BaselinePath))) {
  $files = Collect-Files $targetDir
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
    root = "memory_store"
    files = $items
  }
  $baselineAbs = Join-Path $Root $BaselinePath
  Ensure-Dir $baselineAbs
  ($manifest | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $baselineAbs -Encoding UTF8
  Write-Log "Memory baseline created at $BaselinePath with $($items.Count) files."
  Write-Output "Baseline created: $BaselinePath"
  exit 0
} else {
  $baselineAbs = Join-Path $Root $BaselinePath
  $manifest = Get-Content -LiteralPath $baselineAbs -Raw | ConvertFrom-Json
}

$current = Collect-Files $targetDir
$baselineMap = @{}
foreach ($b in $manifest.files) { $baselineMap[$b.path] = $b }

$report = @{
  date = (Get-Date -Format "yyyy-MM-dd")
  time = (Get-Date -Format "HH:mm:ss")
  summary = @{
    ok = 0; changed = 0; new = 0; missing = 0; total = 0
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
      $report.items += @{ path = $rel; status = "changed"; sha256 = $sha; expected = $expected }
      $report.summary.changed++
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

$statusMsg = "Memory check: ok=$($report.summary.ok), changed=$($report.summary.changed), new=$($report.summary.new), missing=$($report.summary.missing)"
Write-Log $statusMsg

$workLogCsv = Join-Path $Root "logs\\work_log.csv"
Ensure-Dir $workLogCsv
if (-not (Test-Path $workLogCsv)) {
  Set-Content -LiteralPath $workLogCsv -Value "date,time,actor,task,result,details" -Encoding UTF8
}
$result = if ($report.summary.changed -gt 0 -or $report.summary.missing -gt 0) { "CHANGED" } else { "OK" }
$details = "ok=$($report.summary.ok); changed=$($report.summary.changed); new=$($report.summary.new); missing=$($report.summary.missing)"
Add-Content -LiteralPath $workLogCsv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", "memory_integrity_check", $result, $details)

Write-Output $statusMsg
