# implement_vm_architecture.ps1
# 執行 VM 化架構實施
# 協調腳本：啟用 Hyper-V -> 創建 VM -> 配置網絡

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      Wuchang VM Architecture Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Enable Hyper-V
Write-Host "[Step 1/3] Enabling Hyper-V..." -ForegroundColor Yellow
$enableScript = Join-Path $ScriptDir "enable_hyperv.ps1"
if (Test-Path $enableScript) {
    & $enableScript
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Hyper-V enablement failed. Please restart and try again."
        exit $LASTEXITCODE
    }
} else {
    Write-Error "Script not found: $enableScript"
    exit 1
}

# 2. Create VM
Write-Host "`n[Step 2/3] Creating Store Control VM..." -ForegroundColor Yellow
$createVmScript = Join-Path $ScriptDir "create_store_vm.ps1"
if (Test-Path $createVmScript) {
    & $createVmScript
    if ($LASTEXITCODE -ne 0) {
        Write-Error "VM creation failed."
        exit $LASTEXITCODE
    }
} else {
    Write-Error "Script not found: $createVmScript"
    exit 1
}

# 3. Setup Network
Write-Host "`n[Step 3/3] Setting up VM Network..." -ForegroundColor Yellow
$networkScript = Join-Path $ScriptDir "setup_vm_network.ps1"
if (Test-Path $networkScript) {
    & $networkScript
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Network setup failed."
        exit $LASTEXITCODE
    }
} else {
    Write-Error "Script not found: $networkScript"
    exit 1
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "      VM Architecture Setup Complete" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Next Steps:"
Write-Host "1. Open Hyper-V Manager to verify 'Wuchang-Store-Control' VM."
Write-Host "2. Install OS on the VM (Attach ISO)."
Write-Host "3. Configure networking inside the VM (IP: 192.168.100.x)."
