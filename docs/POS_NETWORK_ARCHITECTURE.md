# 五常 POS 系統 - 全店網路架構與小 J 智慧服務藍圖

## 0. 系統願景

打造一個「本地優先、雙角色、語音交互」的店鋪智慧系統：

-   **店家用戶**：透過自然語言/語音指揮小 j，進行日常營業管理（結帳、查詢、報表、客服）
-   **架構師用戶**：透過自然語言/語音指揮小 j，設計與優化系統、社區營運策略
-   **小 j 核心**：本地 LLM (Ollama) 優先；區網/外網可達；所有決策與操作永久記錄

---

## 第一部分：全店網路架構設計

### 1.1 網路拓樸圖

```
【外網（可選）】
        |
   [中華電信 / WiFi]
        |
   [路由器 192.168.50.1]
    /    |    \    \
   /     |     \    \
【主伺服器】【POS 1】【客顯】【智慧看板】
192.168.50.249:8080  POS_PC    Chrome OS   (未來)
(FastAPI+小j)

【本地設備】
- 筆電（開發/管理用）
- 手機/平板（店家快速互動）
```

### 1.2 IP 規劃

| 設備名稱     | IP             | 埠             | 用途                |
| ------------ | -------------- | -------------- | ------------------- |
| 路由器       | 192.168.50.1   | 53(DNS)/80/443 | DHCP / 網路管理     |
| 主伺服器     | 192.168.50.249 | 8080           | FastAPI + 小 j 核心 |
| Odoo         | 192.168.50.249 | 8069           | ERP / POS UI        |
| POS 機 1     | 192.168.50.x   | 動態           | 結帳 / 客服         |
| 客顯         | 192.168.50.x   | 動態           | Chrome OS / 公告    |
| 筆電（開發） | 192.168.50.x   | 動態           | 架構師管理介面      |
| 手機（店家） | 192.168.50.x   | 動態           | 語音指揮 / 快速查詢 |

### 1.3 網路連接方式

#### 無線 (WiFi 推薦)

```
設定 SSID：wuchang-pos
密碼：(由店家設定，安全起見)
頻段：2.4GHz (相容性佳) + 5GHz (速度)
```

#### 有線 (可選，伺服器專用)

```
主伺服器 ← 網線 ← 路由器
(確保穩定性)
```

### 1.4 防火牆與安全規則

```powershell
# 開放內部 8080 (LAN 使用)
New-NetFirewallRule -DisplayName "小j API (內網)" -Direction Inbound -Protocol TCP -LocalPort 8080 -RemoteAddress 192.168.50.0/24 -Action Allow

# 若需外網暴露，建議用 Cloudflare Tunnel 或 ngrok（見後續）
```

---

## 第二部分：雙角色權限系統設計

### 2.1 角色定義

#### 角色 A：店家 (MERCHANT)

-   **權限**：營業操作、報表查詢、客服決策、庫存檢查
-   **禁區**：系統配置、資料庫修改、架構變更
-   **互動方式**：自然語言（文字/語音）、簡單指令
-   **界面**：行動裝置優先（手機/平板）、語音為主

**店家可以問小 j：**

-   「今天營業額多少？」
-   「A 產品剩多少庫存？」
-   「幫我查一下這位客人的購買記錄」
-   「寫一份今日營運報告」
-   「推薦一個合適的進貨量」

#### 角色 B：架構師 (ARCHITECT)

-   **權限**：全系統存取、政策配置、模型微調、社區營運決策
-   **禁區**：無（但所有操作需記錄與回溯）
-   **互動方式**：進階自然語言、技術指令、JSON 結構化輸入
-   **界面**：桌機優先、儀表板 + 語音混用

**架構師可以問小 j：**

-   「我想為商家版小 j 微調決策邏輯，該怎麼做？」
-   「分析本月決策日誌，找出系統瓶頸」
-   「設計一個新的社區服務流程來處理補助申請」
-   「為教育版小 j 撰寫 10 個培訓課程」
-   「重新配置系統隱私政策」

### 2.2 權限矩陣

| 端點 / 操作                | 店家     | 架構師   |
| -------------------------- | -------- | -------- |
| `/devices` (查詢)          | ✓        | ✓        |
| `/devices` (修改)          | ✗        | ✓        |
| `/llm/chat` (營業)         | ✓        | ✓        |
| `/skills/execute` (翻譯等) | ✓        | ✓        |
| `/admin/config`            | ✗        | ✓        |
| `/admin/audit`             | 查看自己 | 查看全部 |
| `/ai/clone/deploy`         | ✗        | ✓        |
| `/ai/knowledge/upload`     | ✗        | ✓        |
| `/system/shutdown`         | ✗        | ✓        |

### 2.3 身份認證方式

```python
# 簡單方案：UUID token
TOKENS = {
    "merchant-shop-001": {"role": "MERCHANT", "shop": "五常門市"},
    "architect-001": {"role": "ARCHITECT", "name": "系統設計師"}
}

# 驗證：所有 API 需提供 X-Auth-Token 標頭
headers = {"X-Auth-Token": "merchant-shop-001"}
```

---

## 第三部分：語音交互模組

### 3.1 語音流程

```
【用戶語音輸入】
    ↓ (麥克風)
【STT - 語音轉文字】(OpenAI Whisper / Google Speech-to-Text)
    ↓
【小j 理解與回應】(Ollama little-j)
    ↓
【TTS - 文字轉語音】(微軟 SAPI 或線上 TTS)
    ↓ (喇叭)
【用戶語音輸出】
```

### 3.2 支援的語音平台

| 平台                 | 成本 | 延遲   | 準確度 | 推薦用途         |
| -------------------- | ---- | ------ | ------ | ---------------- |
| 本地 (Whisper CPU)   | 免   | ~2 秒  | 90%    | 開發/內部        |
| Azure Speech         | 便宜 | 0.5 秒 | 95%    | **推薦生產環境** |
| Google Cloud Speech  | 中等 | 0.3 秒 | 98%    | 高要求場景       |
| OpenAI Whisper (API) | 便宜 | 1 秒   | 95%    | 備選方案         |

### 3.3 語音 API 端點

```
POST /voice/recognize
- 上傳 WAV/MP3 音檔
- 回傳：{ text: "...", language: "zh-TW", confidence: 0.95 }

POST /voice/synthesize
- 輸入：{ text: "今日營業額 $5000", lang: "zh-TW" }
- 回傳：MP3 音檔（播放給用戶）

POST /voice/command
- 集成：STT → 理解 → 執行 → TTS
- 輸入：WAV 語音
- 回傳：{ action: "...", result: "...", audio: "..." }
```

---

## 第四部分：POS 系統啟動與整合

### 4.1 POS 啟動檢查清單

```powershell
# 1. 啟動 Docker (Odoo + DB)
docker-compose -f docker-compose.yml up -d

# 2. 確認 Odoo 線上 (http://192.168.50.249:8069)
Invoke-RestMethod http://192.168.50.249:8069 -ErrorAction SilentlyContinue

# 3. 啟動小j 伺服器
powershell -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\run_server.ps1"

# 4. 啟動 POS 代理 (各收銀機)
powershell -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\run_agent_POS.bat"

# 5. 驗證網路連接
Invoke-RestMethod http://localhost:8080/devices | ConvertTo-Json -Depth 5
```

### 4.2 POS 與小 j 整合流程

```
【店家結帳畫面】(Odoo POS UI @ 8069)
    ↓ (WebSocket / REST API)
【小j 輔助決策】(FastAPI @ 8080)
    ↓
【返回建議】(折扣/優惠/推薦/警告)
    ↓
【店家確認】(點擊/語音)
    ↓
【交易完成】
```

### 4.3 POS 常用場景與小 j 回應

| 場景     | 店家說/問                  | 小 j 回應                                             |
| -------- | -------------------------- | ----------------------------------------------------- |
| 客人常客 | 「這位客人打幾折？」       | 「王先生是 VIP，建議 9 折；本月購買超過 3000 元」     |
| 庫存警告 | 「產品 A 還能賣嗎？」      | 「剩 5 件，本週有進貨單待確認」                       |
| 退貨處理 | 「該怎麼處理這筆退貨？」   | 「此產品允許 7 日無條件退貨，此客人在期限內，已記錄」 |
| 推薦搭售 | 「推薦這位客人買什麼？」   | 「基於購買歷史，推薦配件 B；他常配合產品 A 購買」     |
| 疑難雜症 | 「為什麼這筆交易過不了？」 | 「客人超出月信用額度；建議改成現金或分期」            |

---

## 第五部分：外網暴露與遠端管理（可選）

### 5.1 安全考量

外網暴露需要：

-   ✓ HTTPS 加密
-   ✓ API 驗證（Token / OAuth）
-   ✓ IP 白名單
-   ✓ 流量限制（Rate Limiting）

### 5.2 推薦方案：Cloudflare Tunnel（無須公網 IP）

```bash
# 安裝 cloudflared
# 下載：https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/install-and-setup/

# 連接隧道
cloudflared tunnel create wuchang-pos
cloudflared tunnel route dns wuchang-pos littlej.example.com
cloudflared tunnel run wuchang-pos

# 本地伺服器
cloudflared tunnel config
# 設定：http://localhost:8080 ← littlej.example.com
```

### 5.3 外網 API 端點（經過 Tunnel）

```
https://littlej.example.com/voice/command
https://littlej.example.com/llm/chat
https://littlej.example.com/devices
（均需 X-Auth-Token）
```

---

## 第六部分：店內營業管理技能集

小 j 為店家預設能力：

```python
MERCHANT_SKILLS = {
    "daily_report": "產生今日營運報告（銷售額、客流、轉換率）",
    "inventory_check": "查詢指定產品庫存",
    "customer_lookup": "查詢客戶購買歷史與偏好",
    "recommendation": "根據購物籃推薦搭售",
    "price_check": "查詢產品價格與折扣規則",
    "refund_process": "指導退貨流程",
    "vip_identify": "識別 VIP 並給予優惠提示",
    "sales_forecast": "預測本週/月銷售趨勢",
    "staff_schedule": "查詢員工班表",
    "alert_check": "提醒待處理事項（過期商品、應收帳款等）"
}
```

---

## 第七部分：架構師系統設計交互介面

小 j 為架構師預設能力：

```python
ARCHITECT_SKILLS = {
    "ai_clone_manage": "建立/升級 AI 分身版本",
    "knowledge_update": "更新知識庫（補助方案、流程、規則）",
    "decision_analysis": "分析決策日誌，找出系統瓶頸",
    "workflow_design": "設計新的社區服務流程",
    "api_config": "動態調整 API 端點與權限",
    "audit_report": "產生審計報告",
    "privacy_policy": "配置隱私與資料保留政策",
    "training_content": "編撰員工或社區培訓教材",
    "performance_tune": "優化 LLM 與系統效能",
    "integration_plan": "規劃與第三方系統的整合（Line、Google Workspace 等）"
}
```

---

## 第八部分：部署步驟與檢查清單

### 步驟 1：網路基礎設定（已完成）

-   ✓ 路由器配置（DHCP / DNS）
-   ✓ IP 規劃與分配
-   ✓ WiFi SSID 與密碼設定

### 步驟 2：伺服器與 LLM 啟動（接下來）

-   [ ] 啟動 Ollama 服務
-   [ ] 啟動 FastAPI 伺服器 (port 8080)
-   [ ] 驗證 `/devices` 端點
-   [ ] 驗證 `/llm/chat` 回應 source=local

### 步驟 3：POS 系統啟動

-   [ ] Docker Odoo 啟動
-   [ ] POS 代理連接
-   [ ] 測試結帳流程

### 步驟 4：語音交互配置

-   [ ] 選定 STT/TTS 服務（Azure / Google / 本地）
-   [ ] 集成語音 API
-   [ ] 測試麥克風與喇叭
-   [ ] 調整語言與方言（台灣華語）

### 步驟 5：雙角色系統啟動

-   [ ] 生成店家 Token
-   [ ] 生成架構師 Token
-   [ ] 設定權限矩陣
-   [ ] 測試角色切換

### 步驟 6：外網整合（可選）

-   [ ] 設定 Cloudflare Tunnel
-   [ ] 配置 HTTPS
-   [ ] IP 白名單設定
-   [ ] 遠端訪問測試

### 步驟 7：驗收與上線

-   [ ] 完整功能測試
-   [ ] 決策日誌檢視
-   [ ] 安全審計
-   [ ] 協會簽署上線確認

---

## 附件：快速指令參考

```powershell
# 啟動全套系統
./start_full_pos_system.ps1

# 查詢系統狀態
Invoke-RestMethod http://192.168.50.249:8080/health | ConvertTo-Json

# 店家語音查詢
curl -X POST http://192.168.50.249:8080/voice/command \
  -H "X-Auth-Token: merchant-shop-001" \
  --data-binary @voice.wav

# 架構師決策分析
Invoke-RestMethod http://192.168.50.249:8080/admin/decisions \
  -H "X-Auth-Token: architect-001"
```

---

版本：v1.0 (2026-01-10)  
狀態：藍圖階段，待逐步實作
