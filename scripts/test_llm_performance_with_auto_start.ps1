# Wuchang OS 本地 LLM 性能測試腳本 (自動啟動版本)
# 如果 Ollama 未運行，會自動嘗試啟動

$ErrorActionPreference = "Continue"

Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "     Wuchang OS - 本地 LLM 模型性能測試 (自動啟動版)" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Ollama 是否運行
$ollamaUrl = "http://localhost:11434/api/tags"
$ollamaRunning = $false

Write-Host "檢查 Ollama 服務狀態..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri $ollamaUrl -Method GET -TimeoutSec 5 -ErrorAction Stop
    $ollamaRunning = $true
    Write-Host "  ✓ Ollama 服務正在運行" -ForegroundColor Green
    $models = $response.models | ForEach-Object { $_.name }
    Write-Host "  可用模型: $($models -join ', ')" -ForegroundColor White
} catch {
    Write-Host "  ⚠ Ollama 服務未運行" -ForegroundColor Yellow
    
    # 嘗試啟動 Ollama
    Write-Host ""
    Write-Host "嘗試啟動 Ollama 服務..." -ForegroundColor Yellow
    Write-Host "  執行: docker-compose --profile ui up -d" -ForegroundColor Gray
    
    $workspacePath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $composeFile = Join-Path $workspacePath "docker-compose.yml"
    
    if (-not (Test-Path $composeFile)) {
        Write-Host "  ✗ 找不到 docker-compose.yml 文件" -ForegroundColor Red
        Write-Host "  路徑: $composeFile" -ForegroundColor Gray
    } else {
        try {
            Push-Location $workspacePath
            docker-compose -f $composeFile --profile ui up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Docker Compose 命令執行成功" -ForegroundColor Green
            Write-Host "  等待服務啟動 (10秒)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
            
            # 再次檢查
            try {
                $response = Invoke-RestMethod -Uri $ollamaUrl -Method GET -TimeoutSec 5 -ErrorAction Stop
                $ollamaRunning = $true
                Write-Host "  ✓ Ollama 服務已啟動" -ForegroundColor Green
                $models = $response.models | ForEach-Object { $_.name }
                Write-Host "  可用模型: $($models -join ', ')" -ForegroundColor White
            } catch {
                Write-Host "  ⚠ Ollama 服務可能仍在啟動中" -ForegroundColor Yellow
                Write-Host "  提示：請稍後再運行測試，或手動檢查服務狀態" -ForegroundColor Yellow
            }
            } else {
                Write-Host "  ✗ Docker Compose 啟動失敗 (退出碼: $LASTEXITCODE)" -ForegroundColor Red
                Write-Host "  提示：請手動運行 'docker-compose --profile ui up -d'" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ✗ Docker Compose 配置文件不存在" -ForegroundColor Red
    } catch {
        Write-Host "  ✗ 無法啟動 Ollama 服務: $_" -ForegroundColor Red
        Write-Host "  提示：請手動運行 'docker-compose --profile ui up -d' 或 'scripts/auto_install_ai.ps1'" -ForegroundColor Yellow
    } finally {
        Pop-Location
    }
}

Write-Host ""

if (-not $ollamaRunning) {
    Write-Host "❌ 無法繼續測試：Ollama 服務不可用" -ForegroundColor Red
    Write-Host ""
    Write-Host "請執行以下步驟：" -ForegroundColor Yellow
    Write-Host "  1. 運行: docker-compose --profile ui up -d" -ForegroundColor White
    Write-Host "  2. 或運行: scripts/auto_install_ai.ps1" -ForegroundColor White
    Write-Host "  3. 等待服務啟動後，再次運行此腳本" -ForegroundColor White
    exit 1
}

# 運行 Python 測試腳本
Write-Host "開始運行性能測試..." -ForegroundColor Cyan
Write-Host ""

$pythonScript = Join-Path $PSScriptRoot "test_local_llm_performance.py"

if (-not (Test-Path $pythonScript)) {
    Write-Host "❌ 找不到測試腳本: $pythonScript" -ForegroundColor Red
    exit 1
}

try {
    python $pythonScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ 測試完成" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠ 測試過程中有問題 (退出碼: $LASTEXITCODE)" -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "❌ 運行測試腳本時發生錯誤: $_" -ForegroundColor Red
    exit 1
}

exit 0