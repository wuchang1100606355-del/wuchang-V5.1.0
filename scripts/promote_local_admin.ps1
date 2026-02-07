Param(
  [string]$User = "xiao-j",
  [string]$Root = (Get-Location).Path
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
function Append-WorkLog($task,$result,$details) {
  $csv = Join-Path $Root "logs\work_log.csv"
  Ensure-Dir $csv
  if (-not (Test-Path $csv)) { Set-Content -LiteralPath $csv -Value "date,time,actor,task,result,details" -Encoding UTF8 }
  Add-Content -LiteralPath $csv -Value ("{0},{1},{2},{3},{4},{5}" -f (Get-Date -Format "yyyy-MM-dd"), (Get-Date -Format "HH:mm:ss"), "xiao-j", $task, $result, $details)
}

try {
  $lu = Get-LocalUser -Name $User -ErrorAction SilentlyContinue
  if (-not $lu) {
    Append-WorkLog "local_admin_promote" "USER_NOT_FOUND" ("user=" + $User)
    Write-Output ("user_missing: " + $User)
    exit 1
  }
} catch {
  # On systems where Get-LocalUser is unavailable
}

try {
  Add-LocalGroupMember -Group "Administrators" -Member $User -ErrorAction Stop
  Append-WorkLog "local_admin_promote" "OK" ("user=" + $User)
  Write-Log ("local_admin_promote: user=" + $User + " OK")
  Write-Output ("promoted: " + $User)
} catch {
  Append-WorkLog "local_admin_promote" "FAILED" ("user=" + $User + "; error=" + $_.Exception.Message)
  Write-Log ("local_admin_promote_failed: user=" + $User + " error=" + $_.Exception.Message)
  Write-Output ("failed: " + $_.Exception.Message)
  exit 1
}

