# POS（銷售點）系統檢查報告

## 📊 檢查結果

**檢查時間：** 2026-01-20  
**資料庫：** admin

---

## ✅ POS 系統總數

**共有 4 組 POS 系統**

---

## 📋 POS 系統詳細資訊

| ID | 名稱 | 啟用狀態 | 公司 ID |
|----|------|---------|---------|
| 1 | Shop | ❌ 停用 | 1 |
| 2 | Restaurant | ✅ 啟用 | 2 |
| 3 | 上品聊國咖啡館重新總店 | ✅ 啟用 | 1 |
| 4 | 上品聊國咖啡館重新總店 | ✅ 啟用 | 1 |

---

## 📊 統計資訊

### 啟用狀態
- **啟用的 POS：** 3 組 ✅
- **停用的 POS：** 1 組 ❌

### 公司分布
- **公司 1：** 3 組 POS（1 組停用，2 組啟用）
- **公司 2：** 1 組 POS（啟用）

### 名稱分析
- **Shop** - 商店 POS（停用）
- **Restaurant** - 餐廳 POS（啟用，公司 2）
- **上品聊國咖啡館重新總店** - 咖啡館 POS（啟用，公司 1，有 2 組相同名稱）

---

## 🔍 詳細資訊查詢

### 查詢所有 POS 配置
```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT id, name, active, company_id FROM pos_config ORDER BY id;"
```

### 查詢啟用的 POS
```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT id, name, active, company_id FROM pos_config WHERE active = true ORDER BY id;"
```

### 查詢特定公司的 POS
```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT id, name, active FROM pos_config WHERE company_id = 1 ORDER BY id;"
```

### 查詢 POS 會話
```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT config_id, COUNT(*) as session_count FROM pos_session GROUP BY config_id;"
```

### 查詢 POS 訂單
```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT config_id, COUNT(*) as order_count FROM pos_order GROUP BY config_id ORDER BY config_id;"
```

### 當前狀態
- **POS 會話：** 0 個（目前沒有開啟的會話）
- **POS 訂單：** 0 個（目前沒有訂單記錄）

---

## 📝 注意事項

### 重複名稱
- **發現：** ID 3 和 ID 4 有相同的名稱「上品聊國咖啡館重新總店」
- **建議：** 考慮重新命名以區分不同的 POS 配置

### 停用的 POS
- **Shop (ID: 1)** 目前停用
- **建議：** 如果不需要，可以考慮刪除或重新啟用

---

## 🎯 管理建議

### 通過 Odoo 網頁介面管理

1. **訪問 POS 配置**
   - URL: http://localhost:8069
   - 前往：銷售點 > 配置 > 銷售點

2. **查看 POS 列表**
   - 可以看到所有 4 組 POS 系統
   - 可以查看每組的詳細配置

3. **管理 POS**
   - 啟用/停用 POS
   - 編輯 POS 配置
   - 刪除不需要的 POS

---

## ✅ 總結

**POS 系統狀態：**
- ✅ 總數：4 組
- ✅ 啟用：3 組
- ✅ 停用：1 組
- ⚠️ 注意：有 2 組相同名稱的 POS

**系統運行正常，可以正常使用！**

---

**檢查完成時間：** 2026-01-20
