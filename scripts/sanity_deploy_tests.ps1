Param(
  [string]$BaseUrl = "http://localhost",
  [string]$Db = "admin",
  [string]$Login = "admin",
  [string]$Password = "admin"
)

function CallJsonPost($path, $payload) {
  try {
    $url = "$BaseUrl$path"
    $json = $payload | ConvertTo-Json -Depth 5
    return Invoke-RestMethod -Uri $url -Method POST -Body $json -ContentType 'application/json' -TimeoutSec 20
  } catch {
    Write-Host "[Test] POST $path failed: $($_.Exception.Message)" -ForegroundColor Red
    return $null
  }
}

function DetectDb() {
  try {
    $resp = Invoke-WebRequest -Uri ("$BaseUrl/supreme/dbs") -Method GET -TimeoutSec 10
    $data = $resp.Content | ConvertFrom-Json
    $names = @($data.databases)
    if ($names -and $names.Count -gt 0) { return $names[0] }
  } catch {}
  return $Db
}

function LoginSession($db, $login, $password) {
  try {
    $useDb = if ($db) { $db } else { DetectDb }
    # Bootstrap a dev session with superuser via /supreme/open_all (auth=none)
    $openUrl = "$BaseUrl/supreme/open_all?db=$useDb"
    Invoke-WebRequest -Uri $openUrl -Method GET -SessionVariable WebSession -TimeoutSec 10 | Out-Null
    # Read current session info to obtain session_id
    $get = Invoke-RestMethod -Uri "$BaseUrl/web/session/get" -Method POST -Body '{}' -ContentType 'application/json' -WebSession $WebSession -TimeoutSec 10
    $sid = $get.result.session_id
    # If no sid yet, try normal authentication to bind session to a real user if provided
    if (-not $sid -and $login -and $password) {
      $body = @{ db = $useDb; login = $login; password = $password } | ConvertTo-Json -Depth 3
      $resp = Invoke-WebRequest -Uri "$BaseUrl/web/session/authenticate" -Method POST -Body $body -ContentType 'application/json' -WebSession $WebSession -TimeoutSec 20
      $data = $resp.Content | ConvertFrom-Json
      $sid = $data.result.session_id
    }
    if ($sid) {
      try {
        # Ensure cookie is present in the session for subsequent calls
        $cookie = New-Object System.Net.Cookie
        $cookie.Name = 'session_id'
        $cookie.Value = $sid
        $cookie.Path = '/'
        # Domain: prefer Host header if provided via BaseUrl; fallback to 'localhost'
        $uri = [Uri]$BaseUrl
        $cookie.Domain = if ($uri.Host) { $uri.Host } else { 'localhost' }
        $WebSession.Cookies.Add($cookie)
        # Promote to global scope for CallJsonPostAuth
        Set-Variable -Name WebSession -Scope Global -Value $WebSession -ErrorAction SilentlyContinue
      } catch {}
    }
    return $sid
  } catch {
    Write-Host "[Auth] Login failed: $($_.Exception.Message)" -ForegroundColor Yellow
    return $null
  }
}

function CallJsonPostAuth($path, $payload, $sid) {
  if ($sid) {
    try {
      $url = "$BaseUrl$path"
      $json = $payload | ConvertTo-Json -Depth 5
      # Prefer WebSession cookies captured via authentication
      if ($Global:WebSession) {
        $resp = Invoke-WebRequest -Uri $url -Method POST -Body $json -ContentType 'application/json' -WebSession $Global:WebSession -TimeoutSec 20
        return ($resp.Content | ConvertFrom-Json)
      } else {
        $resp = Invoke-WebRequest -Uri $url -Method POST -Body $json -ContentType 'application/json' -TimeoutSec 20
        return ($resp.Content | ConvertFrom-Json)
      }
    } catch {
      Write-Host "[Test] POST $path (auth) failed: $($_.Exception.Message)" -ForegroundColor Red
      return $null
    }
  } else {
    return CallJsonPost $path $payload
  }
}

Write-Host "[Auth] Trying to authenticate" -ForegroundColor Cyan
$sid = LoginSession $Db $Login $Password
if ($sid) { Write-Host ("[Auth] Session: " + $sid) -ForegroundColor Green } else { Write-Host "[Auth] No session; will call public endpoints or expect 401/SessionExpired" -ForegroundColor Yellow }
try {
  $sess = Invoke-RestMethod -Uri "$BaseUrl/web/session/get" -Method POST -Body '{}' -ContentType 'application/json' -WebSession $Global:WebSession -TimeoutSec 10
  Write-Host ($sess | ConvertTo-Json -Depth 5)
} catch {}

Write-Host "[Test] Dependency Diagnosis" -ForegroundColor Cyan
$diag = CallJsonPostAuth "/api/deploy/diag" @{} $sid
Write-Host ($diag | ConvertTo-Json -Depth 5)

Write-Host "[Test] Performance Status" -ForegroundColor Cyan
$perf = CallJsonPostAuth "/api/perf/status" @{} $sid
Write-Host ($perf | ConvertTo-Json -Depth 5)

Write-Host "[Test] Performance Allocate" -ForegroundColor Cyan
$alloc = CallJsonPostAuth "/api/perf/allocate" @{} $sid
Write-Host ($alloc | ConvertTo-Json -Depth 5)

Write-Host "[Test] IDE Tools" -ForegroundColor Cyan
$ide = CallJsonPostAuth "/api/ide/tools" @{} $sid
Write-Host ($ide | ConvertTo-Json -Depth 5)

Write-Host "[Test] AI Resources" -ForegroundColor Cyan
try {
  $res = Invoke-RestMethod -Uri "$BaseUrl/api/ai/resources" -Method POST -Body '{}' -ContentType 'application/json' -TimeoutSec 20
  Write-Host ($res | ConvertTo-Json -Depth 5)
} catch {
  Write-Host "[Test] AI Resources failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "[Test] UI Total AI Spec" -ForegroundColor Cyan
$spec = CallJsonPostAuth "/api/ui_ai/spec" @{} $sid
Write-Host ($spec | ConvertTo-Json -Depth 5)

Write-Host "[Test] UI Total AI Modules" -ForegroundColor Cyan
$mods = CallJsonPostAuth "/api/ui_ai/modules" @{} $sid
Write-Host ($mods | ConvertTo-Json -Depth 5)

Write-Host "[Test] UI Total AI Config Sync" -ForegroundColor Cyan
$cfg = @{ defaultRole = "advisor"; allowExternal = $true }
$cfgRes = CallJsonPostAuth "/api/ui_ai/config/sync" @{ config = $cfg } $sid
Write-Host ($cfgRes | ConvertTo-Json -Depth 5)

Write-Host "[Test] Odoo Advisor Consult" -ForegroundColor Cyan
$q = "請用三點說明Odoo顧問功能整合"
$ctx = @{ system = "UI總AI"; module = "odoo_advisor" }
$ans = CallJsonPostAuth "/api/ui_ai/odoo/consult" @{ question = $q; context = $ctx } $sid
Write-Host ($ans | ConvertTo-Json -Depth 5)

Write-Host "[Test] Data Migrate" -ForegroundColor Cyan
$his = @(@{ type = "note"; text = "migrated" })
$mig = CallJsonPostAuth "/api/ui_ai/data/migrate" @{ config = $cfg; history = $his } $sid
Write-Host ($mig | ConvertTo-Json -Depth 5)

Write-Host "[Test] Odoo Export (ir.attachment name,mimetype)" -ForegroundColor Cyan
$exp = CallJsonPostAuth "/api/ui_ai/odoo/export" @{ model = "ir.attachment"; fields = @("name","mimetype"); limit = 5 } $sid
Write-Host ($exp | ConvertTo-Json -Depth 5)

Write-Host "[Test] Data Map (name+type -> title)" -ForegroundColor Cyan
$items = @(
  @{ name = "A"; type = "doc" },
  @{ name = "B"; type = "img" }
)
$mapping = @{ title = @{ join = @("name","type"); sep = "-" } }
$mapped = CallJsonPostAuth "/api/ui_ai/data/map" @{ items = $items; mapping = $mapping } $sid
Write-Host ($mapped | ConvertTo-Json -Depth 5)

Write-Host "[Test] Secrets Status" -ForegroundColor Cyan
$sec = CallJsonPostAuth "/api/secrets/status" @{} $sid
Write-Host ($sec | ConvertTo-Json -Depth 5)

Write-Host "[Test] Set Google Key (masked)" -ForegroundColor Cyan
$setg = CallJsonPostAuth "/api/secrets/set_google" @{ key = "DUMMY-KEY-FOR-TEST" } $sid
Write-Host ($setg | ConvertTo-Json -Depth 5)

Write-Host "[Test] GCP VM Exists (needs valid token)" -ForegroundColor Cyan
$vm = CallJsonPostAuth "/api/gcp/vm/exists" @{ project_id = "your-project"; name = "your-vm"; zone = "your-zone"; access_token = "YOUR_OAUTH_TOKEN" } $sid
Write-Host ($vm | ConvertTo-Json -Depth 5)

Write-Host "[Test] Router RT-86U Probe" -ForegroundColor Cyan
$rt = CallJsonPostAuth "/api/router/rt86u/probe" @{ address = "192.168.50.1" } $sid
Write-Host ($rt | ConvertTo-Json -Depth 5)

Write-Host "[Test] SSH Probe (22/tcp)" -ForegroundColor Cyan
$ssh = CallJsonPostAuth "/api/ssh/probe" @{ host = "192.168.50.1"; port = 22 } $sid
Write-Host ($ssh | ConvertTo-Json -Depth 5)

Write-Host "[Test] Done" -ForegroundColor Green
