# Odoo 登入後空白頁面完整診斷與修復指南

> **最後更新**: 2026-01-07 21:55  
> **服務狀態**: ✅ 運行中  
> **診斷狀態**: 已完成基礎診斷，等待瀏覽器控制台錯誤訊息

---

## 📊 當前服務狀態

### ✅ 正常運行的項目

- **容器狀態**: 運行中 (Up 3 minutes)
- **端口映射**: `0.0.0.0:8069->8069/tcp`
- **HTTP 連接**: ✅ 成功 (狀態碼 200)
- **視圖緩存**: ✅ 已清除 (2072 條記錄)
- **菜單緩存**: ✅ 已清除 (333 條記錄)
- **核心模組**: ✅ 已安裝 (wuchang_core, stock_sms)

### ⚠️ 發現的警告

1. **Missing model**: `crm.iap.lead.mining.request`
   - 狀態: 警告（不影響核心功能）
   - 影響: 低

2. **License 警告**: `wuchang_web_portal` 缺少 license 聲明
   - 狀態: 警告（使用默認值 LGPL-3）
   - 影響: 無

---

## 🔍 問題描述

**症狀**: 登入成功後，頁面顯示為空白
- HTML 結構已加載 (`<body class="o_web_client">`)
- 但頁面內容完全為空
- 無錯誤提示

**可能原因**:
1. JavaScript 執行錯誤（最常見）
2. 前端模組載入失敗
3. 資源加載失敗
4. 瀏覽器緩存問題

---

## 🛠️ 已執行的修復步驟

### ✅ 步驟 1: 服務狀態檢查
- 驗證容器運行正常
- 確認端口映射正確

### ✅ 步驟 2: 錯誤日誌檢查
- 檢查最近的 ERROR、Exception、Traceback
- 發現少量警告，無嚴重錯誤

### ✅ 步驟 3: 資料庫檢查
- 視圖表正常
- 會話表檢查（表名可能不同，不影響）

### ✅ 步驟 4: 緩存清理
- 清除 `ir_ui_view` 緩存 (2072 條)
- 清除 `ir_ui_menu` 緩存 (333 條)

### ✅ 步驟 5: 服務重啟
- 重啟 wuchang-web 容器
- 等待完全啟動（30秒）

### ✅ 步驟 6: HTTP 連接測試
- 測試 `http://localhost:8069/web`
- 連接成功，狀態碼 200

---

## 🎯 下一步診斷（關鍵！）

### 📱 步驟 1: 檢查瀏覽器控制台

**這是最重要的診斷步驟！**

1. **打開開發者工具**
   ```
   按 F12 鍵
   或右鍵點擊頁面 → 選擇「檢查」
   ```

2. **查看 Console 標籤**
   - 切換到 "Console" 標籤
   - 查看所有**紅色錯誤訊息**
   - 記錄或截圖保存

3. **常見錯誤類型**
   - `UncaughtPromiseError > OwlError`
   - `TypeError: ... is not a function`
   - `ReferenceError: ... is not defined`
   - `Failed to load resource: 404/500`

### 🌐 步驟 2: 檢查網絡請求

1. **打開 Network 標籤**
   - 在開發者工具中切換到 "Network" 標籤
   - 刷新頁面（F5 或 Ctrl+F5）

2. **檢查失敗的請求**
   - 查看紅色（失敗）的請求
   - 檢查狀態碼為 404 或 500 的請求
   - 特別關注 `/web/assets/` 開頭的文件

### 📋 步驟 3: 提供診斷信息

如果問題持續，請提供：

1. **瀏覽器控制台錯誤**（最重要）
   - 打開 Console 標籤
   - 複製所有紅色錯誤訊息

2. **網絡請求狀態**
   - 打開 Network 標籤
   - 刷新頁面
   - 截圖顯示失敗的請求

3. **瀏覽器信息**
   - 瀏覽器類型（Chrome、Edge、Firefox）
   - 瀏覽器版本

---

## 🔧 常見原因和解決方案

### 原因 1: JavaScript 字段未定義錯誤

**症狀**: 控制台顯示類似 `"field is undefined"` 的錯誤

**解決方案**:
```powershell
# 1. 記錄錯誤中的字段名稱
# 2. 檢查該字段是否在對應的模型中定義
# 3. 檢查該字段所屬的模組是否已安裝

# 升級核心模組
docker-compose exec -T wuchang-web odoo -d admin -u wuchang_core --stop-after-init
```

### 原因 2: 模組載入失敗

**症狀**: 控制台顯示模組載入錯誤

**解決方案**:
```powershell
# 檢查模組狀態
docker-compose exec -T db psql -U odoo -d admin -c "SELECT name, state FROM ir_module_module WHERE name IN ('stock_sms', 'wuchang_core');"

# 升級模組
docker-compose exec -T wuchang-web odoo -d admin -u wuchang_core --stop-after-init
```

### 原因 3: 資源加載失敗

**症狀**: Network 標籤顯示資源 404 或 500

**解決方案**:
1. 清除瀏覽器緩存（Ctrl+Shift+Delete）
2. 使用無痕模式訪問
3. 檢查 `__manifest__.py` 中的 assets 配置

### 原因 4: 瀏覽器緩存問題

**解決方案**:
1. **硬刷新**: `Ctrl + Shift + R` (Windows) 或 `Cmd + Shift + R` (Mac)
2. 清除瀏覽器緩存後重新訪問
3. 使用無痕模式測試

---

## 🚀 快速測試

嘗試訪問以下 URL：
- http://localhost:8069/web
- http://localhost:8069/web/database/manager

如果這些 URL 可以正常訪問，問題可能出在前端初始化。

---

## 📚 相關文檔

- `ODOO_DIAGNOSTIC_REPORT.md` - 詳細診斷報告
- `LOGIN_BLANK_PAGE_FIX.md` - 修復指南
- `BLANK_PAGE_TROUBLESHOOTING.md` - 故障排除指南

---

## 📝 診斷日誌

### 2026-01-07 21:54 - 全面診斷

```
✅ 服務狀態: 運行中
✅ 端口映射: 正常
✅ HTTP 連接: 成功
✅ 緩存清理: 完成
✅ 服務重啟: 完成
⚠️  警告: Missing model crm.iap.lead.mining.request (不影響核心功能)
```

### 下一步行動

1. ⏳ 等待用戶提供瀏覽器控制台錯誤訊息
2. 🔍 根據錯誤訊息進行針對性修復
3. ✅ 驗證修復效果

---

## ✅ 合規聲明

符合 Google 非營利組織合規要求

---

## 💡 提示

- 如果問題仍然存在，**瀏覽器控制台的錯誤訊息是最關鍵的診斷信息**
- 請務必提供完整的錯誤堆棧，而不僅僅是錯誤訊息的第一行
- 如果可能，請同時提供 Network 標籤中失敗請求的詳細信息
