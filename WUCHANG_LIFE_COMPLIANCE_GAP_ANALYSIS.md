# wuchang.life 首頁全球可見與 Google 非營利組織合規缺口分析

**更新時間**：2026-01-15  
**分析依據**：系統盤點報告、DNS 審計、資產盤點、Google 非營利組織要求

---

## 一、技術基礎設施缺口（關鍵優先級）

### 1.1 HTTPS/SSL 證書配置 ❌ **關鍵缺失**

**現況**：
- `certs/` 目錄為空（無證書檔案）
- 雖有 `_acme-challenge` TXT 記錄，但證書可能尚未成功申請或配置
- DNS 審計報告顯示：`http_accessible: 0`, `http_inaccessible: 14`

**必須補齊**：
- [ ] 為 `wuchang.life` 和 `www.wuchang.life` 申請並配置有效的 SSL 證書（Let's Encrypt 或商業證書）
- [ ] 確保所有 HTTP 請求自動重定向到 HTTPS
- [ ] 驗證證書在瀏覽器中顯示為有效（無警告）

**Google 非營利組織要求**：
> 網站必須使用 HTTPS/SSL 安全憑證，全面透過 HTTPS 提供服務。

---

### 1.2 網站可訪問性問題 ❌ **關鍵缺失**

**現況**（依據 `dns_audit_report.json`）：
- 所有 14 個子網域的 HTTP 測試結果：**0 個可訪問，14 個不可訪問**
- 根域名 `wuchang.life` 指向 `35.185.167.23` 和 `220.135.21.74`
- `www.wuchang.life` 指向 `220.135.21.74`（路由器/店內側）
- 從本機出網測試顯示：`220.135.21.74:80/443` 端口不可達（TCP 連線失敗）

**必須補齊**：
- [ ] 在 `220.135.21.74`（或選定的主機）上配置並啟動 Web 伺服器（Nginx/Apache/Caddy 等）
- [ ] 開放防火牆規則，允許全球訪問 80 和 443 端口
- [ ] 配置虛擬主機（Virtual Host），正確處理 `wuchang.life` 和 `www.wuchang.life` 的請求
- [ ] 確保首頁內容可正常載入（HTML/CSS/JS 資源可訪問）

**驗證方法**：
```bash
# 從外部測試（使用 8.8.8.8 或 1.1.1.1 解析）
curl -I https://wuchang.life
curl -I https://www.wuchang.life
```

---

### 1.3 DNS 記錄一致性 ⚠️ **部分缺失**

**現況**：
- DNS 審計報告顯示：`mismatched: 1`（有 1 個 DNS 記錄不匹配）
- 根域名有兩個 A 記錄：`35.185.167.23` 和 `220.135.21.74`（可能造成負載分散或路由不確定）

**建議**：
- [ ] 確認根域名的主要 IP（建議統一指向一個穩定的主機）
- [ ] 修復不匹配的 DNS 記錄
- [ ] 確保 `www.wuchang.life` 和 `wuchang.life` 都指向同一個有效的 Web 伺服器

---

## 二、網站內容合規性缺口（Google Ad Grants 要求）

### 2.1 核心頁面內容 ❓ **待驗證**

**必須包含的頁面**：
- [ ] **關於我們（About Us）**：明確說明組織身份、使命、歷史
- [ ] **使命與活動（Mission & Activities）**：詳細描述組織的公益目標和主要活動
- [ ] **聯絡方式（Contact）**：提供可聯繫的地址、電話、電子郵件
- [ ] **非營利組織資訊披露**：
  - 組織名稱：新北市三重區五常社區發展協會
  - 登記號碼或法定資料（如適用）
  - 所屬國家/地區：台灣

**現況檢查**：
- 需要實際訪問 `https://wuchang.life` 確認上述頁面是否存在
- 若網站尚未部署，此項為 **完全缺失**

---

### 2.2 內容質量要求 ❓ **待驗證**

**Google 要求**：
- [ ] 網站內容充實、原創，不是單頁或非常簡化的樣板
- [ ] 內容定期更新，顯示組織活躍運作
- [ ] 網站載入速度快（不同裝置與網絡速度下體驗良好）
- [ ] 響應式設計（Mobile Friendly），支援手機、平板訪問

**檢查項目**：
- [ ] 使用 Google PageSpeed Insights 測試：https://pagespeed.web.dev/
- [ ] 使用 Google Mobile-Friendly Test：https://search.google.com/test/mobile-friendly

---

### 2.3 網站結構與導航 ❓ **待驗證**

**必須具備**：
- [ ] 清晰的菜單/導航結構
- [ ] 沒有壞連結、404 頁面錯誤
- [ ] 網站地圖（sitemap.xml）可訪問
- [ ] robots.txt 配置正確

---

### 2.4 禁止內容與限制 ❓ **待驗證**

**絕對禁止**：
- [ ] 網站**不得**包含 Google AdSense 廣告
- [ ] 網站**不得**包含其他 affiliate 廣告連結
- [ ] 若有商業活動（贊助、販售商品），必須清楚說明收入如何支持組織使命
- [ ] 商業活動不能是網站的主要焦點

**現況**：
- 根據 `ASSET_INVENTORY.md`，系統包含「商店（shop.wuchang.life）」功能
- 需要確認商店頁面是否符合「收入支持使命」的披露要求

---

## 三、轉換追蹤設定缺口（Google Ad Grants 要求）

### 3.1 轉換追蹤配置 ❌ **缺失**

**Google 要求**：
> 必須設定至少一項「有意義的轉換」並定期追蹤。不能只是頁面載入或簡單瀏覽。

**必須補齊**：
- [ ] 設定 Google Analytics 4（GA4）或 Universal Analytics
- [ ] 配置至少一個轉換事件，例如：
  - 捐款表單提交
  - 志願者註冊
  - 會員加入
  - 聯絡表單提交
  - 活動報名
- [ ] 在 Google Ads 帳戶中連結轉換追蹤
- [ ] 定期監控轉換數據（至少每月檢查一次）

---

## 四、組織資格驗證（已確認 ✅）

**依據 `AGENT_CONSTITUTION.md` 和 `ASSET_INVENTORY.md`**：
- ✅ 協會已完成 **Google for Nonprofits 驗證**（永久事實）
- ✅ 組織主體：新北市三重區五常社區發展協會
- ✅ 合法註冊的非營利組織

**注意**：此項已滿足，無需額外行動。

---

## 五、優先級行動清單

### 🔴 **P0 - 立即處理（阻擋全球可見）**

1. **配置 Web 伺服器並開放端口**
   - 在 `220.135.21.74` 或選定的主機上部署 Web 伺服器
   - 配置防火牆規則，開放 80/443 端口
   - 確保首頁 HTML 可正常載入

2. **申請並配置 SSL 證書**
   - 使用 Let's Encrypt（已有 `_acme-challenge` TXT 記錄）或商業證書
   - 配置 HTTPS 並設定 HTTP → HTTPS 自動重定向
   - 驗證證書有效性

3. **修復 DNS 記錄不匹配問題**
   - 確認並統一根域名的 A 記錄指向

### 🟡 **P1 - 高優先級（阻擋 Google Ad Grants 合規）**

4. **建立核心頁面內容**
   - 關於我們、使命與活動、聯絡方式
   - 非營利組織資訊披露

5. **設定轉換追蹤**
   - 安裝 Google Analytics
   - 配置至少一個轉換事件
   - 連結到 Google Ads 帳戶

### 🟢 **P2 - 中優先級（優化與完善）**

6. **優化網站性能與體驗**
   - 頁面載入速度優化
   - 響應式設計驗證
   - 修復壞連結

7. **內容充實與定期更新**
   - 確保內容原創、充實
   - 建立內容更新機制

8. **商業活動披露（如適用）**
   - 若商店功能對外開放，需明確說明收入用途

---

## 六、驗證檢查表

完成上述項目後，使用以下檢查表驗證：

### 技術驗證
- [ ] `https://wuchang.life` 可正常訪問（無 SSL 警告）
- [ ] `https://www.wuchang.life` 可正常訪問（無 SSL 警告）
- [ ] HTTP 自動重定向到 HTTPS
- [ ] 從多個地理位置測試可訪問性（使用 https://www.whatsmydns.net/ 或類似工具）

### 內容驗證
- [ ] 關於我們頁面存在且內容充實
- [ ] 使命與活動頁面存在且內容充實
- [ ] 聯絡方式頁面存在
- [ ] 非營利組織資訊明確披露

### 合規驗證
- [ ] 無 AdSense 或其他 affiliate 廣告
- [ ] 商業活動（如有）有明確披露
- [ ] Google Analytics 已安裝並運作
- [ ] 至少一個轉換事件已配置

### 性能驗證
- [ ] PageSpeed Insights 分數 ≥ 70（建議 ≥ 90）
- [ ] Mobile-Friendly Test 通過
- [ ] 無壞連結（使用工具如 https://www.deadlinkchecker.com/）

---

## 七、參考資源

- Google for Nonprofits 資格要求：https://www.google.com/nonprofits/qualify/
- Google Ad Grants 網站要求：https://support.google.com/grants/answer/9055283
- Let's Encrypt 證書申請：https://letsencrypt.org/
- Google Analytics 設定：https://support.google.com/analytics

---

## 八、備註

- 本分析基於 2026-01-15 的系統狀態
- 若實際網站已部署但未在本 workspace 中，請提供實際 URL 以便進一步驗證
- 建議定期（每季度）重新審核此清單，確保持續合規
