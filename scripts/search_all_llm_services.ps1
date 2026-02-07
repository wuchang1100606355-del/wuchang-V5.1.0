# 全容器 LLM 服務搜索腳本
# 搜索所有可能運行的 LLM 服務

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  全容器 LLM 服務搜索" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

$foundServices = @()

# 1. 檢查所有運行中的容器
Write-Host "[1] 檢查運行中的容器..." -ForegroundColor Yellow
$runningContainers = docker ps --format "{{json .}}"
$containers = $runningContainers | ConvertFrom-Json

foreach ($container in $containers) {
    $name = $container.Names
    $image = $container.Image
    $ports = $container.Ports
    
    # 檢查是否為 LLM 相關服務
    $llmKeywords = @("ollama", "llm", "model", "ai", "gemini", "openai", "anthropic", "claude", "webui", "open-webui", "lmstudio", "vllm", "text-generation", "transformers", "huggingface")
    
    foreach ($keyword in $llmKeywords) {
        if ($name -match $keyword -or $image -match $keyword) {
            $foundServices += [PSCustomObject]@{
                Type = "容器"
                Name = $name
                Image = $image
                Ports = $ports
                Status = "運行中"
            }
            Write-Host "  ✓ 發現 LLM 服務: $name ($image)" -ForegroundColor Green
            break
        }
    }
}

Write-Host ""

# 2. 檢查所有容器（包括停止的）
Write-Host "[2] 檢查所有容器（包括停止的）..." -ForegroundColor Yellow
$allContainers = docker ps -a --format "{{json .}}"
$allContainersList = $allContainers | ConvertFrom-Json

$stoppedLLM = @()
foreach ($container in $allContainersList) {
    $name = $container.Names
    $image = $container.Image
    $status = $container.Status
    
    $llmKeywords = @("ollama", "llm", "model", "ai", "gemini", "openai", "anthropic", "claude", "webui", "open-webui", "lmstudio", "vllm", "text-generation", "transformers")
    
    foreach ($keyword in $llmKeywords) {
        if ($name -match $keyword -or $image -match $keyword) {
            if ($status -notmatch "Up") {
                $stoppedLLM += [PSCustomObject]@{
                    Name = $name
                    Image = $image
                    Status = $status
                }
                Write-Host "  ⚠ 發現停止的 LLM 服務: $name ($status)" -ForegroundColor Yellow
            }
            break
        }
    }
}

Write-Host ""

# 3. 檢查常見 LLM 服務端口
Write-Host "[3] 檢查常見 LLM 服務端口..." -ForegroundColor Yellow
$commonPorts = @{
    11434 = "Ollama"
    8080 = "Open WebUI"
    7860 = "Gradio"
    5000 = "Flask/FastAPI"
    8000 = "通用 API"
    3000 = "Node.js"
    5001 = "LM Studio"
    8081 = "備用 Web UI"
}

foreach ($port in $commonPorts.Keys) {
    try {
        $result = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        if ($result.TcpTestSucceeded) {
            $serviceName = $commonPorts[$port]
            Write-Host "  ✓ 端口 $port 正在監聽 ($serviceName)" -ForegroundColor Green
            
            # 嘗試獲取服務信息
            try {
                if ($port -eq 11434) {
                    $response = Invoke-RestMethod -Uri "http://localhost:$port/api/tags" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
                    $modelCount = ($response.models | Measure-Object).Count
                    Write-Host "     → Ollama 可用，模型數量: $modelCount" -ForegroundColor Cyan
                } elseif ($port -eq 8080) {
                    $response = Invoke-WebRequest -Uri "http://localhost:$port" -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
                    if ($response.StatusCode -eq 200) {
                        Write-Host "     → Web UI 服務可用" -ForegroundColor Cyan
                    }
                }
            } catch {
                # 忽略錯誤
            }
        }
    } catch {
        # 端口未監聽
    }
}

Write-Host ""

# 4. 檢查 Docker Compose 配置文件
Write-Host "[4] 檢查 Docker Compose 配置文件..." -ForegroundColor Yellow
$composeFiles = @(
    "docker-compose.yml",
    "docker-compose-ai.yml",
    "migration_pack\docker-compose.yml"
)

foreach ($file in $composeFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -ErrorAction SilentlyContinue
        if ($content) {
            $llmServices = @()
            if ($content -match "ollama:") { $llmServices += "Ollama" }
            if ($content -match "open-webui:") { $llmServices += "Open WebUI" }
            if ($content -match "lmstudio:") { $llmServices += "LM Studio" }
            if ($content -match "vllm:") { $llmServices += "vLLM" }
            
            if ($llmServices.Count -gt 0) {
                Write-Host "  ✓ $file 包含: $($llmServices -join ', ')" -ForegroundColor Green
            }
        }
    }
}

Write-Host ""

# 5. 檢查 Odoo 內部的 AI 服務
Write-Host "[5] 檢查 Odoo 內部的 AI 配置..." -ForegroundColor Yellow
$odooContainer = docker ps --format "{{.Names}}" | Select-String "wuchang-web|odoo"
if ($odooContainer) {
    $odooName = $odooContainer.ToString().Trim()
    Write-Host "  Odoo 容器: $odooName" -ForegroundColor White
    
    try {
        # 檢查環境變量
        $envVars = docker exec $odooName env 2>&1 | Select-String -Pattern "(AI|LLM|OLLAMA|GEMINI|GOOGLE)" -ErrorAction SilentlyContinue
        if ($envVars) {
            Write-Host "    發現 AI 相關環境變量:" -ForegroundColor Cyan
            $envVars | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
        }
    } catch {
        Write-Host "    無法檢查環境變量" -ForegroundColor Yellow
    }
}

Write-Host ""

# 總結
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  搜索結果總結" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

if ($foundServices.Count -gt 0) {
    Write-Host "發現 $($foundServices.Count) 個運行中的 LLM 服務:" -ForegroundColor Green
    $foundServices | ForEach-Object {
        Write-Host "  - $($_.Name) ($($_.Image))" -ForegroundColor White
    }
} else {
    Write-Host "⚠ 未發現運行中的 LLM 服務" -ForegroundColor Yellow
}

if ($stoppedLLM.Count -gt 0) {
    Write-Host ""
    Write-Host "發現 $($stoppedLLM.Count) 個停止的 LLM 服務:" -ForegroundColor Yellow
    $stoppedLLM | ForEach-Object {
        Write-Host "  - $($_.Name) ($($_.Status))" -ForegroundColor Gray
        Write-Host "    可以啟動: docker start $($_.Name)" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan