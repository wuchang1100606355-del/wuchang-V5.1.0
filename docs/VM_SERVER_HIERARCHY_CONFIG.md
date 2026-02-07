# VM 伺服器位階設定確認文件

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**VM IP**: 192.168.50.84  
**控制端**: UI 設備（主機控制端點）  
**被控制端**: 192.168.50.84（VM，主機控制端點）

---

## 🎯 架構概述

### 控制端點架構

```
┌─────────────────────────────────────────┐
│         UI 設備（主機控制端點）          │
│      (Control Endpoint / Master)        │
│                                         │
│  - 發送控制指令                         │
│  - 監控被控制端狀態                     │
│  - 管理設備配置                         │
└─────────────────────────────────────────┘
                    │
                    │ 控制指令 / 狀態查詢
                    ▼
┌─────────────────────────────────────────┐
│     192.168.50.84 (VM)                 │
│   (被控制端 / Controlled Endpoint)     │
│                                         │
│  - 接收控制指令                         │
│  - 執行操作                             │
│  - 回報狀態                             │
│  - 運行 Odoo 服務                      │
└─────────────────────────────────────────┘
```

### 角色定義

| 角色 | IP 地址 | 類型 | 功能 |
|------|---------|------|------|
| **控制端** | UI 設備 IP | 主機控制端點 | 發送指令、監控狀態 |
| **被控制端** | 192.168.50.84 | VM（主機控制端點） | 接收指令、執行操作、運行服務 |

---

## 🌐 wuchang.life 網域設定

### 公開 DNS 記錄

根據 `workshop_deploy/dns_records.json`，wuchang.life 網域的公開 DNS 記錄如下：

| 子域名 | 類型 | IP 地址 | 說明 |
|--------|------|---------|------|
| `@` (root) | A | 104.199.144.93 | 主站入口 |
| `www` | A | 104.199.144.93 | 主站入口 |
| `shop` | A | 220.135.21.74 | 重新總店實體路由器 |
| `odoo` | A | 104.199.144.93 | Odoo 服務 |
| `pos` | A | 104.199.144.93 | POS 服務 |

### 內網 DNS 設定

**192.168.50.84 (VM)** 為內網 IP，不在公開 DNS 記錄中，但已配置私人 DNS：

| 主機名稱 | IP 地址 | 用途 |
|---------|---------|------|
| `pos-server.chong-sin.local` | 192.168.50.84 | POS 伺服器 |
| `odoo.chong-sin.local` | 192.168.50.84 | Odoo 服務 |
| `api.chong-sin.local` | 192.168.50.84 | API 服務 |

### 位階確認

✅ **192.168.50.84 (VM) 在 wuchang.life 網域中的位階**：
- **類型**: 內網伺服器（不直接對外）
- **角色**: 被控制端（Controlled Endpoint）
- **服務**: 運行 Odoo、POS、API 等核心服務
- **訪問方式**: 
  - 內網：`http://192.168.50.84:8069`
  - 私人 DNS：`http://pos-server.chong-sin.local:8069`
  - 外網：透過 `wuchang.life` 主站（104.199.144.93）反向代理

---

## 🔐 Google Workspace 設備管理設定

### 設備納管狀態

根據 `Chrome_OS設備納管說明.md` 和相關配置：

#### 1. Google Workspace Admin Console 設定

**管理帳號**: `admin@wuchang.life`（小J 的操作載體）

**設備管理功能**：
- ✅ 設備註冊與納管
- ✅ 遠程控制
- ✅ 安全策略管理
- ✅ 應用程式分發

#### 2. VM (192.168.50.84) 在 Google Workspace 中的位階

**設備類型**: VM（虛擬機）

**管理方式**:
- **納管狀態**: 可透過 Google Workspace Endpoint Management 納管
- **設備識別**: 使用 IP 地址 `192.168.50.84` 或設備 ID
- **管理權限**: 由 `admin@wuchang.life` 管理

**建議配置**:

```json
{
  "device_id": "VM_192_168_50_84",
  "device_name": "Wuchang OS VM Server",
  "ip_address": "192.168.50.84",
  "device_type": "vm",
  "role": "controlled_endpoint",
  "managed_by": "admin@wuchang.life",
  "organization_unit": "Infrastructure/Servers",
  "status": "online",
  "capabilities": {
    "odoo_service": true,
    "pos_service": true,
    "api_service": true,
    "remote_control": true,
    "file_sharing": true
  }
}
```

#### 3. UI 設備（控制端）在 Google Workspace 中的位階

**設備類型**: 控制端設備（Control Endpoint）

**管理方式**:
- **納管狀態**: 已納管到 Google Workspace
- **設備識別**: UI 設備的主機名稱或 IP
- **管理權限**: 擁有控制其他設備的權限

**建議配置**:

```json
{
  "device_id": "UI_CONTROL_ENDPOINT",
  "device_name": "UI Control Endpoint",
  "device_type": "control_endpoint",
  "role": "master",
  "managed_by": "admin@wuchang.life",
  "organization_unit": "Infrastructure/Control",
  "status": "online",
  "capabilities": {
    "device_control": true,
    "remote_management": true,
    "command_execution": true,
    "status_monitoring": true
  },
  "controlled_devices": [
    "VM_192_168_50_84"
  ]
}
```

---

## 📋 位階設定確認清單

### wuchang.life 網域

- [x] **192.168.50.84 為內網 IP**，不在公開 DNS 記錄中
- [x] **已配置私人 DNS** (`pos-server.chong-sin.local` 等)
- [x] **外網訪問**透過主站 (104.199.144.93) 反向代理
- [x] **位階**: 內網伺服器（被控制端）

### Google Workspace

- [ ] **VM (192.168.50.84) 需納管到 Google Workspace**
  - 設備 ID: `VM_192_168_50_84`
  - 組織單位: `Infrastructure/Servers`
  - 管理帳號: `admin@wuchang.life`
  
- [ ] **UI 設備需納管到 Google Workspace**
  - 設備 ID: `UI_CONTROL_ENDPOINT`
  - 組織單位: `Infrastructure/Control`
  - 管理帳號: `admin@wuchang.life`
  
- [ ] **設定控制關係**
  - UI 設備擁有控制 VM 的權限
  - VM 接受來自 UI 設備的指令

---

## 🔧 設定步驟

### Step 1: Google Workspace Admin Console 設定

1. **登入 Google Workspace Admin Console**
   - 網址: `https://admin.google.com`
   - 帳號: `admin@wuchang.life`

2. **建立組織單位 (OU)**
   ```
   Infrastructure
   ├── Control (控制端設備)
   └── Servers (伺服器設備)
   ```

3. **納管 VM (192.168.50.84)**
   - 進入「設備」→「行動裝置與端點」
   - 選擇「新增設備」
   - 輸入設備資訊：
     - 設備名稱: `Wuchang OS VM Server`
     - 設備 ID: `VM_192_168_50_84`
     - IP 地址: `192.168.50.84`
     - 設備類型: `VM`
     - 組織單位: `Infrastructure/Servers`

4. **納管 UI 設備（控制端）**
   - 進入「設備」→「行動裝置與端點」
   - 選擇「新增設備」
   - 輸入設備資訊：
     - 設備名稱: `UI Control Endpoint`
     - 設備 ID: `UI_CONTROL_ENDPOINT`
     - 設備類型: `Control Endpoint`
     - 組織單位: `Infrastructure/Control`

5. **設定控制權限**
   - 在 UI 設備的設定中，授予「設備控制」權限
   - 指定可控制的設備：`VM_192_168_50_84`

### Step 2: Odoo 系統設定

1. **更新設備模型**
   - 在 Odoo 中建立或更新 `wuchang.infrastructure.device` 記錄
   - 設定 VM (192.168.50.84) 為「被控制端」
   - 設定 UI 設備為「控制端」

2. **設定 Sister Control**
   - 確認 `wuchang.sister.control` 模型正確配置
   - 設定控制端點 URL: `http://192.168.50.84:8069/wuchang/sister/poll`

### Step 3: 驗證設定

1. **測試控制端連線**
   ```powershell
   # 從 UI 設備測試連接到 VM
   Test-NetConnection -ComputerName 192.168.50.84 -Port 8069
   ```

2. **測試控制指令**
   ```powershell
   # 發送測試指令到 VM
   Invoke-WebRequest -Uri "http://192.168.50.84:8069/wuchang/sister/poll" -Method POST -Body '{"device_type":"POS"}' -ContentType "application/json"
   ```

3. **檢查 Google Workspace 設備狀態**
   - 登入 Google Workspace Admin Console
   - 確認兩個設備都已納管並顯示為「在線」

---

## 📊 位階總結

### 控制端點架構

| 層級 | 設備 | IP/識別 | 角色 | 位階 |
|------|------|---------|------|------|
| **控制層** | UI 設備 | UI IP | 主機控制端點 | Master |
| **服務層** | VM | 192.168.50.84 | 被控制端 | Controlled |

### wuchang.life 網域位階

| 設備 | 公開 DNS | 內網 DNS | 位階 |
|------|----------|----------|------|
| VM (192.168.50.84) | ❌ 無（內網） | ✅ `pos-server.chong-sin.local` | 內網伺服器 |
| 主站 | ✅ `wuchang.life` → 104.199.144.93 | - | 公開入口 |

### Google Workspace 位階

| 設備 | 組織單位 | 管理帳號 | 位階 |
|------|----------|----------|------|
| UI 設備 | `Infrastructure/Control` | `admin@wuchang.life` | 控制端 |
| VM (192.168.50.84) | `Infrastructure/Servers` | `admin@wuchang.life` | 被控制端 |

---

## ✅ 確認結果

### wuchang.life 網域

✅ **已確認**: 192.168.50.84 為內網 IP，不在公開 DNS 記錄中  
✅ **已配置**: 私人 DNS 主機名稱 (`pos-server.chong-sin.local` 等)  
✅ **位階**: 內網伺服器（被控制端）

### Google Workspace

⏳ **待設定**: VM (192.168.50.84) 需納管到 Google Workspace  
⏳ **待設定**: UI 設備需納管到 Google Workspace  
⏳ **待設定**: 設定控制關係

---

## 📝 後續行動

1. **執行 Google Workspace 納管**
   - 使用 `scripts/setup_google_wifi_mdm.py` 或手動納管
   - 確認兩個設備都已納管

2. **更新 Odoo 設備記錄**
   - 在 Odoo 中更新設備資訊
   - 設定控制關係

3. **測試控制功能**
   - 從 UI 設備發送控制指令
   - 確認 VM 正確接收並執行

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)  
**VM IP**: 192.168.50.84
