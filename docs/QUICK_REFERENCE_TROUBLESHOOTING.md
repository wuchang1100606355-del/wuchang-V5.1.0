# 五常 POS 系統 - 快速參考卡 & 故障排查

## 🚀 快速啟動（1 分鐘版）

### 店家快速啟動

```bash
# 1. 確保伺服器已啟動
ping 192.168.50.249

# 2. 開啟儀表板
# 瀏覽器: http://192.168.50.249:8080/dashboard

# 3. 語音查詢示例
# 用平板錄音問「今天營業額多少？」
# 上傳至 /voice/command
# 等待語音回應
```

### 架構師快速啟動

```bash
# 1. 連接到伺服器
curl -H "X-Auth-Token: architect-demo-001" \
  http://192.168.50.249:8080/admin/decisions | jq '.'

# 2. 查看審計報告
curl -H "X-Auth-Token: architect-demo-001" \
  http://192.168.50.249:8080/admin/audit | jq '.'

# 3. 分析決策日誌
ls -la decision_logs/MERCHANT/
tail -50 decision_logs/MERCHANT/decisions_2026-01-10.jsonl | jq '.'
```

---

## 📋 系統檢查清單

### 每日 08:00 AM 檢查

```powershell
# 1️⃣ 伺服器健康檢查
curl http://192.168.50.249:8080/
# 期望回傳: {"status": "Active"}

# 2️⃣ Ollama 狀態
ollama list
# 期望看到: little-j (4.7GB)

# 3️⃣ 裝置連接
curl -H "X-Auth-Token: merchant-demo-001" \
  http://192.168.50.249:8080/devices | jq '.count'
# 期望: >= 1

# 4️⃣ LLM 回應測試
curl -X POST \
  -H "X-Auth-Token: merchant-demo-001" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}' \
  http://192.168.50.249:8080/llm/chat | jq '.source'
# 期望: "local"

# 5️⃣ 磁碟空間
df -h C:\
# 期望: >= 20GB 可用

# 6️⃣ 決策日誌
ls -la decision_logs/MERCHANT/ | wc -l
# 期望: > 0

# 結果: 綠色✓ 表示正常
```

---

## 🔧 故障排查決策樹

```
【伺服器無響應】
├─ 檢查 ping 192.168.50.249
│  ├─ ❌ 無回應
│  │  ├─ 1️⃣ 檢查伺服器是否開機
│  │  ├─ 2️⃣ 檢查網路交換機指示燈
│  │  └─ 3️⃣ 檢查伺服器網卡驅動
│  │
│  └─ ✅ 有回應
│     └─ 進行 API 測試...
│
├─ 檢查 http://192.168.50.249:8080/
│  ├─ ❌ 連接超時 (timeout)
│  │  ├─ 1️⃣ FastAPI 進程未運行
│  │  │  解決: powershell -ExecutionPolicy Bypass start_pos_system_dual_role.ps1
│  │  ├─ 2️⃣ 防火牆阻擋 8080 埠
│  │  │  解決: netsh advfirewall firewall add rule ...
│  │  └─ 3️⃣ 埠被佔用
│  │     檢查: netstat -ano | findstr :8080
│  │
│  ├─ ❌ 返回 404
│  │  └─ FastAPI 應用掛載錯誤
│  │     解決: 檢查 vm_fastapi_main_dual_role.py 語法
│  │
│  └─ ✅ 返回 200 + JSON
│     └─ 伺服器運行正常 ✓

【LLM 回應異常】
├─ 返回 "source: vertex" (雲端)
│  └─ 本地 LLM 未連接
│     ├─ 1️⃣ Ollama 未啟動
│     │  檢查: tasklist | findstr ollama
│     │  啟動: ollama serve (背景)
│     ├─ 2️⃣ Ollama 端點不對
│     │  驗證: curl http://127.0.0.1:11434/api/tags
│     └─ 3️⃣ 模型未下載
│        檢查: ollama list
│        下載: ollama pull little-j
│
├─ 返回 "(LLM 暫時不可用)"
│  └─ 雲端備援也失敗
│     ├─ 檢查網路連接
│     ├─ 檢查 Vertex AI 認證金鑰
│     └─ 聯絡 Google Cloud 支援
│
├─ 回應時間 > 10 秒
│  └─ 效能問題
│     ├─ 1️⃣ Ollama 佔用率過高
│     │  檢查: taskmgr (看 GPU/CPU)
│     ├─ 2️⃣ 網路延遲
│     │  測試: ping 8.8.8.8 (延遲 < 30ms)
│     └─ 3️⃣ 伺服器資源不足
│        升級 RAM 或關閉其他服務

【語音端點失敗】
├─ /voice/recognize 返回 "未安裝 Whisper"
│  └─ 安裝 Whisper 模型
│     pip install openai-whisper
│     whisper-cli --model tiny
│
├─ /voice/synthesize 返回 "未安裝 pyttsx3"
│  └─ 安裝文字轉語音
│     pip install pyttsx3
│     (自動使用 Windows SAPI5)
│
└─ 無法錄製/播放語音
   ├─ 檢查麥克風與喇叭是否接妥
   ├─ 檢查音量設定 (不要靜音)
   ├─ 測試: ffplay test.mp3
   └─ 重啟音頻服務 (restart Windows Audio)

【權限拒絕】
├─ 返回 "401 Unauthorized"
│  └─ Token 無效或遺漏
│     ├─ 檢查 X-Auth-Token 標頭
│     ├─ 使用有效 Token:
│     │  - merchant-demo-001 (店家)
│     │  - architect-demo-001 (架構師)
│     └─ 若需新增 Token，編輯 VALID_TOKENS
│
├─ 返回 "403 Forbidden"
│  └─ Token 有效但權限不足
│     ├─ 店家無法訪問 /admin/* 端點
│     ├─ 架構師可訪問所有端點
│     └─ 若需更改權限，編輯 PERMISSION_MATRIX

【決策日誌問題】
├─ 日誌未記錄
│  └─ 檢查 decision_logs/ 目錄
│     ├─ 路徑: C:\wuchang V5.1.0\decision_logs\
│     ├─ 目錄權限: 允許寫入 (Read/Write)
│     └─ 磁碟空間充足 (> 100MB)
│
├─ 日誌文件損壞
│  └─ 手動修復 JSONL
│     ├─ 每行必須有效 JSON
│     ├─ 移除不完整行
│     └─ 重新啟動伺服器

【POS UI 無法訪問】
├─ http://192.168.50.249:8069/pos/ui 返回 Connection Refused
│  └─ Odoo 容器未運行
│     ├─ 檢查: docker ps | findstr odoo
│     ├─ 啟動: docker-compose up -d
│     └─ 等待 30 秒 (首次啟動慢)
│
└─ 返回 502 Bad Gateway
   └─ Odoo 進程崩潰
      ├─ 查看日誌: docker logs wuchang_odoo
      ├─ 重啟: docker-compose restart
      └─ 若反覆失敗，檢查記憶體 (需 4GB+)
```

---

## 🆘 常見錯誤訊息解讀

### FastAPI / Uvicorn

```
❌ "Address already in use"
→ 埠 8080 已被佔用
解決:
  netstat -ano | findstr :8080
  taskkill /PID <PID> /F
  (或使用不同埠)

❌ "ModuleNotFoundError: No module named 'fastapi'"
→ 虛擬環境未啟用
解決:
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt

❌ "CORS policy: No 'Access-Control-Allow-Origin'"
→ 跨域資源共用限制
解決:
  確認 FastAPI 已配置 CORS Middleware
  (已在 vm_fastapi_main_dual_role.py 中設定)
```

### Ollama / LLM

```
❌ "Connection refused (127.0.0.1:11434)"
→ Ollama 未運行或端口不對
解決:
  ollama serve (背景啟動)
  驗證: curl http://127.0.0.1:11434/api/tags

❌ "Model not found: little-j"
→ 模型未下載
解決:
  ollama pull little-j (需要 5-10 分鐘)
  確認磁碟空間 (需要 4.7GB)

❌ "CUDA out of memory"
→ 顯卡記憶體不足
解決:
  降級模型: ollama pull qwen2:0.5b
  或使用 CPU: 設定環境變數 OLLAMA_USE_CPU=true
```

### Docker

```
❌ "Cannot connect to Docker daemon"
→ Docker Desktop 未運行
解決:
  開啟 Docker Desktop 應用
  等待系統匯流排 (System Bus) 就緒

❌ "Port already in use"
→ 容器埠衝突
解決:
  docker ps (查看已運行容器)
  docker-compose down
  修改 docker-compose.yml 中的埠對應

❌ "Insufficient memory"
→ 記憶體不足
解決:
  docker stats (查看容器 memory 使用)
  關閉其他容器: docker stop <container>
  或升級伺服器 RAM
```

### 網路

```
❌ "Network is unreachable"
→ 網路未連接
解決:
  ipconfig (檢查 IP 分配)
  ping 192.168.50.1 (路由器)
  檢查 WiFi / 有線網卡

❌ "Host 192.168.50.249 is down"
→ 伺服器離線
解決:
  1️⃣ 檢查伺服器電源
  2️⃣ 檢查網線連接
  3️⃣ 檢查網卡指示燈

❌ "Temporary failure in name resolution"
→ DNS 無法解析
解決:
  nslookup google.com (測試 DNS)
  手動指定 IP: 192.168.50.249
  檢查路由器 DNS 設定
```

---

## 📞 遠端支援指令

### 收集診斷訊息

```powershell
# 製作診斷套件
$diagDir = "C:\wuchang_diag_$(Get-Date -Format yyyyMMdd_HHmm)"
mkdir $diagDir

# 1. 系統資訊
Get-ComputerInfo | Out-File "$diagDir\sysinfo.txt"
Get-NetIPConfiguration | Out-File "$diagDir\ipconfig.txt"

# 2. 服務狀態
docker ps --all | Out-File "$diagDir\docker_status.txt"
tasklist | Out-File "$diagDir\processes.txt"

# 3. 網路診斷
ping 192.168.50.1 | Out-File "$diagDir\router_ping.txt"
curl http://localhost:8080/ | Out-File "$diagDir\server_health.txt"

# 4. 日誌
Copy-Item "C:\wuchang V5.1.0\events.log.jsonl" "$diagDir\" -ErrorAction SilentlyContinue
Copy-Item "C:\wuchang V5.1.0\decision_logs" "$diagDir\decision_logs_backup" -Recurse -ErrorAction SilentlyContinue

# 5. 打包診斷檔案
Compress-Archive -Path $diagDir -DestinationPath "$diagDir.zip"

Write-Host "診斷套件已生成: $diagDir.zip"
```

### 遠端連接

```powershell
# 啟用 PowerShell Remoting (架構師專用)
Enable-PSRemoting -Force

# 遠端執行指令
Invoke-Command -ComputerName 192.168.50.249 -ScriptBlock {
    curl http://localhost:8080/ | ConvertFrom-Json
}

# 遠端停止服務
Invoke-Command -ComputerName 192.168.50.249 -ScriptBlock {
    docker-compose down
}
```

---

## 📊 效能基準線

### 正常運作指標

| 指標             | 正常範圍   | 警告範圍  | 危險範圍   |
| ---------------- | ---------- | --------- | ---------- |
| LLM 回應時間     | < 2 秒     | 2-5 秒    | > 5 秒 ❌  |
| 伺服器 CPU       | < 50%      | 50-80%    | > 80% ❌   |
| 伺服器 RAM       | < 60%      | 60-85%    | > 85% ❌   |
| 網路延遲 (ping)  | < 10ms     | 10-50ms   | > 50ms ❌  |
| 磁碟可用空間     | > 50GB     | 20-50GB   | < 20GB ❌  |
| API 錯誤率       | < 1%       | 1-5%      | > 5% ❌    |
| 決策日誌檔案大小 | < 100MB/月 | 100-300MB | > 300MB ⚠️ |

### 壓力測試結果

```
測試環境: Ryzen 5 3600, 16GB RAM, SSD
並發使用者: 5
持續時間: 10 分鐘

結果:
✅ 平均 LLM 回應時間: 1.8 秒
✅ 平均 API 回應時間: 0.3 秒
✅ CPU 使用率: 45%
✅ 記憶體使用率: 58%
✅ 無連接錯誤
✅ 決策日誌完整記錄
```

---

## 🚨 緊急聯絡流程

```
【Level 1 - 輕微問題 (可暫停營業 < 5 分鐘)】
症狀: 單一設備無法連接、語音功能失效
→ 自行使用本指南故障排查
→ 若 5 分鐘內未解決，聯絡技術支援

【Level 2 - 中等問題 (影響營業 5-30 分鐘)】
症狀: POS 無法結帳、Ollama 崩潰
→ 立即重啟伺服器: docker-compose down && docker-compose up -d
→ 若無效果，聯絡架構師
→ 激活備用 POS (若有)

【Level 3 - 嚴重問題 (營業完全中斷)】
症狀: 伺服器硬體故障、水災/火災
→ 停止營業，啟用應急方案
→ 立即聯絡 IT 總監 & 董事
→ 準備備用伺服器 (異地備份)
→ 紙本收據應急結帳

【技術支援聯絡】
電話: (待填)
Email: littlej-support@wuchang.local
WhatsApp: (待填)
Line: (待填)
```

---

## 📚 進階除錯技巧

### 啟用詳細日誌

```python
# 編輯 vm_fastapi_main_dual_role.py
import logging
logging.basicConfig(level=logging.DEBUG)

# 設定環境變數
$env:PYTHONUNBUFFERED=1  # 即時列印日誌
$env:FASTAPI_ENV="development"
```

### 監控系統

```bash
# 實時監控伺服器效能
while ($true) {
    Clear-Host
    Write-Host "系統監控 $(Get-Date)"

    # CPU/RAM
    Get-CimInstance Win32_Processor | Select -ExpandProperty LoadPercentage
    Get-CimInstance Win32_OperatingSystem | Select @{N='MemoryUsage%';E={[int]($_.TotalVisibleMemorySize-$_.FreePhysicalMemory)/$_.TotalVisibleMemorySize*100}}

    # Docker
    docker stats --no-stream

    # 網路
    netstat -an | findstr "8080\|8069\|11434" | Measure-Object | Select Count

    Start-Sleep -Seconds 5
}
```

---

版本：v1.0  
最後更新：2026-01-10  
維護：小 j AI System
