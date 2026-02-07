# 時空系統部署指南 - AI 小 J 整合

**版本**: 1.0.0  
**日期**: 2026-01-18  
**目標**: 將時空能力完整部署到系統及 AI 小 J

---

## 📋 部署流程

### 步驟 1: 安裝依賴套件

```powershell
# 以管理員權限執行
cd "C:\wuchang V5.1.0\spatiotemporal_system"
.\scripts\install_dependencies.ps1
```

或手動安裝：

```bash
pip install -r requirements.txt
```

### 步驟 2: 設定完整授權

```powershell
# 以管理員權限執行
.\scripts\setup_full_authorization.ps1 -EnableCloudCompute -FullAccess
```

這會設定：
- AI 小 J 完整授權
- 時空系統存取權限
- 雲端算力存取權限（如需要）

### 步驟 3: 部署到 AI 小 J

```bash
python scripts/deploy_to_ai_j.py
```

或使用完整安裝腳本：

```powershell
.\scripts\install_and_deploy.ps1
```

---

## 🔑 雲端算力設定

### 設定 API Key

#### OpenAI
```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-key-here", "User")
```

#### Anthropic
```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "your-key-here", "User")
```

#### Google
```powershell
[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "your-key-here", "User")
```

### 驗證設定

```python
import os
print("OpenAI:", bool(os.getenv('OPENAI_API_KEY')))
print("Anthropic:", bool(os.getenv('ANTHROPIC_API_KEY')))
print("Google:", bool(os.getenv('GOOGLE_API_KEY')))
```

---

## 🧪 測試部署

### 測試時空系統

```python
from spatiotemporal_system.core.spatiotemporal import SpatiotemporalSystem
from spatiotemporal_system.core.ai_agent import AIAgent

# 初始化
st_system = SpatiotemporalSystem()
ai_j = AIAgent(st_system)

# 測試建議功能
suggestions = ai_j.suggest_optimal_time_and_space(
    event_type="meeting",
    participants=10,
    duration_hours=2
)
print(suggestions)
```

### 測試 AI 小 J 整合

```python
from spatiotemporal_system.config.ai_j_integration import get_ai_j_spatiotemporal

# 取得整合實例
st_integration = get_ai_j_spatiotemporal()

# 查看能力
capabilities = st_integration.get_capabilities()
print(capabilities)

# 測試建議
suggestions = st_integration.suggest_event(
    event_type="meeting",
    participants=10,
    duration_hours=2
)
print(suggestions)
```

---

## 🔧 AI 小 J 中使用時空能力

### 在 AI 小 J 代碼中整合

```python
# 在 AI 小 J 的初始化代碼中
from spatiotemporal_system.config.ai_j_integration import get_ai_j_spatiotemporal

class AIJ:
    def __init__(self):
        # 載入時空能力
        self.spatiotemporal = get_ai_j_spatiotemporal()
        
    def handle_spatiotemporal_request(self, request):
        """處理時空相關請求"""
        if "建議活動時間" in request:
            # 使用時空能力
            suggestions = self.spatiotemporal.suggest_event(
                event_type="meeting",
                participants=10,
                duration_hours=2
            )
            return suggestions
```

### 在對話中使用

AI 小 J 現在可以回應：

- "幫我建議一個會議的時間和地點"
- "分析一下五常里的活動模式"
- "排程一個社區活動"
- "查詢五常里今天的日程"

---

## 📊 功能清單

### 已部署的時空能力

- ✅ 時空事件管理
- ✅ 時間空間智能建議
- ✅ 排程優化
- ✅ 活動模式分析
- ✅ 空間使用率預測
- ✅ 社區服務管理

### 雲端算力功能（如已設定）

- ✅ OpenAI GPT 整合
- ✅ Anthropic Claude 整合
- ✅ Google Gemini 整合

---

## 🚨 故障排除

### 問題：模組找不到

```bash
# 檢查 Python 路徑
python -c "import sys; print(sys.path)"

# 添加時空系統路徑
export PYTHONPATH="${PYTHONPATH}:C:\wuchang V5.1.0\spatiotemporal_system"
```

### 問題：權限不足

```powershell
# 以管理員權限執行
Start-Process powershell -Verb RunAs
```

### 問題：API Key 無效

```python
# 檢查環境變數
import os
print(os.getenv('OPENAI_API_KEY'))
```

---

## 📝 授權配置檔案

授權配置儲存在：
`spatiotemporal_system/config/authorization.json`

內容範例：
```json
{
  "ai_j": {
    "full_authorization": true,
    "spatiotemporal_access": true,
    "cloud_compute_access": true
  },
  "spatiotemporal_system": {
    "enabled": true,
    "version": "1.0.0"
  }
}
```

---

## 🔄 更新部署

當更新時空系統時：

```powershell
# 1. 更新依賴
pip install -r requirements.txt --upgrade

# 2. 重新部署
python scripts/deploy_to_ai_j.py

# 3. 重啟 AI 小 J
```

---

**部署狀態**: ✅ 就緒  
**維護者**: AI 小 J
