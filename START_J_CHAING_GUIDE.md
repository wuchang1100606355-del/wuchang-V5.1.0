# 五常互動工作區管理腳本使用指南
# Wu Chang Interactive Workspace Management Script Guide

## 概述 (Overview)

`start_j_chaing.ps1` 是一個強大的 PowerShell 腳本，用於管理互動式工作區，提供變更認可、命令執行、以及雲端代理程式委派等功能。

This is a powerful PowerShell script for managing interactive workspaces, providing features such as change approval, command execution, and cloud agent delegation.

## 功能特性 (Features)

1. **工作區初始化** - 設定並檢查 Git 倉庫狀態
2. **讀取最新變更** - 查看工作區中的所有變更
3. **執行命令** - 在工作區中執行自定義命令
4. **認可變更** - 添加並提交變更到 Git
5. **委派至雲端** - 將提交推送到遠端倉庫
6. **一鍵認可並委派** - 同時執行認可和委派操作
7. **工作區狀態** - 查看完整的工作區和 Git 狀態

## 使用方法 (Usage)

### 方式一：互動式選單模式 (Interactive Menu Mode)

直接執行腳本，進入互動式選單：

```powershell
.\start_j_chaing.ps1
```

或使用完整路徑：

```powershell
powershell -ExecutionPolicy Bypass -File ".\start_j_chaing.ps1"
```

選單選項：
- `1` - 初始化工作區
- `2` - 讀取最新變更
- `3` - 執行命令
- `4` - 認可變更
- `5` - 委派至雲端代理程式
- `6` - 認可變更並委派
- `7` - 檢視工作區狀態
- `8` - 離開

### 方式二：命令行參數模式 (Command-Line Mode)

使用參數直接執行特定操作：

```powershell
# 初始化工作區
.\start_j_chaing.ps1 -Action init

# 讀取最新變更
.\start_j_chaing.ps1 -Action read

# 執行命令
.\start_j_chaing.ps1 -Action execute

# 認可變更
.\start_j_chaing.ps1 -Action approve

# 委派至雲端
.\start_j_chaing.ps1 -Action delegate

# 認可並委派
.\start_j_chaing.ps1 -Action both

# 查看狀態
.\start_j_chaing.ps1 -Action status
```

### 方式三：自動化模式 (Automated Mode)

使用開關參數進行自動化操作：

```powershell
# 自動認可變更（無需手動確認）
.\start_j_chaing.ps1 -Action approve -AutoApprove

# 自動認可並委派到雲端
.\start_j_chaing.ps1 -Action both -AutoApprove
```

## 工作流程範例 (Workflow Examples)

### 範例 1: 日常工作流程

```powershell
# 1. 初始化工作區
.\start_j_chaing.ps1 -Action init

# 2. 進行一些程式碼修改...

# 3. 讀取變更
.\start_j_chaing.ps1 -Action read

# 4. 認可並委派變更
.\start_j_chaing.ps1 -Action both
```

### 範例 2: 快速提交流程

```powershell
# 一次性認可所有變更並推送到雲端（自動模式）
.\start_j_chaing.ps1 -Action both -AutoApprove
```

### 範例 3: 檢查工作區狀態

```powershell
# 查看詳細的工作區狀態
.\start_j_chaing.ps1 -Action status
```

### 範例 4: 執行自定義命令

```powershell
# 進入互動模式選擇「3. 執行命令」
.\start_j_chaing.ps1
# 然後輸入要執行的命令，例如：
# git log --oneline -10
# python diagnose_connection.py
# npm test
```

## 參數說明 (Parameters)

- `-Action <string>`: 指定要執行的操作
  - `init` - 初始化工作區
  - `read` - 讀取最新變更
  - `execute` - 執行命令
  - `approve` - 認可變更
  - `delegate` - 委派至雲端
  - `both` - 認可並委派
  - `status` - 查看狀態
  - `menu` - 顯示互動式選單（預設）

- `-AutoApprove`: 自動認可變更，無需手動確認
- `-DelegateToCloud`: 保留供未來使用

## 系統需求 (Requirements)

- Windows PowerShell 5.1 或更高版本
- Git 已安裝並配置
- 對 Git 倉庫的讀寫權限

## 注意事項 (Notes)

1. **執行策略**: 如果無法執行腳本，請使用以下命令設定執行策略：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **UTF-8 編碼**: 腳本已配置為使用 UTF-8 編碼，支援中文顯示。

3. **Git 配置**: 確保已正確配置 Git 使用者名稱和電子郵件：
   ```bash
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

4. **遠端倉庫**: 確保已配置遠端倉庫（origin）並有推送權限。

## 常見問題 (FAQ)

### Q: 腳本執行時出現「無法執行」錯誤？
A: 使用以下命令繞過執行策略：
```powershell
powershell -ExecutionPolicy Bypass -File ".\start_j_chaing.ps1"
```

### Q: 如何在不同位置執行此腳本？
A: 可以將腳本複製到系統路徑，或建立別名：
```powershell
Set-Alias workspace "C:\path\to\start_j_chaing.ps1"
```

### Q: 推送時需要認證怎麼辦？
A: 配置 Git 認證助手：
```bash
git config --global credential.helper wincred
```

### Q: 如何自動化整個工作流程？
A: 建立批次腳本或使用任務排程器：
```powershell
# auto_workflow.ps1
.\start_j_chaing.ps1 -Action init
# ... 進行修改 ...
.\start_j_chaing.ps1 -Action both -AutoApprove
```

## 與其他工具整合 (Integration)

此腳本可以與以下工具整合使用：

- **Python 腳本**: 執行 Python 診斷工具
  ```powershell
  .\start_j_chaing.ps1 -Action execute
  # 輸入: python diagnose_connection.py
  ```

- **路由器連接工具**: 配合本倉庫的路由器管理工具使用
  ```powershell
  .\start_j_chaing.ps1 -Action execute
  # 輸入: python login_router.py
  ```

## 故障排除 (Troubleshooting)

1. **UTF-8 顯示問題**: 
   - 確保 PowerShell 控制台支援 UTF-8
   - 在 Windows 10/11 中啟用 Beta UTF-8 支援

2. **Git 推送失敗**:
   - 檢查網路連接
   - 驗證遠端倉庫 URL: `git remote -v`
   - 確認有推送權限

3. **顏色顯示異常**:
   - 使用 Windows Terminal 或 PowerShell 7+ 以獲得更好的顏色支援

## 版本歷史 (Version History)

- **v5.1.0** (2026-02-07)
  - 初始版本
  - 支援互動式工作區管理
  - 支援變更認可和雲端委派
  - 支援自定義命令執行

## 授權 (License)

此腳本是五常雲端空間系統的一部分，遵循倉庫的授權條款。

## 聯絡資訊 (Contact)

如有問題或建議，請在 GitHub 倉庫中提交 Issue。
