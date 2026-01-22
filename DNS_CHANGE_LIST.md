# DNS 更改清單

## 📋 概述

本文件列出所有需要將本機DNS更改為伺服器DNS的檔案清單。

## 📊 統計摘要

- **需要更改的檔案數**: 111 個
- **總DNS出現次數**: 330 處
- **DNS類型分布**:
  - `127.0.0.1`: 54 個檔案，131 處
  - `localhost`: 42 個檔案，114 處
  - `192.168.50.84`: 15 個檔案，85 處

## 🔄 DNS 替換規則

### 基本替換
- `127.0.0.1` → `wuchang.life`
- `localhost` → `wuchang.life`
- `192.168.50.84` → `wuchang.life`

### HTTP/HTTPS 替換
- `http://127.0.0.1` → `https://wuchang.life`
- `http://localhost` → `https://wuchang.life`
- `https://127.0.0.1` → `https://wuchang.life`

### 端口替換（保留端口號）
- `127.0.0.1:8788` → `wuchang.life:8788`
- `localhost:5000` → `wuchang.life:5000`

### 特定服務對應
- `http://127.0.0.1:8788` → `https://admin.wuchang.life`
- `http://127.0.0.1:5000` → `https://ui.wuchang.life`
- `http://127.0.0.1:8069` → `https://odoo.wuchang.life`

## 📁 需要更改的檔案清單

### 127.0.0.1 (54 個檔案，131 處)

主要檔案包括：
- `local_control_center.py` - 控制中心主程式
- `wuchang_control_center.html` - 控制中心UI
- `dual_j_file_sync_with_dns_replace.py` - 檔案同步工具
- `dual_j_full_deployment.py` - 全面部署工具
- `AUTHORIZATION_GUIDE.md` - 授權指南
- `DUAL_J_FILE_SYNC_GUIDE.md` - 同步指南
- 以及其他多個配置和文檔檔案

### localhost (42 個檔案，114 處)

主要檔案包括：
- `local_control_center.py`
- `router_integration.py`
- `router_full_control.py`
- `property_management_router_integration.py`
- 各種部署和配置腳本

### 192.168.50.84 (15 個檔案，85 處)

主要檔案包括：
- `router_full_control.py` - 路由器控制
- `router_integration.py` - 路由器整合
- `jules_memory_bank.json` - 記憶庫
- `ROUTER_FULL_CONTROL_GUIDE.md` - 路由器控制指南

## 🔧 自動化工具

使用以下工具可以自動進行DNS替換：

### 1. 生成DNS更改清單
```bash
python dual_j_full_deployment.py --dns-list-only
```

### 2. 執行DNS替換和同步
```bash
python dual_j_file_sync_with_dns_replace.py
```

### 3. 全面部署（包含DNS替換）
```bash
python dual_j_full_deployment.py
```

## 📝 注意事項

1. **備份**: 在執行DNS替換前，請先備份重要檔案
2. **測試**: 建議先在測試環境驗證DNS替換效果
3. **驗證**: 替換後請驗證所有服務是否正常運作
4. **回滾**: 保留原始檔案以便需要時回滾

## 📅 清單生成時間

2026-01-22 08:21:58

## 🔗 相關檔案

- `dns_change_list_YYYYMMDD_HHMMSS.json` - 詳細DNS更改清單（JSON格式）
- `dual_j_file_sync_with_dns_replace.py` - DNS替換和同步工具
- `dual_j_full_deployment.py` - 全面部署工具
