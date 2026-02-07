# 五常 AI 瀏覽器代理功能使用指南

## 功能概述

小 j AI 控制台現已整合 **瀏覽器代理功能**，類似 ChatGPT 的網頁瀏覽能力，可以：

-   🔍 執行網頁搜尋（使用 DuckDuckGo）
-   🌐 直接訪問並擷取網頁內容
-   💬 將搜尋/網頁內容交給小 j AI 分析理解

---

## 使用方式

### 1. 啟動瀏覽模式

在控制台 GUI 中點擊 **「🌐 瀏覽模式: OFF」** 按鈕：

-   啟用後按鈕變為綠色 **「🌐 瀏覽模式: ON」**
-   聊天視窗會顯示可用指令

### 2. 網頁搜尋

**語法：**

```
搜尋：關鍵字
```

或

```
search:keyword
```

**範例：**

```
搜尋：Azure Vertex AI 整合方式
```

**流程：**

1. 系統自動使用 DuckDuckGo 搜尋引擎
2. 抓取前 5 筆搜尋結果摘要
3. 顯示搜尋結果在聊天視窗
4. 小 j AI 根據搜尋結果回答原問題

---

### 3. 訪問網頁

**語法：**

```
訪問：https://example.com
```

或

```
visit:https://example.com
```

**範例：**

```
訪問：https://cloud.google.com/vertex-ai/docs
```

**流程：**

1. 系統使用 PowerShell 的 Invoke-WebRequest 抓取網頁
2. 自動移除 HTML 標籤、Script、CSS
3. 擷取前 2000 字純文字內容
4. 小 j AI 分析網頁內容並回應

---

### 4. 自動偵測網址

**直接輸入含有網址的問題：**

```
https://example.com 這個網站在說什麼？
```

系統會自動：

-   偵測 URL（http:// 或 https://）
-   抓取網頁內容
-   替換原問題中的 URL 為網頁內容
-   交給小 j 分析

---

## 技術實現

### 後端邏輯（PowerShell）

```powershell
# 網頁搜尋
function Search-Web($query) {
    $encodedQuery = [System.Web.HttpUtility]::UrlEncode($query)
    $searchUrl = "https://html.duckduckgo.com/html/?q=$encodedQuery"
    $response = Invoke-WebRequest -Uri $searchUrl -UseBasicParsing -TimeoutSec 10
    # 解析搜尋結果...
}

# 網頁抓取
function Fetch-Webpage($url) {
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 15
    # 清理 HTML 標籤...
    return $content.Substring(0, [Math]::Min(2000, $content.Length))
}
```

### AI 整合流程

```
[用戶輸入]
    ↓
[瀏覽模式檢查]
    ↓
[搜尋/訪問處理] → [網頁內容擷取]
    ↓
[內容注入提示詞]
    ↓
[Docker exec → Odoo Shell] → [wuchang.ai.logic.analyze_operations()]
    ↓
[小j AI 回應]
```

---

## 安全設計

### 超時保護

-   搜尋請求：10 秒超時
-   網頁抓取：15 秒超時
-   避免長時間卡住

### 內容限制

-   網頁內容僅擷取前 2000 字
-   避免過長內容影響 AI 推理
-   自動清理 HTML/Script/CSS

### 隱私保護

-   使用 DuckDuckGo（不追蹤搜尋）
-   不儲存瀏覽歷史
-   所有請求在本地執行

---

## 使用場景

### 1. 技術文件查詢

```
搜尋：Python asyncio best practices 2026
```

### 2. 即時資訊獲取

```
訪問：https://status.cloud.google.com
小j 幫我看一下 GCP 現在的服務狀態
```

### 3. 競品分析

```
訪問：https://competitor.com/pricing
小j 幫我分析這個定價策略
```

### 4. 技術問題排查

```
搜尋：Odoo 17 database connection refused docker
小j 根據這些結果幫我解決問題
```

---

## 限制與注意事項

### 當前限制

1. **無 JavaScript 執行**：只能抓取靜態 HTML
2. **無驗證登入**：無法訪問需要登入的頁面
3. **搜尋引擎單一**：目前僅支援 DuckDuckGo
4. **內容長度限制**：網頁內容僅 2000 字

### 防止濫用

-   瀏覽模式需手動啟用
-   每次請求都有超時限制
-   錯誤處理友善提示

### 最佳實踐

-   優先使用「搜尋」而非直接訪問未知網站
-   對於已知網站使用「訪問」獲取精確內容
-   若網頁過長，可先搜尋摘要再訪問

---

## 故障排除

### 搜尋失敗

**症狀：** 顯示「搜尋失敗」
**原因：** DuckDuckGo 網站無法訪問或網路問題
**解決：** 檢查網路連線，或稍後重試

### 網頁無法取得

**症狀：** 顯示「無法取得網頁」
**原因：**

-   網站有 Cloudflare 保護
-   網站需要 JavaScript
-   網路逾時

**解決：**

1. 改用「搜尋」找相關摘要
2. 確認網址正確
3. 檢查網站是否需要登入

### AI 回應異常

**症狀：** 小 j 回應錯誤或不相關
**原因：** 網頁內容過於複雜或格式化問題
**解決：**

1. 使用更精確的搜尋關鍵字
2. 訪問官方文件而非論壇
3. 將問題拆解成多次查詢

---

## 開發者資訊

### 檔案位置

-   GUI 腳本：`tools/local_root_control_gui.ps1`
-   文件：`docs/AI_BROWSER_AGENT_USAGE.md`

### 相依套件

```powershell
Add-Type -AssemblyName System.Web  # URL 編碼
```

### 擴展建議

未來可增強：

-   支援多搜尋引擎（Google/Bing）
-   Playwright/Selenium 執行 JavaScript
-   網頁截圖功能
-   搜尋歷史記錄
-   更智能的內容摘要

---

## 版本歷史

### v5.1.0 (2026-01-08)

-   ✅ 新增瀏覽模式切換按鈕
-   ✅ 整合 DuckDuckGo 網頁搜尋
-   ✅ 支援直接訪問網址並擷取內容
-   ✅ 自動偵測網址並抓取
-   ✅ 與小 j AI 完整整合

---

## 權限聲明

此功能由 **江政隆 F1247717117**（系統創始人）授權開發，遵循五常系統隱私與安全規範。

---

**Powered by 小 j AI 🤖 | Wuchang OS v5.1.0**
