# AI 小 J 完整授權設定腳本
# 需要管理員權限執行

param(
    [switch]$EnableCloudCompute,
    [switch]$FullAccess
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI 小 J 完整授權設定" -ForegroundColor Cyan
Write-Host "時空系統最高權限配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "警告: 需要管理員權限以設定完整授權" -ForegroundColor Yellow
    Write-Host "請以管理員身份重新執行此腳本" -ForegroundColor Yellow
}

# 設定環境變數
Write-Host "`n設定環境變數..." -ForegroundColor Green

# 時空系統路徑
$spatiotemporalPath = Join-Path $PSScriptRoot ".."
[Environment]::SetEnvironmentVariable("SPATIOTEMPORAL_SYSTEM_PATH", $spatiotemporalPath, "Machine")
Write-Host "✓ SPATIOTEMPORAL_SYSTEM_PATH 已設定" -ForegroundColor Green

# AI 小 J 授權
[Environment]::SetEnvironmentVariable("AI_J_FULL_AUTHORIZATION", "true", "Machine")
Write-Host "✓ AI_J_FULL_AUTHORIZATION 已啟用" -ForegroundColor Green

# 時空系統啟用
[Environment]::SetEnvironmentVariable("SPATIOTEMPORAL_ENABLED", "true", "Machine")
Write-Host "✓ SPATIOTEMPORAL_ENABLED 已啟用" -ForegroundColor Green

# 雲端算力設定
if ($EnableCloudCompute -or $FullAccess) {
    Write-Host "`n設定雲端算力授權..." -ForegroundColor Green
    
    # 檢查 API Key
    $openaiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
    $anthropicKey = [Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
    $googleKey = [Environment]::GetEnvironmentVariable("GOOGLE_API_KEY", "User")
    
    if ($openaiKey) {
        [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $openaiKey, "Machine")
        Write-Host "✓ OpenAI API Key 已設定（機器層級）" -ForegroundColor Green
    } else {
        Write-Host "⚠ OpenAI API Key 未設定，請手動設定" -ForegroundColor Yellow
    }
    
    if ($anthropicKey) {
        [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $anthropicKey, "Machine")
        Write-Host "✓ Anthropic API Key 已設定（機器層級）" -ForegroundColor Green
    } else {
        Write-Host "⚠ Anthropic API Key 未設定，請手動設定" -ForegroundColor Yellow
    }
    
    if ($googleKey) {
        [Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $googleKey, "Machine")
        Write-Host "✓ Google API Key 已設定（機器層級）" -ForegroundColor Green
    } else {
        Write-Host "⚠ Google API Key 未設定，請手動設定" -ForegroundColor Yellow
    }
    
    [Environment]::SetEnvironmentVariable("CLOUD_COMPUTE_ENABLED", "true", "Machine")
    Write-Host "✓ 雲端算力已啟用" -ForegroundColor Green
}

# 建立授權配置檔案
Write-Host "`n建立授權配置檔案..." -ForegroundColor Green
$configPath = Join-Path $spatiotemporalPath "config\authorization.json"
$configDir = Split-Path $configPath -Parent

if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$authorizationConfig = @{
    ai_j = @{
        full_authorization = $true
        spatiotemporal_access = $true
        cloud_compute_access = ($EnableCloudCompute -or $FullAccess)
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    }
    spatiotemporal_system = @{
        enabled = $true
        version = "1.0.0"
        cloud_compute_enabled = ($EnableCloudCompute -or $FullAccess)
    }
} | ConvertTo-Json -Depth 10

$authorizationConfig | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "✓ 授權配置已建立: $configPath" -ForegroundColor Green

# 設定 Python 路徑
Write-Host "`n設定 Python 路徑..." -ForegroundColor Green
$pythonPath = (Get-Command python).Source
$pythonDir = Split-Path $pythonPath -Parent
[Environment]::SetEnvironmentVariable("PYTHONPATH", "$spatiotemporalPath;$pythonDir", "Machine")
Write-Host "✓ PYTHONPATH 已設定" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "授權設定完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n已設定的授權項目:" -ForegroundColor Yellow
Write-Host "  ✓ AI 小 J 完整授權" -ForegroundColor Green
Write-Host "  ✓ 時空系統存取權限" -ForegroundColor Green
if ($EnableCloudCompute -or $FullAccess) {
    Write-Host "  ✓ 雲端算力存取權限" -ForegroundColor Green
}

Write-Host "`n注意: 需要重新啟動應用程式以使環境變數生效" -ForegroundColor Yellow
