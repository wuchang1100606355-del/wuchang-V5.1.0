# Docker 雙向同步設定腳本
# 設定 UI 筆電和 VM 伺服器可以互相訪問對方的 Docker

Param(
    [string]$UIIP = "192.168.50.84",
    [string]$VMIP = "192.168.50.249",
    [string]$UIUser = $env:USERNAME,
    [string]$VMUser = "administrator",
    [switch]$SetupPortainer = $true
)

Write-Host "`n=== Docker 雙向同步設定 ===" -ForegroundColor Cyan
Write-Host "UI 筆電: $UIIP" -ForegroundColor White
Write-Host "VM 伺服器: $VMIP" -ForegroundColor White
Write-Host ""

# 1. 在 UI 筆電上建立 VM 伺服器的 Context
Write-Host "[1] 在 UI 筆電上建立 VM 伺服器的 Context..." -ForegroundColor Yellow
try {
    docker context create vm-server --docker "host=ssh://${VMUser}@${VMIP}" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Context 'vm-server' 已建立" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Context 'vm-server' 可能已存在" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ 建立 Context 時發生錯誤: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 2. 測試 VM 伺服器連接
Write-Host "`n[2] 測試 VM 伺服器連接..." -ForegroundColor Yellow
try {
    docker --context vm-server ps --format "{{.Names}}" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ 可以連接到 VM 伺服器" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ 無法連接到 VM 伺服器，請檢查 SSH 設定" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ 連接測試失敗: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3. 設定 Portainer（如果啟用）
if ($SetupPortainer) {
    Write-Host "`n[3] 設定 Portainer 雙向管理..." -ForegroundColor Yellow
    Write-Host "`n  Portainer 設定步驟：" -ForegroundColor Cyan
    Write-Host "  1. 在 VM 伺服器上啟動 Portainer Agent：" -ForegroundColor White
    Write-Host "     docker run -d -p 9001:9001 --name portainer_agent --restart=always -v /var/run/docker.sock:/var/run/docker.sock portainer/agent:latest" -ForegroundColor Gray
    Write-Host "`n  2. 在 UI 筆電上啟動 Portainer：" -ForegroundColor White
    Write-Host "     docker run -d -p 9000:9000 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer-ce:latest" -ForegroundColor Gray
    Write-Host "`n  3. 在 Portainer UI 中添加遠程環境：" -ForegroundColor White
    Write-Host "     - 訪問 http://localhost:9000" -ForegroundColor Gray
    Write-Host "     - 添加環境 → Docker → Agent" -ForegroundColor Gray
    Write-Host "     - Agent URL: $VMIP:9001" -ForegroundColor Gray
}

# 4. 建立便利腳本
Write-Host "`n[4] 建立便利腳本..." -ForegroundColor Yellow

# 建立 docker-vm.ps1（快速切換到 VM）
$dockerVmScript = @"
# 快速切換到 VM 伺服器的 Docker Context
docker context use vm-server
Write-Host "已切換到 VM 伺服器 Docker Context" -ForegroundColor Green
"@
$dockerVmScript | Out-File -FilePath "scripts\docker-vm.ps1" -Encoding UTF8
Write-Host "  ✓ 已建立 scripts\docker-vm.ps1" -ForegroundColor Green

# 建立 docker-local.ps1（快速切換回本地）
$dockerLocalScript = @"
# 快速切換回本地 Docker Context
docker context use default
Write-Host "已切換回本地 Docker Context" -ForegroundColor Green
"@
$dockerLocalScript | Out-File -FilePath "scripts\docker-local.ps1" -Encoding UTF8
Write-Host "  ✓ 已建立 scripts\docker-local.ps1" -ForegroundColor Green

# 建立 docker-sync.ps1（同步操作）
$dockerSyncScript = @"
# Docker 雙向同步操作腳本
Param(
    [Parameter(Mandatory=`$true)]
    [string]`$Command,
    [string]`$Context = "vm-server"
)

Write-Host "執行命令: `$Command" -ForegroundColor Cyan
Write-Host "使用 Context: `$Context" -ForegroundColor Cyan
Write-Host ""

docker --context `$Context `$Command.Split(' ')
"@
$dockerSyncScript | Out-File -FilePath "scripts\docker-sync.ps1" -Encoding UTF8
Write-Host "  ✓ 已建立 scripts\docker-sync.ps1" -ForegroundColor Green

Write-Host "`n=== 設定完成 ===" -ForegroundColor Cyan
Write-Host "`n使用範例：" -ForegroundColor Yellow
Write-Host "  .\scripts\docker-vm.ps1          # 切換到 VM" -ForegroundColor White
Write-Host "  docker ps                         # 查看 VM 的容器" -ForegroundColor White
Write-Host "  .\scripts\docker-local.ps1        # 切換回本地" -ForegroundColor White
Write-Host "  .\scripts\docker-sync.ps1 -Command 'ps' -Context 'vm-server'  # 在 VM 上執行命令" -ForegroundColor White
Write-Host ""
