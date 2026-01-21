# 網路共享問題修復指南

根據 Microsoft 官方支援文件建立：
- [Network Share Issues (中文)](https://learn.microsoft.com/zh-cn/answers/questions/3860772/network-share-issues)
- [SMB Network Share Issue (英文)](https://learn.microsoft.com/en-us/answers/questions/1650278/smb-network-share-issue)

## 問題診斷

常見的網路共享問題包括：
- 錯誤代碼 `0x80004005`：無法訪問網路中的其他電腦
- 錯誤代碼 `0x00000003`：無法連接共享打印機
- SMB 版本不匹配：提示需要 SMB1 協議（不安全）

## 修復工具

使用 `fix_network_share_issues.py` 進行自動診斷和修復：

### 模擬執行（建議先執行）

```powershell
python fix_network_share_issues.py --dry-run
```

### 實際修復

```powershell
python fix_network_share_issues.py
```

### 測試特定共享路徑

```powershell
python fix_network_share_issues.py --test-share "\\HOME-COMMPUT\wuchang V5.1.0"
```

## 修復步驟

工具會自動執行以下步驟：

### 1. 檢查文件和打印機共享
- 檢查網路設定檔狀態
- 檢查防火牆規則

### 2. 檢查功能發現服務
- **FDResPub**（功能發現資源發布）：應設為自動啟動並運行
- **FDHost**（功能發現提供程序主機）：應設為自動啟動並運行

### 3. 檢查 SMB 配置
- **SMB 1.0**：不建議使用（有安全風險），應停用
- **SMB 2.0**：建議啟用
- **SMB 3.0**：建議啟用（最佳選擇）

### 4. 啟用文件和打印機共享
- 將所有網路設定檔設為「私人」
- 啟用相關防火牆規則

### 5. 啟用功能發現服務
- 設定服務為自動啟動
- 啟動服務

### 6. 配置 SMB 版本
- 啟用 SMB 2.0 和 3.0
- 停用 SMB 1.0（除非必須相容舊系統）

## 手動修復步驟

如果自動工具無法解決問題，可以手動執行以下步驟：

### 啟用文件和打印機共享

1. 開啟「控制台」→「網路和網際網路」→「網路和共用中心」
2. 點擊「變更進階共用設定」
3. 在「私人」設定檔中：
   - 啟用「網路探索」
   - 啟用「檔案及印表機共用」

### 檢查功能發現服務

1. 按 `Win + R`，輸入 `services.msc`
2. 找到以下服務並確保它們正在運行且設為自動啟動：
   - **功能發現資源發布** (FDResPub)
   - **功能發現提供程序主機** (FDHost)

### 配置 SMB 版本

在 PowerShell（以管理員身份執行）中：

```powershell
# 檢查 SMB 版本狀態
Get-SmbServerConfiguration | Select EnableSMB1Protocol, EnableSMB2Protocol, EnableSMB3Protocol

# 啟用 SMB 2.0
Set-SmbServerConfiguration -EnableSMB2Protocol $true -Force

# 啟用 SMB 3.0
Set-SmbServerConfiguration -EnableSMB3Protocol $true -Force

# 停用 SMB 1.0（安全建議）
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart
```

### 檢查防火牆規則

```powershell
# 檢查文件和打印機共享規則
Get-NetFirewallRule | Where-Object {
    $_.DisplayName -like "*文件和打印機共享*" -or
    $_.DisplayName -like "*File and Printer Sharing*"
} | Select DisplayName, Enabled, Direction
```

## 常見問題

### Q: 為什麼要停用 SMB 1.0？

A: SMB 1.0 有已知的安全漏洞（如 WannaCry 勒索軟體利用的漏洞）。Microsoft 強烈建議使用 SMB 2.0 或更高版本。

### Q: 如果必須使用 SMB 1.0 怎麼辦？

A: 僅在絕對必要時啟用，並確保：
- 系統已安裝所有安全更新
- 網路環境相對安全
- 定期檢查是否有安全更新

使用工具時可以加上 `--enable-smb1` 參數（不建議）。

### Q: 兩端都需要配置嗎？

A: 是的，**客戶端和伺服器端都需要使用相同的 SMB 版本**。如果伺服器只支援 SMB 1.0，客戶端也必須啟用 SMB 1.0（不建議）。

### Q: 如何檢查遠端伺服器的 SMB 版本？

A: 可以通過以下方式檢查：
1. 查看伺服器端的 SMB 配置
2. 查看錯誤訊息（如果提示需要 SMB1，表示伺服器可能只支援 SMB1）
3. 聯繫伺服器管理員確認

## 參考資料

- [Microsoft 支援：Network Share Issues](https://learn.microsoft.com/zh-cn/answers/questions/3860772/network-share-issues)
- [Microsoft 支援：SMB Network Share Issue](https://learn.microsoft.com/en-us/answers/questions/1650278/smb-network-share-issue)
- [Microsoft 文件：Detect, enable and disable SMBv1, SMBv2, and SMBv3](https://learn.microsoft.com/en-us/windows-server/storage/file-server/troubleshoot/detect-enable-and-disable-smbv1-v2-v3?tabs=server)
