# 五常 AI - 啟動自動連線守護服務

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  🌐 五常 AI - 自動連線守護服務" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 切換到正確目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 檢查 Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ 找不到 Python" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Python 環境正常" -ForegroundColor Green
Write-Host ""

# 設定環境變數（可自訂）
if (-not $env:INTERNAL_SERVER) { $env:INTERNAL_SERVER = "192.168.50.249" }
if (-not $env:INTERNAL_PORT) { $env:INTERNAL_PORT = "8766" }
if (-not $env:EXTERNAL_SERVER) { $env:EXTERNAL_SERVER = "wuchang.life" }
if (-not $env:EXTERNAL_PORT) { $env:EXTERNAL_PORT = "8766" }
if (-not $env:CHECK_INTERVAL) { $env:CHECK_INTERVAL = "30" }

Write-Host "配置:" -ForegroundColor Yellow
Write-Host "  內網: $env:INTERNAL_SERVER`:$env:INTERNAL_PORT" -ForegroundColor White
Write-Host "  外網: $env:EXTERNAL_SERVER`:$env:EXTERNAL_PORT" -ForegroundColor White
Write-Host "  檢查間隔: $env:CHECK_INTERVAL 秒" -ForegroundColor White
Write-Host ""

# 選擇運行模式
Write-Host "請選擇運行模式:" -ForegroundColor Yellow
Write-Host "  1. 前台運行（可看日誌）" -ForegroundColor White
Write-Host "  2. 背景運行（最小化）" -ForegroundColor White
Write-Host "  3. 安裝為系統服務（需管理員權限）" -ForegroundColor White
Write-Host ""

$mode = Read-Host "請選擇 (1-3)"

Write-Host ""

switch ($mode) {
    "1" {
        Write-Host "🚀 前台運行模式" -ForegroundColor Green
        Write-Host ""
        & python auto_connect_service.py
    }
    "2" {
        Write-Host "🔄 背景運行模式" -ForegroundColor Green
        Write-Host ""
        
        $job = Start-Job -ScriptBlock {
            param($path)
            Set-Location $path
            & python auto_connect_service.py
        } -ArgumentList $scriptPath
        
        Write-Host "✅ 服務已在背景啟動 (Job ID: $($job.Id))" -ForegroundColor Green
        Write-Host ""
        Write-Host "管理命令:" -ForegroundColor Yellow
        Write-Host "  查看狀態: Get-Job" -ForegroundColor White
        Write-Host "  查看輸出: Receive-Job -Id $($job.Id) -Keep" -ForegroundColor White
        Write-Host "  停止服務: Stop-Job -Id $($job.Id); Remove-Job -Id $($job.Id)" -ForegroundColor White
    }
    "3" {
        Write-Host "🔧 安裝為系統服務" -ForegroundColor Green
        Write-Host ""
        
        # 檢查管理員權限
        $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if (-not $isAdmin) {
            Write-Host "❌ 需要管理員權限" -ForegroundColor Red
            Write-Host "請以管理員身份重新執行此腳本" -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host "此功能需要 NSSM (Non-Sucking Service Manager)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "安裝 NSSM:" -ForegroundColor White
        Write-Host "  1. 下載: https://nssm.cc/download" -ForegroundColor Gray
        Write-Host "  2. 解壓到 C:\Tools\nssm\" -ForegroundColor Gray
        Write-Host "  3. 重新執行此腳本" -ForegroundColor Gray
        Write-Host ""
        
        $nssmPath = "C:\Tools\nssm\win64\nssm.exe"
        
        if (Test-Path $nssmPath) {
            $serviceName = "WuchangAutoConnect"
            $pythonPath = (Get-Command python).Source
            $scriptFullPath = Join-Path $scriptPath "auto_connect_service.py"
            
            Write-Host "安裝服務..." -ForegroundColor Yellow
            
            # 安裝服務
            & $nssmPath install $serviceName $pythonPath $scriptFullPath
            & $nssmPath set $serviceName AppDirectory $scriptPath
            & $nssmPath set $serviceName DisplayName "五常 AI - 自動連線服務"
            & $nssmPath set $serviceName Description "監控內外網並自動切換連線模式"
            & $nssmPath set $serviceName Start SERVICE_AUTO_START
            
            # 設定環境變數
            & $nssmPath set $serviceName AppEnvironmentExtra "INTERNAL_SERVER=$env:INTERNAL_SERVER" "INTERNAL_PORT=$env:INTERNAL_PORT" "EXTERNAL_SERVER=$env:EXTERNAL_SERVER" "EXTERNAL_PORT=$env:EXTERNAL_PORT"
            
            # 啟動服務
            Start-Service $serviceName
            
            Write-Host ""
            Write-Host "✅ 服務安裝成功！" -ForegroundColor Green
            Write-Host ""
            Write-Host "管理命令:" -ForegroundColor Yellow
            Write-Host "  查看狀態: Get-Service $serviceName" -ForegroundColor White
            Write-Host "  啟動服務: Start-Service $serviceName" -ForegroundColor White
            Write-Host "  停止服務: Stop-Service $serviceName" -ForegroundColor White
            Write-Host "  移除服務: & '$nssmPath' remove $serviceName confirm" -ForegroundColor White
        } else {
            Write-Host "❌ 找不到 NSSM" -ForegroundColor Red
        }
    }
    default {
        Write-Host "❌ 無效的選項" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  完成" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
