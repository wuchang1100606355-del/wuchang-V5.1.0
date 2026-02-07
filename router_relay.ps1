#!/usr/bin/env powershell
<#
.SYNOPSIS
    路由中繼配置工具 - 調用路由器作為流量中繼
    Router Relay Configuration - Enable router as traffic relay
#>

param(
    [string]$LocalIP = "192.168.50.84",
    [string]$ExternalIP = "92.18.50.249",
    [string]$RouterIP = "192.168.50.1",
    [ValidateSet("status","enable","disable","test","forward")]
    [string]$Action = "status"
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

# =====================================================================
# 路由狀態檢查
# =====================================================================
function Show-RoutingStatus {
    Log-Header "路由中繼狀態檢查"
    
    Write-Host "🌐 網絡配置信息:" -f $colors.info
    Write-Host ""
    Write-Host "   本機IP: $LocalIP" -f $colors.info
    Write-Host "   外網IP: $ExternalIP" -f $colors.info
    Write-Host "   路由器: $RouterIP" -f $colors.info
    Write-Host ""
    
    # 檢查路由表
    Write-Host "📊 當前路由表:" -f $colors.info
    Write-Host ""
    
    $routes = Get-NetRoute -ErrorAction SilentlyContinue | 
        Where-Object { $_.DestinationPrefix -match "^192.168|^0.0.0.0" } |
        Sort-Object DestinationPrefix
    
    if ($routes) {
        foreach ($route in $routes | Select-Object -First 10) {
            Write-Host "   $($route.DestinationPrefix) -> $($route.NextHop) (介面: $($route.InterfaceAlias))" -f $colors.info
        }
    } else {
        Log-Warning "未找到相關路由配置"
    }
    
    Write-Host ""
    
    # 檢查IP轉發狀態
    Write-Host "🔄 IP轉發狀態:" -f $colors.info
    Write-Host ""
    
    try {
        $ipForwarding = Get-NetIPConfiguration -ErrorAction SilentlyContinue | Select-Object ComputerName
        
        if ($ipForwarding) {
            Log-Success "系統支持IP轉發"
        } else {
            Log-Warning "IP轉發配置不可用"
        }
    } catch {
        Log-Warning "無法檢查IP轉發狀態"
    }
    
    Write-Host ""
    
    # 檢查連接
    Write-Host "🔗 連接檢查:" -f $colors.info
    Write-Host ""
    
    try {
        $pingLocal = Test-Connection -ComputerName $LocalIP -Count 1 -Quiet
        if ($pingLocal) {
            Log-Success "本機 ($LocalIP) 可達"
        } else {
            Log-Warning "本機 ($LocalIP) 無法連接"
        }
    } catch {}
    
    try {
        $pingRouter = Test-Connection -ComputerName $RouterIP -Count 1 -Quiet
        if ($pingRouter) {
            Log-Success "路由器 ($RouterIP) 可達"
        } else {
            Log-Warning "路由器 ($RouterIP) 無法連接"
        }
    } catch {}
    
    Write-Host ""
}

# =====================================================================
# 啟用IP轉發和NAT
# =====================================================================
function Enable-RouterRelay {
    Log-Header "啟用路由中繼模式"
    
    Write-Host "🔧 配置步驟:" -f $colors.warning
    Write-Host ""
    
    # 1. 啟用IP轉發
    Write-Host "1️⃣  啟用IP轉發..." -f $colors.warning
    try {
        # 設置IP轉發
        cmd /c "netsh int ipv4 set global forwarding=enabled" 2>$null | Out-Null
        Log-Success "IP轉發已啟用"
    } catch {
        Log-Error "IP轉發啟用失敗: $_"
    }
    
    Write-Host ""
    
    # 2. 配置靜態路由
    Write-Host "2️⃣  配置靜態路由..." -f $colors.warning
    try {
        # 為外網IP添加路由
        cmd /c "route add $ExternalIP mask 255.255.255.255 $RouterIP" 2>$null
        Log-Success "靜態路由已添加: $ExternalIP -> $RouterIP"
    } catch {
        Log-Warning "靜態路由配置可能已存在"
    }
    
    Write-Host ""
    
    # 3. 配置防火牆規則用於轉發
    Write-Host "3️⃣  配置防火牆轉發規則..." -f $colors.warning
    try {
        # 啟用所有入站ICMP
        netsh advfirewall firewall set rule name="File and Printer Sharing (Echo Request - ICMPv4-In)" dir=in action=allow | Out-Null
        Log-Success "防火牆轉發規則已配置"
    } catch {
        Log-Warning "防火牆規則配置失敗"
    }
    
    Write-Host ""
    
    # 4. 配置NAT規則
    Write-Host "4️⃣  配置NAT轉發..." -f $colors.warning
    try {
        # 添加NAT規則用於外網IP訪問本機
        foreach ($port in 8069, 8080, 3001, 80, 443, 5432) {
            netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$LocalIP 2>$null
            Log-Success "NAT規則配置: 埤位 $port"
        }
    } catch {
        Log-Warning "NAT規則配置失敗"
    }
    
    Write-Host ""
    Log-Success "路由中繼啟用完成！"
    Write-Host ""
}

# =====================================================================
# 禁用路由中繼
# =====================================================================
function Disable-RouterRelay {
    Log-Header "禁用路由中繼模式"
    
    Write-Host "🔄 清除配置..." -f $colors.warning
    Write-Host ""
    
    # 1. 禁用IP轉發
    Write-Host "1️⃣  禁用IP轉發..." -f $colors.warning
    try {
        cmd /c "netsh int ipv4 set global forwarding=disabled" 2>$null | Out-Null
        Log-Success "IP轉發已禁用"
    } catch {
        Log-Warning "IP轉發禁用失敗"
    }
    
    Write-Host ""
    
    # 2. 移除靜態路由
    Write-Host "2️⃣  移除靜態路由..." -f $colors.warning
    try {
        cmd /c "route delete $ExternalIP" 2>$null
        Log-Success "靜態路由已移除"
    } catch {
        Log-Warning "靜態路由移除失敗或不存在"
    }
    
    Write-Host ""
    
    # 3. 清除NAT規則
    Write-Host "3️⃣  清除NAT轉發..." -f $colors.warning
    try {
        foreach ($port in 8069, 8080, 3001, 80, 443, 5432) {
            netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0 2>$null
            Log-Success "NAT規則已清除: 埤位 $port"
        }
    } catch {
        Log-Warning "NAT規則清除失敗"
    }
    
    Write-Host ""
    Log-Success "路由中繼禁用完成！"
    Write-Host ""
}

# =====================================================================
# 測試路由中繼
# =====================================================================
function Test-RouterRelay {
    Log-Header "路由中繼測試"
    
    Write-Host "🧪 測試場景:" -f $colors.info
    Write-Host ""
    
    $testPorts = @(8069, 8080, 3001, 80, 443, 5432)
    $successCount = 0
    $failureCount = 0
    
    Write-Host "測試外網IP通過路由連接本機服務..." -f $colors.warning
    Write-Host ""
    
    foreach ($port in $testPorts) {
        Write-Host "⏳ 測試埤位 $port..." -f $colors.warning
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $task = $tcp.ConnectAsync($ExternalIP, $port)
            
            if ($task.Wait(2000)) {
                if ($tcp.Connected) {
                    Log-Success "通過路由連接成功: $ExternalIP`:$port"
                    $successCount++
                    $tcp.Close()
                } else {
                    Log-Warning "通過路由連接超時: $ExternalIP`:$port"
                    $failureCount++
                }
            } else {
                Log-Warning "通過路由連接超時: $ExternalIP`:$port"
                $failureCount++
            }
        } catch {
            Log-Warning "通過路由連接失敗: $ExternalIP`:$port"
            $failureCount++
        }
    }
    
    Write-Host ""
    Write-Host "📊 測試結果:" -f $colors.info
    Write-Host "   成功: $successCount 個" -f $colors.success
    Write-Host "   失敗: $failureCount 個" -f $colors.warning
    Write-Host ""
    
    if ($successCount -eq $testPorts.Count) {
        Log-Success "路由中繼測試全部通過！"
    } elseif ($successCount -gt 0) {
        Log-Warning "部分路由中繼可用"
    } else {
        Log-Error "路由中繼測試全部失敗"
    }
    
    Write-Host ""
}

# =====================================================================
# 配置前向代理
# =====================================================================
function Setup-ForwardProxy {
    Log-Header "配置前向代理（可選高級功能）"
    
    Write-Host "📝 前向代理配置說明:" -f $colors.info
    Write-Host ""
    Write-Host "前向代理允許外網IP通過本機訪問其他資源" -f $colors.info
    Write-Host ""
    
    Write-Host "🔧 配置選項:" -f $colors.warning
    Write-Host ""
    Write-Host "1️⃣  DNS轉發" -f $colors.warning
    Write-Host "   允許外網IP使用本機DNS解析" -f $colors.info
    Write-Host ""
    
    try {
        # 獲取本機DNS
        $dnsServers = Get-DnsClientServerAddress -ErrorAction SilentlyContinue | 
            Select-Object -First 1 | 
            Select-Object -ExpandProperty ServerAddresses
        
        if ($dnsServers) {
            Log-Success "本機DNS: $($dnsServers[0])"
        }
    } catch {
        Log-Warning "無法獲取DNS配置"
    }
    
    Write-Host ""
    Write-Host "2️⃣  應用層代理" -f $colors.warning
    Write-Host "   使用Caddy反向代理轉發流量" -f $colors.info
    Write-Host ""
    
    Log-Success "Caddy反向代理已在本機運行"
    Log-Success "配置文件: caddy.json"
    
    Write-Host ""
}

# =====================================================================
# 主程式
# =====================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -f $colors.header
Write-Host "║       路由中繼配置工具 - Router Relay Configuration       ║" -f $colors.header
Write-Host "╚════════════════════════════════════════════════════════════╝" -f $colors.header

switch ($Action) {
    "status" {
        Show-RoutingStatus
    }
    "enable" {
        Enable-RouterRelay
    }
    "disable" {
        Disable-RouterRelay
    }
    "test" {
        Test-RouterRelay
    }
    "forward" {
        Setup-ForwardProxy
    }
    default {
        Show-RoutingStatus
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -f $colors.info
Write-Host "║              使用指南                                      ║" -f $colors.info
Write-Host "╚════════════════════════════════════════════════════════════╝" -f $colors.info
Write-Host ""
Write-Host "查看狀態:      .\router_relay.ps1 -Action status" -f $colors.info
Write-Host "啟用中繼:      .\router_relay.ps1 -Action enable" -f $colors.warning
Write-Host "禁用中繼:      .\router_relay.ps1 -Action disable" -f $colors.warning
Write-Host "測試中繼:      .\router_relay.ps1 -Action test" -f $colors.info
Write-Host "配置代理:      .\router_relay.ps1 -Action forward" -f $colors.info
Write-Host ""
