# 修復 Ollama 服務啟動問題
# 選項：
#   1. 啟用 docker-compose.yml 中的 Ollama
#   2. 使用 docker-compose-ai.yml 啟動 Ollama
#   3. 顯示診斷信息

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("enable", "use-ai-file", "diagnose")]
    [string]$Action = "enable"
)

$ErrorActionPreference = "Continue"

Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "  Ollama 服務修復工具" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host ""

$workspacePath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$composeFile = Join-Path $workspacePath "docker-compose.yml"
$aiComposeFile = Join-Path $workspacePath "docker-compose-ai.yml"

switch ($Action) {
    "enable" {
        Write-Host "選項 1: 啟用 docker-compose.yml 中的 Ollama 服務" -ForegroundColor Yellow
        Write-Host ""
        
        if (-not (Test-Path $composeFile)) {
            Write-Host "❌ 找不到 docker-compose.yml" -ForegroundColor Red
            exit 1
        }
        
        # 讀取文件
        $content = Get-Content $composeFile -Raw
        
        # 檢查是否已啟用
        if ($content -match "(?m)^\s+ollama:") {
            Write-Host "✓ Ollama 服務已啟用" -ForegroundColor Green
            Write-Host "  運行: docker-compose --profile ui up -d ollama" -ForegroundColor White
        } elseif ($content -match "(?m)^\s+#\s+ollama:") {
            Write-Host "⚠ 發現 Ollama 服務被註釋" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "需要取消註釋以下行（第 115-123 行）:" -ForegroundColor White
            Write-Host "  # ollama:" -ForegroundColor Gray
            Write-Host "  #   image: ollama/ollama:latest" -ForegroundColor Gray
            Write-Host "  #   ports:" -ForegroundColor Gray
            Write-Host "  #     - \"11434:11434\"" -ForegroundColor Gray
            Write-Host "  #   volumes:" -ForegroundColor Gray
            Write-Host "  #     - \${AI_MEMORY_PATH:-/mnt/ai-memory}/ollama:/root/.ollama" -ForegroundColor Gray
            Write-Host "  #   restart: unless-stopped" -ForegroundColor Gray
            Write-Host "  #   profiles:" -ForegroundColor Gray
            Write-Host "  #     - ui" -ForegroundColor Gray
            Write-Host ""
            
            $choice = Read-Host "是否要自動取消註釋並啟用？(Y/N)"
            if ($choice -eq "Y" -or $choice -eq "y") {
                # 取消註釋 - 使用更簡單的方法
                # 找到 Ollama 服務配置塊並取消註釋
                $lines = Get-Content $composeFile
                $inOllamaBlock = $false
                $newLines = @()
                
                foreach ($line in $lines) {
                    if ($line -match '^\s*#\s*ollama:') {
                        $inOllamaBlock = $true
                        # 取消註釋 ollama:
                        $newLines += $line -replace '^\s*#\s*(ollama:)', '  $1'
                    } elseif ($inOllamaBlock -and $line -match '^\s*#\s+(image|ports|volumes|restart|profiles):') {
                        # 取消註釋主要配置項
                        $newLines += $line -replace '^\s*#\s+', '    '
                    } elseif ($inOllamaBlock -and $line -match '^\s*#\s+-') {
                        # 取消註釋列表項
                        $newLines += $line -replace '^\s*#\s+', '      '
                    } elseif ($inOllamaBlock -and $line -match '^\s*#\s+$') {
                        # 空註釋行，跳過或保留
                        $newLines += $line
                    } elseif ($inOllamaBlock -and -not ($line -match '^\s*#')) {
                        # 遇到非註釋行，結束 Ollama 塊
                        $inOllamaBlock = $false
                        $newLines += $line
                    } elseif ($line -match '^\s*# AI Services moved to AI VM') {
                        # 移除這行註釋
                        continue
                    } else {
                        $newLines += $line
                    }
                }
                
                $newContent = $newLines -join "`n"
                
                # 同時移除 "AI Services moved to AI VM" 註釋
                $newContent = $newContent -replace "(?m)^\s+# AI Services moved to AI VM\s*$", ""
                
                # 備份原文件
                $backupFile = "$composeFile.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                Copy-Item $composeFile $backupFile
                Write-Host "✓ 已備份原文件到: $backupFile" -ForegroundColor Green
                
                # 寫入新內容
                Set-Content -Path $composeFile -Value $newContent -Encoding UTF8
                Write-Host "✓ 已啟用 Ollama 服務配置" -ForegroundColor Green
                
                # 啟動服務
                Write-Host ""
                Write-Host "正在啟動 Ollama 服務..." -ForegroundColor Yellow
                Push-Location $workspacePath
                try {
                    docker-compose --profile ui up -d ollama
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "✓ Ollama 服務已啟動" -ForegroundColor Green
                        Write-Host "  等待 10 秒讓服務完全啟動..." -ForegroundColor Yellow
                        Start-Sleep -Seconds 10
                        
                        # 驗證服務
                        try {
                            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5
                            Write-Host "✓ Ollama 服務驗證成功" -ForegroundColor Green
                        } catch {
                            Write-Host "⚠ Ollama 服務可能仍在啟動中" -ForegroundColor Yellow
                        }
                    }
                } catch {
                    Write-Host "✗ 啟動 Ollama 服務失敗: $_" -ForegroundColor Red
                } finally {
                    Pop-Location
                }
            } else {
                Write-Host "已取消操作" -ForegroundColor Yellow
            }
        } else {
            Write-Host "⚠ 未找到 Ollama 服務配置" -ForegroundColor Yellow
        }
    }
    
    "use-ai-file" {
        Write-Host "選項 2: 使用 docker-compose-ai.yml 啟動 Ollama" -ForegroundColor Yellow
        Write-Host ""
        
        if (-not (Test-Path $aiComposeFile)) {
            Write-Host "❌ 找不到 docker-compose-ai.yml" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✓ 找到 docker-compose-ai.yml" -ForegroundColor Green
        Write-Host ""
        Write-Host "正在啟動 AI 服務（Ollama + Open WebUI）..." -ForegroundColor Yellow
        
        Push-Location $workspacePath
        try {
            docker-compose -f $aiComposeFile up -d
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ AI 服務已啟動" -ForegroundColor Green
                Write-Host "  等待 15 秒讓服務完全啟動..." -ForegroundColor Yellow
                Start-Sleep -Seconds 15
                
                # 驗證服務
                Write-Host ""
                Write-Host "驗證服務狀態..." -ForegroundColor Yellow
                
                try {
                    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5 -ErrorAction Stop
                    Write-Host "  ✓ Ollama: 運行中 (http://localhost:11434)" -ForegroundColor Green
                    $models = $ollamaResponse.models | ForEach-Object { $_.name }
                    if ($models) {
                        Write-Host "    可用模型: $($models -join ', ')" -ForegroundColor White
                    }
                } catch {
                    Write-Host "  ⚠ Ollama: 可能仍在啟動中" -ForegroundColor Yellow
                }
                
                try {
                    $webuiResponse = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 5 -ErrorAction Stop
                    if ($webuiResponse.StatusCode -eq 200) {
                        Write-Host "  ✓ Open WebUI: 運行中 (http://localhost:8080)" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "  ⚠ Open WebUI: 可能仍在啟動中" -ForegroundColor Yellow
                }
            } else {
                Write-Host "✗ 啟動 AI 服務失敗 (退出碼: $LASTEXITCODE)" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ 啟動 AI 服務時發生錯誤: $_" -ForegroundColor Red
        } finally {
            Pop-Location
        }
    }
    
    "diagnose" {
        Write-Host "診斷 Ollama 服務狀態..." -ForegroundColor Yellow
        Write-Host ""
        
        # 檢查容器
        Write-Host "[1] 檢查 Docker 容器..." -ForegroundColor Cyan
        $containers = docker ps -a --format "{{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "ollama"
        if ($containers) {
            Write-Host "  找到 Ollama 相關容器:" -ForegroundColor White
            $containers | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
        } else {
            Write-Host "  ✗ 未找到 Ollama 容器" -ForegroundColor Red
        }
        Write-Host ""
        
        # 檢查端口
        Write-Host "[2] 檢查端口 11434..." -ForegroundColor Cyan
        try {
            $connection = Test-NetConnection -ComputerName localhost -Port 11434 -WarningAction SilentlyContinue
            if ($connection.TcpTestSucceeded) {
                Write-Host "  ✓ 端口 11434 正在監聽" -ForegroundColor Green
            } else {
                Write-Host "  ✗ 端口 11434 未監聽" -ForegroundColor Red
            }
        } catch {
            Write-Host "  ✗ 無法檢查端口 11434" -ForegroundColor Red
        }
        Write-Host ""
        
        # 檢查服務
        Write-Host "[3] 檢查 Ollama API..." -ForegroundColor Cyan
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5 -ErrorAction Stop
            Write-Host "  ✓ Ollama API 可用" -ForegroundColor Green
            $models = $response.models | ForEach-Object { $_.name }
            Write-Host "    可用模型: $($models -join ', ')" -ForegroundColor White
        } catch {
            Write-Host "  ✗ Ollama API 不可用: $($_.Exception.Message)" -ForegroundColor Red
        }
        Write-Host ""
        
        # 檢查配置文件
        Write-Host "[4] 檢查配置文件..." -ForegroundColor Cyan
        if (Test-Path $composeFile) {
            $content = Get-Content $composeFile -Raw
            if ($content -match "(?m)^\s+ollama:") {
                Write-Host "  ✓ docker-compose.yml: Ollama 已啟用" -ForegroundColor Green
            } elseif ($content -match "(?m)^\s+#\s+ollama:") {
                Write-Host "  ⚠ docker-compose.yml: Ollama 被註釋" -ForegroundColor Yellow
            } else {
                Write-Host "  ✗ docker-compose.yml: 未找到 Ollama 配置" -ForegroundColor Red
            }
        } else {
            Write-Host "  ✗ docker-compose.yml: 文件不存在" -ForegroundColor Red
        }
        
        if (Test-Path $aiComposeFile) {
            Write-Host "  ✓ docker-compose-ai.yml: 文件存在" -ForegroundColor Green
        } else {
            Write-Host "  ✗ docker-compose-ai.yml: 文件不存在" -ForegroundColor Red
        }
        Write-Host ""
        
        # 建議
        Write-Host "[5] 建議..." -ForegroundColor Cyan
        Write-Host "  - 如果要啟用本地 Ollama:" -ForegroundColor White
        Write-Host "    .\scripts\fix_ollama_service.ps1 -Action enable" -ForegroundColor Gray
        Write-Host "  - 如果要使用 AI 專用配置文件:" -ForegroundColor White
        Write-Host "    .\scripts\fix_ollama_service.ps1 -Action use-ai-file" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "==================================================================================" -ForegroundColor Cyan
Write-Host "完成" -ForegroundColor Cyan
Write-Host "==================================================================================" -ForegroundColor Cyan