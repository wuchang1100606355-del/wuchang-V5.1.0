# PowerShell 擴展終止問題修復指南

## 問題描述
PowerShell 終端進程終止，錯誤代碼: 1。錯誤信息顯示：
```
終端機處理序 "C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe" ... 已終止。結束代碼: 1。
```

## 問題診斷

### 已檢查項目
✅ PowerShell 擴展已安裝: `ms-vscode.powershell-2025.4.0-universal`  
✅ PowerShellEditorServices 模組存在  
✅ PowerShell 執行策略: Bypass (正常)  
✅ 擴展目錄權限: 正常  
✅ 模組可以正常載入  

### 可能原因

1. **擴展版本兼容性問題**
   - PowerShell 擴展版本 2025.4.0 可能與 Cursor 版本不兼容
   - 或與 Windows PowerShell 5.1 有兼容性問題

2. **模組載入時序問題**
   - PowerShellEditorServices 在啟動時載入失敗
   - 可能是因為模組依賴項缺失

3. **防毒軟體或安全軟體干擾**
   - 安全軟體可能阻止 PowerShell 擴展運行
   - Windows Defender 可能誤報

4. **Cursor 配置問題**
   - Cursor 的 PowerShell 擴展配置可能不正確
   - 擴展設置衝突

## 解決方案

### 方案 1: 更新 VS Code 設置（已執行）

已更新 `.vscode/settings.json` 添加以下設置：
```json
{
    "powershell.enableProfileLoading": true,
    "powershell.scriptAnalysis.enable": true,
    "powershell.integratedConsole.showOnStartup": false,
    "powershell.powerShellDefaultVersion": "Windows PowerShell (x64)"
}
```

### 方案 2: 重新安裝 PowerShell 擴展

執行修復腳本：
```powershell
.\scripts\reinstall_powershell_extension.ps1
```

或手動操作：
1. 打開 Cursor
2. 按 `Ctrl+Shift+X` 打開擴展面板
3. 搜索 `PowerShell`
4. 卸載 `ms-vscode.powershell`
5. 重新安裝 `ms-vscode.powershell`

### 方案 3: 禁用並重新啟用擴展

1. 打開 Cursor
2. 按 `Ctrl+Shift+X` 打開擴展面板
3. 找到 `PowerShell` 擴展
4. 點擊「禁用」
5. 重新啟動 Cursor
6. 重新啟用擴展

### 方案 4: 使用系統 PowerShell 而非擴展

如果擴展持續有問題，可以：

1. **禁用 PowerShell 擴展的集成終端**
   - 在設置中禁用 `powershell.integratedConsole.showOnStartup`

2. **使用系統 PowerShell**
   - 在 Cursor 終端中選擇「PowerShell」而非「PowerShell (Extension)」
   - 或直接使用系統 PowerShell 窗口

### 方案 5: 檢查並修復模組依賴

執行診斷腳本：
```powershell
.\scripts\fix_powershell_extension.ps1
```

### 方案 6: 降級 PowerShell 擴展版本

如果最新版本有問題，可以嘗試安裝較舊的穩定版本：

1. 卸載當前版本
2. 在擴展市場搜索 `PowerShell`
3. 點擊擴展的「齒輪」圖標
4. 選擇「安裝另一個版本」
5. 選擇較舊的穩定版本（如 2024.x.x）

## 驗證修復

1. **檢查擴展狀態**
   - 打開擴展面板
   - 確認 PowerShell 擴展已啟用且無錯誤

2. **測試 PowerShell 終端**
   - 按 `` Ctrl+` `` 打開終端
   - 選擇「PowerShell」
   - 執行簡單命令：`Get-Host`

3. **檢查日誌**
   - 打開 Cursor 輸出面板 (`Ctrl+Shift+U`)
   - 選擇「PowerShell」輸出
   - 查看是否有錯誤信息

## 預防措施

1. **定期更新擴展**
   - 保持 PowerShell 擴展為最新版本
   - 但注意版本兼容性

2. **備份擴展配置**
   - 保存 `.vscode/settings.json` 中的 PowerShell 設置

3. **監控擴展狀態**
   - 定期檢查擴展是否正常運行
   - 注意擴展更新後的兼容性問題

## 相關文件

- `scripts/fix_powershell_extension.ps1` - 修復腳本
- `scripts/reinstall_powershell_extension.ps1` - 重新安裝腳本
- `.vscode/settings.json` - VS Code 設置（包含 PowerShell 配置）

## 技術細節

### PowerShellEditorServices 模組結構
```
PowerShellEditorServices/
├── PowerShellEditorServices.psd1
├── Start-EditorServices.ps1
├── InvokePesterStub.ps1
├── bin/
│   └── (二進制文件)
└── Commands/
    └── (命令模組)
```

### 擴展啟動流程
1. Cursor 啟動 PowerShell 擴展
2. 擴展載入 PowerShellEditorServices 模組
3. 模組啟動編輯器服務
4. 建立與 PowerShell 進程的通信
5. 如果任何步驟失敗，會導致進程終止

---

**最後更新**: 2026-01-15  
**狀態**: 診斷完成，修復腳本已準備
