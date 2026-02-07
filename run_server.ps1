# 啟動 Wuchang 管理伺服器（本機 UI + 本地 LLM 優先）
# 目標伺服器：192.168.50.249，預設 Port：8080

# 1) 啟用虛擬環境
& "C:/wuchang V5.1.0/.venv/Scripts/Activate.ps1"

# 2) 安裝相依套件（如已安裝可略過）
python -m pip install -r "C:/wuchang V5.1.0/requirements.txt"

# 3) 設定 UI 與本地 LLM 端點（依需求調整）
$env:POS_UI_URL = "http://192.168.50.249:8069/pos/ui"
$env:CUSTOMER_UI_URL = "http://192.168.50.249:8069/pos/customer_display"
# 使用 Ollama 本地 LLM（妹妹的本地大腦）
$env:LOCAL_LLM_ENDPOINT = "http://127.0.0.1:11434/v1/chat/completions"
$env:LOCAL_LLM_MODEL = "little-j"
$env:LOCAL_LLM_API_KEY = ""  # Ollama 不需要認證
# 隱私/備援：1=允許雲端備援；0=嚴格本地僅用
$env:LLM_FALLBACK = "1"

# 4) 啟動伺服器（外網可達）
# 建議同時開放防火牆：
# New-NetFirewallRule -DisplayName "Wuchang FastAPI 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
python "C:/wuchang V5.1.0/vm_port_server.py"
