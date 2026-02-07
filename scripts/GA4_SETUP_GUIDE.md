# Google Analytics 4 設定指南

## 步驟 1: 建立 GA4 屬性

1. 前往 [Google Analytics](https://analytics.google.com/)
2. 建立新的 GA4 屬性
3. 取得測量 ID（格式：G-XXXXXXXXXX）

## 步驟 2: 更新 HTML 檔案

在以下檔案中更新 Google Analytics ID：
- `index.html`
- `about.html`
- `mission.html`
- `contact.html`

將 `G-XXXXXXXXXX` 替換為您的實際 GA4 測量 ID。

## 步驟 3: 配置轉換事件

在 Google Analytics 中設定轉換事件：
1. 前往「管理」>「事件」
2. 標記重要事件為「轉換」
3. 建議的轉換事件：
   - 聯絡表單提交
   - 頁面瀏覽（關鍵頁面）
   - 下載（如有提供下載）

## 步驟 4: 驗證安裝

1. 使用 [Google Tag Assistant](https://tagassistant.google.com/) 驗證
2. 在 GA4 中查看即時報表確認資料接收

## 注意事項

- 確保符合 GDPR 和隱私權政策
- 考慮添加 Cookie 同意橫幅
- 定期檢查轉換追蹤是否正常運作
