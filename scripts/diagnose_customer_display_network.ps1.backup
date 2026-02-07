# 客顯設備網路診斷腳本
# 檢查客顯設備的網路連線狀態

Param(
    [string]$CustomerDisplayIP = "",
    [string]$VMIP = "192.168.50.249",
    [int]$Port = 8069
)

Write-Host "`n=== 客顯設備網路診斷 ===" -ForegroundColor Cyan
Write-Host "VM 伺服器 IP: $VMIP" -ForegroundColor White
Write-Host ""

# 1. 檢查本機網路連線
Write-Host "[1] 檢查本機網路連線..." -ForegroundColor Yellow
try {
    $pingResult = Test-Connection -ComputerName "8.8.8.8" -Count 2 -Quiet
    if ($pingResult) {
        Write-Host "  ✓ 本機可以連接到外部網路 (8.8.8.8)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ 本機無法連接到外部網路" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ 網路檢查失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. 檢查路由器連線
Write-Host "`n[2] 檢查路由器連線..." -ForegroundColor Yellow
try {
    $gateway = (Get-NetRoute -DestinationPrefix "0.0.0.0/0" | Where-Object {$_.InterfaceAlias -like "*乙太*" -or $_.InterfaceAlias -like "*Ethernet*"} | Select-Object -First 1).NextHop
    if ($gateway) {
        Write-Host "  預設閘道: $gateway" -ForegroundColor White
        $gatewayPing = Test-Connection -ComputerName $gateway -Count 2 -Quiet
        if ($gatewayPing) {
            Write-Host "  ✓ 路由器連線正常" -ForegroundColor Green
        } else {
            Write-Host "  ❌ 無法連接到路由器" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠ 無法找到預設閘道" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ 路由器檢查失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. 檢查 VM 伺服器連線
Write-Host "`n[3] 檢查 VM 伺服器連線..." -ForegroundColor Yellow
try {
    $vmPing = Test-Connection -ComputerName $VMIP -Count 2 -Quiet
    if ($vmPing) {
        Write-Host "  ✓ VM 伺服器 ($VMIP) 連線正常" -ForegroundColor Green
        
        # 檢查 Odoo 服務
        try {
            $odooUrl = "http://${VMIP}:${Port}/web"
            $response = Invoke-WebRequest -Uri $odooUrl -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✓ Odoo 服務 (Port $Port) 正常運行" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ⚠ Odoo 服務 (Port $Port) 無法訪問: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ❌ VM 伺服器 ($VMIP) 無法連線" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ VM 伺服器檢查失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. 檢查客顯設備（如果提供了 IP）
if ($CustomerDisplayIP) {
    Write-Host "`n[4] 檢查客顯設備 ($CustomerDisplayIP)..." -ForegroundColor Yellow
    try {
        $displayPing = Test-Connection -ComputerName $CustomerDisplayIP -Count 2 -Quiet
        if ($displayPing) {
            Write-Host "  ✓ 客顯設備連線正常" -ForegroundColor Green
            
            # 檢查客顯設備的網路設定
            Write-Host "`n  檢查客顯設備網路設定..." -ForegroundColor Cyan
            try {
                # 嘗試透過 Odoo API 查詢設備資訊
                $deviceUrl = "http://${VMIP}:${Port}/api/device/query?ip_address=$CustomerDisplayIP"
                $deviceInfo = Invoke-RestMethod -Uri $deviceUrl -Method GET -TimeoutSec 5 -ErrorAction Stop
                if ($deviceInfo.status -eq 'success') {
                    Write-Host "    設備名稱: $($deviceInfo.device.name)" -ForegroundColor White
                    Write-Host "    設備類型: $($deviceInfo.device.device_type)" -ForegroundColor White
                    Write-Host "    狀態: $($deviceInfo.device.status)" -ForegroundColor White
                    Write-Host "    最後連線: $($deviceInfo.device.last_seen)" -ForegroundColor White
                }
            } catch {
                Write-Host "    ⚠ 無法透過 API 查詢設備資訊: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ❌ 客顯設備無法連線" -ForegroundColor Red
            Write-Host "`n  可能原因：" -ForegroundColor Yellow
            Write-Host "    1. 設備未開機或未連接到網路" -ForegroundColor White
            Write-Host "    2. IP 地址不正確" -ForegroundColor White
            Write-Host "    3. 設備與本機不在同一網段" -ForegroundColor White
            Write-Host "    4. 防火牆阻擋連線" -ForegroundColor White
        }
    } catch {
        Write-Host "  ❌ 客顯設備檢查失敗: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "`n[4] 檢查已註冊的客顯設備..." -ForegroundColor Yellow
    Write-Host "  💡 提示：使用 -CustomerDisplayIP 參數指定客顯設備 IP 以進行詳細檢查" -ForegroundColor Cyan
}

# 5. 檢查 DNS 設定
Write-Host "`n[5] 檢查 DNS 設定..." -ForegroundColor Yellow
try {
    $dnsServers = (Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*乙太*" -or $_.InterfaceAlias -like "*Ethernet*"} | Select-Object -First 1).ServerAddresses
    if ($dnsServers) {
        Write-Host "  DNS 伺服器: $($dnsServers -join ', ')" -ForegroundColor White
        
        # 測試 DNS 解析
        try {
            $dnsTest = Resolve-DnsName -Name "google.com" -ErrorAction Stop
            if ($dnsTest) {
                Write-Host "  ✓ DNS 解析正常 (google.com)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  ❌ DNS 解析失敗" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠ 無法找到 DNS 設定" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ DNS 檢查失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. 檢查網路介面狀態
Write-Host "`n[6] 檢查網路介面狀態..." -ForegroundColor Yellow
try {
    $interfaces = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}
    foreach ($iface in $interfaces) {
        $ipConfig = Get-NetIPAddress -InterfaceIndex $iface.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
        if ($ipConfig) {
            Write-Host "  $($iface.Name): $($ipConfig.IPAddress) (狀態: $($iface.Status))" -ForegroundColor White
        }
    }
} catch {
    Write-Host "  ❌ 網路介面檢查失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. 提供修復建議
Write-Host "`n=== 修復建議 ===" -ForegroundColor Cyan
Write-Host "如果客顯設備無法上網，請嘗試以下步驟：" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 檢查客顯設備的 Wi-Fi 連線：" -ForegroundColor White
Write-Host "   - 確認設備已連接到正確的 Wi-Fi 網路 (SSID: coova.org 或對應的網路)" -ForegroundColor Gray
Write-Host "   - 檢查 Wi-Fi 密碼是否正確" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 檢查客顯設備的 IP 設定：" -ForegroundColor White
Write-Host "   - 確認設備 IP 在 192.168.50.x 網段" -ForegroundColor Gray
Write-Host "   - 確認子網路遮罩為 255.255.255.0" -ForegroundColor Gray
Write-Host "   - 確認預設閘道為 192.168.50.1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 檢查 DNS 設定：" -ForegroundColor White
Write-Host "   - 確認 DNS 伺服器為 192.168.50.1 或 8.8.8.8" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 檢查路由器設定：" -ForegroundColor White
Write-Host "   - 確認路由器未對客顯設備進行網路限制" -ForegroundColor Gray
Write-Host "   - 檢查路由器是否啟用了 MAC 地址過濾" -ForegroundColor Gray
Write-Host ""
Write-Host "5. 重新註冊客顯設備：" -ForegroundColor White
Write-Host "   .\scripts\enroll_chrome_os_customer_display.py" -ForegroundColor Gray
Write-Host ""

Write-Host "=== 診斷完成 ===" -ForegroundColor Cyan
