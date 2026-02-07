# POS（銷售點）系統檢查總結

## 📊 檢查結果

**檢查時間：** 2026-01-20  
**資料庫：** admin

---

## ✅ POS 系統總數

**共有 4 組 POS 系統**

---

## 📋 POS 系統列表

### 1. Shop
- **ID：** 1
- **狀態：** ❌ 停用
- **公司：** 公司 1

### 2. Restaurant
- **ID：** 2
- **狀態：** ✅ 啟用
- **公司：** 公司 2

### 3. 上品聊國咖啡館重新總店
- **ID：** 3
- **狀態：** ✅ 啟用
- **公司：** 公司 1

### 4. 上品聊國咖啡館重新總店
- **ID：** 4
- **狀態：** ✅ 啟用
- **公司：** 公司 1

---

## 📊 統計資訊

### 啟用狀態
- **啟用的 POS：** 3 組 ✅
- **停用的 POS：** 1 組 ❌

### 公司分布
- **公司 1：** 3 組 POS
  - Shop（停用）
  - 上品聊國咖啡館重新總店（啟用，ID: 3）
  - 上品聊國咖啡館重新總店（啟用，ID: 4）
- **公司 2：** 1 組 POS
  - Restaurant（啟用）

### 使用情況
- **POS 會話：** 0 個（目前沒有開啟的會話）
- **POS 訂單：** 0 個（目前沒有訂單記錄）

---

## ⚠️ 注意事項

### 1. 重複名稱
- **發現：** ID 3 和 ID 4 有相同的名稱「上品聊國咖啡館重新總店」
- **建議：** 考慮重新命名以區分不同的 POS 配置
  - 例如：上品聊國咖啡館重新總店 - 櫃台1
  - 例如：上品聊國咖啡館重新總店 - 櫃台2

### 2. 停用的 POS
- **Shop (ID: 1)** 目前停用
- **建議：** 
  - 如果不需要，可以考慮刪除
  - 如果需要，可以重新啟用

---

## 🔍 管理方式

### 通過 Odoo 網頁介面

1. **訪問 POS 配置**
   ```
   http://localhost:8069
   ```

2. **前往 POS 管理**
   - 銷售點 > 配置 > 銷售點
   - 可以看到所有 4 組 POS 系統

3. **管理操作**
   - 查看 POS 詳細配置
   - 啟用/停用 POS
   - 編輯 POS 設定
   - 刪除不需要的 POS

---

## 📝 查詢命令

### 查詢所有 POS
```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT id, name, active, company_id FROM pos_config ORDER BY id;"
```

### 查詢啟用的 POS
```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT id, name, active FROM pos_config WHERE active = true ORDER BY id;"
```

### 查詢特定公司的 POS
```bash
docker exec wuchangv510-db-1 psql -U odoo -d admin -c "SELECT id, name, active FROM pos_config WHERE company_id = 1 ORDER BY id;"
```

---

## ✅ 總結

**POS 系統狀態：**
- ✅ 總數：**4 組**
- ✅ 啟用：**3 組**
- ✅ 停用：**1 組**
- ⚠️ 注意：有 2 組相同名稱的 POS

**系統運行正常，可以正常使用！**

---

**檢查完成時間：** 2026-01-20
