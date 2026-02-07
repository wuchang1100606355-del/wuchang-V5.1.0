# Docker 遠程 Context 設定腳本
# 讓 UI 筆電可以遠程管理 VM 伺服器的 Docker

Param(
    [string]$VMIP = "192.168.50.249",
    [string]$VMUser = "administrator",
    [string]$ContextName = "vm-server",
    [switch]$UseSSH = $true,
    [switch]$UseTLS = $false,
    [int]$TLSPort = 2376
)

Write-Host "`n=== Docker 遠程 Context 設定 ===" -ForegroundColor Cyan
Write-Host "VM 伺服器: $VMIP" -ForegroundColor White
Write-Host "Context 名稱: $ContextName" -ForegroundColor White
Write-Host ""

# 1. 檢查 Docker 是否安裝
Write-Host "[1] 檢查 Docker 安裝..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "  ✓ Docker 已安裝: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Docker 未安裝或未在 PATH 中" -ForegroundColor Red
    exit 1
}

# 2. 檢查現有 Context
Write-Host "`n[2] 檢查現有 Context..." -ForegroundColor Yellow
$existingContext = docker context ls --format "{{.Name}}" | Select-String -Pattern "^$ContextName$"
if ($existingContext) {
    Write-Host "  ⚠ Context '$ContextName' 已存在" -ForegroundColor Yellow
    $overwrite = Read-Host "  是否要刪除並重新建立？ (y/n)"
    if ($overwrite -eq 'y' -or $overwrite -eq 'Y') {
        docker context rm $ContextName -f | Out-Null
        Write-Host "  ✓ 已刪除舊的 Context" -ForegroundColor Green
    } else {
        Write-Host "  跳過建立，使用現有 Context" -ForegroundColor Yellow
        docker context use $ContextName
        Write-Host "  ✓ 已切換到 Context '$ContextName'" -ForegroundColor Green
        exit 0
    }
}

# 3. 測試網路連接
Write-Host "`n[3] 測試網路連接..." -ForegroundColor Yellow
try {
    $pingResult = Test-Connection -ComputerName $VMIP -Count 2 -Quiet
    if ($pingResult) {
        Write-Host "  ✓ VM 伺服器 ($VMIP) 連線正常" -ForegroundColor Green
    } else {
        Write-Host "  ❌ 無法連接到 VM 伺服器" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ 網路測試失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4. 測試 SSH 連接（如果使用 SSH）
if ($UseSSH) {
    Write-Host "`n[4] 測試 SSH 連接..." -ForegroundColor Yellow
    try {
        # 檢查 SSH 是否可用
        $sshTest = ssh -o ConnectTimeout=5 -o BatchMode=yes "$VMUser@$VMIP" "echo 'SSH connection test'" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ SSH 連接正常" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ SSH 連接可能需要密碼或金鑰設定" -ForegroundColor Yellow
            Write-Host "  提示：建議設定 SSH 金鑰認證以提升安全性" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "  ⚠ SSH 測試失敗，但將繼續建立 Context" -ForegroundColor Yellow
    }
}

# 5. 建立 Docker Context
Write-Host "`n[5] 建立 Docker Context..." -ForegroundColor Yellow
try {
    if ($UseSSH) {
        # 使用 SSH 方式
        docker context create $ContextName --docker "host=ssh://${VMUser}@${VMIP}" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Context '$ContextName' 已建立（SSH 方式）" -ForegroundColor Green
        } else {
            Write-Host "  ❌ 建立 Context 失敗" -ForegroundColor Red
            exit 1
        }
    } elseif ($UseTLS) {
        # 使用 TLS 方式
        docker context create $ContextName --docker "host=tcp://${VMIP}:${TLSPort}" --docker "tls=true" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Context '$ContextName' 已建立（TLS 方式）" -ForegroundColor Green
        } else {
            Write-Host "  ❌ 建立 Context 失敗" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ❌ 請指定使用 SSH 或 TLS 方式" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ 建立 Context 失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 6. 切換到新 Context 並測試
Write-Host "`n[6] 測試遠程連接..." -ForegroundColor Yellow
try {
    docker context use $ContextName 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ 已切換到 Context '$ContextName'" -ForegroundColor Green
        
        # 測試連接
        $containers = docker ps --format "{{.Names}}" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n  VM 伺服器上的容器：" -ForegroundColor Cyan
            foreach ($container in $containers) {
                Write-Host "    - $container" -ForegroundColor White
            }
            Write-Host "  ✓ 遠程連接測試成功！" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ 無法列出容器，但 Context 已建立" -ForegroundColor Yellow
            Write-Host "  錯誤訊息: $containers" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ❌ 切換 Context 失敗" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ 測試失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. 顯示使用說明
Write-Host "`n=== 使用說明 ===" -ForegroundColor Cyan
Write-Host "`n切換到遠程 Context：" -ForegroundColor Yellow
Write-Host "  docker context use $ContextName" -ForegroundColor White
Write-Host "`n使用遠程 Context 執行命令：" -ForegroundColor Yellow
Write-Host "  docker --context $ContextName ps" -ForegroundColor White
Write-Host "  docker --context $ContextName compose up -d" -ForegroundColor White
Write-Host "`n切換回本地 Context：" -ForegroundColor Yellow
Write-Host "  docker context use default" -ForegroundColor White
Write-Host "`n查看所有 Context：" -ForegroundColor Yellow
Write-Host "  docker context ls" -ForegroundColor White
Write-Host ""

Write-Host "=== 設定完成 ===" -ForegroundColor Cyan
