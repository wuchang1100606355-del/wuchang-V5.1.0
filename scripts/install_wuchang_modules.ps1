# Wuchang OS 模組安裝腳本 (PowerShell)
# 安裝所有 Wuchang 相關模組

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Wuchang OS 模組安裝工具" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 所有要安裝的 Wuchang 模組
$modules = @(
    'wuchang_core',
    'wuchang_finance',
    'wuchang_business',
    'wuchang_volunteer',
    'wuchang_community_campaign',
    'wuchang_web_portal',
    'wuchang_design_system',
    'wuchang_ui_compliance',
    'wuchang_property_toolkits',
    'wuchang_award_coach',
    'wuchang_guardian',
    'wuchang_life'
)

Write-Host "`n將安裝以下 $($modules.Count) 個模組：" -ForegroundColor Yellow
for ($i = 0; $i -lt $modules.Count; $i++) {
    Write-Host "  $($i+1). $($modules[$i])" -ForegroundColor White
}

$modulesStr = $modules -join ','

# 檢查是否使用 Docker
$useDocker = $false
if ($args.Count -gt 0) {
    if ($args[0] -eq '--docker' -or $args[0] -eq '-d') {
        $useDocker = $true
    }
    elseif ($args[0] -eq '--local' -or $args[0] -eq '-l') {
        $useDocker = $false
    }
} else {
    # 自動檢測
    $workspacePath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $dockerComposeFile = Join-Path $workspacePath 'docker-compose.yml'
    
    if (Test-Path $dockerComposeFile) {
        try {
            docker-compose --version | Out-Null
            $useDocker = $true
            Write-Host "`n✓ 檢測到 Docker Compose，將使用 Docker 方式安裝" -ForegroundColor Green
        } catch {
            Write-Host "`n⚠ 未檢測到 Docker Compose，將嘗試本地安裝" -ForegroundColor Yellow
        }
    }
}

Write-Host ""

if ($useDocker) {
    Write-Host "使用 Docker Compose 安裝模組..." -ForegroundColor Cyan
    Write-Host "執行命令: docker-compose run --rm wuchang-web odoo -i $modulesStr --stop-after-init" -ForegroundColor Gray
    
    try {
        Push-Location (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
        docker-compose run --rm `
            wuchang-web `
            odoo `
            -i $modulesStr `
            --stop-after-init `
            --db_host=db `
            --db_user=odoo `
            --db_password=odoo `
            --addons-path=/mnt/extra-addons
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n============================================================" -ForegroundColor Green
            Write-Host "✅ 模組安裝完成！" -ForegroundColor Green
            Write-Host "============================================================" -ForegroundColor Green
            Write-Host "`n💡 提示：" -ForegroundColor Yellow
            Write-Host "  - 運行: docker-compose up -d" -ForegroundColor White
            Write-Host "  - 訪問: http://localhost:8069" -ForegroundColor White
            Write-Host "  - 登入後在 Apps 菜單中可以確認模組安裝狀態" -ForegroundColor White
        } else {
            Write-Host "`n============================================================" -ForegroundColor Red
            Write-Host "❌ 安裝失敗 (退出碼: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "============================================================" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "`n============================================================" -ForegroundColor Red
        Write-Host "❌ 安裝失敗: $_" -ForegroundColor Red
        Write-Host "============================================================" -ForegroundColor Red
        exit 1
    } finally {
        Pop-Location
    }
} else {
    Write-Host "使用本地 Odoo 安裝模組..." -ForegroundColor Cyan
    
    # 嘗試找到 Odoo 可執行文件
    $odooPaths = @(
        'C:\Users\o0930\odoo\odoo-bin',
        'odoo-bin',
        'odoo'
    )
    
    $odooBin = $null
    foreach ($path in $odooPaths) {
        if (Test-Path $path) {
            $odooBin = $path
            break
        }
    }
    
    if (-not $odooBin) {
        # 嘗試通過命令查找
        try {
            $odooBin = Get-Command odoo-bin -ErrorAction Stop | Select-Object -ExpandProperty Source
        } catch {
            try {
                $odooBin = Get-Command odoo -ErrorAction Stop | Select-Object -ExpandProperty Source
            } catch {
                Write-Host "❌ 找不到 Odoo 可執行文件" -ForegroundColor Red
                Write-Host "請確保 Odoo 已安裝或使用 Docker 方式安裝 (使用 --docker 參數)" -ForegroundColor Yellow
                exit 1
            }
        }
    }
    
    $workspacePath = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $addonsPath = Join-Path $workspacePath 'wuchang_os\addons'
    $configPath = Join-Path $workspacePath 'config\odoo.conf'
    
    Write-Host "執行命令: $odooBin -i $modulesStr --stop-after-init" -ForegroundColor Gray
    
    try {
        & $odooBin `
            -i $modulesStr `
            --stop-after-init `
            --addons-path $addonsPath `
            -c $configPath
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n============================================================" -ForegroundColor Green
            Write-Host "✅ 模組安裝完成！" -ForegroundColor Green
            Write-Host "============================================================" -ForegroundColor Green
        } else {
            Write-Host "`n============================================================" -ForegroundColor Red
            Write-Host "❌ 安裝失敗 (退出碼: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "============================================================" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "`n============================================================" -ForegroundColor Red
        Write-Host "❌ 安裝失敗: $_" -ForegroundColor Red
        Write-Host "============================================================" -ForegroundColor Red
        exit 1
    }
}

exit 0