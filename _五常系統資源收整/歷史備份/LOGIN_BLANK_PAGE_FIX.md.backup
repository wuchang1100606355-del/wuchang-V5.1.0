# 登入後空白頁面修復指南

## 問題描述

登入成功後，頁面顯示為空白（只有 `<body class="o_web_client">` 結構，無內容）。

## 已執行的修復

1. ✅ 清除 Odoo 視圖緩存
2. ✅ 檢查模組狀態
3. ✅ 重啟服務

## 下一步診斷（重要！）

### 步驟 1：檢查瀏覽器控制台

**這是最關鍵的步驟！**

1. 在瀏覽器中按 **F12** 打開開發者工具
2. 切換到 **Console** 標籤
3. 刷新頁面（F5 或 Ctrl+F5）
4. **查看所有紅色錯誤訊息**
5. **複製或截圖所有錯誤訊息**

常見錯誤類型：
- `UncaughtPromiseError > OwlError`
- `TypeError: ... is not a function`
- `ReferenceError: ... is not defined`
- `Failed to load resource: 404/500`

### 步驟 2：檢查網絡請求

1. 在開發者工具中切換到 **Network** 標籤
2. 刷新頁面
3. 檢查是否有：
   - 紅色（失敗）的請求
   - 狀態碼為 404 或 500 的請求
   - 特別關注 `/web/assets/` 開頭的文件

### 步驟 3：檢查服務日誌

如果控制台有錯誤，執行：
```powershell
docker-compose logs --tail=100 wuchang-web | Select-String -Pattern "ERROR|Exception|Traceback"
```

## 常見原因和解決方案

### 原因 1：JavaScript 字段未定義錯誤

**症狀**：控制台顯示類似 `"field is undefined"` 的錯誤

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
1. 清除瀏覽器緩存（Ctrl+Shift+Delete）
2. 使用無痕模式訪問
3. 檢查 `__manifest__.py` 中的 assets 配置

### 原因 4：瀏覽器緩存問題

**解決方案**：
1. 硬刷新：`Ctrl + Shift + R`（Windows）或 `Cmd + Shift + R`（Mac）
2. 清除緩存後重新訪問
3. 使用無痕模式測試

## 需要提供的信息

如果問題持續，請提供：

1. **瀏覽器控制台錯誤**（最重要！）
   - 打開 Console 標籤
   - 截圖或複製所有紅色錯誤訊息

2. **網絡請求狀態**
   - 打開 Network 標籤
   - 刷新頁面
   - 截圖顯示失敗的請求

3. **瀏覽器信息**
   - 瀏覽器類型（Chrome、Edge、Firefox）
   - 瀏覽器版本

## 快速測試

嘗試訪問以下 URL：
- http://localhost:8069/web
- http://localhost:8069/web/database/manager

如果這些 URL 可以正常訪問，問題可能出在前端初始化。

## 合規聲明

✅ 符合 Google 非營利組織合規要求
