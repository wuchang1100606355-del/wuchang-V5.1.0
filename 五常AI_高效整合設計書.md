# 五常市區發展協會 Google 非營利組織 × Odoo × AI × 路由器 高效整合設計書

## 一、專案目標
打造一套以「新北市三重區五常市區發展協會」為核心，結合 Google 非營利組織、Odoo ERP、AI（小j）、Cloud 路由器的高效自動化協作平台，善用 Google 抵免額，確保合規、可追溯、可稽核。

---

## 二、組織與權責映射
- 組織名稱：新北市三重區五常市區發展協會
- 資訊負責人／總幹事：江政隆
- 數位孿生主體：littlej@wuchang.life（Odoo 內部 AI 小j，具備可究責自然人身份）
- 所有自動化、AI、API 行為皆映射至現實組織與負責人，責任明確。

---

## 三、系統架構
1. **Google Workspace（wuchang.life）**
   - 組織帳號統一管理，SSO 登入 Odoo、AI、雲端服務。
   - Google Tasks、Calendar、Drive、Gmail、Sheets 全自動串接。
2. **Odoo ERP**
   - 以 Google SSO 登入，任務、日曆、文件自動同步 Google Workspace。
   - Odoo 內部小j（AI）以 littlej@wuchang.life 身份執行所有自動化。
3. **Google Cloud（for Nonprofits）**
   - 綁定組織專案，享有免費 Gemini、AI、雲端資源。
   - IAM 權限、API 金鑰皆以 littlej@wuchang.life 為主。
4. **Cloudflared 路由器/網域**
   - wuchang.life、www.wuchang.life、app.wuchang.org.tw 等網域指向內部服務。
   - Cloudflare Tunnel 保證安全、彈性、可遠端維運。

---

## 四、協作與自動化流程
1. **Google Tasks × 雙J協作**
   - 任務建立、分派、進度追蹤全自動同步 Odoo/AI。
   - 任務完成自動通知、產生報表。
2. **Google Calendar × Odoo/AI**
   - 所有會議、任務自動同步日曆，重要事件自動提醒。
3. **Google Drive × 文件管理**
   - 任務、專案文件自動歸檔，權限綁定組織帳號。
4. **AI（小j）自動化**
   - 以 littlej@wuchang.life 身份執行所有自動化、協作、API 呼叫。
   - 所有紀錄可追溯、可稽核。
5. **Cloudflared 路由器**
   - 內外網自動切換，所有服務 HTTPS 加密，自動續約憑證。

---

## 五、抵免額與資源最佳化
- Google Cloud 抵免額優先用於 AI、API、雲端儲存、公益專案。
- 定期檢查資源用量，避免浪費。
- 重要服務（如 Gemini、AI 計算）設為高優先級。

---

## 六、合規與稽核
- 所有自動化、AI、API 行為皆以 littlej@wuchang.life 為主體，責任明確。
- 組織負責人江政隆具備最高管理權限。
- 所有紀錄自動保存，方便稽核與回溯。

---

## 七、未來擴充建議
- 可串接 AppSheet、Zapier、Apps Script 進行更進階無程式碼自動化。
- 支援多語言、多組織協作。
- 強化 AI 決策輔助、資料分析。

---

## 八、附錄
- 主要設定檔：cloudflared/config.yml、official_ai_identity.json、Odoo/Google IAM 設定
- 聯絡窗口：江政隆（總幹事）
- 本設計書可作為組織內部培訓、稽核、對外申請補助之正式文件。
