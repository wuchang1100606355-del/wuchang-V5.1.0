# 兩機區網互通設定指南

## 概述

本指南說明如何設定兩機（本機與伺服器）之間的區網互通，實現檔案同步和服務連接。

## 快速開始

### 方式一：使用配置檔案（推薦）

1. **建立配置檔案**
   ```bash
   Copy-Item network_interconnection_config.example.json network_interconnection_config.json
   ```

2. **編輯配置檔案**
   填入實際的伺服器資訊：
   ```json
   {
     "server_ip": "192.168.1.100",
     "server_share": "\\\\SERVER\\share\\wuchang",
     "health_url": "http://192.168.1.100:8788/health",
     "hub_url": "http://192.168.1.100:8799",
     "hub_token": "your_hub_token_here"
   }
   ```

3. **執行自動設定**
   ```bash
   python setup_network_interconnection.py
   ```

### 方式二：使用環境變數

在 PowerShell 中設定：

```powershell
$env:WUCHANG_SERVER_IP = "192.168.1.100"
$env:WUCHANG_COPY_TO = "\\SERVER\share\wuchang"
$env:WUCHANG_HEALTH_URL = "http://192.168.1.100:8788/health"
$env:WUCHANG_HUB_URL = "http://192.168.1.100:8799"
$env:WUCHANG_HUB_TOKEN = "your_token"
```

然後執行：
```bash
python setup_network_interconnection.py
```

### 方式三：使用互動式腳本

```powershell
.\setup_file_sync_env.ps1
```

## 設定步驟詳解

### 步驟 1：檢測網路配置

腳本會自動檢測：
- 本機 IP 地址
- 主機名稱
- 網路介面資訊

### 步驟 2：載入網路配置

優先順序：
1. `network_interconnection_config.json` 配置檔案
2. 環境變數
3. 預設值（本機 IP）

### 步驟 3：測試連接

自動測試：
- 伺服器 IP 連接（端口 80）
- SMB 共享路徑可訪問性
- 健康檢查 URL 可達性

### 步驟 4：設定環境變數

自動設定以下環境變數：
- `WUCHANG_COPY_TO`: 伺服器共享路徑
- `WUCHANG_HEALTH_URL`: 健康檢查 URL
- `WUCHANG_HUB_URL`: Hub URL（如果提供）
- `WUCHANG_HUB_TOKEN`: Hub Token（如果提供）

### 步驟 5：儲存配置

配置會儲存到 `network_interconnection_config.json`，方便後續使用。

### 步驟 6：自動授權（可選）

如果控制中心運行中且配置了 `auto_auth_config.json`，會嘗試自動獲取權限。

## 配置檔案格式

### network_interconnection_config.json

```json
{
  "server_ip": "192.168.1.100",
  "server_share": "\\\\SERVER\\share\\wuchang",
  "health_url": "http://192.168.1.100:8788/health",
  "hub_url": "http://192.168.1.100:8799",
  "hub_token": "your_hub_token_here"
}
```

**欄位說明：**
- `server_ip`: 伺服器 IP 地址（必填）
- `server_share`: SMB 共享路徑（格式：`\\SERVER\share\path`）
- `health_url`: 伺服器健康檢查 URL
- `hub_url`: Little J Hub URL（選填）
- `hub_token`: Hub 認證 Token（選填）

## 網路設定要求

### SMB 共享設定

1. **在伺服器端設定共享資料夾**
   - 建立共享資料夾
   - 設定共享權限
   - 記錄共享路徑（例如：`\\SERVER\share\wuchang`）

2. **在本機端測試連接**
   ```powershell
   Test-Path "\\SERVER\share\wuchang"
   ```

### 防火牆設定

確保以下端口開放：
- **8788**: 本機中控台
- **8799**: Little J Hub（如果使用）
- **80/443**: HTTP/HTTPS（健康檢查）
- **445**: SMB 共享

### 網路連接測試

```bash
# 測試 IP 連接
ping 192.168.1.100

# 測試端口
Test-NetConnection -ComputerName 192.168.1.100 -Port 8788

# 測試 SMB 共享
Test-Path "\\192.168.1.100\share\wuchang"
```

## 驗證設定

### 檢查環境變數

```bash
python setup_env_vars.py status
```

### 測試連接

```bash
python check_server_connection.py
```

### 測試檔案同步

```bash
# 先檢查版本差距
python check_version_diff.py --profile kb

# 執行同步
python sync_all_profiles.py
```

## 常見問題

### Q: SMB 共享無法訪問

**解決方案：**
1. 確認伺服器已啟用 SMB 共享
2. 檢查防火牆設定（端口 445）
3. 確認共享路徑格式正確（`\\SERVER\share\path`）
4. 檢查網路連接（ping 測試）

### Q: 健康檢查 URL 不可達

**解決方案：**
1. 確認伺服器控制中心正在運行
2. 檢查防火牆設定
3. 確認 URL 格式正確
4. 測試直接訪問 URL

### Q: 環境變數設定後無效

**解決方案：**
1. 確認在正確的 PowerShell 會話中設定
2. 重新啟動終端機
3. 使用永久設定（`-Persistent` 參數）
4. 檢查環境變數是否正確設定

## 相關文件

- `setup_file_sync_env.ps1` - 互動式環境變數設定
- `check_server_connection.py` - 連接狀態檢查
- `sync_all_profiles.py` - 檔案同步工具
