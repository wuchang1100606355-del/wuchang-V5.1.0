#!/usr/bin/env powershell
<#
.SYNOPSIS
    外網IP連線測試工具 - 測試特定外網IP的連入可行性
    Test External IP Connection - Verify if external IP can connect to services
#>

param(
    [string]$ExternalIP = "92.18.50.249",
    [ValidateSet("ping","ports","all","firewall","status")]
    [string]$Action = "all"
)

# 顏色配置
$colors = @{
    success = "Green"
    warning = "Yellow"
    error = "Red"
    info = "Cyan"
    header = "Magenta"
}

function Log-Header {
    param([string]$msg)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -f $colors.header
    Write-Host "║ $($msg.PadRight(58)) ║" -f $colors.header
    Write-Host "╚════════════════════════════════════════════════════════════╝" -f $colors.header
    Write-Host ""
}

function Log-Success {
    param([string]$msg)
    Write-Host "✅ $msg" -f $colors.success
}

function Log-Warning {
    param([string]$msg)
    Write-Host "⚠️  $msg" -f $colors.warning
}

function Log-Error {
    param([string]$msg)
    Write-Host "❌ $msg" -f $colors.error
}

function Log-Info {
    param([string]$msg)
    Write-Host "ℹ️  $msg" -f $colors.info
}

# 服務端口配置
$services = @(
    @{ name = "Odoo"; port = 8069; type = "HTTP" }
    @{ name = "AI"; port = 8080; type = "HTTP" }
    @{ name = "Uptime Kuma"; port = 3001; type = "HTTP" }
    @{ name = "CloudFlare HTTPS"; port = 443; type = "HTTPS" }
    @{ name = "HTTP"; port = 80; type = "HTTP" }
    @{ name = "PostgreSQL"; port = 5432; type = "TCP" }
)

# =====================================================================
# 測試 1: Ping 測試
# =====================================================================
function Test-ExternalIPPing {
    Log-Header "測試 1: 外網IP Ping可達性"
    
    Log-Info "測試目標IP: $ExternalIP"
    Write-Host ""
    
    try {
        # Windows ping test
        $result = ping -n 1 -w 2000 $ExternalIP 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Log-Success "外網IP可達 (Ping成功)"
            Write-Host "  結果: $($result | Select-Object -Last 1)" -f $colors.success
        } else {
            Log-Warning "外網IP不可達 (Ping失敗)"
            Log-Info "提示: 某些防火牆可能禁用ICMP，但仍可能允許端口連接"
        }
    } catch {
        Log-Error "Ping測試異常: $_"
    }
}

# =====================================================================
# 測試 2: 端口連接測試
# =====================================================================
function Test-ExternalIPPorts {
    Log-Header "測試 2: 外網IP埤連入測試"
    
    Log-Info "掃描目標IP: $ExternalIP"
    Log-Info "檢測服務埤位: $($services.Count)個"
    Write-Host ""
    
    $reachable = 0
    $unreachable = 0
    
    foreach ($svc in $services) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $tcp.ConnectAsync($ExternalIP, $svc.port).Wait(3000) | Out-Null
            
            if ($tcp.Connected) {
                Log-Success "$($svc.name) ($($ExternalIP):$($svc.port)) ✓ 可連接"
                $reachable++
                $tcp.Close()
            } else {
                Log-Warning "$($svc.name) ($($ExternalIP):$($svc.port)) ✗ 無回應"
                $unreachable++
            }
        } catch {
            Log-Warning "$($svc.name) ($($ExternalIP):$($svc.port)) ✗ 連接失敗"
            $unreachable++
        }
    }
    
    Write-Host ""
    Write-Host "📊 掃描結果摘要:" -f $colors.info
    Write-Host "   可連接: $reachable 個" -f $colors.success
    Write-Host "   無法連接: $unreachable 個" -f $colors.warning
    Write-Host ""
    
    return @{ reachable = $reachable; unreachable = $unreachable }
}

# =====================================================================
# 測試 3: 防火牆規則檢查
# =====================================================================
function Test-FirewallRules {
    Log-Header "測試 3: 防火牆規則檢查"
    
    Log-Info "檢查針對 $ExternalIP 的防火牆規則"
    Write-Host ""
    
    try {
        # 獲取允許該IP的規則
        $rules = Get-NetFirewallRule -Direction Inbound -Action Allow -ErrorAction SilentlyContinue | 
                 Where-Object { $_.DisplayName -match "Allow.*$ExternalIP" }
        
        if ($rules) {
            Log-Success "發現 $($rules.Count) 條允許該IP的防火牆規則"
            Write-Host ""
            foreach ($rule in $rules) {
                Write-Host "  • $($rule.DisplayName)" -f $colors.success
                $addr = Get-NetFirewallAddressFilter -AssociatedNetFirewallRule $rule
                if ($addr) {
                    Write-Host "    埤位: $($addr.RemoteAddress)" -f $colors.info
                }
            }
            Write-Host ""
        } else {
            Log-Warning "未發現針對該IP的防火牆規則"
            Log-Info "建議執行: .\device_identity_auth.ps1 -Action auth"
        }
        
        # 檢查本機監聽狀態
        Write-Host ""
        Log-Info "本機埤監聽狀態:" -f $colors.info
        Write-Host ""
        
        $netstat = netstat -ano 2>$null | Select-String "LISTENING" | ForEach-Object {
            $parts = $_.ToString().Split() | Where-Object { $_ }
            @{
                protocol = $parts[0]
                address = $parts[1]
                state = $parts[3]
            }
        }
        
        foreach ($svc in $services) {
            $listening = $netstat | Where-Object { $_.address -match ":$($svc.port)" }
            if ($listening) {
                Log-Success "$($svc.name) (埤 $($svc.port)): 監聽中 ✓"
            } else {
                Log-Warning "$($svc.name) (埤 $($svc.port)): 未監聽"
            }
        }
        
        Write-Host ""
    } catch {
        Log-Error "防火牆檢查異常: $_"
    }
}

# =====================================================================
# 測試 4: 本機連線狀態
# =====================================================================
function Test-LocalConnectivity {
    Log-Header "測試 4: 本機服務連線測試"
    
    Log-Info "驗證本機服務是否正常運行"
    Write-Host ""
    
    $online = 0
    $offline = 0
    
    foreach ($svc in $services) {
        try {
            if ($svc.type -eq "TCP") {
                $tcp = New-Object System.Net.Sockets.TcpClient
                $tcp.ConnectAsync("localhost", $svc.port).Wait(2000) | Out-Null
                if ($tcp.Connected) {
                    Log-Success "$($svc.name) (localhost:$($svc.port)): 運行中 ✓"
                    $online++
                    $tcp.Close()
                } else {
                    Log-Warning "$($svc.name) (localhost:$($svc.port)): 無回應"
                    $offline++
                }
            } else {
                $result = Invoke-WebRequest -Uri "http://localhost:$($svc.port)" -TimeoutSec 3 -UseBasicParsing -Method Head -ErrorAction SilentlyContinue
                if ($result.StatusCode -eq 200) {
                    Log-Success "$($svc.name) (localhost:$($svc.port)): 運行中 ✓"
                    $online++
                } else {
                    Log-Warning "$($svc.name) (localhost:$($svc.port)): 異常狀態 ($($result.StatusCode))"
                    $offline++
                }
            }
        } catch {
            Log-Warning "$($svc.name) (localhost:$($svc.port)): 離線或無法連接"
            $offline++
        }
    }
    
    Write-Host ""
    Write-Host "📊 本機服務狀態摘要:" -f $colors.info
    Write-Host "   運行中: $online 個" -f $colors.success
    Write-Host "   離線: $offline 個" -f $colors.warning
    Write-Host ""
    
    return @{ online = $online; offline = $offline }
}

# =====================================================================
# 測試 5: 綜合診斷報告
# =====================================================================
function Generate-DiagnosticReport {
    param($portResults, $localResults)
    
    Log-Header "綜合診斷報告 - Diagnostic Report"
    
    Write-Host "外網IP: $ExternalIP" -f $colors.info
    Write-Host "測試時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -f $colors.info
    Write-Host ""
    
    Write-Host "🎯 診斷結果:" -f $colors.header
    Write-Host ""
    
    # 本機狀態
    if ($localResults.online -eq $services.Count) {
        Log-Success "✓ 本機所有服務正常運行"
    } elseif ($localResults.online -gt 0) {
        Log-Warning "⚠ 部分本機服務離線 ($($localResults.offline)/$($services.Count))"
    } else {
        Log-Error "✗ 本機所有服務離線，無法對外提供服務"
    }
    
    Write-Host ""
    
    # 外網連接狀態
    if ($portResults.reachable -eq $services.Count) {
        Log-Success "✓ 外網IP可完全連接本機所有服務"
        Log-Info "   → $ExternalIP 可正常使用 Wuchang 系統"
    } elseif ($portResults.reachable -gt 0) {
        Log-Warning "⚠ 外網IP部分可連接 ($($portResults.reachable)/$($services.Count))"
        Log-Info "   → 建議檢查防火牆規則或網絡配置"
    } else {
        Log-Error "✗ 外網IP無法連接任何服務"
        Log-Info "   → 需要配置防火牆規則"
        Log-Info "   → 執行: .\device_identity_auth.ps1 -Action auth"
    }
    
    Write-Host ""
    Write-Host "📋 後續建議:" -f $colors.header
    Write-Host ""
    
    if ($portResults.reachable -lt $services.Count) {
        Write-Host "1️⃣  配置防火牆允許規則:" -f $colors.warning
        Write-Host "   .\device_identity_auth.ps1 -Action auth" -f $colors.info
        Write-Host ""
    }
    
    Write-Host "2️⃣  驗證IP白名單配置:" -f $colors.warning
    Write-Host "   .\verify_ip_allowlist.ps1 -Action all" -f $colors.info
    Write-Host ""
    
    Write-Host "3️⃣  檢查防火牆狀態:" -f $colors.warning
    Write-Host "   netsh advfirewall show allprofiles" -f $colors.info
    Write-Host ""
    
    Write-Host "4️⃣  訪問UI服務:" -f $colors.warning
    Write-Host "   .\ui_access.ps1 -Service all" -f $colors.info
    Write-Host ""
}

# =====================================================================
# 主程式
# =====================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -f Cyan
Write-Host "║        外網IP連線測試工具 - External IP Connection Test   ║" -f Cyan
Write-Host "║        目標: $ExternalIP" -f Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -f Cyan

switch ($Action) {
    "ping" {
        Test-ExternalIPPing
    }
    "ports" {
        $portResults = Test-ExternalIPPorts
    }
    "firewall" {
        Test-FirewallRules
    }
    "status" {
        $localResults = Test-LocalConnectivity
    }
    "all" {
        Test-ExternalIPPing
        Write-Host ""
        $portResults = Test-ExternalIPPorts
        Write-Host ""
        $localResults = Test-LocalConnectivity
        Write-Host ""
        Test-FirewallRules
        Write-Host ""
        Generate-DiagnosticReport $portResults $localResults
    }
}

Write-Host ""
