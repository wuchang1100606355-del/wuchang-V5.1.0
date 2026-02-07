# AI 總成小 J - 最高權限開發者 UI 使用指南

**版本**: 1.0.0  
**權限等級**: Supervisor U (最高權限開發者)

---

## 🚀 快速啟動

### 啟動開發者 UI

```powershell
# 方法 1: 使用 PowerShell 腳本
cd "C:\wuchang V5.1.0\ai_j_supervisor"
.\scripts\start_developer_ui.ps1

# 方法 2: 直接執行 Python
python api\supervisor_api.py
```

### 訪問開發者 UI

```
http://localhost:8888/developer-ui
```

---

## 🎯 功能說明

### 1. 系統狀態

顯示 AI 總成小 J 的當前狀態：
- 名稱和版本
- 權限等級
- 運行狀態
- 系統時間

### 2. 能力清單

顯示所有已啟用的能力：
- **時空系統**: 時空事件管理、時間空間建議等
- **AI 能力**: 本地 Ollama、OpenAI、Anthropic、Google
- **系統權限**: 完整系統存取權限

### 3. 權限測試

執行完整權限測試，驗證：
- 時空系統存取
- AI 系統存取
- 系統配置存取
- 資料存取

### 4. 命令執行

執行各種命令：
- `spatiotemporal.suggest` - 時空建議
- `spatiotemporal.schedule` - 排程活動
- `spatiotemporal.analyze` - 分析模式
- `system.status` - 系統狀態
- `system.config` - 系統配置

### 5. 時空系統快速操作

快速執行常用操作：
- 智能建議活動時間
- 分析活動模式

---

## 🔐 權限說明

### Supervisor U (最高權限開發者)

具備以下權限：

- ✅ **完整系統存取**: 所有系統功能
- ✅ **配置修改**: 修改系統配置
- ✅ **資料存取**: 讀取和寫入所有資料
- ✅ **監控權限**: 系統監控和日誌
- ✅ **API 金鑰存取**: 所有 API 金鑰

---

## 📊 API 端點

### 系統狀態

```bash
GET http://localhost:8888/api/supervisor/status
```

### 能力清單

```bash
GET http://localhost:8888/api/supervisor/capabilities
```

### 權限測試

```bash
POST http://localhost:8888/api/supervisor/test-permissions
```

### 執行命令

```bash
POST http://localhost:8888/api/supervisor/execute
Content-Type: application/json

{
  "command": "spatiotemporal.suggest",
  "params": {
    "event_type": "meeting",
    "participants": 10,
    "duration_hours": 2
  }
}
```

---

## 🧪 測試範例

### 測試時空建議

```javascript
fetch('http://localhost:8888/api/supervisor/execute', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    command: 'spatiotemporal.suggest',
    params: {
      event_type: 'meeting',
      participants: 10,
      duration_hours: 2,
      preferred_village: 'wuchang_li'
    }
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

### 測試權限

```javascript
fetch('http://localhost:8888/api/supervisor/test-permissions')
.then(r => r.json())
.then(data => console.log(data));
```

---

## 🔧 配置

### 修改端口

編輯 `api/supervisor_api.py`:

```python
app.run(host='0.0.0.0', port=8888, debug=True)
```

### 啟用/停用功能

在 `core/supervisor.py` 中修改能力初始化邏輯。

---

## 📝 使用注意事項

1. **權限控制**: 此 UI 僅供最高權限開發者使用
2. **安全性**: 請勿在公開網路環境使用
3. **測試環境**: 建議在測試環境中先進行測試
4. **日誌記錄**: 所有操作都會記錄日誌

---

**開發者 UI 已就緒，可開始使用！**


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:22:39
---
