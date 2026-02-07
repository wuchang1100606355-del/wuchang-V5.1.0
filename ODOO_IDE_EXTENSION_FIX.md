# Odoo IDE 擴展安裝問題修復指南

## 問題描述
Odoo IDE 擴展 (`trinhanhngoc.vscode-odoo`) 每次開啟都無法完成安裝，安裝完成後下次開啟又得重新安裝。

## 可能原因

1. **擴展安裝目錄權限問題**
   - 擴展安裝在臨時目錄或沒有寫入權限的位置
   - Windows 用戶目錄權限限制

2. **工作區配置問題**
   - 擴展配置沒有正確保存到工作區
   - `.vscode/extensions.json` 被 `.gitignore` 忽略

3. **擴展緩存損壞**
   - VS Code/Cursor 擴展緩存損壞
   - 需要清理緩存

4. **擴展安裝位置衝突**
   - 多個 VS Code/Cursor 實例使用不同的擴展目錄

## 解決方案

### 方案 1: 手動安裝並固定擴展（推薦）

1. **打開擴展面板**
   - 按 `Ctrl+Shift+X` 或點擊左側擴展圖標

2. **搜索並安裝 Odoo IDE**
   - 搜索: `trinhanhngoc.vscode-odoo`
   - 點擊「安裝」

3. **確認安裝位置**
   - 檢查擴展是否安裝在正確位置
   - Windows 默認位置: `%USERPROFILE%\.vscode\extensions\`

4. **固定擴展到工作區**
   - 右鍵點擊已安裝的擴展
   - 選擇「固定到工作區」

### 方案 2: 使用工作區配置文件

創建或更新 `wuchang.code-workspace` 文件：

```json
{
    "folders": [
        {
            "path": "."
        }
    ],
    "settings": {
        "extensions.ignoreRecommendations": false
    },
    "extensions": {
        "recommendations": [
            "trinhanhngoc.vscode-odoo",
            "ms-python.python",
            "cweijan.vscode-postgresql-client2",
            "redhat.vscode-xml"
        ]
    }
}
```

### 方案 3: 清理擴展緩存

1. **關閉所有 VS Code/Cursor 實例**

2. **清理擴展緩存**
   ```powershell
   # 清理 VS Code 擴展緩存
   Remove-Item -Path "$env:USERPROFILE\.vscode\extensions\.obsolete" -ErrorAction SilentlyContinue
   
   # 清理 Cursor 擴展緩存（如果使用 Cursor）
   Remove-Item -Path "$env:USERPROFILE\.cursor\extensions\.obsolete" -ErrorAction SilentlyContinue
   ```

3. **重新安裝擴展**

### 方案 4: 使用本地擴展目錄（項目級）

如果使用 `launch_vscode_controlled.ps1`，擴展會安裝在項目目錄：

1. **確保擴展目錄存在**
   ```powershell
   New-Item -ItemType Directory -Path "vscode_ext" -Force
   ```

2. **使用控制啟動腳本**
   ```powershell
   .\scripts\launch_vscode_controlled.ps1
   ```

3. **擴展會安裝在 `vscode_ext` 目錄**

### 方案 5: 檢查並修復權限

1. **檢查擴展目錄權限**
   ```powershell
   # VS Code 擴展目錄
   $extDir = "$env:USERPROFILE\.vscode\extensions"
   if (Test-Path $extDir) {
       icacls $extDir
   }
   ```

2. **修復權限（如果需要）**
   ```powershell
   # 給予完全控制權限
   icacls "$env:USERPROFILE\.vscode\extensions" /grant "$env:USERNAME:(OI)(CI)F" /T
   ```

## 驗證修復

1. **檢查擴展是否已安裝**
   - 打開擴展面板 (`Ctrl+Shift+X`)
   - 搜索 `trinhanhngoc.vscode-odoo`
   - 應該顯示「已安裝」而非「安裝」

2. **檢查擴展功能**
   - 打開 Odoo 模組文件（如 `__manifest__.py`）
   - 應該有語法高亮和自動完成

3. **重啟 VS Code/Cursor**
   - 完全關閉並重新開啟
   - 檢查擴展是否仍然安裝

## 預防措施

1. **將 `.vscode/extensions.json` 加入版本控制**
   - 從 `.gitignore` 中移除 `.vscode/extensions.json`（如果需要的話）
   - 或創建 `.vscode/.gitkeep` 文件

2. **使用工作區文件**
   - 創建 `*.code-workspace` 文件
   - 在文件中指定推薦擴展

3. **定期備份擴展列表**
   ```powershell
   code --list-extensions > extensions-list.txt
   ```

## 相關文件

- `.vscode/extensions.json` - 工作區擴展推薦
- `devcontainer.json` - 開發容器擴展配置
- `scripts/launch_vscode_controlled.ps1` - 控制啟動腳本

---

**最後更新**: 2026-01-13
