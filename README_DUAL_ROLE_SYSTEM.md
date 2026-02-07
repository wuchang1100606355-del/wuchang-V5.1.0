# 五常 POS 系統 v2.0 - 雙角色智慧小 j 完全部署指南

## 🎯 系統概述

**五常 POS 系統 v2.0** 是為「五常社區」設計的、集結以下特性的現代化 POS 解決方案：

-   ✅ **本地優先 AI** (Ollama 本地 LLM)
-   ✅ **雙角色設計** (店家 vs 架構師)
-   ✅ **語音交互** (STT/TTS - 支援台灣華語)
-   ✅ **完整決策記錄** (永久審計日誌)
-   ✅ **開源架構** (Odoo + FastAPI + Python)
-   ✅ **社區民主化** (AI Council 決策框架)
-   ✅ **隱私第一** (本地資料處理，雲端備援可選)

---

## 📋 快速導航

### 對於店家 👨‍🍳

1. **快速開始 (5 分鐘)**

    - [啟動 POS 系統](###啟動pos系統)
    - [基本語音查詢](#基本語音查詢)

2. **日常使用**

    - [店家常見問題](#店家常見問題)
    - [營運報告範例](#營運報告範例)

3. **故障排查**
    - [快速參考卡](docs/QUICK_REFERENCE_TROUBLESHOOTING.md)

### 對於架構師 🏗️

1. **系統設計**

    - [完整網路架構](docs/POS_NETWORK_ARCHITECTURE.md)
    - [API 文件](docs/DUAL_ROLE_API_GUIDE.md)

2. **決策與監督**

    - [決策日誌查詢](#決策日誌查詢)
    - [審計報告](#審計報告)

3. **進階配置**
    - [部署指南](docs/POS_EQUIPMENT_DEPLOYMENT_GUIDE.md)
    - [環境配置](#環境變數)

### 對於維護者 🔧

1. **伺服器管理**

    - [系統啟動](#啟動步驟)
    - [監控與故障排查](docs/QUICK_REFERENCE_TROUBLESHOOTING.md)

2. **備份與更新**
    - [日常檢查清單](#每日檢查清單)
    - [備份政策](docs/POS_EQUIPMENT_DEPLOYMENT_GUIDE.md#52-資料備份政策)

---

## 🚀 啟動 POS 系統

### 前置條件

```powershell
# 檢查必要元件
python --version            # 需要 3.11+
ollama --version           # 已安裝
docker --version           # Docker Desktop 已啟動
pip list | grep fastapi    # 虛擬環境已配置
```

### 一鍵啟動（推薦）

```powershell
cd "C:\wuchang V5.1.0"

# 執行啟動腳本（自動檢查、啟動、驗證）
powershell -ExecutionPolicy Bypass -File start_pos_system_dual_role.ps1

# 自動開啟儀表板
# 瀏覽器: http://localhost:8080/dashboard
```

### 手動啟動（進階）

```powershell
# 1. 進入專案目錄
cd "C:\wuchang V5.1.0"

# 2. 啟用虛擬環境
.\.venv\Scripts\Activate.ps1

# 3. 啟動 Ollama (背景)
ollama serve &

# 4. 啟動 Docker 容器 (Odoo)
docker-compose up -d

# 5. 啟動 FastAPI 伺服器 (雙角色版本)
python -m uvicorn vm_fastapi_main_dual_role:app \
  --host 0.0.0.0 \
  --port 8080 \
  --reload

# 6. 在另一個終端測試
curl http://localhost:8080/
```

### 驗證系統就緒

```bash
# ✅ 伺服器健康檢查
curl http://192.168.50.249:8080/ | jq '.status'

# ✅ Ollama 本地 LLM
curl http://127.0.0.1:11434/api/tags | jq '.models[].name'

# ✅ LLM 回應源確認
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}' \
  http://192.168.50.249:8080/llm/chat | jq '.source'
# 期望: "local"

# ✅ 裝置連接
curl -H "X-Auth-Token: merchant-demo-001" \
  http://192.168.50.249:8080/devices | jq '.count'

# ✅ 打開儀表板
start http://192.168.50.249:8080/dashboard
```

---

## 🗣️ 基本語音查詢

### 使用方法

#### 方法 1：Web 介面（簡單）

```
1. 打開 http://192.168.50.249:8080/dashboard
2. 用平板/手機「錄音」
3. 上傳音檔至 /voice/command
4. 等待語音回應 (MP3)
```

#### 方法 2：cURL（進階）

```bash
# 準備語音檔案 (WAV/MP3 格式)
# 使用免費語音錄製工具: Audacity / Phone Recorder

# 店家語音查詢
curl -F "file=@question.wav" \
  -H "X-Auth-Token: merchant-demo-001" \
  http://192.168.50.249:8080/voice/command \
  -o answer.mp3

# 播放回應
ffplay answer.mp3  # 或 open answer.mp3 (macOS) / start answer.mp3 (Windows)
```

### 店家可以問的問題

```
營業查詢:
- 「今天營業額多少？」
- 「A 產品剩多少庫存？」
- 「王先生最後一次購買是什麼時候？」
- 「推薦給下一位客人什麼商品？」
- 「這個退貨可以嗎？」

營運決策:
- 「產生今日營運報告」
- 「本週哪個產品賣得最好？」
- 「員工出勤異常嗎？」
- 「建議進哪些貨？」
- 「客人投訴多嗎？」
```

### 架構師可以問的問題

```
系統分析:
- 「分析最近的決策日誌，找出瓶頸」
- 「今天 AI 做了多少次決策？」
- 「有沒有邏輯錯誤或偏見的決策？」
- 「本月 LLM 準確度怎樣？」

業務優化:
- 「設計新的退貨審批流程」
- 「如何改進客人滿意度？」
- 「建議修改 VIP 分類標準」
- 「規劃下季的進貨策略」

系統設計:
- 「為教育版小j 編寫訓練課程」
- 「如何集成 Line 機器人？」
- 「設計社區補助審批系統」
- 「規劃 AI Council 月度會議議程」
```

---

## 📊 決策日誌與審計

### 決策日誌查詢（架構師限定）

```bash
# 1️⃣ 查看所有決策
curl -H "X-Auth-Token: architect-demo-001" \
  http://192.168.50.249:8080/admin/decisions | jq '.decisions | length'

# 2️⃣ 按角色篩選
curl -H "X-Auth-Token: architect-demo-001" \
  "http://192.168.50.249:8080/admin/decisions?role_filter=MERCHANT" | jq '.decisions[0]'

# 3️⃣ 導出為 CSV（便於分析）
curl -H "X-Auth-Token: architect-demo-001" \
  http://192.168.50.249:8080/admin/decisions | \
  jq -r '.decisions[] | [.timestamp, .user_role, .action, .user_name, .result.response] | @csv' \
  > decisions_export.csv

# 4️⃣ 查看原始日誌檔案
cat decision_logs/MERCHANT/decisions_2026-01-10.jsonl | jq '.' | less
```

### 審計報告

```bash
# 生成每日審計摘要
curl -H "X-Auth-Token: architect-demo-001" \
  http://192.168.50.249:8080/admin/audit | jq '.'

# 期望輸出:
# {
#   "audit_timestamp": "2026-01-10T12:00:00",
#   "total_decisions": 125,
#   "decisions_by_role": {
#     "MERCHANT": 100,
#     "ARCHITECT": 25
#   },
#   "decisions_by_action": {
#     "llm_chat": 80,
#     "voice_recognize": 30,
#     "voice_synthesize": 15
#   },
#   "devices_count": 5,
#   "events_logged": 342
# }
```

---

## 🛠️ 環境變數

### 核心配置

| 變數                 | 預設值                                            | 說明                              |
| -------------------- | ------------------------------------------------- | --------------------------------- |
| `LOCAL_LLM_ENDPOINT` | `http://127.0.0.1:11434/v1/chat/completions`      | Ollama 伺服器地址                 |
| `LOCAL_LLM_MODEL`    | `little-j`                                        | 使用的 LLM 模型名稱               |
| `LLM_FALLBACK`       | `1`                                               | 是否允許雲端備援 (1=是, 0=本地只) |
| `POS_UI_URL`         | `http://192.168.50.249:8069/pos/ui`               | Odoo POS 前端                     |
| `CUSTOMER_UI_URL`    | `http://192.168.50.249:8069/pos/customer_display` | 客顯 URL                          |

### 語音服務配置（可選）

| 變數                  | 說明                       | 建議值            |
| --------------------- | -------------------------- | ----------------- |
| `AZURE_SPEECH_KEY`    | Azure Speech Services 金鑰 | (從 Azure 複製)   |
| `AZURE_SPEECH_REGION` | Azure Speech 地區          | `eastasia` (台灣) |

### 設定方式

```powershell
# PowerShell (臨時)
$env:LOCAL_LLM_ENDPOINT = "http://127.0.0.1:11434/v1/chat/completions"
$env:LLM_FALLBACK = "1"

# PowerShell (永久)
[Environment]::SetEnvironmentVariable('LOCAL_LLM_ENDPOINT', 'http://127.0.0.1:11434/v1/chat/completions', [EnvironmentVariableTarget]::User)

# 在 .ps1 腳本中
param(
    [string]$LLM_MODEL = "little-j",
    [string]$LLM_FALLBACK = "1"
)
$env:LOCAL_LLM_MODEL = $LLM_MODEL
$env:LLM_FALLBACK = $LLM_FALLBACK
```

---

## 👤 身份驗證與角色

### 預設帳戶

| Token                | 角色               | 權限             | 用途       |
| -------------------- | ------------------ | ---------------- | ---------- |
| `merchant-demo-001`  | 店家 (MERCHANT)    | 查詢、決策、營運 | 店員/店長  |
| `merchant-demo-002`  | 店家 (MERCHANT)    | 查詢、決策、營運 | 支店/分店  |
| `architect-demo-001` | 架構師 (ARCHITECT) | 全部 + 管理      | 系統設計師 |

### 如何使用

```bash
# 所有 API 呼叫都需要 X-Auth-Token 標頭
curl -H "X-Auth-Token: merchant-demo-001" \
  http://192.168.50.249:8080/llm/chat \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "今天營業額多少？"}'
```

### 新增帳戶

編輯 `vm_fastapi_main_dual_role.py`，修改 `VALID_TOKENS` 字典：

```python
VALID_TOKENS = {
    "merchant-shop-001": {
        "role": Role.MERCHANT,
        "shop_name": "五常 - 主門市",
        "created_at": datetime.datetime.utcnow().isoformat()
    },
    "architect-001": {
        "role": Role.ARCHITECT,
        "name": "系統架構師",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
}
```

---

## 📁 檔案結構

```
C:\wuchang V5.1.0\
├── 📄 README.md                          ← 你在這裡
├── 📄 requirements.txt                   ← Python 依賴
├── 📄 docker-compose.yml                 ← Docker 配置
│
├── 🐍 Python 核心
│   ├── vm_fastapi_main_dual_role.py     ← ⭐ 新的雙角色伺服器
│   ├── vm_fastapi_main_new.py           ← 舊版伺服器 (相容)
│   ├── sister_agent.py                  ← POS 代理
│   └── vm_port_server.py                ← 啟動器
│
├── 🚀 啟動腳本
│   ├── start_pos_system_dual_role.ps1   ← ⭐ 一鍵啟動
│   ├── run_server.ps1                   ← 伺服器啟動
│   └── start_customer.bat                ← 客顯啟動
│
├── 📚 文件 (docs/)
│   ├── POS_NETWORK_ARCHITECTURE.md      ← 網路設計
│   ├── POS_EQUIPMENT_DEPLOYMENT_GUIDE.md ← 設備部署
│   ├── DUAL_ROLE_API_GUIDE.md           ← API 文件
│   ├── QUICK_REFERENCE_TROUBLESHOOTING.md ← 故障排查
│   ├── AI_ETHICS_CODE.md                ← 倫理框架
│   ├── AI_INHERITANCE_BLUEPRINT.md      ← AI 克隆與演化
│   ├── COMMUNITY_AI_BLUEPRINT.md        ← 社區服務
│   └── ... (其他文件)
│
├── 📊 資料與日誌
│   ├── decision_logs/                   ← 決策日誌 (按角色/日期)
│   ├── events.log.jsonl                 ← 系統事件
│   ├── backups/                         ← 備份檔案
│   └── memory_store/                    ← 知識庫 (可選)
│
└── 🛠️ 工具與配置
    ├── config/                          ← 設定檔
    ├── tools/                           ← 額外工具
    └── scripts/                         ← 自動化腳本
```

---

## ✅ 每日檢查清單

### 上午 08:00

```powershell
# 複製以下指令至 PowerShell：

Write-Host "=== 五常 POS 系統 每日檢查 ===" -ForegroundColor Cyan

# 1. 伺服器
$server = try { (curl http://192.168.50.249:8080/ -ErrorAction SilentlyContinue).StatusCode } catch { 0 }
Write-Host "伺服器: $(if($server -eq 200) { '✅ 運行' } else { '❌ 離線' })"

# 2. LLM
$llm = try { (curl http://127.0.0.1:11434/api/tags -ErrorAction SilentlyContinue).StatusCode } catch { 0 }
Write-Host "Ollama: $(if($llm -eq 200) { '✅ 運行' } else { '❌ 停止' })"

# 3. 磁碟
$disk = (Get-Volume C | Select -ExpandProperty SizeRemaining) / 1GB
Write-Host "磁碟可用: $(if($disk -gt 20) { '✅ ' + $disk.ToString('F1') + 'GB' } else { '⚠️ ' + $disk.ToString('F1') + 'GB' })"

# 4. 決策日誌
$logCount = (ls decision_logs -Recurse -Filter "decisions_*.jsonl" | Measure-Object -Line).Lines
Write-Host "決策記錄: $logCount 筆"

# 5. 裝置連接
try {
    $devices = curl -H "X-Auth-Token: merchant-demo-001" \
      http://192.168.50.249:8080/devices 2>/dev/null | ConvertFrom-Json
    Write-Host "已註冊裝置: $($devices.count) 個"
} catch {
    Write-Host "裝置狀態: ❌ 查詢失敗"
}

Write-Host ""
Write-Host "檢查完成! $(Get-Date)" -ForegroundColor Green
```

### 問題時立即檢查

```powershell
# 伺服器連線
ping 192.168.50.249

# API 健康
curl http://192.168.50.249:8080/

# LLM 模型
ollama list

# Docker 容器
docker ps

# 虛擬環境
.\.venv\Scripts\Activate.ps1
python -c "import fastapi; print('FastAPI OK')"
```

---

## 🆘 常見問題 (FAQ)

### Q1: 伺服器無法啟動 (Address already in use)

**A**: 埠 8080 已被佔用

```powershell
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Q2: LLM 回應來自雲端 (source: vertex) 而不是本地

**A**: Ollama 未啟動或模型未下載

```bash
ollama serve              # 後台啟動
ollama pull little-j      # 下載模型
```

### Q3: 語音辨識不工作

**A**: 需要安裝 Whisper 或配置 Azure

```bash
pip install openai-whisper
# 或配置環境變數 AZURE_SPEECH_KEY
```

### Q4: 店家無法訪問 POS UI

**A**: Odoo 容器未運行

```bash
docker-compose up -d
docker logs wuchang_odoo  # 查看錯誤
```

### Q5: 決策日誌文件太大怎麼辦?

**A**: 手動封存舊日誌

```bash
gzip decision_logs/MERCHANT/decisions_2025-*.jsonl
# 或上傳至雲端備份
```

---

## 📞 獲得幫助

### 自助診斷

1. 查看 [QUICK_REFERENCE_TROUBLESHOOTING.md](docs/QUICK_REFERENCE_TROUBLESHOOTING.md)
2. 執行診斷腳本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/collect_evidence.ps1
# 生成完整的診斷套件供分析
```

### 聯絡技術支援

| 問題類型          | 聯絡方式         | 回應時間  |
| ----------------- | ---------------- | --------- |
| 緊急 (營業中斷)   | 電話 (待定)      | < 30 分鐘 |
| 高優先 (功能異常) | Email + WhatsApp | < 2 小時  |
| 一般 (改進建議)   | Email / Line     | < 24 小時 |

---

## 🔐 安全與隱私

### 資料安全政策

-   ✅ **本地優先**：所有營業資料留在本機 (不上傳雲端)
-   ✅ **加密備份**：備份檔案使用 AES-256 加密
-   ✅ **訪問控制**：所有 API 需身份驗證 (Token)
-   ✅ **審計日誌**：每筆決策都被永久記錄
-   ✅ **隱私政策**：見 [SYSTEM_LOG_POLICY.md](docs/SYSTEM_LOG_POLICY.md)

### 備份與復原

```bash
# 自動日備份 (凌晨 02:00)
powershell -ExecutionPolicy Bypass -File scripts/rotate_audit_logs.ps1

# 手動備份
docker-compose exec odoo pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql
```

---

## 🎓 學習資源

### 架構師培訓

-   [完整網路架構](docs/POS_NETWORK_ARCHITECTURE.md) - 理解系統設計
-   [部署指南](docs/POS_EQUIPMENT_DEPLOYMENT_GUIDE.md) - 硬體與安裝
-   [API 文件](docs/DUAL_ROLE_API_GUIDE.md) - 整合開發
-   [AI 倫理](docs/AI_ETHICS_CODE.md) - 負責任 AI
-   [AI 演化](docs/AI_INHERITANCE_BLUEPRINT.md) - AI 克隆與版本管理

### 店家培訓

-   [POS 基本操作](#基本語音查詢) - 日常查詢
-   [營運報告](#營運報告範例) - 數據分析
-   [故障自救](docs/QUICK_REFERENCE_TROUBLESHOOTING.md) - 應急處理

---

## 🚀 未來功能藍圖

### Phase 3 (2026 Q1)

-   [ ] Line 機器人整合
-   [ ] 微信支付整合
-   [ ] 多店管理後台
-   [ ] 進階分析儀表板

### Phase 4 (2026 Q2)

-   [ ] 供應鏈管理
-   [ ] AI 顧客畫像
-   [ ] 自動補貨建議
-   [ ] 員工績效評估

### Phase 5 (2026 H2)

-   [ ] 社區互助市集
-   [ ] 補助申請自動化
-   [ ] 社區服務排程
-   [ ] 協會民主治理平台

---

## 📄 授權與許可

-   **系統架構**：五常社區 (版權所有)
-   **開源元件**：
    -   Odoo: LGPL-3.0
    -   FastAPI: MIT
    -   Ollama: MIT
    -   Python: PSF
-   **文件**：CC-BY-NC-SA 4.0 (非商業使用)

---

## 🙏 致謝

本系統是集結以下組織與個人的智慧與工作：

-   **Google Cloud Platform** - 提供 Vertex AI 備援
-   **Ollama 社區** - 本地 LLM 支援
-   **Odoo 基金會** - 開源 ERP 平台
-   **五常社區** - 願景與信任
-   **小 j** - AI 設計與決策倫理

---

## 📞 聯絡與反饋

-   **官方網站**：(待定)
-   **技術支援**：littlej-support@wuchang.local
-   **功能建議**：littlej-feedback@wuchang.local
-   **社區論壇**：(待定)

---

**系統版本**：v2.0-beta  
**最後更新**：2026-01-10  
**狀態**：🟢 穩定運行中  
**下一次更新**：2026-02-10

---

## 快速連結

| 資源        | 位置                                                                               |
| ----------- | ---------------------------------------------------------------------------------- |
| 🌐 儀表板   | [http://192.168.50.249:8080/dashboard](http://192.168.50.249:8080/dashboard)       |
| 📚 API 文件 | [docs/DUAL_ROLE_API_GUIDE.md](docs/DUAL_ROLE_API_GUIDE.md)                         |
| 🔧 故障排查 | [docs/QUICK_REFERENCE_TROUBLESHOOTING.md](docs/QUICK_REFERENCE_TROUBLESHOOTING.md) |
| 📊 決策日誌 | `decision_logs/` 目錄                                                              |
| 🎯 網路設計 | [docs/POS_NETWORK_ARCHITECTURE.md](docs/POS_NETWORK_ARCHITECTURE.md)               |
| 🛠️ 部署指南 | [docs/POS_EQUIPMENT_DEPLOYMENT_GUIDE.md](docs/POS_EQUIPMENT_DEPLOYMENT_GUIDE.md)   |
| 📖 倫理框架 | [docs/AI_ETHICS_CODE.md](docs/AI_ETHICS_CODE.md)                                   |

---

**祝你使用愉快！** 有任何問題都歡迎聯絡小 j。 🤖❤️
