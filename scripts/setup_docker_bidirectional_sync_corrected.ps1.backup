# Docker 雙向同步設定腳本（正確版本）
# VM 伺服器 (192.168.50.249) 和 UI 筆電 (192.168.50.84) 互相訪問對方的 Docker

Param(
    [string]$UIIP = "192.168.50.84",
    [string]$VMIP = "192.168.50.249",
    [string]$UIUser = $env:USERNAME,
    [string]$VMUser = "administrator"
)

Write-Host "`n=== Docker 雙向同步設定 ===" -ForegroundColor Cyan
Write-Host "當前機器: VM 伺服器 ($VMIP)" -ForegroundColor White
Write-Host "目標機器: UI 筆電 ($UIIP)" -ForegroundColor White
Write-Host ""

# 檢查當前機器 IP
$currentIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.50.*"} | Select-Object -First 1).IPAddress
Write-Host "檢測到當前 IP: $currentIP" -ForegroundColor Cyan

if ($currentIP -eq $VMIP) {
    Write-Host "`n[VM 伺服器端設定]" -ForegroundColor Yellow
    Write-Host "正在設定 VM 伺服器可以連接到 UI 筆電的 Docker..." -ForegroundColor White
    
    # 1. 在 VM 伺服器上建立 UI 筆電的 Context
    Write-Host "`n[1] 建立 UI 筆電的 Docker Context..." -ForegroundColor Yellow
    try {
        docker context create ui-laptop --docker "host=ssh://${UIUser}@${UIIP}" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Context 'ui-laptop' 已建立" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Context 'ui-laptop' 可能已存在" -ForegroundColor Yellow
            docker context rm ui-laptop -f 2>&1 | Out-Null
            docker context create ui-laptop --docker "host=ssh://${UIUser}@${UIIP}" 2>&1 | Out-Null
            Write-Host "  ✓ Context 'ui-laptop' 已重新建立" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠ 建立 Context 時發生錯誤: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # 2. 測試連接到 UI 筆電
    Write-Host "`n[2] 測試連接到 UI 筆電..." -ForegroundColor Yellow
    try {
        $uiContainers = docker --context ui-laptop ps --format "{{.Names}}" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ 可以連接到 UI 筆電的 Docker" -ForegroundColor Green
            if ($uiContainers) {
                Write-Host "`n  UI 筆電上的容器：" -ForegroundColor Cyan
                foreach ($container in $uiContainers) {
                    Write-Host "    - $container" -ForegroundColor White
                }
            }
        } else {
            Write-Host "  ⚠ 無法連接到 UI 筆電，請確認：" -ForegroundColor Yellow
            Write-Host "    1. UI 筆電的 SSH 服務已啟用" -ForegroundColor White
            Write-Host "    2. SSH 金鑰已設定或可以使用密碼登入" -ForegroundColor White
            Write-Host "    3. UI 筆電的防火牆未阻擋 SSH" -ForegroundColor White
        }
    } catch {
        Write-Host "  ⚠ 連接測試失敗: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # 3. 建立便利腳本
    Write-Host "`n[3] 建立便利腳本..." -ForegroundColor Yellow
    
    # 建立 docker-ui.ps1（從 VM 切換到 UI 筆電）
    $dockerUiScript = @"
# 從 VM 伺服器切換到 UI 筆電的 Docker Context
docker context use ui-laptop
Write-Host "已切換到 UI 筆電 Docker Context" -ForegroundColor Green
"@
    $dockerUiScript | Out-File -FilePath "scripts\docker-ui.ps1" -Encoding UTF8
    Write-Host "  ✓ 已建立 scripts\docker-ui.ps1" -ForegroundColor Green
    
    # 建立 docker-vm-local.ps1（切換回 VM 本地）
    $dockerVmLocalScript = @"
# 切換回 VM 伺服器本地 Docker Context
docker context use default
Write-Host "已切換回 VM 伺服器本地 Docker Context" -ForegroundColor Green
"@
    $dockerVmLocalScript | Out-File -FilePath "scripts\docker-vm-local.ps1" -Encoding UTF8
    Write-Host "  ✓ 已建立 scripts\docker-vm-local.ps1" -ForegroundColor Green
    
    Write-Host "`n=== VM 伺服器端設定完成 ===" -ForegroundColor Cyan
    Write-Host "`n使用範例（在 VM 伺服器上）：" -ForegroundColor Yellow
    Write-Host "  .\scripts\docker-ui.ps1              # 切換到 UI 筆電" -ForegroundColor White
    Write-Host "  docker ps                            # 查看 UI 筆電的容器" -ForegroundColor White
    Write-Host "  .\scripts\docker-vm-local.ps1        # 切換回 VM 本地" -ForegroundColor White
    Write-Host ""
    
} elseif ($currentIP -eq $UIIP) {
    Write-Host "`n[UI 筆電端設定]" -ForegroundColor Yellow
    Write-Host "正在設定 UI 筆電可以連接到 VM 伺服器的 Docker..." -ForegroundColor White
    
    # 1. 在 UI 筆電上建立 VM 伺服器的 Context
    Write-Host "`n[1] 建立 VM 伺服器的 Docker Context..." -ForegroundColor Yellow
    try {
        docker context create vm-server --docker "host=ssh://${VMUser}@${VMIP}" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Context 'vm-server' 已建立" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Context 'vm-server' 可能已存在" -ForegroundColor Yellow
            docker context rm vm-server -f 2>&1 | Out-Null
            docker context create vm-server --docker "host=ssh://${VMUser}@${VMIP}" 2>&1 | Out-Null
            Write-Host "  ✓ Context 'vm-server' 已重新建立" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠ 建立 Context 時發生錯誤: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # 2. 測試連接到 VM 伺服器
    Write-Host "`n[2] 測試連接到 VM 伺服器..." -ForegroundColor Yellow
    try {
        $vmContainers = docker --context vm-server ps --format "{{.Names}}" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ 可以連接到 VM 伺服器的 Docker" -ForegroundColor Green
            if ($vmContainers) {
                Write-Host "`n  VM 伺服器上的容器：" -ForegroundColor Cyan
                foreach ($container in $vmContainers) {
                    Write-Host "    - $container" -ForegroundColor White
                }
            }
        } else {
            Write-Host "  ⚠ 無法連接到 VM 伺服器，請確認：" -ForegroundColor Yellow
            Write-Host "    1. VM 伺服器的 SSH 服務已啟用" -ForegroundColor White
            Write-Host "    2. SSH 金鑰已設定或可以使用密碼登入" -ForegroundColor White
            Write-Host "    3. VM 伺服器的防火牆未阻擋 SSH" -ForegroundColor White
        }
    } catch {
        Write-Host "  ⚠ 連接測試失敗: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # 3. 建立便利腳本
    Write-Host "`n[3] 建立便利腳本..." -ForegroundColor Yellow
    
    # 建立 docker-vm.ps1（從 UI 切換到 VM）
    $dockerVmScript = @"
# 從 UI 筆電切換到 VM 伺服器的 Docker Context
docker context use vm-server
Write-Host "已切換到 VM 伺服器 Docker Context" -ForegroundColor Green
"@
    $dockerVmScript | Out-File -FilePath "scripts\docker-vm.ps1" -Encoding UTF8
    Write-Host "  ✓ 已建立 scripts\docker-vm.ps1" -ForegroundColor Green
    
    # 建立 docker-ui-local.ps1（切換回 UI 本地）
    $dockerUiLocalScript = @"
# 切換回 UI 筆電本地 Docker Context
docker context use default
Write-Host "已切換回 UI 筆電本地 Docker Context" -ForegroundColor Green
"@
    $dockerUiLocalScript | Out-File -FilePath "scripts\docker-ui-local.ps1" -Encoding UTF8
    Write-Host "  ✓ 已建立 scripts\docker-ui-local.ps1" -ForegroundColor Green
    
    Write-Host "`n=== UI 筆電端設定完成 ===" -ForegroundColor Cyan
    Write-Host "`n使用範例（在 UI 筆電上）：" -ForegroundColor Yellow
    Write-Host "  .\scripts\docker-vm.ps1              # 切換到 VM 伺服器" -ForegroundColor White
    Write-Host "  docker ps                            # 查看 VM 的容器" -ForegroundColor White
    Write-Host "  .\scripts\docker-ui-local.ps1        # 切換回 UI 本地" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "⚠ 無法識別當前機器類型" -ForegroundColor Yellow
    Write-Host "當前 IP: $currentIP" -ForegroundColor White
    Write-Host "預期 VM IP: $VMIP" -ForegroundColor White
    Write-Host "預期 UI IP: $UIIP" -ForegroundColor White
}

Write-Host "`n=== 雙向同步設定說明 ===" -ForegroundColor Cyan
Write-Host "`n要完成雙向同步，需要在兩台機器上都執行此腳本：" -ForegroundColor Yellow
Write-Host "`n1. 在 VM 伺服器 (192.168.50.249) 上執行：" -ForegroundColor White
Write-Host "   .\scripts\setup_docker_bidirectional_sync_corrected.ps1" -ForegroundColor Gray
Write-Host "`n2. 在 UI 筆電 (192.168.50.84) 上執行：" -ForegroundColor White
Write-Host "   .\scripts\setup_docker_bidirectional_sync_corrected.ps1" -ForegroundColor Gray
Write-Host "`n3. 確認 SSH 連接正常：" -ForegroundColor White
Write-Host "   - VM → UI: ssh $UIUser@$UIIP" -ForegroundColor Gray
Write-Host "   - UI → VM: ssh $VMUser@$VMIP" -ForegroundColor Gray
Write-Host ""
