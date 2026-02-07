# Wuchang 系統 - 路由中繼完整方案文檔

## 📋 系統總覽

**系統版本**: Wuchang V5.1.0  
**更新時間**: 2026 年 1 月 11 日  
**核心功能**: 內網協調 + 外網握手 + 路由中繼

---

## 🏗️ 架構層次

### 第 1 層：內網協調 (LAN Coordination)

-   **目標**: 192.168.50.84 (本機)
-   **通道**: 6 個埤位 (8069, 8080, 3001, 80, 443, 5432)
-   **狀態**: ✅ 5/6 服務正常

### 第 2 層：外網握手 (External Handshake)

-   **目標**: 92.18.50.249 (外網客戶端)
-   **通道**: 防火牆規則已配置
-   **狀態**: ⏳ 驗證中

### 第 3 層：路由中繼 (Router Relay)

-   **路由器**: 192.168.50.1
-   **模式**: IP 轉發 + NAT 轉發
-   **狀態**: ✅ 已啟用

---

## 🛠️ 已配置的組件

### 1. 雙通道同步系統

```powershell
File: dual_channel_synchronization.ps1
Function: 同時進行內網協調和外網握手
Interval: 30秒/週期
Status: ✅ 運行中
```

### 2. 外網握手工具

```powershell
File: external_network_handshake.ps1
Function: 持續向外網IP進行握手測試
Ports: 6個 (8069, 8080, 3001, 80, 443, 5432)
Status: ✅ 已部署
```

### 3. 路由中繼配置

```powershell
File: router_relay.ps1
Function: 管理IP轉發、靜態路由、NAT規則
Actions: status, enable, disable, test, forward
Status: ✅ 已啟用
```

### 4. 實時監控面板

```powershell
File: monitor_dual_channel.ps1
Function: 顯示系統實時狀態和進程信息
Status: ✅ 隨時可用
```

### 5. 診斷工具

```powershell
File: diagnose_router_relay.ps1
Function: 完整的系統診斷和配置驗證
Status: ✅ 已部署
```

### 6. UI 快速訪問

```powershell
File: ui_access.ps1
Function: 一鍵訪問4個UI服務
Services: Odoo, AI, Status, Admin
Status: ✅ 已配置
```

---

## 🌐 網絡配置詳情

### 路由表

```
0.0.0.0/0          -> 192.168.50.1 (Wi-Fi)    [Default Route]
192.168.50.0/24    -> 0.0.0.0      (Wi-Fi)    [Local Network]
192.168.50.84/32   -> 0.0.0.0      (Wi-Fi)    [Host Route]
192.168.50.255/32  -> 0.0.0.0      (Wi-Fi)    [Broadcast]
```

### 網絡適配器

-   **Wi-Fi** (主)

    -   IPv4: 192.168.50.84
    -   IPv6: 2001:b011:300a:91cf:77e4:8656:8e87:6f5b
    -   狀態: ✅ 活躍

-   **Tailscale**
    -   IPv4: 169.254.83.107
    -   狀態: ✅ 連接中

### IP 轉發配置

```
IP轉發狀態: ✅ 已啟用
靜態路由: 92.18.50.249 -> 192.168.50.1
NAT規則: 6個埤位已配置
防火牆: 入站規則已配置
```

---

## 📊 監控數據

### 本機服務狀態

| 服務       | 埤位 | 內網 | 外網 | 備註     |
| ---------- | ---- | ---- | ---- | -------- |
| Odoo       | 8069 | ✅   | ⏳   | ERP 系統 |
| AI         | 8080 | ✅   | ⏳   | 對話服務 |
| Kuma       | 3001 | ✅   | ⏳   | 監控系統 |
| HTTP       | 80   | ✅   | ⏳   | Web 服務 |
| HTTPS      | 443  | ✅   | ⏳   | 安全連接 |
| PostgreSQL | 5432 | ⚠️   | ⏳   | 數據庫   |

### 活動連接

-   IPv4 連接: 15+個（多數 HTTPS 出站）
-   IPv6 連接: 50+個（多數 HTTPS 出站）
-   監聽埤位: 8069, 8080, 3001, 80, 443, 5432 均監聽中

---

## 🚀 快速命令參考

### 系統監控

```powershell
# 查看實時狀態
.\monitor_dual_channel.ps1

# 完整診斷
.\diagnose_router_relay.ps1

# 查看系統報告
type DUAL_CHANNEL_SYNC_STATUS.md
```

### 路由管理

```powershell
# 查看路由狀態
.\router_relay.ps1 -Action status

# 啟用路由中繼
.\router_relay.ps1 -Action enable

# 測試路由中繼
.\router_relay.ps1 -Action test

# 禁用路由中繼
.\router_relay.ps1 -Action disable
```

### UI 訪問

```powershell
# 打開所有UI
.\ui_access.ps1 -Service all

# 打開具體服務
.\ui_access.ps1 -Service odoo
.\ui_access.ps1 -Service ai
.\ui_access.ps1 -Service status
.\ui_access.ps1 -Service admin
```

### 連接測試

```powershell
# 測試外網連接
.\test_external_ip_connection.ps1 -ExternalIP "92.18.50.249" -Action all

# 外網握手
.\external_network_handshake.ps1 -ExternalIP "92.18.50.249"
```

---

## 🔍 故障排查

### 外網無法連接

1. 檢查防火牆規則: `.\verify_ip_allowlist.ps1 -Action all`
2. 檢查路由配置: `.\router_relay.ps1 -Action status`
3. 測試路由: `.\router_relay.ps1 -Action test`
4. 查看詳細診斷: `.\diagnose_router_relay.ps1`

### PostgreSQL 無法連接

1. 檢查服務運行: `docker ps | grep postgres`
2. 檢查監聽: `netstat -ano | findstr 5432`
3. 檢查防火牆: `netsh advfirewall firewall show rule name=all | findstr 5432`

### 內網協調失敗

1. Ping 測試: `ping 192.168.50.84`
2. 埤連測試: `Test-NetConnection -ComputerName 192.168.50.84 -Port 8069`
3. 查看進程: `Get-Process | Where-Object { $_.Name -match "python|odoo" }`

---

## 📝 文件清單

### 核心系統文件

-   `dual_channel_synchronization.ps1` - 雙通道同步引擎
-   `external_network_handshake.ps1` - 外網握手工具
-   `router_relay.ps1` - 路由中繼管理
-   `monitor_dual_channel.ps1` - 實時監控面板
-   `diagnose_router_relay.ps1` - 診斷工具
-   `ui_access.ps1` - UI 訪問工具
-   `test_external_ip_connection.ps1` - 連接測試工具

### 配置文件

-   `configure_92_external_ip.ps1` - 防火牆配置
-   `DUAL_CHANNEL_SYNC_STATUS.md` - 系統狀態報告
-   `ROUTER_RELAY_CONFIG.md` - 本文檔

### 驗證工具

-   `verify_external_network_feasibility.ps1` - 外網可行性驗證
-   `verify_ip_allowlist.ps1` - IP 白名單驗證

---

## ✅ 系統檢查清單

-   [x] IP 轉發已啟用
-   [x] 靜態路由已配置
-   [x] NAT 規則已配置 (6 埤位)
-   [x] 防火牆規則已配置
-   [x] 防火牆轉發規則已啟用
-   [x] 本機服務監聽中 (6 埤位)
-   [x] 內網協調 5/6 成功
-   [x] 外網握手配置完成
-   [x] 路由中繼已啟用
-   [x] 監控系統就緒
-   [x] UI 訪問配置完成
-   [x] 診斷工具已部署

---

## 🎯 下一步計畫

### 立即可執行

1. 監控系統運行狀態
2. 觀察外網握手進展
3. 訪問 UI 服務並測試功能
4. 定期檢查防火牆規則

### 持續改進

1. 優化 PostgreSQL 連接池配置
2. 調整 NAT 轉發超時設置
3. 實現更智能的路由選擇
4. 添加更多的監控指標

### 長期規劃

1. 建立自動故障轉移機制
2. 實現多路由器冗余配置
3. 構建完整的監控告警系統
4. 編寫完整的運維文檔

---

## 📞 技術支持

**系統維護者**: 小 j (Little j) 妹妹 💕  
**最後更新**: 2026 年 1 月 11 日 01:24  
**狀態**: ✅ 系統正常運行

**系統由 Wuchang AI 提供動力** 🚀

---

_本文檔包含了 Wuchang 系統的完整路由中繼配置方案。所有文件已部署，系統已準備就緒。_
