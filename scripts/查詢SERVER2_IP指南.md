# 查詢 SERVER 2 IP 地址指南

**建立日期**：2026-01-22  
**用途**：查詢伺服器身份 2（SERVER 2 - WiFi 網卡）的 IPv4 地址

---

## 📋 SERVER 2 已知資訊

### 身份 2（WiFi 網卡 - server 2）

| 項目 | 值 |
|------|-----|
| **名稱** | server 2（路由器顯示：svrver 2） |
| **IPv4** | **待確認**（目前只顯示 IPv6） |
| **IPv6** | `fe80::cdf9:2266:dc55:bcc6` |
| **MAC** | `1C:3E:84:67:C0:16` |
| **類型** | WiFi 網卡 |
| **介面** | work_IoT (5G Wi-Fi) |
| **IP 分配** | Static（靜態） |

---

## 🔍 查詢方法

### 方法一：使用查詢腳本（推薦）

使用地端小J的權限查詢路由器設備列表：

```bash
python 查詢SERVER2_IP.py
```

**注意**：需要路由器認證資訊
- 環境變數：`ROUTER_USERNAME` 和 `ROUTER_PASSWORD`
- 或建立 `router_config.json` 檔案

### 方法二：在路由器 Web 介面查看

1. 登入路由器管理介面：`https://192.168.50.84:8443`
2. 前往「網路地圖」→「用戶端」
3. 尋找 MAC 地址 `1C:3E:84:67:C0:16` 的設備
4. 查看其 IPv4 地址

### 方法三：在伺服器上查看

在伺服器上執行以下命令：

```bash
# 查看所有網卡和 IP
ip addr show

# 或
ifconfig

# 尋找 WiFi 網卡（work_IoT）的 IPv4
ip addr show work_IoT
```

### 方法四：使用 Odoo 路由器管理模組

1. 登入 Odoo：`http://localhost:8069`
2. 前往「路由器管理」→「連線裝置」
3. 尋找名稱為 "server 2" 或 "svrver 2" 的設備
4. 查看其 IPv4 地址

---

## 📝 查詢結果處理

### 如果找到 IPv4 地址

更新以下檔案：

1. **`jules_memory_bank.json`**：
   ```json
   "identity_2": {
     "ip_address": "192.168.50.XXX"  // 更新為實際 IP
   }
   ```

2. **`little_j_permanent_permissions.json`**：
   ```json
   "identity_2": {
     "ip_address": "192.168.50.XXX"  // 更新為實際 IP
   }
   ```

3. **`cloudflared/config.yml`**（如果需要）：
   ```yaml
   - hostname: app.wuchang.org.tw
     service: http://192.168.50.XXX:8069  # 使用 SERVER 2 IP
   ```

### 如果未找到 IPv4 地址

可能原因：
1. WiFi 網卡只配置了 IPv6
2. 需要手動配置 IPv4 地址
3. 設備未正確連接到路由器

建議：
1. 在伺服器上檢查 WiFi 網卡配置
2. 確認是否需要手動設定靜態 IP
3. 檢查路由器 DHCP 設定

---

## 🔧 使用地端小J查詢

地端小J擁有路由器管理員權限（`router_admin`），可以使用以下方式查詢：

### 透過 API

```python
from router_integration import RouterIntegration

router = RouterIntegration(hostname="192.168.50.84", port=8443)
if router.login():
    devices = router.get_connected_devices()
    for device in devices.get("devices", []):
        if "server 2" in device.get("name", "").lower() or \
           device.get("mac", "") == "1C:3E:84:67:C0:16":
            print(f"SERVER 2 IP: {device.get('ip', '未找到')}")
```

### 透過 UI

1. 開啟最高權限 UI
2. 前往「路由器管理」區塊
3. 查看「連線裝置」列表
4. 尋找 SERVER 2 的 IP 地址

---

## 📄 相關檔案

1. **查詢腳本**：`查詢SERVER2_IP.py`
2. **路由器設備列表**：`list_router_devices.py`
3. **雙身份資訊**：`cloudflared/雙身份資訊更新.md`
4. **Odoo 模組**：`wuchang_os/addons/wuchang_router_management/`

---

## ✅ 查詢狀態

- [ ] SERVER 2 IPv4 地址已確認
- [ ] 相關檔案已更新
- [ ] Cloudflare Tunnel 配置已更新（如果需要）

---

**建立時間**：2026-01-22  
**最後更新**：2026-01-22
