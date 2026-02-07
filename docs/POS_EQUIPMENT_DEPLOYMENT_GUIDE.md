# 五常社區 POS 系統 - 完整設備配置與部署指南

## 第一部分：店內網路設備清單

### 1.1 核心伺服器（必需）

| 設備               | 規格                         | 用途                                   | 數量 |
| ------------------ | ---------------------------- | -------------------------------------- | ---- |
| **主伺服器**       | Ryzen 5, 16GB RAM, SSD 512GB | FastAPI 伺服器、本地 LLM、Odoo、資料庫 | 1    |
| **網路交換機**     | Gigabit Switch (8-16 埠)     | 局域網集線器                           | 1    |
| **路由器/WiFi**    | WiFi 6 或 5G                 | DHCP、DNS、無線網路                    | 1    |
| **UPS 不斷電系統** | 2000VA+                      | 伺服器電源保護                         | 1    |

### 1.2 POS 收銀機（可擴充）

| 設備                        | 規格                                       | 用途             | 數量 | 預算          |
| --------------------------- | ------------------------------------------ | ---------------- | ---- | ------------- |
| **POS 機 #1**               | Intel i5, 8GB RAM, 256GB SSD, 15" 觸控螢幕 | 收銀、結帳、查詢 | 1-3  | $800-1200 USD |
| **客顯 (Customer Display)** | Chrome OS Tablet 或 Android                | 顯示客人應付金額 | 1-3  | $200-400 USD  |
| **收銀紙印表機**            | 熱敏捲紙印表機 80mm                        | 列印收據         | 1-2  | $150-250 USD  |
| **條碼掃描槍**              | USB 一維/二維掃描器                        | 掃瞄商品條碼     | 1-2  | $50-100 USD   |

### 1.3 管理/監控設備（建議）

| 設備                   | 規格                             | 用途               | 數量 | 預算           |
| ---------------------- | -------------------------------- | ------------------ | ---- | -------------- |
| **架構師筆電**         | MacBook Pro / ThinkPad, 16GB RAM | 系統設計、決策審查 | 1    | $1000-2000 USD |
| **店家平板**           | iPad / Android Tablet 10"        | 語音指揮、即時查詢 | 1-2  | $300-500 USD   |
| **監視攝像頭（可選）** | IP Camera PoE                    | 店面監控           | 1-2  | $150-300 USD   |
| **門鈴/服務鈴**        | IoT 無線按鈕                     | 呼叫服務           | 1    | $30-50 USD     |

---

## 第二部分：網路架構與配置

### 2.1 IP 靜態分配規劃

```
【路由器 WiFi 網路】
基礎 SSID: wuchang-pos
密碼: [由店家保管]
頻段: 2.4GHz (主要) + 5GHz (可選高速)
DHCP 範圍: 192.168.50.100 ~ 192.168.50.200

【靜態 IP 分配】
網路: 192.168.50.0/24

IP | 設備名稱 | 用途 | 類型 |
---|---------|------|------|
192.168.50.1 | 路由器 | 網路閘道 | 固定 |
192.168.50.249 | 主伺服器 | FastAPI、Odoo、LLM | 固定 |
192.168.50.11 | POS 機 #1 | 收銀 | 預留DHCP |
192.168.50.12 | POS 機 #2 | 收銀 (可選) | 預留DHCP |
192.168.50.20 | 客顯 | 顯示 | DHCP |
192.168.50.30 | 架構師筆電 | 管理 | DHCP |
192.168.50.40 | 店家平板 | 語音查詢 | DHCP |
192.168.50.50-98 | 其他設備 | 訪客、監控 | DHCP |
```

### 2.2 物理配線圖

```
【店鋪內部】

┌─────────────────────────────────────────────────┐
│                  5GHz WiFi                       │
│              (高速設備優先)                      │
│                                                   │
│  ┌──────────────────────────────────────────┐  │
│  │         WiFi 6 路由器 (192.168.50.1)     │  │
│  │       ↑ 上行: 中華電信 光纖/ADSL         │  │
│  └──────────────────────────────────────────┘  │
│            ↓ (有線)                              │
│  ┌──────────────────────────────────────────┐  │
│  │      Gigabit 交換機 (8-16 埠)            │  │
│  │     (支援 PoE 供電)                      │  │
│  └──────────────────────────────────────────┘  │
│      ↓          ↓          ↓          ↓         │
│     [1]        [2]        [3]        [4]        │
│                                                   │
│ [1] 主伺服器 (192.168.50.249)                   │
│     ├─ FastAPI 伺服器 :8080                    │
│     ├─ Ollama LLM :11434                       │
│     ├─ Odoo POS :8069                          │
│     └─ PostgreSQL :5432                        │
│                                                   │
│ [2] POS 機 #1 (192.168.50.11)                  │
│     └─ 連接:                                    │
│        - 客顯 (WiFi)                           │
│        - 印表機 (USB)                          │
│        - 掃描槍 (USB)                          │
│                                                   │
│ [3] 備用埠                                      │
│     (未來 POS 機 #2, 監控等)                   │
│                                                   │
│ [4] 其他服務                                    │
│     - 訪客 WiFi                                │
│     - 監控設備                                  │
│                                                   │
│ 【空中】                                        │
│ WiFi 2.4GHz: 所有行動設備                      │
│ - 架構師筆電                                    │
│ - 店家平板                                      │
│ - 客人手機 (可選)                              │
│                                                   │
└─────────────────────────────────────────────────┘
```

### 2.3 交換機連接方案

**推薦機型**: TP-Link TL-SG108E 或 D-Link DES-1210G

```
埠 1-4: 伺服器、POS、印表機、監控
埠 5-8: 保留/訪客

接線:
- 埠 1 → 主伺服器 (有線，確保穩定)
- 埠 2 → POS 機 #1
- 埠 3 → 印表機
- 埠 4 → 路由器 LAN 埠 (若路由器只有 1 個 LAN)
```

---

## 第三部分：軟體環境部署

### 3.1 主伺服器系統安裝

```bash
# 1. 作業系統：Windows Server 2022 或 Windows 11 Pro
# 2. 必要軟體

# 2.1 Docker Desktop
# - 下載: https://www.docker.com/products/docker-desktop
# - 啟用 WSL 2

# 2.2 Python 3.11+
# - 下載: https://www.python.org/downloads/
# - 安裝路徑: C:\Python311

# 2.3 Ollama
# - 下載: https://ollama.ai/download
# - 模型: ollama pull little-j (4.7GB)

# 2.4 Node.js (可選，用於前端工具)
# - 下載: https://nodejs.org/

# 2.5 Git (可選)
# - 下載: https://git-scm.com/
```

### 3.2 專案環境設定

```powershell
# 進入專案目錄
cd "C:\wuchang V5.1.0"

# 建立虛擬環境
python -m venv .venv

# 啟用虛擬環境
.\.venv\Scripts\Activate.ps1

# 安裝依賴
pip install --upgrade pip
pip install -r requirements.txt

# 驗證安裝
python -c "import fastapi, uvicorn, requests; print('All dependencies OK')"
```

### 3.3 Ollama 模型配置

```bash
# 下載模型（可在啟動前完成，避免首次延遲）
ollama pull little-j          # 主要模型 (4.7GB)
ollama pull qwen2.5:7b        # 備選 (4.7GB)
ollama pull gemma3:4b         # 輕量級 (3.3GB)

# 驗證模型
ollama list

# 啟動 Ollama 服務（背景）
ollama serve
```

### 3.4 Docker 容器啟動

```bash
# 在專案根目錄
docker-compose -f docker-compose.yml up -d

# 驗證容器
docker ps

# 檢查 Odoo 日誌
docker logs wuchang_odoo
```

---

## 第四部分：POS 機部署

### 4.1 POS 機硬體要求

```
最低配置:
- 處理器: Intel Core i5 或同等級
- 記憶體: 8GB RAM
- 儲存: 256GB SSD
- 顯示: 15-17" 觸控螢幕
- 作業系統: Windows 10/11 Pro 或 Linux

推薦配置:
- 處理器: Intel Core i7
- 記憶體: 16GB RAM
- 儲存: 512GB SSD
- 顯示: 17-21" 高清觸控螢幕
- 作業系統: Windows 11 Pro
- 額外: 2.5G 網卡、USB 3.0 集線器
```

### 4.2 POS 機軟體安裝

```powershell
# 1. 在 POS 機上重複執行 3.2 和 3.3（或共享 Python 環境）

# 2. 啟動 POS 代理
powershell -ExecutionPolicy Bypass -File "C:\wuchang V5.1.0\sister_agent.py" `
  --device POS `
  --vm-url http://192.168.50.249:8080 `
  --hostname pos-001

# 3. 開啟 Odoo POS UI
# 瀏覽器訪問: http://192.168.50.249:8069/pos/ui

# 4. 設定開機自啟 (工作排程器或啟動資料夾)
```

### 4.3 客顯設備（Chrome OS / Android）

```bash
# Chrome OS (推薦)
# 1. 進入開發者模式
# 2. 啟用 Crostini (Linux 容器)
# 3. 在 Terminal 執行:
   bash
   cd ~/Desktop
   bash <(curl -sSL https://raw.githubusercontent.com/your-repo/run_agent_chromeos.sh)

# Android Tablet
# 1. 安裝 Termux 應用
# 2. 執行 Python Agent:
   python sister_agent.py --device CUSTOMER --vm-url http://192.168.50.249:8080
```

---

## 第五部分：安全配置

### 5.1 WiFi 安全設定

```
路由器後台:
- 設定 WPA3 加密 (若支援) 或 WPA2
- 設定複雜密碼 (16+ 字元)
- 隱藏 SSID (可選，增加安全性)
- 啟用防火牆
- 停用 WPS
```

### 5.2 防火牆規則

```powershell
# 開放內部 8080 (FastAPI)
New-NetFirewallRule -DisplayName "小j API (內網)" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8080 `
  -RemoteAddress 192.168.50.0/24 `
  -Action Allow

# 開放 8069 (Odoo)
New-NetFirewallRule -DisplayName "Odoo POS (內網)" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8069 `
  -RemoteAddress 192.168.50.0/24 `
  -Action Allow

# 開放 11434 (Ollama，本機限定)
New-NetFirewallRule -DisplayName "Ollama (本機)" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 11434 `
  -RemoteAddress 127.0.0.1 `
  -Action Allow
```

### 5.3 資料備份政策

```bash
# 每日備份
Schedule: 02:00 AM (凌晨 2 點)

Backup Location:
- 本地: C:\wuchang V5.1.0\backups\
- 雲端: Google Drive / OneDrive (加密)
- 離站: USB 外接硬碟 (月度)

Backup Items:
- Odoo 資料庫 (events.log.jsonl, Odoo DB dump)
- 決策日誌 (decision_logs/)
- 客戶資料 (POS 交易紀錄)

Retention:
- 日備份: 30 天
- 周備份: 12 週
- 月備份: 2 年
```

---

## 第六部分：啟動與驗收檢查清單

### 6.1 系統啟動檢查

-   [ ] 伺服器電源與 UPS 連接
-   [ ] 網路交換機連接（上行/下行）
-   [ ] 主伺服器有線連接交換機埠 1
-   [ ] 路由器 WiFi 信號可用
-   [ ] 所有設備連接網路
-   [ ] Ollama 服務運行 (`ollama serve` 後台)
-   [ ] Docker 容器啟動 (`docker-compose up -d`)
-   [ ] FastAPI 伺服器運行 (`python -m uvicorn ...`)

### 6.2 功能驗收測試

#### 儀表板測試

-   [ ] 訪問 `http://192.168.50.249:8080/dashboard`
-   [ ] 裝置清單顯示正確
-   [ ] 即時事件流更新
-   [ ] 無 JavaScript 錯誤

#### 本地 LLM 測試

-   [ ] `curl http://127.0.0.1:11434/api/tags` 返回模型清單
-   [ ] `/llm/chat` 端點回應 `source: "local"`
-   [ ] 語言為 Traditional Chinese (台灣)

#### 雙角色權限測試

-   [ ] 店家 Token (`merchant-demo-001`) 可訪問 `/llm/chat`
-   [ ] 店家 Token 無法訪問 `/admin/decisions`
-   [ ] 架構師 Token (`architect-demo-001`) 可訪問所有端點
-   [ ] 無效 Token 返回 401 錯誤

#### 語音交互測試

-   [ ] `/voice/recognize` 上傳 WAV，正確轉文字
-   [ ] `/voice/synthesize` 生成可播放的 MP3
-   [ ] `/voice/command` 完整流程運作
-   [ ] 麥克風與喇叭工作正常

#### POS 結帳測試

-   [ ] POS UI 可訪問 (`http://192.168.50.249:8069/pos/ui`)
-   [ ] 可登入收銀員帳號
-   [ ] 掃描測試條碼，產品顯示正確
-   [ ] 結帳流程完成，發票列印
-   [ ] 客顯顯示應付金額

#### 決策日誌測試

-   [ ] 每個操作記錄於 `decision_logs/`
-   [ ] JSONL 檔案格式正確
-   [ ] 架構師可查詢 `/admin/decisions`
-   [ ] 審計報告統計準確

### 6.3 性能與壓力測試

```bash
# 測試 LLM 回應時間（目標 < 2秒）
time curl -H "X-Auth-Token: merchant-demo-001" \
  -d '{"message": "測試"}' \
  http://192.168.50.249:8080/llm/chat

# 測試並發請求（10 個同時 LLM 查詢）
ab -n 10 -c 10 -H "X-Auth-Token: merchant-demo-001" \
  http://192.168.50.249:8080/devices
```

---

## 第七部分：上線後運維

### 7.1 日常檢查

```powershell
# 每日 08:00 AM
- 檢查伺服器狀態：`curl http://192.168.50.249:8080/`
- 檢查 Ollama：`ollama list`
- 檢查磁碟空間：`df -h C:\`
- 檢查備份日誌：最近一次備份時間

# 每週一
- 審視決策日誌
- 檢查事件日誌大小
- 更新 LLM 模型 (`ollama pull ...`)
```

### 7.2 故障排查

| 問題         | 症狀             | 解決方案                               |
| ------------ | ---------------- | -------------------------------------- |
| 伺服器無響應 | `/` 返回 404     | 重啟 FastAPI: `docker-compose restart` |
| LLM 回應緩慢 | 查詢耗時 > 10 秒 | 檢查 Ollama: `ps aux \| grep ollama`   |
| 裝置無法連接 | POS 登入失敗     | 檢查 IP 分配、WiFi 訊號、防火牆        |
| 決策日誌遺失 | 決策記錄不完整   | 檢查 `decision_logs/` 目錄權限         |

### 7.3 定期升級

```bash
# 月度升級計劃
1. 備份資料庫
2. 更新 Python 套件: pip install --upgrade -r requirements.txt
3. 更新 Docker 映像: docker-compose pull && docker-compose up -d
4. 測試所有關鍵功能
5. 更新文件與訓練資料

# 季度大版本升級
- 升級 Ollama 模型
- 升級 FastAPI 主版本
- 審計決策日誌與 AI 倫理合規性
```

---

## 附表：成本估算

### 初期投資 (Single Shop)

| 項目     | 規格               | 數量 | 單價 USD | 小計       |
| -------- | ------------------ | ---- | -------- | ---------- |
| 主伺服器 | Ryzen 5, 16GB, SSD | 1    | $600     | $600       |
| POS 機   | i5, 8GB, 15" 觸控  | 1    | $1000    | $1000      |
| 客顯     | Android Tablet 10" | 1    | $300     | $300       |
| 交換機   | 8-port Gigabit     | 1    | $50      | $50        |
| 路由器   | WiFi 6             | 1    | $150     | $150       |
| 周邊     | 印表機、掃槍、線材 | -    | $300     | $300       |
| UPS      | 2000VA             | 1    | $200     | $200       |
| **總計** |                    |      |          | **$2,600** |

### 月度營運成本

| 項目              | 成本 USD  |
| ----------------- | --------- |
| 網路頻寬 (10Mbps) | $30       |
| 電費 (伺服器 24h) | $50       |
| 硬體維護          | $30       |
| 軟體授權 (Odoo)   | $0 (開源) |
| **月計**          | **$110**  |

---

## 版本與支援

| 組件                        | 版本         | 維護狀態 |
| --------------------------- | ------------ | -------- |
| Windows Server / Windows 11 | 2022+ / 22H2 | ✓ 支援   |
| Docker                      | 4.20+        | ✓ 支援   |
| Python                      | 3.11+        | ✓ 支援   |
| Ollama                      | 0.13.5+      | ✓ 支援   |
| FastAPI                     | 0.100+       | ✓ 支援   |
| Odoo                        | 17.0         | ✓ 支援   |

---

最後更新：2026-01-10  
維護：Wuchang AI System  
支援連絡：小j@wuchang.local
