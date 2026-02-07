# Odoo IDE 擴展安裝指南

## 問題描述
擴展每次開啟都需要重新安裝，這是因為擴展未正確安裝到用戶目錄。

## 解決方案

### 方法一：手動安裝（推薦）

1. **開啟 Cursor**
2. **開啟擴展面板**
   - 按 Ctrl+Shift+X 或點擊左側擴展圖示
3. **搜索擴展**
   - 搜索：Odoo IDE 或 	rinhanhngoc.vscode-odoo
4. **安裝擴展**
   - 點擊「安裝」按鈕
5. **重新載入視窗**
   - 按 Ctrl+Shift+P
   - 輸入 Reload Window 並執行

### 方法二：使用命令列安裝

在 PowerShell 中執行：

`powershell
code --install-extension trinhanhngoc.vscode-odoo
`

或使用 Cursor CLI：

`powershell
cursor --install-extension trinhanhngoc.vscode-odoo
`

### 方法三：檢查擴展目錄權限

如果擴展安裝後仍然消失，可能是權限問題：

1. 檢查擴展目錄權限：
   - %APPDATA%\Cursor\User\extensions
2. 確保 Cursor 有寫入權限
3. 以管理員身份執行 Cursor（如果需要）

## 驗證安裝

安裝完成後，檢查擴展是否在以下位置：

- %APPDATA%\Cursor\User\extensions\trinhanhngoc.vscode-odoo-*

## 工作區配置

已配置工作區推薦擴展（.vscode/extensions.json），
Cursor 應該會自動提示安裝推薦的擴展。

## 如果問題仍然存在

1. 檢查 Cursor 版本是否為最新
2. 清除擴展緩存：
   - 關閉 Cursor
   - 刪除 %APPDATA%\Cursor\Cache
   - 重新開啟 Cursor
3. 檢查防毒軟體是否阻擋擴展安裝
4. 嘗試以管理員身份執行 Cursor

---
*最後更新: 2026-01-13*
