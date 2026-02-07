# 地端檔案夾內的 LLM 模型位置清單

**生成時間**: 2026-01-07  
**系統版本**: Wuchang OS V5.1.0

---

## 📍 地端檔案夾內的所有 LLM 模型位置

### 1. Docker Volume 實際位置 (Windows)

**Docker Volume 名稱**: `wuchangv510_ollama-data`

**Windows 系統上的實際路徑** (通過 WSL):
```
\\wsl$\docker-desktop-data\data\docker\volumes\wuchangv510_ollama-data\_data
```

**或使用**:
```
\\wsl.localhost\docker-desktop-data\data\docker\volumes\wuchangv510_ollama-data\_data
```

**說明**: 
- 這是 Docker Desktop for Windows 使用的 WSL2 虛擬磁碟位置
- 需要 WSL2 和 Docker Desktop 運行中才能訪問
- 實際文件存儲在 WSL2 的虛擬磁碟中

---

### 2. 容器內的模型目錄結構

**容器內根目錄**: `/root/.ollama`  
**總大小**: 336 MB

**目錄結構**:
```
/root/.ollama/
├── models/
│   ├── manifests/          # 模型清單和元數據
│   └── blobs/              # 模型文件存儲 (GGUF 格式)
├── id_ed25519              # SSH 密鑰
└── id_ed25519.pub          # SSH 公鑰
```

**模型文件實際位置**:
- **清單文件**: `/root/.ollama/models/manifests/registry.ollama.ai/library/qwen2/0.5b`
- **模型文件目錄**: `/root/.ollama/models/blobs/`
- **模型文件列表**:
  - `sha256-8de95da68dc485c0889c205384c24642f83ca18d089559c977ffc6a3972a71a8` (主模型文件)
  - `sha256-62fbfd9ed093d6e5ac83190c86eec5369317919f4b149598d2dbb38900e9faef`
  - `sha256-f02dd72bb2423204352eabc5637b44d79d17f109fdb510a7c51455892aa2d216`
  - `sha256-c156170b718ec29139d3653d40ed1986fd92fb7e0959b5c71f3c48f62e6636f4`
  - `sha256-2184ab82477bc33a5e08fa209df88f0631a19e686320cce2cfe9e00695b2f0e6`
- **模型名稱**: `qwen2:0.5b`
- **模型 ID**: `6f48b936a09f`

---

### 3. 專案目錄中的模型備份

**備份文件位置**:
```
C:\wuchang V5.1.0\migration_pack\volumes\ollama-data.tar.gz
```

**說明**:
- 這是 Ollama 數據的打包備份
- 可能包含已下載的模型文件
- 可用於遷移或恢復

---

### 4. 本地配置文件中的模型引用位置

#### 系統配置

**文件**: `wuchang_os/addons/wuchang_core/data/system_params.xml`
- **行號**: 50
- **參數**: `wuchang.ollama_model = llama3.1` (配置值，實際使用 `qwen2:0.5b`)

#### 代碼文件

**文件**: `wuchang_os/addons/wuchang_core/models/ai_logic.py`
- **行號**: 22
- **模型**: `qwen2:0.5b` (預設值)

**文件**: `小J運動控制.py`
- **行號**: 24
- **模型**: `qwen2:0.5b` (本地可用模型)

---

## 📊 總結

### 地端實際模型文件位置

| 項目 | 路徑 | 說明 |
|------|------|------|
| **Docker Volume** | `\\wsl$\docker-desktop-data\data\docker\volumes\wuchangv510_ollama-data\_data` | Windows 訪問路徑 |
| **容器內路徑** | `/root/.ollama/models/` | 容器內實際目錄 |
| **模型清單** | `/root/.ollama/models/manifests/` | 模型元數據 |
| **模型文件** | `/root/.ollama/models/blobs/` | 實際 GGUF 模型文件 |
| **備份位置** | `migration_pack\volumes\ollama-data.tar.gz` | 專案目錄中的備份 |

### 已下載的模型

- **模型名稱**: `qwen2:0.5b`
- **模型 ID**: `6f48b936a09f`
- **大小**: 336 MB (容器內總大小)
- **格式**: GGUF (Q4_0 量化)
- **位置**: `/root/.ollama/models/blobs/` (容器內)

---

## 🔍 訪問方式

### 從 Windows 訪問模型文件

1. **通過 WSL 路徑** (需要 WSL 運行):
   ```powershell
   # 在文件管理器或 PowerShell 中
   \\wsl$\docker-desktop-data\data\docker\volumes\wuchangv510_ollama-data\_data
   ```

2. **通過 Docker 命令**:
   ```powershell
   # 列出模型文件
   docker exec wuchangv510-ollama-1 find /root/.ollama/models -type f
   
   # 複製模型文件到本地
   docker cp wuchangv510-ollama-1:/root/.ollama/models ./local_models
   ```

3. **查看模型信息**:
   ```powershell
   docker exec wuchangv510-ollama-1 ollama list
   docker exec wuchangv510-ollama-1 ollama show qwen2:0.5b
   ```

---

**最後更新**: 2026-01-07  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)
