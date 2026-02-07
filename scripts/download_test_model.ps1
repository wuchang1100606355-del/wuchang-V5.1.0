# 下載測試用的 Ollama 模型
param(
    [string]$Model = "qwen2:0.5b"
)

Write-Host "下載 Ollama 模型: $Model" -ForegroundColor Cyan
Write-Host ""

try {
    $body = @{ name = $Model } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/pull" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 600
    
    Write-Host "✓ 模型下載完成: $Model" -ForegroundColor Green
} catch {
    Write-Host "✗ 模型下載失敗: $_" -ForegroundColor Red
    exit 1
}