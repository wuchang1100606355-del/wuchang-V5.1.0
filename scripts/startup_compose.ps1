Param(
  [ValidateSet('system','ui','named','all')][string]$Profile = 'all'
)
$root = (Get-Location).Path

function Start-DockerDesktopIfAvailable {
  $dd = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  if (Test-Path $dd) {
    try { Start-Process -FilePath $dd -ErrorAction SilentlyContinue } catch {}
  }
}

function Wait-DockerReady {
  $maxTries = 60
  for ($i = 0; $i -lt $maxTries; $i++) {
    try {
      docker info | Out-Null
      return $true
    }
    catch {
      Start-DockerDesktopIfAvailable
      Start-Sleep -Seconds 3
    }
  }
  return $false
}

$ready = Wait-DockerReady
Push-Location $root
try {
  switch ($Profile) {
    'system' { docker-compose --profile system up -d | Out-Null }
    'ui'     { docker-compose --profile ui up -d | Out-Null }
    'named'  { docker-compose --profile named up -d cloudflared-named | Out-Null }
    default  { docker-compose up -d | Out-Null }
  }
} catch {}
Pop-Location
