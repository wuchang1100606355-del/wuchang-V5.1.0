Param(
  [string]$Action = "check",
  [string]$Root = (Get-Location).Path,
  [string]$RouterCredPath = "config\router_creds.json"
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
  $csv = Join-Path $Root "logs\work_log.csv"
  Ensure-Dir $csv
  if (-not (Test-Path $csv)) { Set-Content -LiteralPath $csv -Value "date,time,actor,task,result,details" -Encoding UTF8 }
  Add-Content -LiteralPath $csv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", $task, $result, $details)
}

function Load-RouterCred() {
  $path = Join-Path $Root $RouterCredPath
  if (Test-Path $path) {
    try { return (Get-Content -LiteralPath $path -Raw | ConvertFrom-Json) } catch { return @{} }
  }
  $secretDir = Join-Path $Root "backups\secrets"
  if (Test-Path $secretDir) {
    $xml = Get-ChildItem -Path $secretDir -Filter "router_*_creds.xml" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($xml) {
      try { $sec = Import-Clixml -Path $xml.FullName; return @{ host = $sec.host; user = $sec.user; pass = $sec.pass } } catch { }
    }
  }
  return @{}
}

function Get-DesiredDomains() {
  return @(
    "wuchang.life", "app.wuchang.life", "ai.wuchang.life", "llm.wuchang.life", "asr.wuchang.life", "tts.wuchang.life",
    "wuchang.global", "app.wuchang.global", "ai.wuchang.global", "llm.wuchang.global", "asr.wuchang.global", "tts.wuchang.global"
  )
}
function Check-HostsMapping($domains) {
  $hosts = Join-Path $env:SystemRoot "System32\drivers\etc\hosts"
  $existing = @()
  try { $existing = Get-Content -LiteralPath $hosts -ErrorAction SilentlyContinue } catch {}
  $ok = $true
  foreach ($d in $domains) {
    $line = "127.0.0.1 " + $d
    if (-not ($existing -match [Regex]::Escape($line))) { $ok = $false; break }
  }
  return @{ ok = $ok; hosts = $hosts }
}
function Backup-Hosts() {
  $hosts = Join-Path $env:SystemRoot "System32\drivers\etc\hosts"
  $ts = Get-Date -Format "yyyyMMddHHmmss"
  $dest = Join-Path $Root ("backups\hosts_" + $ts + ".txt")
  try { Copy-Item $hosts $dest -Force } catch {}
  return $dest
}
function Ensure-HostsMapping($domains) {
  $hosts = Join-Path $env:SystemRoot "System32\drivers\etc\hosts"
  $existing = @()
  try { $existing = Get-Content -LiteralPath $hosts -ErrorAction SilentlyContinue } catch {}
  $added = 0
  foreach ($d in $domains) {
    $line = "127.0.0.1 " + $d
    if (-not ($existing -match [Regex]::Escape($line))) { Add-Content -LiteralPath $hosts -Value $line; $added++ }
  }
  return $added
}
function Snapshot-DNSPlan($domains) {
  $ts = Get-Date -Format "yyyyMMddHHmmss"
  $out = Join-Path $Root ("logs\dns_plan_" + $ts + ".json")
  $plan = @{ ts = (Get-Date -Format "yyyy-MM-dd HH:mm:ss"); domains = $domains; target_ip = "X.X.X.X" }
  Ensure-Dir $out
  try { (ConvertTo-Json $plan -Depth 4) | Set-Content -LiteralPath $out -Encoding UTF8 } catch {}
  return $out
}
function Restart-Compose() {
  Push-Location $Root
  try { docker compose up -d | Out-Null } catch {}
  Pop-Location
}

switch ($Action.ToLower()) {
  "check" {
    $domains = Get-DesiredDomains
    $hostsOk = Check-HostsMapping $domains
    $router = Load-RouterCred
    $routerOk = (($router.host -as [string]) -and ($router.user -as [string]) -and ($router.pass -as [string]))
    $webName = "wuchangv500-wuchang-web-1"
    $svcOk = $false
    try {
      $line = (docker ps --format "{{.Names}}`t{{.Status}}" | Where-Object { $_ -like "$webName*" } | Select-Object -First 1)
      if ($line) { $parts = $line -split "`t"; if ($parts.Length -ge 2 -and ($parts[1] -like "Up*")) { $svcOk = $true } }
    }
    catch {}
    $status = if ($hostsOk.ok -and $svcOk) { "OK" } else { "WARN" }
    Append-WorkLog "dns_daily_check" $status ("hosts=" + ($hostsOk.ok) + "; router_creds=" + ($routerOk) + "; web_up=" + ($svcOk))
    if (-not $svcOk) { Restart-Compose }
    Write-Log ("dns_check: hosts_ok=" + $hostsOk.ok + ", router_creds=" + $routerOk + ", web_up=" + $svcOk)
    return
  }
  "plan" {
    $domains = Get-DesiredDomains
    $planFile = Snapshot-DNSPlan $domains
    Append-WorkLog "dns_plan" "READY" ("file=" + $planFile)
    Write-Log ("dns_plan_ready: " + $planFile)
    return
  }
  "apply" {
    $confirm1 = Join-Path $Root "config\dns_confirm.flag"
    $confirm2 = Join-Path $Root "config\dns_confirm_2.flag"
    $confirmed = (Test-Path $confirm1) -and (Test-Path $confirm2)
    if (-not $confirmed) {
      Append-WorkLog "dns_apply" "AWAIT_CONFIRM" ("flags_missing")
      Write-Log "dns_apply_blocked: missing double confirm flags"
      return
    }
    $domains = Get-DesiredDomains
    $bk = Backup-Hosts
    $added = Ensure-HostsMapping $domains
    Append-WorkLog "dns_apply" "OK" ("hosts_added=" + $added + "; backup=" + $bk)
    Write-Log ("dns_apply_done: hosts_added=" + $added + "; backup=" + $bk)
    try { Restart-Compose } catch {}
    $router = Load-RouterCred
    if (-not $router.host) {
      Append-WorkLog "router_apply" "SKIPPED" "missing_provider"
      Write-Log "router_apply_skipped: missing_provider"
    }
    return
  }
  "heal" {
    $domains = Get-DesiredDomains
    $hostsOk = Check-HostsMapping $domains
    $svcOk = $false
    try {
      $line = (docker ps --format "{{.Names}}`t{{.Status}}" | Where-Object { $_ -like "wuchangv500-wuchang-web-1*" } | Select-Object -First 1)
      if ($line) { $parts = $line -split "`t"; if ($parts.Length -ge 2 -and ($parts[1] -like "Up*")) { $svcOk = $true } }
    }
    catch {}
    if (-not ($hostsOk.ok) -or (-not $svcOk)) {
      $bk = Backup-Hosts
      $added = Ensure-HostsMapping $domains
      Append-WorkLog "dns_heal" "APPLIED" ("hosts_added=" + $added + "; backup=" + $bk + "; web_up=" + $svcOk)
      Write-Log ("dns_heal_applied: hosts_added=" + $added + "; backup=" + $bk + "; web_up=" + $svcOk)
      if (-not $svcOk) { Restart-Compose }
    }
    else {
      Append-WorkLog "dns_heal" "OK" "no_action"
      Write-Log "dns_heal_ok"
    }
    return
  }
  default { Append-WorkLog "dns_guard" "UNKNOWN_ACTION" $Action; Write-Log ("dns_unknown_action: " + $Action); return }
}
