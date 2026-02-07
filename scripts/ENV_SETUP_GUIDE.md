# 環境變數設定指南

## 快速開始

### 方式一：互動式腳本（推薦）

在 PowerShell 中執行：

```powershell
.\setup_file_sync_env.ps1
```

腳本會逐步提示您輸入：
1. **伺服器健康檢查 URL**
   - 範例：`https://wuchang.life/health`
   - 用途：同步前檢查伺服器是否可達

2. **伺服器接收資料夾路徑**
   - 範例：`\\SERVER\share\wuchang`
   - 用途：檔案同步的目標目錄

3. **Hub URL**（選填）
   - 範例：`https://hub.wuchang.life`
   - 用途：Little J Hub 服務器連接

4. **Hub Token**（選填）
   - 用途：Hub 認證 Token

### 方式二：快速設定腳本

1. 編輯 `quick_setup_env.ps1`
2. 修改以下變數：
   ```powershell
   $HealthUrl = "您的健康檢查 URL"
   $CopyTo = "您的伺服器路徑"
   ```
3. 執行：
   ```powershell
   .\quick_setup_env.ps1
   ```

### 方式三：手動設定（當前會話）

在 PowerShell 中執行：

```powershell
$env:WUCHANG_HEALTH_URL = "https://wuchang.life/health"
$env:WUCHANG_COPY_TO = "\\SERVER\share\wuchang"
```

### 方式四：永久設定（系統環境變數）

使用互動式腳本並加上 `-Persistent` 參數：

```powershell
.\setup_file_sync_env.ps1 -Persistent
```

或使用 Python 工具：

```bash
python setup_env_vars.py set --var WUCHANG_HEALTH_URL --value "https://wuchang.life/health" --persistent
python setup_env_vars.py set --var WUCHANG_COPY_TO --value "\\SERVER\share\wuchang" --persistent
```

## 驗證設定

設定完成後，驗證環境變數：

```bash
# 檢查環境變數狀態
python setup_env_vars.py status

# 檢查伺服器連接
python check_server_connection.py

# 檢查版本差距
python check_version_diff.py --profile kb
python check_version_diff.py --profile rules
```

## 常見問題

### Q: 如何知道伺服器路徑？
A: 通常是 SMB 網路分享路徑，格式為 `\\伺服器名稱\分享名稱\路徑`

### Q: 健康檢查 URL 是什麼？
A: 這是伺服器提供的健康狀態端點，用於確認伺服器是否正常運行

### Q: 設定後如何確認是否生效？
A: 執行 `python setup_env_vars.py status` 查看環境變數狀態

### Q: 設定只在當前會話有效？
A: 是的，除非使用 `-Persistent` 參數或手動設定系統環境變數

## 下一步

設定完成後：
1. 檢查真實伺服器版本差距
2. 執行擇優同步
3. 驗證同步結果
