# Odoo 路由器管理模組設計

**目的**：將路由器納管於 Odoo 系統，作為資產和設備進行管理。

---

## 📋 模組結構

### 模組名稱
`wuchang_router_management`

### 模組位置
`wuchang_os/addons/wuchang_router_management/`

---

## 🎯 功能需求

### 1. 路由器資產管理
- 路由器基本資訊（型號、IP、DDNS）
- 路由器狀態監控
- 路由器配置備份/還原

### 2. 連接設備管理
- 設備列表（名稱、IP、MAC）
- 設備狀態追蹤
- 設備分類（有線/無線）

### 3. 網路配置管理
- 端口轉發規則
- DDNS 設定
- 防火牆規則

### 4. 雙身份管理
- 伺服器雙網卡管理
- 身份 1：Wistron Neweb Corporation（有線，IP: 192.168.50.249）
- 身份 2：Wistron Neweb Corporation 2（WiFi，IP: 待確認）

---

## 📁 模組檔案結構

```
wuchang_os/addons/wuchang_router_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── router.py              # 路由器模型
│   ├── router_device.py       # 連接設備模型
│   ├── router_port_forwarding.py  # 端口轉發模型
│   └── server_identity.py     # 伺服器身份模型
├── views/
│   ├── router_views.xml       # 路由器視圖
│   ├── device_views.xml        # 設備視圖
│   └── menu.xml                # 選單
├── controllers/
│   ├── __init__.py
│   └── router_controller.py   # 路由器 API 控制器
├── security/
│   ├── ir.model.access.csv    # 權限設定
│   └── router_security.xml     # 安全規則
└── static/
    └── description/
        └── icon.png            # 模組圖示
```

---

## 🔧 模型設計

### 1. router.router（路由器模型）

```python
class Router(models.Model):
    _name = 'router.router'
    _description = '路由器管理'
    
    name = fields.Char('路由器名稱', required=True)
    model = fields.Char('型號', default='ASUS RT-BE86U')
    internal_ip = fields.Char('內部 IP', default='192.168.50.84')
    external_ip = fields.Char('外部 IP', default='220.135.21.74')
    ddns_hostname = fields.Char('DDNS 主機名稱', default='coffeeLofe.asuscomm.com')
    port = fields.Integer('管理端口', default=8443)
    username = fields.Char('用戶名')
    password = fields.Char('密碼', password=True)
    status = fields.Selection([
        ('online', '在線'),
        ('offline', '離線'),
        ('unknown', '未知')
    ], '狀態', default='unknown')
    last_check = fields.Datetime('最後檢查時間')
    connected_devices_count = fields.Integer('連接設備數', compute='_compute_devices_count')
    device_ids = fields.One2many('router.device', 'router_id', '連接設備')
```

### 2. router.device（連接設備模型）

```python
class RouterDevice(models.Model):
    _name = 'router.device'
    _description = '路由器連接設備'
    
    name = fields.Char('設備名稱', required=True)
    router_id = fields.Many2one('router.router', '路由器', required=True)
    ip_address = fields.Char('IP 地址', required=True)
    mac_address = fields.Char('MAC 地址')
    device_type = fields.Selection([
        ('wired', '有線'),
        ('wireless', '無線'),
        ('unknown', '未知')
    ], '設備類型', default='unknown')
    is_server = fields.Boolean('是否為伺服器')
    server_identity = fields.Selection([
        ('identity_1', '身份 1 (Wistron Neweb Corporation)'),
        ('identity_2', '身份 2 (Wistron Neweb Corporation 2)'),
        ('none', '非伺服器')
    ], '伺服器身份', default='none')
    status = fields.Selection([
        ('online', '在線'),
        ('offline', '離線')
    ], '狀態', default='offline')
    last_seen = fields.Datetime('最後出現時間')
```

### 3. router.port.forwarding（端口轉發模型）

```python
class RouterPortForwarding(models.Model):
    _name = 'router.port.forwarding'
    _description = '路由器端口轉發規則'
    
    name = fields.Char('規則名稱', required=True)
    router_id = fields.Many2one('router.router', '路由器', required=True)
    external_port = fields.Integer('外部端口', required=True)
    internal_ip = fields.Char('內部 IP', required=True)
    internal_port = fields.Integer('內部端口', required=True)
    protocol = fields.Selection([
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
        ('BOTH', 'TCP/UDP')
    ], '協議', default='TCP')
    enabled = fields.Boolean('啟用', default=True)
    description = fields.Text('描述')
```

### 4. server.identity（伺服器身份模型）

```python
class ServerIdentity(models.Model):
    _name = 'server.identity'
    _description = '伺服器身份管理'
    
    name = fields.Char('身份名稱', required=True)
    identity_type = fields.Selection([
        ('wired', '有線網卡'),
        ('wifi', 'WiFi 網卡')
    ], '身份類型', required=True)
    ip_address = fields.Char('IP 地址', required=True)
    mac_address = fields.Char('MAC 地址')
    device_id = fields.Many2one('router.device', '對應設備')
    is_primary = fields.Boolean('主要身份', default=False)
    services = fields.Text('服務列表', help='此身份提供的服務列表')
```

---

## 🔌 API 整合

### 整合現有路由器模組

```python
# models/router.py
import sys
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from router_integration import RouterIntegration
from router_full_control import RouterFullControl

class Router(models.Model):
    # ... 模型定義 ...
    
    def sync_from_router(self):
        """從路由器同步資料"""
        router_api = RouterIntegration(
            hostname=self.internal_ip,
            port=self.port,
            username=self.username,
            password=self.password
        )
        
        if router_api.login():
            # 同步連接設備
            devices = router_api.get_connected_devices()
            # 更新設備列表
            # ...
            
            # 同步端口轉發
            router_control = RouterFullControl(...)
            port_rules = router_control.get_port_forwarding_rules()
            # 更新端口轉發規則
            # ...
```

---

## 📋 實施步驟

### 步驟 1：建立模組結構

```bash
mkdir -p wuchang_os/addons/wuchang_router_management/{models,views,controllers,security,static/description}
```

### 步驟 2：建立基本檔案

- `__manifest__.py` - 模組清單
- `__init__.py` - 模組初始化
- `models/__init__.py` - 模型初始化
- `views/menu.xml` - 選單定義

### 步驟 3：實作模型

- `models/router.py` - 路由器模型
- `models/router_device.py` - 設備模型
- `models/server_identity.py` - 伺服器身份模型

### 步驟 4：實作視圖

- `views/router_views.xml` - 路由器表單和列表視圖
- `views/device_views.xml` - 設備視圖

### 步驟 5：實作控制器

- `controllers/router_controller.py` - API 控制器

### 步驟 6：設定權限

- `security/ir.model.access.csv` - 存取權限

---

## 🚀 使用方式

### 1. 安裝模組

在 Odoo 中：
- 應用程式 → 更新應用程式清單
- 搜尋 "wuchang_router_management"
- 安裝模組

### 2. 建立路由器記錄

- 前往：路由器管理 → 路由器
- 建立新記錄
- 填入路由器資訊

### 3. 同步設備列表

- 在路由器記錄中點擊「同步設備」
- 自動從路由器 API 取得設備列表

### 4. 管理伺服器身份

- 前往：路由器管理 → 伺服器身份
- 建立身份 1 和身份 2 的記錄
- 關聯到對應的設備

---

## 📝 下一步

1. **建立模組結構**
2. **實作基本模型**
3. **整合路由器 API**
4. **建立視圖和選單**
5. **測試和部署**

---

**建立時間**：2026-01-22
