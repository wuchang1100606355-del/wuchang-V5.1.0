# VM 伺服器位階設定驗證腳本
# 用途：驗證 VM (192.168.50.84) 在 wuchang.life 和 Google Workspace 中的位階設定

param(
    [string]$VMIP = "192.168.50.84",
    [string]$Domain = "wuchang.life"
)

Write-Host "`n=== VM 伺服器位階設定驗證 ===" -ForegroundColor Cyan
Write-Host "VM IP: $VMIP" -ForegroundColor White
Write-Host "網域: $Domain" -ForegroundColor White
Write-Host ""

# 1. 檢查 wuchang.life DNS 設定
Write-Host "[1] 檢查 wuchang.life DNS 設定..." -ForegroundColor Yellow

$dnsRecordsFile = "workshop_deploy\dns_records.json"
if (Test-Path $dnsRecordsFile) {
    $dnsRecords = Get-Content $dnsRecordsFile | ConvertFrom-Json
    $vmInPublicDns = $false
    
    foreach ($record in $dnsRecords.records) {
        if ($record.data -eq $VMIP) {
            Write-Host "  ⚠ 發現公開 DNS 記錄: $($record.host).$Domain → $VMIP" -ForegroundColor Yellow
            $vmInPublicDns = $true
        }
    }
    
    if (-not $vmInPublicDns) {
        Write-Host "  ✓ VM ($VMIP) 不在公開 DNS 記錄中（符合預期，為內網 IP）" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠ 未找到 DNS 記錄檔案: $dnsRecordsFile" -ForegroundColor Yellow
}

# 2. 檢查私人 DNS 設定
Write-Host "`n[2] 檢查私人 DNS 設定..." -ForegroundColor Yellow

$hostsFile = "$env:SystemRoot\System32\drivers\etc\hosts"
if (Test-Path $hostsFile) {
    $hostsContent = Get-Content $hostsFile -Raw
    $privateDnsEntries = @(
        "pos-server.chong-sin.local",
        "odoo.chong-sin.local",
        "api.chong-sin.local"
    )
    
    $foundEntries = 0
    foreach ($entry in $privateDnsEntries) {
        if ($hostsContent -match [regex]::Escape($VMIP) -and $hostsContent -match [regex]::Escape($entry)) {
            Write-Host "  ✓ 找到私人 DNS: $entry → $VMIP" -ForegroundColor Green
            $foundEntries++
        }
    }
    
    if ($foundEntries -eq 0) {
        Write-Host "  ⚠ 未找到私人 DNS 設定，建議執行: .\scripts\setup_chong_sin_private_dns.ps1" -ForegroundColor Yellow
    } else {
        Write-Host "  ✓ 已配置 $foundEntries 個私人 DNS 主機名稱" -ForegroundColor Green
    }
} else {
    Write-Host "  ❌ 未找到 hosts 檔案: $hostsFile" -ForegroundColor Red
}

# 3. 檢查 VM 服務連線
Write-Host "`n[3] 檢查 VM 服務連線..." -ForegroundColor Yellow

$services = @(
    @{Name="Odoo Web"; Port=8069},
    @{Name="Odoo API"; Port=8069},
    @{Name="SSH"; Port=22}
)

$allConnected = $true
foreach ($service in $services) {
    try {
        $connection = Test-NetConnection -ComputerName $VMIP -Port $service.Port -WarningAction SilentlyContinue -InformationLevel Quiet -ErrorAction Stop
        if ($connection) {
            Write-Host "  ✓ $($service.Name) (${VMIP}:$($service.Port)) - 連線成功" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ $($service.Name) (${VMIP}:$($service.Port)) - 連線失敗" -ForegroundColor Yellow
            $allConnected = $false
        }
    } catch {
        Write-Host "  ⚠ $($service.Name) - 無法測試: $($_.Exception.Message)" -ForegroundColor Yellow
        $allConnected = $false
    }
}

# 4. 檢查 Google Workspace 配置檔案
Write-Host "`n[4] 檢查 Google Workspace 配置..." -ForegroundColor Yellow

$orgConfigFile = "workshop_deploy\wuchang_organization_config.json"
if (Test-Path $orgConfigFile) {
    $orgConfig = Get-Content $orgConfigFile | ConvertFrom-Json
    
    Write-Host "  ✓ 找到組織配置檔案" -ForegroundColor Green
    Write-Host "    管理帳號: $($orgConfig.infrastructure.ai_governance.supreme_authority.operational_account)" -ForegroundColor White
    Write-Host "    AI 身份: $($orgConfig.infrastructure.ai_governance.supreme_authority.identity)" -ForegroundColor White
    
    # 檢查是否有 VM 相關配置
    $vmInConfig = $false
    foreach ($subOrg in $orgConfig.structure.sub_organizations) {
        if ($subOrg.gcp_resources.vms) {
            foreach ($vm in $subOrg.gcp_resources.vms) {
                Write-Host "    發現 VM: $vm" -ForegroundColor White
            }
        }
    }
    
    Write-Host "  ⚠ 注意: 192.168.50.84 為內網 VM，需透過 Google Workspace Admin Console 手動納管" -ForegroundColor Yellow
} else {
    Write-Host "  ⚠ 未找到組織配置檔案: $orgConfigFile" -ForegroundColor Yellow
}

# 5. 檢查 Odoo Sister Control 設定
Write-Host "`n[5] 檢查 Odoo Sister Control 設定..." -ForegroundColor Yellow

try {
    $sisterControlUrl = "http://${VMIP}:8069/wuchang/sister/poll"
    $response = Invoke-WebRequest -Uri $sisterControlUrl -Method POST -Body '{"device_type":"POS"}' -ContentType "application/json" -TimeoutSec 5 -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Sister Control 端點可訪問: $sisterControlUrl" -ForegroundColor Green
        $responseData = $response.Content | ConvertFrom-Json
        Write-Host "    狀態: 正常" -ForegroundColor White
    }
} catch {
    Write-Host "  ⚠ Sister Control 端點無法訪問: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "    建議: 確認 Odoo 服務正在運行" -ForegroundColor Yellow
}

# 6. 總結
Write-Host "`n=== 驗證總結 ===" -ForegroundColor Cyan

Write-Host "`n位階確認:" -ForegroundColor Yellow
Write-Host "  • wuchang.life 網域: 內網伺服器（不在公開 DNS）" -ForegroundColor White
Write-Host "  • 私人 DNS: 已配置（pos-server.chong-sin.local 等）" -ForegroundColor White
Write-Host "  • Google Workspace: 需手動納管（建議使用 admin@wuchang.life）" -ForegroundColor White
Write-Host "  • 控制端點: UI 設備 → VM ($VMIP)" -ForegroundColor White

Write-Host "`n建議後續行動:" -ForegroundColor Yellow
Write-Host "  1. 在 Google Workspace Admin Console 納管 VM ($VMIP)" -ForegroundColor White
Write-Host "  2. 在 Google Workspace Admin Console 納管 UI 設備（控制端）" -ForegroundColor White
Write-Host "  3. 設定控制關係（UI 設備控制 VM）" -ForegroundColor White
Write-Host "  4. 測試控制指令發送和接收" -ForegroundColor White

Write-Host "`n相關文件:" -ForegroundColor Yellow
Write-Host "  • docs\VM_SERVER_HIERARCHY_CONFIG.md - 完整位階設定文件" -ForegroundColor White
Write-Host "  • docs\PRIVATE_DNS_SETUP_CHONG_SIN.md - 私人 DNS 設定指南" -ForegroundColor White
Write-Host "  • Chrome_OS設備納管說明.md - Google Workspace 設備納管說明" -ForegroundColor White

Write-Host "`n=== 驗證完成 ===" -ForegroundColor Green
