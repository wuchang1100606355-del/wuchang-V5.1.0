Param(
  [string]$User = "xiao-j",
  [string]$FullName = "小J",
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

$existing = Get-LocalUser -Name $User -ErrorAction SilentlyContinue
if ($existing) {
  try {
    Add-LocalGroupMember -Group "Administrators" -Member $User -ErrorAction Stop
    Append-WorkLog "local_admin_create_or_promote" "OK" ("user=" + $User + "; action=promote")
    Write-Log ("local_admin_promote: user=" + $User + " OK")
    Write-Output ("promoted_existing: " + $User)
    exit 0
  } catch {
    Append-WorkLog "local_admin_create_or_promote" "FAILED" ("user=" + $User + "; action=promote; error=" + $_.Exception.Message)
    Write-Output ("failed: " + $_.Exception.Message)
    exit 1
  }
}

# Generate random secure password (not printed)
$rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
$b = New-Object byte[] (24)
$rng.GetBytes($b)
$plain = [Convert]::ToBase64String($b) + "!Ab1"
$secure = ConvertTo-SecureString -String $plain -AsPlainText -Force

try {
  New-LocalUser -Name $User -Password $secure -FullName $FullName -Description "Delegated local admin for operations" -AccountNeverExpires:$true -ErrorAction Stop
  Add-LocalGroupMember -Group "Administrators" -Member $User -ErrorAction Stop
  $secretDir = Join-Path $Root "backups\secrets"
  New-Item -ItemType Directory -Force -Path $secretDir | Out-Null
  $secretPath = Join-Path $secretDir ("local_user_" + $User + "_pwd.xml")
  $secure | Export-Clixml -Path $secretPath
  Append-WorkLog "local_admin_create_or_promote" "OK" ("user=" + $User + "; action=create+promote; secret=" + $secretPath)
  Write-Log ("local_admin_create: user=" + $User + " OK")
  Write-Output ("created_and_promoted: " + $User)
  exit 0
} catch {
  Append-WorkLog "local_admin_create_or_promote" "FAILED" ("user=" + $User + "; action=create; error=" + $_.Exception.Message)
  Write-Log ("local_admin_create_failed: user=" + $User + " error=" + $_.Exception.Message)
  Write-Output ("failed: " + $_.Exception.Message)
  exit 1
}
