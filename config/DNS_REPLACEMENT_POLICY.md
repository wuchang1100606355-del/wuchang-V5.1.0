# DNS 替換政策

## 📋 核心原則

**不可更動網域網址**

在DNS替換過程中，系統會自動跳過已包含網域網址的檔案，確保不會更改現有的網域配置。

## 🔒 保護機制

### 1. 自動檢測網域網址
系統會自動檢測檔案中是否已包含網域網址（如 `wuchang.life`），如果包含則跳過DNS替換。

### 2. 只替換IP地址和localhost
DNS替換規則只會替換：
- `127.0.0.1` → `wuchang.life`（僅當檔案中不存在網域時）
- `localhost` → `wuchang.life`（僅當檔案中不存在網域時）
- `192.168.50.84` → `wuchang.life`（僅當檔案中不存在網域時）

### 3. 不替換已存在的網域
如果檔案中已包含以下任何網域網址，將跳過DNS替換：
- `wuchang.life`
- `admin.wuchang.life`
- `ui.wuchang.life`
- `odoo.wuchang.life`
- 任何 `.life` 網域

## 🔍 檢測邏輯

```python
# 檢查是否已包含網域網址
if re.search(r'wuchang\.life|\.life', content, re.IGNORECASE):
    # 跳過DNS替換
    return content, 0
```

## 📝 替換規則

### 會被替換的內容
- `127.0.0.1` → `wuchang.life`
- `localhost` → `wuchang.life`
- `192.168.50.84` → `wuchang.life`
- `http://127.0.0.1:8788` → `https://admin.wuchang.life`

### 不會被替換的內容
- `wuchang.life`（已存在的網域）
- `admin.wuchang.life`（已存在的網域）
- `https://wuchang.life`（已存在的網域URL）
- 任何包含 `.life` 的網域

## ⚠️ 注意事項

1. **自動保護**: 系統會自動檢測並保護已存在的網域網址
2. **手動檢查**: 建議在部署前手動檢查重要檔案的網域配置
3. **備份**: 執行DNS替換前請先備份重要檔案
4. **驗證**: 替換後請驗證網域配置是否正確

## 🔗 相關檔案

- `dual_j_file_sync_with_dns_replace.py` - DNS替換邏輯
- `dual_j_full_deployment.py` - 全面部署工具
- `DNS_CHANGE_LIST.md` - DNS更改清單

## 📅 政策建立日期

2026-01-22
