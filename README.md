# 五常系統 V5.1.0

這是五常系統的主要儲存庫，包含多個工具和功能模組。

## 主要功能

### 1. 雲端代理程式委派與變更認可系統

互動式工作區工具，用於：
- 認可程式碼變更
- 委派任務至雲端代理程式
- 管理工作流程和任務追蹤

**快速開始：**
```powershell
.\start_j_chaing.ps1
```

詳細文件：[雲端代理程式委派指南](./CLOUD_AGENT_DELEGATION_GUIDE.md)

### 2. 華碩路由器 DDNS 連接工具

用於連接到華碩路由器的 DDNS 地址 `coffeeLofe.asuscomm.com` 或直接使用 IP 地址連接。

**功能：**
- 測試連接到華碩路由器
- 支持 HTTPS 連接（使用本機已安裝的證書）
- 路由器登錄功能
- 獲取路由器信息

### 3. 雙J重點記憶系統

核心記憶系統，包含七大重點記憶：
- 工作日誌
- Google非營利規範
- 系統白皮書
- 雙J部署流程
- 雙J維運流程
- 最高權限授權
- 工具清單

詳細文件：[雙J重點記憶系統](./DUAL_J_CRITICAL_MEMORY_SYSTEM.md)

## 安裝

### Python 工具

```bash
pip install -r requirements.txt
```

### PowerShell 工具

PowerShell 腳本無需特別安裝，直接執行即可。部分腳本需要管理員權限。

## 使用方法

### 雲端代理程式委派工具

```powershell
# 啟動互動式工作區
.\start_j_chaing.ps1

# 主要功能：
# 1. 檢視待認可的變更
# 2. 認可變更
# 3. 委派至雲端代理程式
# 4. 認可變更並委派至雲端代理程式
# 5. 檢視工作區狀態
# 6. 設定互動工作區
# 7. 執行自訂命令
```

### 路由器連接工具

#### 1. 基本連接測試

```bash
python router_connection.py
```

#### 2. 登錄路由器

**方式一：交互式登錄**
```bash
python login_router.py
```
然後按提示輸入用戶名和密碼。

**方式二：命令行參數**
```bash
python login_router.py <用戶名> <密碼>
```

例如：
```bash
python login_router.py admin mypassword
```

#### 3. 在代碼中使用

```python
from router_connection import AsusRouterConnection

# 創建連接對象
router = AsusRouterConnection(
    hostname="220.135.21.74",  # 或使用域名
    port=8443,
    use_https=True
)

# 測試連接
router.test_connection(verify_cert=False)

# 登錄
router.login(username="admin", password="your_password", verify_cert=False)

# 獲取路由器信息
info = router.get_router_info(verify_cert=False)
```

## 連接信息

- **IP 地址**: `220.135.21.74`
- **域名**: `coffeeLofe.asuscomm.com` (DDNS，目前無法解析)
- **端口**: `8443` (HTTPS)
- **協議**: HTTPS

## 注意事項

1. **域名修正**: 原輸入為 `coffeeLofe.asuscomm.comm`，已修正為 `coffeeLofe.asuscomm.com`
2. **證書**: 使用 IP 地址連接時，SSL 證書驗證會失敗（因為證書是為域名簽發的），這是正常現象
3. **端口**: 默認使用 8443（HTTPS），如果路由器使用其他端口，請修改 `port` 參數
4. **防火牆**: 確保防火牆允許連接到路由器端口

## 常見端口

- 8443: HTTPS（推薦，當前使用）
- 8080: HTTP
- 443: 標準 HTTPS
- 80: 標準 HTTP

## 故障排除

如果連接失敗：

1. 檢查路由器是否開啟並連接到網路
2. 確認 DDNS 配置正確（如果使用域名）
3. 檢查防火牆設置
4. 驗證證書是否正確安裝
5. 嘗試不同的端口號
6. 使用 IP 地址直接連接（如果 DDNS 無法解析）

## 登錄問題

如果登錄失敗：

1. 確認用戶名和密碼正確
2. 檢查路由器是否啟用了遠程登錄
3. 某些路由器可能需要額外的認證步驟
4. 嘗試在瀏覽器中手動登錄以確認憑證

### 實用工具（UTS 目錄）

`uts/` 目錄包含多個實用工具腳本：

- **cleanup_and_compress_virtual_disks.ps1** - 清理和壓縮虛擬硬碟
- **compress_docker_disk.ps1** - 壓縮 Docker 虛擬硬碟
- **move_bluestacks_to_j_drive.ps1** - 移動 BlueStacks 到 J 碟
- **remove_virtualbox_completely.ps1** - 完全移除 VirtualBox
- **analyze_virtual_disks.py** - 分析虛擬硬碟使用情況
- **check_virtualbox.py** - 檢查 VirtualBox 安裝狀態

## 專案結構

```
wuchang-V5.1.0/
├── start_j_chaing.ps1              # 雲端代理程式委派工具（主程式）
├── cloud_agent_config.json         # 雲端代理配置檔案
├── CLOUD_AGENT_DELEGATION_GUIDE.md # 雲端代理使用指南
├── DUAL_J_CRITICAL_MEMORY_SYSTEM.md# 雙J重點記憶系統
├── README.md                       # 專案說明文件
├── router_connection.py            # 路由器連接模組
├── login_router.py                 # 路由器登錄工具
├── diagnose_connection.py          # 連接診斷工具
├── test_local_connection.py        # 本地連接測試
├── requirements.txt                # Python 依賴項
└── uts/                           # 實用工具目錄
    ├── cleanup_and_compress_virtual_disks.ps1
    ├── compress_docker_disk.ps1
    ├── move_bluestacks_to_j_drive.ps1
    ├── remove_virtualbox_completely.ps1
    ├── analyze_virtual_disks.py
    ├── check_virtualbox.py
    ├── BLUESTACKS_INFO.md
    ├── VIRTUAL_DISK_EXPLANATION.md
    └── virtualbox_usage_analysis.md
```

## 配置檔案

### cloud_agent_config.json

配置雲端代理程式的行為和偏好設定。主要設定包括：

- **cloudAgent**: 雲端代理程式配置（名稱、類型、端點）
- **workspace**: 工作區設定（互動模式、自動提交、自動委派）
- **approval**: 認可設定（需要確認、自動認可小變更）
- **delegation**: 委派設定（預設代理、任務記錄路徑、最大併發任務）
- **git**: Git 設定（自動暫存、自動推送、預設分支）

詳細說明請參閱 [雲端代理程式委派指南](./CLOUD_AGENT_DELEGATION_GUIDE.md)。

## 相關文件

- [雲端代理程式委派指南](./CLOUD_AGENT_DELEGATION_GUIDE.md) - 詳細的使用說明和工作流程
- [雙J重點記憶系統](./DUAL_J_CRITICAL_MEMORY_SYSTEM.md) - 核心記憶系統文件
- [BlueStacks 說明](./uts/BLUESTACKS_INFO.md) - BlueStacks 使用說明
- [虛擬硬碟說明](./uts/VIRTUAL_DISK_EXPLANATION.md) - 虛擬硬碟管理說明
- [VirtualBox 使用分析](./uts/virtualbox_usage_analysis.md) - VirtualBox 分析報告

## 貢獻

歡迎提交問題和改進建議。請遵循以下指南：

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 授權

此專案為五常系統的一部分，遵循相關授權協議。

## 聯絡方式

如有問題或建議，請透過 GitHub Issues 回報。