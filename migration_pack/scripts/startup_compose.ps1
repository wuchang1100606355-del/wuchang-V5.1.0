Param()
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
try { docker-compose up -d | Out-Null } catch {}
Pop-Location
