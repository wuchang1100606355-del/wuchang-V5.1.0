# 空白頁問題診斷步驟

## 🔍 當前診斷狀態

### 已檢查項目
- ✅ 容器運行狀態：正常
- ✅ HTTP 連接：成功 (200)
- ✅ 服務端日誌：無嚴重錯誤
- ✅ 模組狀態：已安裝

### 待確認項目
- ⏳ **瀏覽器控制台錯誤**（最關鍵！）
- ⏳ 前端資源加載狀態
- ⏳ JavaScript 執行錯誤

---

## 📱 必須執行的診斷步驟

### 步驟 1：檢查瀏覽器控制台（最重要！）

**這是診斷空白頁問題的關鍵步驟！**

1. **打開開發者工具**
   - 按 `F12` 鍵
   - 或右鍵點擊頁面 → 選擇「檢查」

2. **查看 Console 標籤**
   - 切換到 "Console" 標籤
   - **查看所有紅色錯誤訊息**
   - **複製或截圖所有錯誤訊息**

3. **常見錯誤類型**
   ```
   UncaughtPromiseError > OwlError
   TypeError: ... is not a function
   ReferenceError: ... is not defined
   Failed to load resource: 404/500
   ```

### 步驟 2：檢查網絡請求

1. **打開 Network 標籤**
   - 在開發者工具中切換到 "Network" 標籤
   - **清除網絡日誌**（點擊 🚫 圖標）
   - **刷新頁面**（F5 或 Ctrl+F5）

2. **檢查失敗的請求**
   - 查看**紅色**（失敗）的請求
   - 檢查狀態碼為 **404** 或 **500** 的請求
   - 特別關注：
     - `/web/assets/` 開頭的文件
     - `/web/webclient/` 開頭的文件
     - `/web/database/manager` 或類似的初始化請求

3. **截圖或記錄**
   - 截圖顯示失敗的請求
   - 記錄請求的 URL 和狀態碼

### 步驟 3：檢查頁面源代碼

1. **查看頁面 HTML**
   - 在開發者工具中切換到 "Elements" 標籤
   - 查看 `<body>` 標籤的內容
   - 檢查是否有 JavaScript 錯誤阻止渲染

2. **檢查資源加載**
   - 查看 `<head>` 標籤中的 `<script>` 和 `<link>` 標籤
   - 確認所有資源路徑正確

---

## 🔧 快速修復嘗試

### 方法 1：清除瀏覽器緩存

1. **硬刷新頁面**
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **清除瀏覽器緩存**
   - 按 `Ctrl + Shift + Delete`
   - 選擇「緩存的圖片和文件」
   - 點擊「清除數據」

3. **使用無痕模式**
   - 按 `Ctrl + Shift + N` (Chrome) 或 `Ctrl + Shift + P` (Firefox)
   - 訪問 http://localhost:8069

### 方法 2：檢查服務端配置

```powershell
# 檢查 Odoo 配置
docker-compose exec -T wuchang-web cat /etc/odoo/odoo.conf 2>&1 | Select-String -Pattern "workers|max_cron_threads"
```

### 方法 3：重啟服務並清除緩存

```powershell
# 清除視圖緩存
docker-compose exec -T db psql -U odoo -d admin -c "UPDATE ir_ui_view SET write_date = NOW();"

# 重啟服務
docker-compose restart wuchang-web

# 等待 30 秒後刷新頁面
```

---

## 📋 需要提供的信息

如果問題持續，請提供：

### 1. 瀏覽器控制台錯誤（最重要！）
- 打開 Console 標籤
- **複製所有紅色錯誤訊息**
- 或截圖保存

### 2. 網絡請求狀態
- 打開 Network 標籤
- 刷新頁面
- **截圖顯示失敗的請求**

### 3. 瀏覽器信息
- 瀏覽器類型（Chrome、Edge、Firefox）
- 瀏覽器版本
- 操作系統版本

### 4. 問題發生時機
- 登入後立即空白？
- 還是載入一段時間後空白？
- 是否有任何內容短暫顯示？

---

## 🎯 常見原因和解決方案

### 原因 1：JavaScript 字段未定義錯誤

**症狀**：控制台顯示 `"field is undefined"` 或類似錯誤

**解決方案**：
1. 記錄錯誤中的字段名稱
2. 檢查該字段是否在對應的模型中定義
3. 檢查該字段所屬的模組是否已安裝

### 原因 2：模組載入失敗

**症狀**：控制台顯示模組載入錯誤

**解決方案**：
```powershell
# 升級核心模組
docker-compose exec -T wuchang-web odoo -d admin -u wuchang_core --stop-after-init
```

### 原因 3：資源加載失敗

**症狀**：Network 標籤顯示資源 404 或 500

**解決方案**：
1. 清除瀏覽器緩存
2. 檢查 `__manifest__.py` 中的 assets 配置
3. 重啟服務

### 原因 4：瀏覽器兼容性問題

**症狀**：特定瀏覽器出現問題

**解決方案**：
1. 嘗試其他瀏覽器
2. 更新瀏覽器到最新版本
3. 禁用瀏覽器擴展

---

## ✅ 合規聲明

符合 Google 非營利組織合規要求

---

## 💡 重要提示

**空白頁問題的診斷關鍵是瀏覽器控制台的錯誤訊息！**

沒有控制台錯誤訊息，很難準確診斷問題。請務必：
1. 打開開發者工具（F12）
2. 查看 Console 標籤
3. 複製或截圖所有錯誤訊息
4. 發送給我進行進一步診斷
