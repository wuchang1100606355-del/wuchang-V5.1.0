Param(
  [string]$Root = (Get-Location).Path,
  [string]$CsvPath = "config\points_accounts.csv",
  [int]$WarnDays = 14
)
$ErrorActionPreference = "Stop"

function Write-Log($msg) {
  $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] " + $msg
  Add-Content -Path (Join-Path $Root "automation.log") -Value $line
}

function Ensure-Dir($p) {
  $dir = Split-Path -Parent $p
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}

$csvAbs = Join-Path $Root $CsvPath
$accounts = @()
if (Test-Path $csvAbs) {
  try {
    $accounts = Import-Csv -LiteralPath $csvAbs
  } catch {
    $accounts = @()
  }
}

$alerts = @()
$expired = @()
$now = Get-Date
foreach ($a in $accounts) {
  $provider = "" + $a.provider
  $points = [double]::Parse(("" + $a.points), [System.Globalization.CultureInfo]::InvariantCulture)
  $expStr = "" + $a.expires
  $exp = $null
  try { $exp = [datetime]::ParseExact($expStr, "yyyy-MM-dd", $null) } catch {}
  if (-not $exp) { try { $exp = [datetime]::ParseExact($expStr, "yyyy/MM/dd", $null) } catch {} }
  if (-not $exp) { try { $exp = [datetime]::Parse($expStr) } catch {} }
  if ($exp) {
    $daysLeft = [math]::Floor(($exp - $now).TotalDays)
    if ($daysLeft -le $WarnDays -and $daysLeft -gt 0) {
      $alerts += @{ provider = $provider; points = $points; expires = $exp.ToString("yyyy-MM-dd"); days = $daysLeft }
    } elseif ($daysLeft -le 0) {
      $expired += @{ provider = $provider; points = $points; expired_on = $exp.ToString("yyyy-MM-dd") }
    }
  }
}

$summaryMsg = "Points reminder: accounts=" + $accounts.Count + ", alerts=" + $alerts.Count + ", expired=" + $expired.Count
Write-Log $summaryMsg

$workLogCsv = Join-Path $Root "logs\work_log.csv"
Ensure-Dir $workLogCsv
if (-not (Test-Path $workLogCsv)) {
  Set-Content -LiteralPath $workLogCsv -Value "date,time,actor,task,result,details" -Encoding UTF8
}
$result = if ($alerts.Count -gt 0 -or $expired.Count -gt 0) { "ACTION NEEDED" } else { "OK" }
$details = "accounts=" + $accounts.Count + "; alerts=" + $alerts.Count + "; expired=" + $expired.Count
Add-Content -LiteralPath $workLogCsv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", "points_reminder", $result, $details)

Write-Output $summaryMsg
