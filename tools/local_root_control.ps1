<#
Local Root Control Panel (Desktop Shortcut)
- Scope: local machine only; highest-privilege actions are gated by UAC and visible logs.
- Functions: start/stop core stack, view key AI params, open logs.
- Usage: run in elevated PowerShell (Run as Administrator). Create a desktop shortcut pointing to:
    powershell.exe -NoLogo -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\tools\local_root_control.ps1"
#>

param()

# Guard: require admin
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "[FAIL] 請用系統管理員模式啟動此面板 (Run as Administrator)" -ForegroundColor Red
    exit 1
}

$workspace = "C:\wuchang V5.1.0"
$compose = Join-Path $workspace "docker-compose.yml"
$logDir = Join-Path $workspace "logs"

function Start-Core {
    Write-Host "[INFO] 啟動核心服務 (docker-compose up -d)" -ForegroundColor Cyan
    pushd $workspace
    docker-compose up -d | Write-Host
    popd
}

function Stop-Core {
    Write-Host "[WARN] 停止核心服務 (docker-compose down)" -ForegroundColor Yellow
    pushd $workspace
    docker-compose down | Write-Host
    popd
}

function Show-AIParams {
    $cmd = @"
docker exec -it wuchangv510-wuchang-web-1 bash -lc ""odoo shell -d admin --db_host=db --db_user=odoo --db_password=odoo <<'PY'
env = env['ir.config_parameter'].sudo()
keys = [
    'wuchang.cloud_approved',
    'wuchang.google.project_id',
    'wuchang.google.location',
    'wuchang.ai_mode',
    'wuchang.llm_base_url',
    'wuchang.gemini_api_key'
]
for k in keys:
    print(k, '=>', env.get_param(k))
PY"""
"@
    Write-Host "[INFO] 查詢 AI 參數" -ForegroundColor Cyan
    Invoke-Expression $cmd
}

function Tail-OdooLog {
    Write-Host "[INFO] 追蹤 Odoo 記錄 (docker logs -f) 按 Ctrl+C 離開" -ForegroundColor Cyan
    docker logs -f wuchangv510-wuchang-web-1
}

function Tail-CaddyLog {
    Write-Host "[INFO] 追蹤 Caddy 記錄 (docker logs -f) 按 Ctrl+C 離開" -ForegroundColor Cyan
    docker logs -f wuchangv510-caddy-1
}

# Simple text UI
Write-Host "================= Wuchang Local Root Control =================" -ForegroundColor Green
Write-Host "[1] 啟動核心服務 (docker-compose up -d)"
Write-Host "[2] 停止核心服務 (docker-compose down)"
Write-Host "[3] 查詢 AI 參數 (Odoo ir.config_parameter)"
Write-Host "[4] 追蹤 Odoo 日誌"
Write-Host "[5] 追蹤 Caddy 日誌"
Write-Host "[Q] 離開"
Write-Host "===============================================================" -ForegroundColor Green

while ($true) {
    $choice = Read-Host "請輸入選項"
    switch ($choice.ToUpper()) {
        '1' { Start-Core }
        '2' { Stop-Core }
        '3' { Show-AIParams }
        '4' { Tail-OdooLog }
        '5' { Tail-CaddyLog }
        'Q' { break }
        default { Write-Host "無效選項" -ForegroundColor Yellow }
    }
}
