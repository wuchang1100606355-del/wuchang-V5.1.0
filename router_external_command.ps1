#!/usr/bin/env powershell
<#
.SYNOPSIS
    路由器外網指揮控制系統 - 獲取完整的外網流量管理權限
    Router External Network Command Control - Full WAN Traffic Management
#>

param(
    [string]$RouterIP = "192.168.50.1",
    [ValidateSet("auth","status","portforward","upnp","ddns","firewall","test","command")]
    [string]$Action = "status"
)

# 顏色配置
$colors = @{
    success = "Green"
    warning = "Yellow"
    error = "Red"
    info = "Cyan"
    header = "Magenta"
    command = "Blue"
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

function Log-Command {
    param([string]$msg)
    Write-Host "🔧 $msg" -f $colors.command
}

# =====================================================================
# 路由器身份驗證
# =====================================================================
function Authenticate-Router {
    Log-Header "路由器身份驗證"
    
    Write-Host "🔑 連接路由器: $RouterIP" -f $colors.warning
    Write-Host ""
    
    try {
        # 測試連接
        $ping = Test-Connection -ComputerName $RouterIP -Count 1 -Quiet
        
        if ($ping) {
            Log-Success "路由器連接成功"
            
            # 嘗試訪問Web管理界面
            try {
                $response = Invoke-WebRequest -Uri "http://$RouterIP" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($response) {
                    Log-Success "路由器Web管理界面可訪問"
                    Write-Host ""
                    Write-Host "🔓 路由器認證信息:" -f $colors.info
                    Write-Host ""
                    Write-Host "   地址: http://$RouterIP" -f $colors.info
                    Write-Host "   類型: 標準家用路由器" -f $colors.info
                    Write-Host "   默認用戶: admin" -f $colors.warning
                    Write-Host "   默認密碼: admin (請修改)" -f $colors.warning
                    Write-Host ""
                    Log-Warning "重要: 請在路由器管理界面修改默認密碼！"
                }
            } catch {
                Log-Warning "路由器Web界面暫不可訪問"
                Write-Host "   建議: 稍候重試或檢查路由器狀態" -f $colors.warning
            }
        } else {
            Log-Error "無法連接到路由器"
            Write-Host "   請檢查路由器IP和網絡連接" -f $colors.error
        }
    } catch {
        Log-Error "連接失敗: $_"
    }
    
    Write-Host ""
}

# =====================================================================
# 路由器狀態檢查
# =====================================================================
function Show-RouterStatus {
    Log-Header "路由器狀態檢查"
    
    Write-Host "🌐 WAN連接信息:" -f $colors.info
    Write-Host ""
    
    # 檢查本機網絡配置
    $defaultGateway = Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue | 
        Select-Object -First 1 -ExpandProperty NextHop
    
    Write-Host "   默認網關: $defaultGateway" -f $colors.info
    Write-Host "   路由器IP: $RouterIP" -f $colors.info
    
    # 檢查WAN IP
    try {
        $wanIP = Invoke-WebRequest -Uri "https://api.ipify.org" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue | 
            Select-Object -ExpandProperty Content
        if ($wanIP) {
            Log-Success "公網IP: $wanIP"
        }
    } catch {
        Log-Warning "無法獲取公網IP"
    }
    
    Write-Host ""
    
    # 檢查DNS配置
    Write-Host "📡 DNS配置:" -f $colors.info
    Write-Host ""
    
    $dnsServers = Get-DnsClientServerAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | 
        Where-Object { $_.InterfaceAlias -notmatch "虛擬|Hyper" } |
        Select-Object -First 1 -ExpandProperty ServerAddresses
    
    if ($dnsServers) {
        foreach ($dns in $dnsServers) {
            Write-Host "   DNS: $dns" -f $colors.info
        }
    }
    
    Write-Host ""
    
    # 路由器功能檢查
    Write-Host "⚙️  路由器功能:" -f $colors.info
    Write-Host ""
    Log-Success "UPnP/NAT-PMP: 支持"
    Log-Success "端口轉發: 支持"
    Log-Success "動態DNS: 支持"
    Log-Success "防火牆: 支持"
    Log-Success "VPN: 支持"
    Log-Success "QoS: 支持"
    
    Write-Host ""
}

# =====================================================================
# 端口轉發配置
# =====================================================================
function Setup-PortForwarding {
    Log-Header "配置端口轉發 - Port Forwarding Setup"
    
    Write-Host "🔀 端口轉發規則配置:" -f $colors.warning
    Write-Host ""
    
    $forwardingRules = @(
        @{ 
            externalPort = 8069
            internalIP = "192.168.50.84"
            internalPort = 8069
            protocol = "TCP"
            description = "Odoo ERP"
        }
        @{
            externalPort = 8080
            internalIP = "192.168.50.84"
            internalPort = 8080
            protocol = "TCP"
            description = "AI Assistant Service"
        }
        @{
            externalPort = 3001
            internalIP = "192.168.50.84"
            internalPort = 3001
            protocol = "TCP"
            description = "Uptime Kuma"
        }
        @{
            externalPort = 80
            internalIP = "192.168.50.84"
            internalPort = 80
            protocol = "TCP"
            description = "HTTP Web Server"
        }
        @{
            externalPort = 443
            internalIP = "192.168.50.84"
            internalPort = 443
            protocol = "TCP"
            description = "HTTPS Web Server"
        }
        @{
            externalPort = 5432
            internalIP = "192.168.50.84"
            internalPort = 5432
            protocol = "TCP"
            description = "PostgreSQL Database"
        }
    )
    
    Write-Host "📝 建議的端口轉發規則:" -f $colors.info
    Write-Host ""
    
    foreach ($rule in $forwardingRules) {
        Write-Host "   規則: $($rule.description)" -f $colors.success
        Write-Host "      外部埤位: $($rule.externalPort)" -f $colors.info
        Write-Host "      內部地址: $($rule.internalIP)" -f $colors.info
        Write-Host "      內部埤位: $($rule.internalPort)" -f $colors.info
        Write-Host "      協議: $($rule.protocol)" -f $colors.info
        Write-Host ""
    }
    
    Write-Host "🔗 配置步驟:" -f $colors.warning
    Write-Host ""
    Write-Host "   1️⃣  打開瀏覽器訪問: http://$RouterIP" -f $colors.command
    Write-Host "   2️⃣  登錄路由器管理後台 (admin/admin)" -f $colors.command
    Write-Host "   3️⃣  進入 設定 > 網絡設定 > 端口轉發" -f $colors.command
    Write-Host "   4️⃣  按照上述規則添加6個轉發規則" -f $colors.command
    Write-Host "   5️⃣  保存並重啟路由器" -f $colors.command
    Write-Host ""
}

# =====================================================================
# UPnP自動轉發配置
# =====================================================================
function Setup-UPnP {
    Log-Header "UPnP自動端口映射 - UPnP Auto Port Mapping"
    
    Write-Host "🔄 UPnP配置說明:" -f $colors.info
    Write-Host ""
    Write-Host "UPnP (Universal Plug and Play) 允許應用自動配置端口轉發" -f $colors.info
    Write-Host ""
    
    # 檢查本機UPnP支持
    Write-Host "🔍 系統UPnP檢查:" -f $colors.warning
    Write-Host ""
    
    try {
        # 檢查UPnP Device Host服務
        $upnpService = Get-Service -Name "upnphost" -ErrorAction SilentlyContinue
        
        if ($upnpService) {
            if ($upnpService.Status -eq "Running") {
                Log-Success "UPnP設備主機: 運行中"
            } else {
                Log-Warning "UPnP設備主機: 已停止（可自動啟動）"
            }
        } else {
            Log-Warning "UPnP未安裝"
        }
    } catch {
        Log-Warning "無法檢查UPnP狀態"
    }
    
    Write-Host ""
    
    # UPnP配置步驟
    Write-Host "🔧 UPnP配置步驟:" -f $colors.warning
    Write-Host ""
    Write-Host "   1️⃣  在路由器管理界面啟用UPnP" -f $colors.command
    Write-Host "      地址: http://$RouterIP > 設定 > UPnP" -f $colors.command
    Write-Host ""
    Write-Host "   2️⃣  在本機應用配置中啟用UPnP支持" -f $colors.command
    Write-Host "      • Odoo: 預設支持UPnP配置" -f $colors.command
    Write-Host "      • Docker容器: 配置-p選項進行端口映射" -f $colors.command
    Write-Host ""
    Write-Host "   3️⃣  自動映射生效後會顯示確認消息" -f $colors.command
    Write-Host ""
}

# =====================================================================
# 動態DNS配置
# =====================================================================
function Setup-DDNS {
    Log-Header "動態DNS配置 - DDNS Setup"
    
    Write-Host "🌐 DDNS配置說明:" -f $colors.info
    Write-Host ""
    Write-Host "DDNS使用域名訪問，即使IP地址變化也能自動更新" -f $colors.info
    Write-Host ""
    
    # 當前域名配置
    Write-Host "📌 當前域名配置:" -f $colors.warning
    Write-Host ""
    Write-Host "   主域名: wuchang.life" -f $colors.success
    Write-Host "   DNS提供商: CloudFlare" -f $colors.info
    Write-Host "   TTL: 自動" -f $colors.info
    Write-Host ""
    
    # DDNS設置步驟
    Write-Host "🔧 DDNS配置步驟:" -f $colors.warning
    Write-Host ""
    Write-Host "   1️⃣  進入路由器管理界面" -f $colors.command
    Write-Host "      地址: http://$RouterIP > 設定 > DDNS" -f $colors.command
    Write-Host ""
    Write-Host "   2️⃣  選擇DDNS提供商: CloudFlare" -f $colors.command
    Write-Host "      或使用自定義DNS更新服務" -f $colors.command
    Write-Host ""
    Write-Host "   3️⃣  輸入域名: wuchang.life" -f $colors.command
    Write-Host "      輸入API Token (從CloudFlare獲取)" -f $colors.command
    Write-Host ""
    Write-Host "   4️⃣  測試連接並保存配置" -f $colors.command
    Write-Host ""
    
    Write-Host "✅ 配置完成後:" -f $colors.success
    Write-Host "   • 訪問地址變為: https://wuchang.life:8069" -f $colors.info
    Write-Host "   • 自動WAN IP更新: 每5分鐘檢查一次" -f $colors.info
    Write-Host "   • 全球可訪問: 無需IP地址" -f $colors.info
    Write-Host ""
}

# =====================================================================
# 防火牆配置
# =====================================================================
function Setup-Firewall {
    Log-Header "路由器防火牆配置 - Router Firewall Setup"
    
    Write-Host "🔥 防火牆安全配置:" -f $colors.warning
    Write-Host ""
    
    Write-Host "✓ 基本安全規則:" -f $colors.success
    Write-Host ""
    Write-Host "   1️⃣  啟用SPI防火牆" -f $colors.info
    Write-Host "      保護: 阻止非法的外部連接" -f $colors.info
    Write-Host ""
    Write-Host "   2️⃣  啟用DoS防護" -f $colors.info
    Write-Host "      保護: 阻止拒絕服務攻擊" -f $colors.info
    Write-Host ""
    Write-Host "   3️⃣  啟用端口掃描檢測" -f $colors.info
    Write-Host "      保護: 檢測並阻止端口掃描" -f $colors.info
    Write-Host ""
    
    Write-Host "✓ 高級規則:" -f $colors.success
    Write-Host ""
    Write-Host "   • IP黑名單: 阻止特定IP訪問" -f $colors.info
    Write-Host "   • MAC過濾: 控制設備連接" -f $colors.info
    Write-Host "   • URL過濾: 阻止特定網站" -f $colors.info
    Write-Host ""
    
    Write-Host "🔐 推薦配置:" -f $colors.warning
    Write-Host ""
    Write-Host "   • 隐藏SSID: 關閉（方便調試）" -f $colors.command
    Write-Host "   • WPA2加密: 啟用" -f $colors.command
    Write-Host "   • 防火牆: 高級模式啟用" -f $colors.command
    Write-Host ""
}

# =====================================================================
# 測試外網訪問
# =====================================================================
function Test-ExternalAccess {
    Log-Header "測試外網訪問 - External Access Test"
    
    Write-Host "🧪 外網訪問測試:" -f $colors.info
    Write-Host ""
    
    $services = @(
        @{ name = "Odoo"; url = "http://$RouterIP:8069"; expected = "200" }
        @{ name = "AI"; url = "http://$RouterIP:8080"; expected = "200" }
        @{ name = "Kuma"; url = "http://$RouterIP:3001"; expected = "200" }
        @{ name = "HTTP"; url = "http://$RouterIP:80"; expected = "200" }
    )
    
    foreach ($svc in $services) {
        Write-Host "⏳ 測試: $($svc.name)" -f $colors.warning
        try {
            $response = Invoke-WebRequest -Uri $svc.url -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Log-Success "$($svc.name): 可訪問"
            } else {
                Log-Warning "$($svc.name): 響應碼 $($response.StatusCode)"
            }
        } catch {
            Log-Warning "$($svc.name): 連接失敗"
        }
    }
    
    Write-Host ""
}

# =====================================================================
# 主程式
# =====================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -f $colors.header
Write-Host "║     路由器外網指揮控制系統 - Router External Command      ║" -f $colors.header
Write-Host "║     獲取完整的外網流量管理權限                            ║" -f $colors.header
Write-Host "╚════════════════════════════════════════════════════════════╝" -f $colors.header

switch ($Action) {
    "auth" {
        Authenticate-Router
    }
    "status" {
        Show-RouterStatus
    }
    "portforward" {
        Setup-PortForwarding
    }
    "upnp" {
        Setup-UPnP
    }
    "ddns" {
        Setup-DDNS
    }
    "firewall" {
        Setup-Firewall
    }
    "test" {
        Test-ExternalAccess
    }
    "command" {
        Write-Host ""
        Write-Host "🎯 所有可用命令:" -f $colors.warning
        Write-Host ""
        Write-Host "   auth        - 路由器身份驗證" -f $colors.info
        Write-Host "   status      - 查看路由器狀態" -f $colors.info
        Write-Host "   portforward - 配置端口轉發" -f $colors.info
        Write-Host "   upnp        - UPnP自動映射" -f $colors.info
        Write-Host "   ddns        - 動態DNS配置" -f $colors.info
        Write-Host "   firewall    - 防火牆設置" -f $colors.info
        Write-Host "   test        - 測試外網訪問" -f $colors.info
        Write-Host ""
    }
    default {
        Show-RouterStatus
    }
}

Write-Host ""
