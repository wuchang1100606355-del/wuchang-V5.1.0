# Odoo 空白頁面故障排除指南

## 問題描述

頁面結構已加載（`<body class="o_web_client">`），但內容完全為空。

## 可能的原因

1. **JavaScript 執行錯誤**：前端 JavaScript 在初始化時發生錯誤
2. **資源加載失敗**：某些關鍵資源（JS/CSS）未正確加載
3. **模組載入問題**：Odoo 模組載入失敗導致前端無法初始化

## 診斷步驟

### 1. 檢查瀏覽器控制台（重要！）

在開發者工具中：
1. 切換到 **Console** 標籤
2. 查看是否有紅色錯誤訊息
3. 記錄所有錯誤訊息

常見錯誤：
- `TypeError: ... is not a function`
- `ReferenceError: ... is not defined`
- `Failed to load resource: 404/500`
- `UncaughtPromiseError`

### 2. 檢查網絡請求

在開發者工具中：
1. 切換到 **Network** 標籤
2. 刷新頁面（F5）
3. 檢查是否有紅色（失敗）的請求
4. 特別關注：
   - `/web/assets/` 開頭的 JS 文件
   - `/web/assets/` 開頭的 CSS 文件
   - `/web/database/manager` 或類似的初始化請求

### 3. 檢查服務日誌

執行以下命令查看服務端錯誤：
```powershell
docker-compose logs --tail=100 wuchang-web | Select-String -Pattern "ERROR|Exception"
```

## 快速修復嘗試

### 方法 1：清除 Odoo 緩存

```powershell
cd "C:\wuchang V5.1.0"
docker-compose exec -T db psql -U odoo -d admin -c "UPDATE ir_ui_view SET write_date = NOW();"
docker-compose restart wuchang-web
```

### 方法 2：重啟服務

```powershell
docker-compose restart wuchang-web
```

等待 20-30 秒後刷新頁面。

### 方法 3：檢查資料庫連接

確認資料庫正常運行：
```powershell
docker-compose ps db
```

## 常見解決方案

### 如果控制台顯示 JavaScript 錯誤

1. **字段未定義錯誤**：
   - 可能還有其他模型字段未添加到資料庫
   - 檢查錯誤訊息中的字段名稱
   - 添加缺失字段到對應表

2. **模組載入錯誤**：
   - 檢查 `wuchang_core` 模組是否正確安裝
   - 嘗試升級模組：
   ```powershell
   docker-compose exec -T wuchang-web odoo -d admin -u wuchang_core --stop-after-init
   ```

3. **資源路徑錯誤**：
   - 檢查 `__manifest__.py` 中的 assets 配置
   - 確認靜態文件路徑正確

## 需要提供的信息

如果問題持續，請提供：

1. **瀏覽器控制台錯誤**：
   - 打開 Console 標籤
   - 截圖或複製所有紅色錯誤訊息

2. **網絡請求狀態**：
   - 打開 Network 標籤
   - 刷新頁面
   - 截圖顯示失敗的請求

3. **服務日誌**：
   - 執行 `docker-compose logs --tail=100 wuchang-web` 的輸出

## 合規聲明

✅ 符合 Google 非營利組織合規要求
