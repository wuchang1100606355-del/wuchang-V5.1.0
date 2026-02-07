Param(
  [string]$Root = (Get-Location).Path
)
$ErrorActionPreference = "Stop"

function Ensure-Dir($p) {
  $dir = Split-Path -Parent $p
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}

function Write-Log($msg) {
  $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] " + $msg
  Add-Content -Path (Join-Path $Root "automation.log") -Value $line
}

try {
  docker compose exec wuchang-web sh -lc "odoo shell -d odoo < /opt/wuchang/scripts/odoo_read_architecture.py" | Out-Null
} catch {
  Write-Log ("architecture_read: odoo_shell_failed " + $_.Exception.Message)
}

try {
  $json = docker compose exec wuchang-web sh -lc "cat /tmp/arch.json"
} catch {
  $json = "{}"
}

$ts = Get-Date -Format "yyyyMMddHH"
$outPath = Join-Path $Root ("logs/architecture/" + $ts + ".json")
Ensure-Dir $outPath
Set-Content -LiteralPath $outPath -Value $json -Encoding UTF8

try {
  $obj = $json | ConvertFrom-Json
  $ok = [bool]$obj.ok
  $featured = "" + $obj.snapshot.featured_store
  $stores = @($obj.snapshot.pos_configs).Count
  $msg = "architecture_read: ok=" + $ok + ", stores=" + $stores + ", featured='" + $featured + "'"
  Write-Log $msg
  $workLogCsv = Join-Path $Root "logs/work_log.csv"
  Ensure-Dir $workLogCsv
  if (-not (Test-Path $workLogCsv)) { Set-Content -LiteralPath $workLogCsv -Value "date,time,actor,task,result,details" -Encoding UTF8 }
  $result = if ($ok) { "OK" } else { "FAILED" }
  $details = "stores=" + $stores + "; featured='" + $featured + "'"
  Add-Content -LiteralPath $workLogCsv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", "architecture_read", $result, $details)
} catch {
  Write-Log ("architecture_read: parse_failed " + $_.Exception.Message)
}

Write-Output $outPath
