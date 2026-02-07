# 路由器完整控制指南 - 物業管理模組整合

## 📋 概述

本指南說明如何透過程式化方式完全掌控路由器，用於物業管理模組的網路基礎設施控制。

## 🎯 核心目標

1. **完全掌控解析**：DNS/DDNS 解析控制
2. **物業管理整合**：為物業管理模組提供網路基礎設施
3. **程式化控制**：所有功能可透過 API 程式化控制

## 📦 模組架構

### 1. router_full_control.py
**完整路由器控制模組**

提供：
- DNS/DDNS 控制
- 端口轉發管理
- 防火牆規則管理
- 無線網路控制
- 訪客網路管理
- 系統控制（重啟、備份等）

### 2. property_management_router_integration.py
**物業管理路由器整合模組**

提供：
- 物業網路基礎設施初始化
- 設備端口轉發管理
- 活動訪客網路設定
- 網路使用報告

### 3. router_integration.py
**基礎路由器整合模組**

提供：
- 連線裝置監控
- 網路流量監控
- 基本狀態查詢

## 🔧 使用範例

### 基本路由器控制

```python
from router_full_control import get_router_full_control

# 獲取路由器控制實例
router = get_router_full_control()

# 登錄
if router.login():
    # 獲取 DDNS 狀態
    ddns_status = router.get_ddns_status()
    print(f"DDNS 狀態: {ddns_status}")
    
    # 獲取端口轉發規則
    rules = router.get_port_forwarding_rules()
    print(f"端口轉發規則: {len(rules)} 條")
    
    # 添加端口轉發規則
    router.add_port_forwarding_rule(
        external_port=8080,
        internal_ip="192.168.50.100",
        internal_port=8080,
        description="物業管理系統"
    )
```

### 物業管理整合

```python
from property_management_router_integration import get_property_router_integration

# 獲取物業管理路由器整合
integration = get_property_router_integration("wuchang_community")

# 初始化網路基礎設施
result = integration.initialize_network_infrastructure()
print(f"初始化結果: {result}")

# 獲取網路儀表板
dashboard = integration.get_network_dashboard()
print(f"連線裝置: {dashboard['connected_devices']['total']}")

# 為活動設定訪客網路
event_network = integration.setup_guest_network_for_event(
    event_name="社區活動",
    duration_hours=24
)
print(f"訪客網路 SSID: {event_network['ssid']}")
print(f"密碼: {event_network['password']}")
```

## 🌐 API 端點

### 路由器完整控制 API

#### 獲取 DDNS 狀態
```
GET /api/router/full_control/ddns_status
```

#### 獲取端口轉發規則
```
GET /api/router/full_control/port_forwarding
```

#### 添加端口轉發規則
```
POST /api/router/full_control/add_port_forwarding
Body: {
  "external_port": 8080,
  "internal_ip": "192.168.50.100",
  "internal_port": 8080,
  "protocol": "TCP",
  "description": "物業管理系統"
}
```

### 物業管理路由器整合 API

#### 獲取網路儀表板
```
GET /api/property/router/dashboard?property_id=wuchang_community
```

#### 初始化網路基礎設施
```
POST /api/property/router/initialize
Body: {
  "property_id": "wuchang_community"
}
```

## 🔐 DNS/DDNS 控制

### 獲取 DDNS 狀態
```python
ddns_status = router.get_ddns_status()
# 返回：
# {
#   "status": {...},
#   "ddns_hostname": "coffeeLofe.asuscomm.com",
#   "external_ip": "220.135.21.74",
#   "timestamp": "..."
# }
```

### 更新 DDNS 設定
```python
router.update_ddns(
    hostname="coffeeLofe.asuscomm.com",
    service="asuscomm.com"
)
```

### 設定 DNS 伺服器
```python
router.set_dns_servers(
    primary="8.8.8.8",
    secondary="8.8.4.4"
)
```

## 🔌 端口轉發控制

### 添加端口轉發規則
```python
router.add_port_forwarding_rule(
    external_port=8080,
    internal_ip="192.168.50.100",
    internal_port=8080,
    protocol="TCP",
    description="物業管理系統"
)
```

### 移除端口轉發規則
```python
router.remove_port_forwarding_rule(rule_index=0)
```

### 獲取所有規則
```python
rules = router.get_port_forwarding_rules()
for rule in rules:
    print(f"規則: {rule}")
```

## 🛡️ 防火牆控制

### 添加防火牆規則
```python
router.add_firewall_rule(
    name="允許物業管理系統",
    src_ip="",
    dst_ip="192.168.50.100",
    port="8080",
    protocol="TCP",
    action="ACCEPT"
)
```

### 獲取防火牆規則
```python
rules = router.get_firewall_rules()
```

## 📶 無線網路控制

### 設定無線網路 SSID
```python
router.set_wireless_ssid(
    band="5G",
    ssid="Wuchang-Community",
    password="SecurePassword123"
)
```

### 啟用訪客網路
```python
router.enable_guest_network(
    band="5G",
    ssid="Wuchang-Guest",
    password="GuestPassword",
    duration_hours=24
)
```

## 🏢 物業管理專用功能

### 初始化物業網路基礎設施
```python
result = integration.initialize_network_infrastructure()
# 自動設定：
# - Odoo ERP 端口轉發 (8069)
# - Control Center 端口轉發 (5000)
# - Local Control Center 端口轉發 (8788)
# - SSH 自訂端口轉發 (65433)
# - 訪客網路
```

### 為設備添加端口轉發
```python
integration.add_device_port_forward(
    device_name="門禁系統",
    device_ip="192.168.50.101",
    external_port=9000,
    internal_port=9000,
    description="門禁系統控制"
)
```

### 為活動設定臨時訪客網路
```python
event_network = integration.setup_guest_network_for_event(
    event_name="社區活動-2026",
    duration_hours=48,
    password="Event2026"  # 可選，不提供則自動生成
)
```

## 📊 監控與報告

### 獲取網路儀表板
```python
dashboard = integration.get_network_dashboard()
# 包含：
# - 連線裝置數量和列表
# - 網路狀態
# - 系統資訊
# - DDNS 狀態
```

### 獲取網路使用報告
```python
report = integration.get_network_usage_report(days=7)
# 包含：
# - 連線裝置數量
# - 活動端口轉發規則
# - 報告期間
```

## ⚙️ 設定檔

### router_config.json（可選）
```json
{
  "username": "admin",
  "password": "your_password",
  "hostname": "192.168.50.84",
  "port": 8443
}
```

### 環境變數
```bash
export ROUTER_USERNAME="admin"
export ROUTER_PASSWORD="your_password"
```

## 🔄 系統整合

### 與物業管理模組整合

在物業管理模組中：

```python
from property_management_router_integration import get_property_router_integration

class PropertyManagementModule:
    def __init__(self, property_id):
        self.property_id = property_id
        self.router_integration = get_property_router_integration(property_id)
    
    def setup_network(self):
        """設定物業網路"""
        return self.router_integration.initialize_network_infrastructure()
    
    def get_network_status(self):
        """獲取網路狀態"""
        return self.router_integration.get_network_dashboard()
    
    def add_device(self, device_name, device_ip, port):
        """添加設備端口轉發"""
        return self.router_integration.add_device_port_forward(
            device_name=device_name,
            device_ip=device_ip,
            external_port=port
        )
```

## 📝 注意事項

1. **認證安全**：不要在程式碼中硬編碼密碼，使用環境變數或設定檔
2. **操作風險**：端口轉發和防火牆規則修改會影響網路連線
3. **備份設定**：重要操作前先備份路由器設定
4. **錯誤處理**：所有操作都應包含錯誤處理邏輯
5. **日誌記錄**：記錄所有路由器操作以便稽核

## 🔗 相關檔案

- `router_full_control.py` - 完整路由器控制模組
- `property_management_router_integration.py` - 物業管理整合模組
- `router_integration.py` - 基礎整合模組
- `router_api_controller.py` - API 控管工具
- `router_api_explorer.py` - API 探索工具

## 📅 文檔建立日期

2026-01-22
