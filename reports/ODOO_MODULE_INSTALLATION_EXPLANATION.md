# Odoo 模組安裝狀態說明

**檢查時間：** 2026-01-20  
**資料庫：** admin

---

## 🔍 當前狀態

### 模組統計

- **總模組數：** 658 個
- **已安裝模組：** 11 個（僅基礎模組）
- **未安裝模組：** 647 個

### 已安裝的模組（11個）

目前資料庫中標記為 `installed` 狀態的模組：

1. `auth_totp` - 雙因素驗證
2. `base` - 基礎模組（核心）
3. `base_import` - 資料匯入
4. `base_import_module` - 模組匯入
5. `base_setup` - 基礎設定
6. `bus` - 訊息匯流排
7. `iap` - 應用內購買
8. `web` - Web 介面（核心）
9. `web_editor` - 網頁編輯器
10. `web_tour` - 網頁導覽

---

## ❓ 為什麼資料庫中沒有更多已安裝模組？

### 原因說明

這是 **正常的 Odoo 行為**。原因如下：

1. **基礎安裝模式**
   - Odoo 預設只安裝核心基礎模組
   - 業務模組（sale, purchase, account等）需要手動安裝
   - 這是為了讓用戶選擇所需的業務功能

2. **模組狀態**
   - `installed` - 已安裝並啟用
   - `uninstalled` - 未安裝（但存在於系統中）
   - `to install` - 待安裝
   - `to upgrade` - 待升級

3. **安裝流程**
   - 模組需要在 Odoo 介面中選擇安裝
   - 或通過命令列安裝
   - 安裝後才會更新資料庫中的狀態

---

## ✅ 解決方案

### 方法 1：通過 Odoo 網頁介面安裝（推薦）

1. **訪問 Odoo**
   ```
   http://localhost:8069
   ```

2. **登入管理員帳號**

3. **安裝模組**
   - 前往：**應用程式**
   - 點擊：**更新應用程式清單**
   - 搜尋要安裝的模組（如：sale, purchase, account）
   - 點擊：**安裝** 按鈕

4. **常用業務模組**
   - `sale` - 銷售管理
   - `purchase` - 採購管理
   - `account` - 會計模組
   - `stock` - 庫存管理
   - `crm` - 客戶關係管理
   - `project` - 專案管理
   - `website` - 網站功能

### 方法 2：通過命令列安裝

```bash
# 安裝特定模組（例如：sale）
docker exec wuchang-wuchang-web-1 odoo-bin -d admin -u sale --stop-after-init

# 安裝多個模組
docker exec wuchang-wuchang-web-1 odoo-bin -d admin -u sale,purchase,account --stop-after-init

# 安裝所有模組（不建議，會安裝太多不需要的模組）
# docker exec wuchang-wuchang-web-1 odoo-bin -d admin -u all --stop-after-init
```

### 方法 3：通過資料庫直接更新（不推薦）

```sql
-- 注意：此方法可能導致模組狀態不一致，建議使用前兩種方法
UPDATE ir_module_module 
SET state = 'to install' 
WHERE name IN ('sale', 'purchase', 'account');

-- 然後重啟 Odoo 讓它安裝模組
```

---

## 📋 建議安裝的模組

### 核心業務模組

| 模組 | 說明 | 建議安裝 |
|------|------|---------|
| `sale` | 銷售管理 | ✅ 是 |
| `purchase` | 採購管理 | ✅ 是 |
| `account` | 會計模組 | ✅ 是 |
| `stock` | 庫存管理 | ✅ 是 |
| `crm` | 客戶關係管理 | ✅ 是 |
| `project` | 專案管理 | ✅ 是 |

### 網站與介面

| 模組 | 說明 | 建議安裝 |
|------|------|---------|
| `website` | 網站功能 | ✅ 是 |
| `portal` | 客戶入口網站 | ⚠️ 可選 |

### 其他功能模組

| 模組 | 說明 | 建議安裝 |
|------|------|---------|
| `hr` | 人力資源 | ⚠️ 可選 |
| `calendar` | 行事曆 | ⚠️ 可選 |
| `mail` | 郵件功能 | ✅ 是 |
| `contacts` | 聯絡人管理 | ✅ 是 |

---

## 🔧 檢查模組安裝狀態

### 查詢已安裝模組

```bash
docker exec wuchang-db-1 psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE state='installed' ORDER BY name;"
```

### 查詢模組狀態分布

```bash
docker exec wuchang-db-1 psql -U odoo -d admin -c "SELECT state, COUNT(*) as count FROM ir_module_module GROUP BY state ORDER BY count DESC;"
```

### 查詢特定模組狀態

```bash
docker exec wuchang-db-1 psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE name IN ('sale', 'purchase', 'account', 'stock') ORDER BY name;"
```

---

## 📝 總結

**當前狀態：**
- ✅ 資料庫中有 658 個模組記錄
- ✅ 11 個基礎模組已安裝
- ⚠️ 其他業務模組需要手動安裝

**這是正常現象，因為：**
- Odoo 預設只安裝核心基礎模組
- 業務模組需要根據需求選擇安裝
- 可以通過 Odoo 介面輕鬆安裝所需模組

**建議行動：**
1. 通過 Odoo 網頁介面安裝所需的業務模組
2. 不要一次性安裝所有模組
3. 根據實際業務需求選擇性安裝

---

**說明時間：** 2026-01-20  
**狀態：** 正常，需要手動安裝業務模組
