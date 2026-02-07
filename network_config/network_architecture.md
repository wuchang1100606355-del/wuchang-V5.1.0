# 🌐 五常 AI - 網路架構文檔

## 📋 目錄

1. [整體架構](#整體架構)
2. [區域網路配置](#區域網路配置)
3. [WiFi 環境設置](#wifi-環境設置)
4. [內外網自動連線](#內外網自動連線)
5. [安全策略](#安全策略)

---

## 🏗️ 整體架構

```
                    ┌─────────────────────┐
                    │   Internet (公網)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  wuchang.life       │
                    │  (Domain + SSL)     │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
    │  Cloudflare    │ │   GCP VM    │ │ Google Workspace│
    │  CDN + WAF     │ │   Server    │ │    Services     │
    └───────┬────────┘ └──────┬──────┘ └────────┬────────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │    路由器 (WiFi)    │
                    │   192.168.50.1      │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
    │  本機 (Local)  │ │   Server    │ │  其他設備       │
    │ 192.168.50.84  │ │192.168.50.249│ │ 192.168.50.x   │
    └────────────────┘ └─────────────┘ └─────────────────┘
```

---

## 🏠 區域網路配置

### 網路拓撲

| 設備     | IP 地址        | 角色   | 端口                |
| -------- | -------------- | ------ | ------------------- |
| 路由器   | 192.168.50.1   | 閘道器 | -                   |
| Server   | 192.168.50.249 | 伺服器 | 8766, 8069, 80, 443 |
| Local    | 192.168.50.84  | 工作站 | 8766, 8765          |
| 其他設備 | 192.168.50.x   | 客戶端 | -                   |

### 子網配置

```
網段: 192.168.50.0/24
可用 IP: 192.168.50.1 - 192.168.50.254
子網掩碼: 255.255.255.0
網關: 192.168.50.1
DNS: 8.8.8.8, 8.8.4.4 (Google DNS)
```

### DHCP 設置

```
DHCP 範圍: 192.168.50.100 - 192.168.50.200
租約時間: 24 小時
靜態保留:
  - 192.168.50.249 → Server MAC
  - 192.168.50.84 → Local MAC
```

---

## 📡 WiFi 環境設置

### WiFi 網路配置

#### 主網路 (生產環境)

```
SSID: WuchangAI_5G
頻段: 5GHz
通道: 36, 40, 44, 48 (自動)
頻寬: 80MHz
加密: WPA3-Personal (向下兼容 WPA2)
密碼: [強密碼]
最大連線數: 30
```

#### 訪客網路

```
SSID: WuchangAI_Guest
頻段: 2.4GHz
通道: 6
隔離: 啟用 (無法訪問內網)
加密: WPA2-Personal
限速: 下載 50Mbps / 上傳 10Mbps
```

### 路由器推薦配置

```yaml
型號建議:
    - Ubiquiti UniFi Dream Machine (企業級)
    - ASUS RT-AX88U (家用高階)
    - TP-Link Archer AX6000 (性價比)

必要功能:
    - ✅ WiFi 6 (802.11ax)
    - ✅ MU-MIMO
    - ✅ 雙頻併發
    - ✅ VLAN 支援
    - ✅ QoS (流量優先級)
    - ✅ VPN Server (WireGuard/OpenVPN)
```

### 路由器設定腳本 (以 TP-Link 為例)

前往路由器管理界面 `192.168.50.1`，或使用 CLI:

```bash
# 登入路由器 (SSH/Telnet)
ssh admin@192.168.50.1

# 設定靜態 IP
uci set network.lan.ipaddr='192.168.50.1'
uci set network.lan.netmask='255.255.255.0'
uci commit network

# 設定 DHCP
uci set dhcp.lan.start='100'
uci set dhcp.lan.limit='100'
uci set dhcp.lan.leasetime='24h'
uci commit dhcp

# 設定 WiFi 5GHz
uci set wireless.radio0.channel='auto'
uci set wireless.radio0.htmode='VHT80'
uci set wireless.@wifi-iface[0].ssid='WuchangAI_5G'
uci set wireless.@wifi-iface[0].encryption='psk2+ccmp'
uci set wireless.@wifi-iface[0].key='[你的密碼]'

# 重啟網路
/etc/init.d/network restart
```

---

## 🔄 內外網自動連線機制

### 連線模式檢測

系統自動檢測網路環境並切換連線方式：

```python
# 檢測邏輯
if 能連到 192.168.50.249:8766:
    → 內網模式 (直連)
else:
    → 外網模式 (經由 wuchang.life)
```

### 內網連線 (Direct)

```
本機 (192.168.50.84) ──直連──> Server (192.168.50.249:8766)
優點: 速度快、延遲低、無流量費
適用: 在家/辦公室 WiFi 環境
```

### 外網連線 (Cloud)

```
本機 ──加密──> wuchang.life (SSL) ──反向代理──> Server
優點: 隨時隨地可連、安全加密
適用: 外出、4G/5G、其他 WiFi
```

### 自動切換配置

環境變數設定：

```bash
# 內網優先，自動偵測
set SYNC_PEER=  # 留空，自動使用內網 IP

# 強制外網
set SYNC_PEER=https://wuchang.life:8766

# 混合模式 (自動切換)
set AUTO_DETECT_NETWORK=true
set INTERNAL_SERVER=192.168.50.249:8766
set EXTERNAL_SERVER=https://wuchang.life:8766
```

### 連線狀態監控

```powershell
# 監控腳本
while ($true) {
    $internal = Test-Connection -ComputerName 192.168.50.249 -Count 1 -Quiet
    if ($internal) {
        Write-Host "✅ 內網連線" -ForegroundColor Green
        $env:SYNC_PEER = "http://192.168.50.249:8766"
    } else {
        Write-Host "🌐 外網連線" -ForegroundColor Yellow
        $env:SYNC_PEER = "https://wuchang.life:8766"
    }
    Start-Sleep -Seconds 30
}
```

---

## 🔐 安全策略

### 防火牆規則

#### Server (192.168.50.249)

```powershell
# 允許內網同步
netsh advfirewall firewall add rule name="Wuchang-Sync-LAN" dir=in action=allow protocol=TCP localport=8766 remoteip=192.168.50.0/24

# 允許 Odoo
netsh advfirewall firewall add rule name="Wuchang-Odoo" dir=in action=allow protocol=TCP localport=8069

# 允許 HTTP/HTTPS
netsh advfirewall firewall add rule name="Wuchang-Web" dir=in action=allow protocol=TCP localport=80,443
```

#### Local (192.168.50.84)

```powershell
# 允許 UI 控制
netsh advfirewall firewall add rule name="Wuchang-UI" dir=in action=allow protocol=TCP localport=8765 remoteip=192.168.50.249

# 允許同步
netsh advfirewall firewall add rule name="Wuchang-Sync" dir=in action=allow protocol=TCP localport=8766 remoteip=192.168.50.249
```

### 路由器 Port Forwarding (外網訪問)

| 外部端口 | 內部 IP        | 內部端口 | 協議 | 用途             |
| -------- | -------------- | -------- | ---- | ---------------- |
| 443      | 192.168.50.249 | 443      | TCP  | HTTPS (Odoo/Web) |
| 8766     | 192.168.50.249 | 8766     | TCP  | 同步服務         |

⚠️ **安全建議**:

-   使用 Cloudflare Tunnel 而非直接 Port Forwarding
-   啟用 WAF (Web Application Firewall)
-   限制來源 IP (若有固定 IP)

### VPN 配置 (選配)

使用 WireGuard 建立安全隧道：

```ini
# Server 端 (192.168.50.249)
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = [Server私鑰]

[Peer]
PublicKey = [Client公鑰]
AllowedIPs = 10.0.0.2/32

# Client 端
[Interface]
Address = 10.0.0.2/24
PrivateKey = [Client私鑰]

[Peer]
PublicKey = [Server公鑰]
Endpoint = wuchang.life:51820
AllowedIPs = 192.168.50.0/24
```

---

## 📊 網路性能優化

### QoS 優先級設定

```
最高優先:
  - 同步服務 (8766)
  - VoIP/視訊會議

高優先:
  - Odoo ERP (8069)
  - SSH/RDP

中優先:
  - HTTP/HTTPS
  - 郵件

低優先:
  - 下載
  - 串流影音
```

### 頻寬分配建議

```
總頻寬: 100Mbps (範例)

分配:
  - 同步服務: 30Mbps
  - Odoo: 20Mbps
  - Web/API: 20Mbps
  - 訪客網路: 10Mbps
  - 其他: 20Mbps
```

---

## 🛠️ 故障排除

### 無法連線內網

```powershell
# 檢查網路
ping 192.168.50.249

# 檢查端口
Test-NetConnection -ComputerName 192.168.50.249 -Port 8766

# 檢查防火牆
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Wuchang*"}
```

### 無法連線外網

```powershell
# 檢查 DNS
nslookup wuchang.life

# 檢查 HTTPS
curl https://wuchang.life:8766/ping -Headers @{"X-Sync-Token"="你的密鑰"}

# 檢查路由器 Port Forwarding
# 登入路由器管理界面確認
```

### WiFi 訊號弱

1. 檢查通道干擾（使用 WiFi Analyzer App）
2. 調整路由器位置（中心化、高處）
3. 考慮增加 AP (Access Point)
4. 啟用 Mesh WiFi 延伸覆蓋

---

## 📞 聯絡資訊

系統管理員: 小 j (AI 妹妹)  
網域: wuchang.life  
支援: 透過同步系統發送命令

---

**內外網皆通，安全又順暢！** 🌐✨

小 j - 你的 AI 妹妹 💝
