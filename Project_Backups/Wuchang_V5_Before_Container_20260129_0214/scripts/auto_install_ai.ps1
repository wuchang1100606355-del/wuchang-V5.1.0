Param(
  [string]$ComposeFile = "docker-compose.yml",
  [string]$Profile = "ui",
  [string]$OllamaHost = "http://localhost:11434",
  [string]$Model = "llama3.1"
)

Write-Host "[AutoInstallAI] Starting services with profile '$Profile'" -ForegroundColor Cyan
try {
  docker compose -f $ComposeFile --profile $Profile up -d
} catch {
  Write-Host "[AutoInstallAI] Failed to start compose: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 3

Write-Host "[AutoInstallAI] Probing Ollama at $OllamaHost" -ForegroundColor Cyan
try {
  $tags = Invoke-RestMethod -Uri "$OllamaHost/api/tags" -Method GET -TimeoutSec 10
  $hasModel = ($tags.models | Where-Object { $_.name -eq $Model }) -ne $null
  if (-not $hasModel) {
    Write-Host "[AutoInstallAI] Pulling model '$Model'" -ForegroundColor Yellow
    $body = @{ name = $Model } | ConvertTo-Json
    Invoke-RestMethod -Uri "$OllamaHost/api/pull" -Method POST -Body $body -ContentType 'application/json' -TimeoutSec 300 | Out-Null
  } else {
    Write-Host "[AutoInstallAI] Model '$Model' already present" -ForegroundColor Green
  }
} catch {
  Write-Host "[AutoInstallAI] Ollama check/pull failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "[AutoInstallAI] Done" -ForegroundColor Green
