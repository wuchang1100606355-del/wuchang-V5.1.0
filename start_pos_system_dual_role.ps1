#!/usr/bin/env powershell
<#
.SYNOPSIS
五常 POS 系統完整啟動與驗證
- 檢查硬體
- 啟動 Ollama LLM
- 啟動 FastAPI 伺服器 (雙角色)
- 驗證所有服務
- 開啟儀表板
#>

param(
    [switch]$DualRole = $true,  # 使用新的雙角色伺服器
    [switch]$SkipOllama = $false,
    [switch]$NoOpen = $false,
    [string]$Token = "merchant-demo-001"
)

$ErrorActionPreference = "Continue"
$projectRoot = "C:\wuchang V5.1.0"
$serverPort = 8080

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  五常 POS 系統 - 完整啟動腳本                              ║" -ForegroundColor Cyan
Write-Host "║  Wuchang Dual-Role Little-j System                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================
# 1. 環境檢查
# ============================================
Write-Host "📋 步驟 1：環境檢查" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────"

# 檢查 Python
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if ($pythonPath) {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python 未安裝" -ForegroundColor Red
    exit 1
}

# 檢查虛擬環境
if (Test-Path "$projectRoot\.venv\Scripts\Activate.ps1") {
    Write-Host "✓ 虛擬環境已存在" -ForegroundColor Green
} else {
    Write-Host "⚠️  虛擬環境不存在，建立中..." -ForegroundColor Yellow
    cd $projectRoot
    python -m venv .venv
    & "$projectRoot\.venv\Scripts\Activate.ps1"
    pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "✓ 虛擬環境已建立" -ForegroundColor Green
}

# 啟用虛擬環境
& "$projectRoot\.venv\Scripts\Activate.ps1"

# 檢查 Ollama
$ollamaVersion = ollama --version 2>&1
if ($?) {
    Write-Host "✓ Ollama: $ollamaVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Ollama 未安裝或未在 PATH 中" -ForegroundColor Yellow
    Write-Host "   建議下載：https://ollama.ai/download" -ForegroundColor Gray
}

# 檢查必要套件
Write-Host "✓ 檢查必要套件..." -ForegroundColor Green
$requiredPackages = @("fastapi", "uvicorn", "requests")
foreach ($pkg in $requiredPackages) {
    $check = pip show $pkg 2>&1 | Select-String "Name"
    if ($?) {
        Write-Host "  ✓ $pkg" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $pkg" -ForegroundColor Red
    }
}

Write-Host ""

# ============================================
# 2. 啟動 Ollama
# ============================================
if (-not $SkipOllama) {
    Write-Host "🚀 步驟 2：啟動 Ollama 本地 LLM" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────────"
    
    # 檢查 Ollama 進程
    $ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
    if ($ollamaProcess) {
        Write-Host "✓ Ollama 已在運行 (PID: $($ollamaProcess.Id))" -ForegroundColor Green
    } else {
        Write-Host "啟動 Ollama 服務..." -ForegroundColor Gray
        # 嘗試啟動 Ollama
        if (Test-Path "C:\Program Files\Ollama\ollama.exe") {
            Start-Process "C:\Program Files\Ollama\ollama.exe" -ArgumentList "serve" -NoNewWindow
            Write-Host "✓ Ollama 啟動中..." -ForegroundColor Green
            Start-Sleep -Seconds 3
        } else {
            Write-Host "⚠️  Ollama 執行檔未找到，請手動啟動 Ollama" -ForegroundColor Yellow
            Write-Host "   命令：ollama serve" -ForegroundColor Gray
        }
    }
    
    # 驗證 Ollama 端點
    Write-Host "驗證 Ollama 端點..." -ForegroundColor Gray
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:11434/api/tags" -Method Get -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $tags = $response.Content | ConvertFrom-Json
            $modelCount = ($tags.models | Measure-Object).Count
            Write-Host "✓ Ollama 端點: http://127.0.0.1:11434 (模型數: $modelCount)" -ForegroundColor Green
            
            # 列出可用模型
            if ($tags.models) {
                Write-Host "可用模型:" -ForegroundColor Gray
                $tags.models | ForEach-Object {
                    Write-Host "  - $($_.name)" -ForegroundColor Gray
                }
            }
        }
    } catch {
        Write-Host "⚠️  無法連接 Ollama 端點，請確認 Ollama 運行中" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# ============================================
# 3. 配置環境變數
# ============================================
Write-Host "⚙️  步驟 3：配置環境變數" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────"

$env:LOCAL_LLM_ENDPOINT = "http://127.0.0.1:11434/v1/chat/completions"
$env:LOCAL_LLM_MODEL = "little-j"
$env:LLM_FALLBACK = "1"
$env:POS_UI_URL = "http://192.168.50.249:8069/pos/ui"
$env:CUSTOMER_UI_URL = "http://192.168.50.249:8069/pos/customer_display"

Write-Host "✓ LOCAL_LLM_ENDPOINT=$env:LOCAL_LLM_ENDPOINT" -ForegroundColor Green
Write-Host "✓ LOCAL_LLM_MODEL=$env:LOCAL_LLM_MODEL" -ForegroundColor Green
Write-Host "✓ LLM_FALLBACK=$env:LLM_FALLBACK" -ForegroundColor Green

Write-Host ""

# ============================================
# 4. 啟動 FastAPI 伺服器
# ============================================
Write-Host "🎯 步驟 4：啟動 FastAPI 伺服器" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────"

$serverScript = if ($DualRole) { "vm_fastapi_main_dual_role" } else { "vm_fastapi_main_new" }

Write-Host "使用伺服器: $serverScript.py" -ForegroundColor Gray
Write-Host "埠口: $serverPort" -ForegroundColor Gray

# 建立伺服器啟動任務（背景進程）
$serverJob = Start-Job -ScriptBlock {
    param($root, $script, $port)
    Set-Location $root
    & "$root\.venv\Scripts\Activate.ps1"
    python -m uvicorn "${script}:app" --host 0.0.0.0 --port $port --reload
} -ArgumentList $projectRoot, $serverScript, $serverPort

Write-Host "✓ FastAPI 伺服器啟動中..." -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host ""

# ============================================
# 5. 驗證伺服器
# ============================================
Write-Host "🧪 步驟 5：驗證伺服器" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────"

$maxRetry = 10
$retryCount = 0
$serverReady = $false

while ($retryCount -lt $maxRetry) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$serverPort/" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            Write-Host "✓ 伺服器狀態: $($data.status)" -ForegroundColor Green
            Write-Host "✓ 系統版本: $($data.version)" -ForegroundColor Green
            Write-Host "✓ 時間戳: $($data.timestamp)" -ForegroundColor Green
            $serverReady = $true
            break
        }
    } catch {
        $retryCount++
        Write-Host "  重試中... ($retryCount/$maxRetry)" -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $serverReady) {
    Write-Host "✗ 伺服器未能啟動，請檢查日誌" -ForegroundColor Red
    Get-Job -Id $serverJob.Id | Stop-Job
    exit 1
}

Write-Host ""

# ============================================
# 6. 測試 API 端點
# ============================================
Write-Host "🔍 步驟 6：測試 API 端點" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────"

# 測試裝置清單
Write-Host "測試 /devices..." -ForegroundColor Gray
try {
    $devices = Invoke-WebRequest -Uri "http://localhost:$serverPort/devices" -Method Get -Headers @{"X-Auth-Token" = $Token} | ConvertFrom-Json
    Write-Host "✓ /devices: $($devices.count) 個裝置已註冊" -ForegroundColor Green
} catch {
    Write-Host "✗ /devices 端點失敗" -ForegroundColor Red
}

# 測試 LLM 對話
Write-Host "測試 /llm/chat..." -ForegroundColor Gray
try {
    $chatParams = @{
        Uri = "http://localhost:$serverPort/llm/chat"
        Method = "POST"
        Headers = @{
            "X-Auth-Token" = $Token
            "Content-Type" = "application/json"
        }
        Body = ConvertTo-Json @{
            message = "你好，請簡單介紹一下自己"
        }
    }
    $chatResp = Invoke-WebRequest @chatParams | ConvertFrom-Json
    Write-Host "✓ /llm/chat: 來源=$($chatResp.source), 角色=$($chatResp.role)" -ForegroundColor Green
    Write-Host "  回應片段: $($chatResp.response.Substring(0, [Math]::Min(50, $chatResp.response.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ /llm/chat 端點失敗: $_" -ForegroundColor Red
}

# 測試儀表板
Write-Host "測試 /dashboard..." -ForegroundColor Gray
try {
    $dashboard = Invoke-WebRequest -Uri "http://localhost:$serverPort/dashboard" -Method Get | Select-Object -ExpandProperty RawContent
    if ($dashboard -match "五常.*儀表板") {
        Write-Host "✓ /dashboard: HTML 頁面已生成" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  /dashboard 存取失敗" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# 7. 顯示系統摘要
# ============================================
Write-Host "📊 系統摘要" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────"

Write-Host "🌐 伺服器地址: http://localhost:$serverPort" -ForegroundColor Cyan
Write-Host "📱 儀表板: http://localhost:$serverPort/dashboard" -ForegroundColor Cyan
Write-Host "🎤 語音 API: /voice/recognize, /voice/synthesize, /voice/command" -ForegroundColor Cyan
Write-Host "💬 LLM 端點: /llm/chat (本地優先)" -ForegroundColor Cyan
Write-Host "👤 身份驗證: X-Auth-Token 標頭" -ForegroundColor Cyan
Write-Host "🔑 預設 Token:" -ForegroundColor Cyan
Write-Host "   - merchant-demo-001 (店家)" -ForegroundColor Gray
Write-Host "   - architect-demo-001 (架構師)" -ForegroundColor Gray
Write-Host "📝 決策日誌: ./decision_logs/" -ForegroundColor Cyan
Write-Host "📊 事件日誌: ./events.log.jsonl" -ForegroundColor Cyan

Write-Host ""

# ============================================
# 8. 打開儀表板（可選）
# ============================================
if (-not $NoOpen) {
    Write-Host "🎯 開啟儀表板..." -ForegroundColor Yellow
    $dashboardUrl = "http://localhost:$serverPort/dashboard"
    
    try {
        Start-Process $dashboardUrl
        Write-Host "✓ 儀表板已在瀏覽器開啟" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  無法自動開啟瀏覽器，請手動訪問: $dashboardUrl" -ForegroundColor Yellow
    }
}

Write-Host ""

# ============================================
# 9. 伺服器運行監控
# ============================================
Write-Host "▶️  伺服器運行中... (按 Ctrl+C 停止)" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────────────────────"

# 監控背景工作
while ($true) {
    $job = Get-Job -Id $serverJob.Id -ErrorAction SilentlyContinue
    if ($job.State -ne "Running") {
        Write-Host "✗ 伺服器已停止" -ForegroundColor Red
        break
    }
    
    # 每 10 秒檢查一次健康狀態
    Start-Sleep -Seconds 10
    try {
        $health = Invoke-WebRequest -Uri "http://localhost:$serverPort/" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($health.StatusCode -eq 200) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✓ 伺服器運行正常" -ForegroundColor Green
        }
    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ⚠️  伺服器無響應" -ForegroundColor Yellow
    }
}

# 清理
Write-Host ""
Write-Host "清理中..." -ForegroundColor Yellow
Stop-Job -Id $serverJob.Id
Remove-Job -Id $serverJob.Id
Write-Host "✓ 伺服器已停止" -ForegroundColor Green
