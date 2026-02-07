Param(
  [string]$Root = (Get-Location).Path,
  [int]$TimeoutSec = 3
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
function Append-WorkLog($task, $result, $details) {
  $csv = Join-Path $Root "logs/work_log.csv"
  Ensure-Dir $csv
  if (-not (Test-Path $csv)) { Set-Content -LiteralPath $csv -Value "date,time,actor,task,result,details" -Encoding UTF8 }
  Add-Content -LiteralPath $csv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", $task, $result, $details)
}

function Get-GatewayIp() {
  try {
    $def = Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Sort-Object -Property RouteMetric | Select-Object -First 1
    if ($def) { return $def.NextHop }
  } catch {}
  return $null
}

function Get-LocalSubnetIps() {
  $ips = @()
  try {
    $gw = Get-GatewayIp
    $cfgs = Get-NetIPConfiguration | Where-Object { $_.IPv4Address -and $_.IPv4Address.IPAddress }
    $best = $cfgs | Select-Object -First 1
    if ($best -and $best.IPv4Address) {
      $ip = [System.Net.IPAddress]::Parse($best.IPv4Address.IPAddress)
      $mask = [System.Net.IPAddress]::Parse($best.IPv4Address.PrefixLength)
    }
  } catch {}
  try {
    $arpRaw = arp -a | Out-String
    $lines = $arpRaw -split "`r`n"
    foreach ($l in $lines) {
      $m = [Regex]::Match($l, "(\d+\.\d+\.\d+\.\d+)")
      if ($m.Success) { $ips += $m.Groups[1].Value }
    }
  } catch {}
  $ips = $ips | Sort-Object -Unique
  return $ips
}

function Probe-Ports($ip, $ports) {
  $open = @()
  foreach ($p in $ports) {
    try {
      $t = Test-NetConnection -ComputerName $ip -Port $p -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
      if ($t.TcpTestSucceeded) { $open += $p }
    } catch {}
  }
  return $open
}

function Guess-Brand($ip) {
  $server = ""
  $title = ""
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec $TimeoutSec ("http://" + $ip)
    if ($resp.Headers.ContainsKey("Server")) { $server = "" + $resp.Headers["Server"] }
    $html = "" + $resp.Content
    $t = [Regex]::Match($html, "<title>(.*?)</title>", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    if ($t.Success) { $title = $t.Groups[1].Value }
  } catch {}
  $b = ""
  $signal = ($server + " " + $title)
  if ($signal -match "Hikvision|Hik") { $b = "Hikvision" }
  elseif ($signal -match "Dahua|Amcrest") { $b = "Dahua" }
  elseif ($signal -match "Uniview|UNV") { $b = "Uniview" }
  elseif ($signal -match "Ezviz") { $b = "Ezviz" }
  elseif ($signal -match "Milesight") { $b = "Milesight" }
  elseif ($signal -match "Axis") { $b = "Axis" }
  elseif ($signal -match "Reolink") { $b = "Reolink" }
  return @{ brand = $b; server = $server; title = $title }
}

$ports = @(80, 443, 554, 8000, 8080, 8899)
$targets = Get-LocalSubnetIps
$out = @()
foreach ($ip in $targets) {
  $open = Probe-Ports $ip $ports
  if ($open.Count -gt 0) {
    $brand = Guess-Brand $ip
    $out += @{ ip = $ip; ports = $open; brand = $brand.brand; server = $brand.server; title = $brand.title }
  }
}

$ts = Get-Date -Format "yyyyMMddHHmmss"
$reportPath = Join-Path $Root ("logs/nvr_probe_" + $ts + ".json")
Ensure-Dir $reportPath
($out | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $reportPath -Encoding UTF8
Write-Log ("nvr_probe: targets=" + ($targets.Count) + "; detected=" + ($out.Count) + "; file=" + $reportPath)
Append-WorkLog "nvr_probe" "OK" ("targets=" + ($targets.Count) + "; detected=" + ($out.Count) + "; file=" + $reportPath)
Write-Output $reportPath
