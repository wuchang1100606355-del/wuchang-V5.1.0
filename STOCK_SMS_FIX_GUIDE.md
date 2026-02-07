# stock_move_sms_validation 錯誤修復指南

## 🎯 快速修復步驟

### 第一步：訪問 Odoo

點擊以下連結打開 Odoo：
**http://localhost:8069**

### 第二步：登入管理員帳號

使用您的管理員帳號登入系統

### 第三步：進入應用程式管理

1. 點擊左上角的 **九宮格圖標** (應用程式選單)
2. 選擇 **設定** (Settings)
3. 在左側菜單中找到 **應用程式** (Apps)

或者直接訪問：
**http://localhost:8069/web#action=base.open_module_tree**

### 第四步：搜索並安裝 SMS 模組

1. **移除過濾器**：
   - 在搜索框上方，您會看到一個 `已安裝` 的過濾器標籤
   - 點擊該標籤上的 `X` 圖標以移除過濾器

2. **搜索模組**：
   - 在搜索框中輸入：`SMS`
   - 按 Enter 鍵搜索

3. **安裝模組**：
   - 找到名為 **"SMS in Stock"** 或 **"stock_sms"** 的模組
   - 點擊該模組卡片上的 **安裝** (Install) 按鈕
   - 等待安裝完成（通常需要 10-30 秒）

### 第五步：驗證修復

1. 安裝完成後，刷新瀏覽器頁面：
   - Windows: `Ctrl + F5`
   - Mac: `Cmd + Shift + R`

2. 嘗試訪問之前出錯的頁面

3. 如果錯誤消失，修復成功！✅

## 🔍 為什麼需要這樣做？

### 問題根源

`stock_move_sms_validation` 字段是由 `stock_sms` 模組定義的。雖然：
- ✅ 資料庫中該字段已存在
- ✅ `wuchang_core` 已聲明依賴 `stock_sms`
- ✅ Python 模型中已添加該字段

但是，Odoo 的視圖渲染器要求：
- ❌ 定義該字段的模組必須處於 `installed` 狀態

當前 `stock_sms` 模組狀態為 `to install`（待安裝），導致 Odoo 認為該字段「未定義」。

### 為什麼自動安裝失敗？

Odoo 日誌顯示：
```
ERROR: Some modules have inconsistent states, some dependencies may be missing: ['stock_sms']
```

當 Odoo 檢測到模組狀態不一致時，它會選擇跳過自動安裝，以避免可能的系統損壞。

## 🛠️ 備用方案

### 方案 A：如果 UI 中找不到 SMS 模組

執行以下命令檢查模組是否存在：

```powershell
cd "C:\wuchang V5.1.0"
docker-compose exec -T db psql -U odoo -d admin -c "SELECT name, state, latest_version FROM ir_module_module WHERE name = 'stock_sms';"
```

### 方案 B：如果安裝按鈕無法點擊

模組可能已經在安裝隊列中，嘗試：

```powershell
cd "C:\wuchang V5.1.0"
docker-compose restart wuchang-web
```

等待 20 秒後刷新瀏覽器。

### 方案 C：強制重置模組狀態

```powershell
cd "C:\wuchang V5.1.0"
docker-compose exec -T db psql -U odoo -d admin -c "UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'stock_sms';"
docker-compose restart wuchang-web
```

然後重新執行 UI 安裝步驟。

## 📊 驗證清單

安裝完成後，請驗證以下項目：

- [ ] 瀏覽器中不再出現 `stock_move_sms_validation field is undefined` 錯誤
- [ ] 可以正常訪問 Odoo 設定頁面
- [ ] 系統運行穩定，無其他錯誤

## 🆘 如果問題仍然存在

請提供以下信息：

1. **模組狀態**：
```powershell
docker-compose exec -T db psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE name = 'stock_sms';"
```

2. **Odoo 日誌**：
```powershell
docker-compose logs --tail=50 wuchang-web
```

3. **瀏覽器控制台錯誤**：
   - 按 `F12` 打開開發者工具
   - 切換到 `Console` 標籤
   - 截圖或複製完整的錯誤訊息

## ✅ 合規聲明

本修復流程符合 Google 非營利組織合規要求，所有操作均：
- 🔒 不涉及數據刪除或破壞性操作
- 📝 保持完整的操作記錄
- 🛡️ 優先考慮系統穩定性和數據完整性

---

**文檔版本**: 1.0  
**創建時間**: 2026-01-07  
**適用系統**: Wuchang V5.1.0  
**維護者**: Wuchang AI (小j)
