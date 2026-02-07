# 雲端代理程式使用指南
# Cloud Agent Usage Guide

## 概述

此指南說明如何使用 `start_j_chaing.ps1` 腳本來管理互動工作區和雲端代理程式委派。

## 主要功能

### 1. 互動工作區設定
設定和驗證當前工作區環境，包括：
- 檢查 Git 倉庫狀態
- 識別可用的工具腳本
- 驗證工作區配置

### 2. 讀取最新變更
查看工作區中的所有變更，包括：
- Git 狀態概覽
- 未提交的變更統計
- 最近的提交歷史

### 3. 執行命令
在工作區環境中執行任意命令或腳本。

### 4. 認可變更
將工作區變更提交到 Git 倉庫：
- 自動加入所有變更 (`git add .`)
- 提供自訂提交訊息
- 確認提交成功

### 5. 委派至雲端代理程式
將認可的變更推送到遠端倉庫（雲端代理程式）：
- 檢查遠端倉庫配置
- 推送到當前分支
- 觸發雲端代理程式處理

### 6. 整合工作流程
一鍵完成「認可變更 + 委派至雲端代理程式」的完整流程。

## 使用方法

### 互動模式（預設）

```powershell
.\start_j_chaing.ps1
```

啟動後會顯示功能選單，可以依序選擇需要的功能。

#### 選單選項：
1. **設定互動工作區** - 初始化和檢查工作區環境
2. **讀取作業區最新變更** - 查看所有待處理的變更
3. **執行命令或腳本** - 執行任意命令
4. **認可變更** - 提交變更到本地倉庫
5. **委派至雲端代理程式** - 推送到遠端倉庫
6. **認可變更 + 委派至雲端代理程式** - 完整工作流程
7. **查看工作區狀態** - 顯示當前狀態概覽
0. **退出** - 結束程式

### 自動模式

#### 僅認可變更
```powershell
.\start_j_chaing.ps1 -AutoApprove
```

#### 僅委派至雲端
```powershell
.\start_j_chaing.ps1 -DelegateToCloud
```

#### 認可變更並委派（一鍵完成）
```powershell
.\start_j_chaing.ps1 -AutoApprove -DelegateToCloud
```

#### 指定工作區路徑
```powershell
.\start_j_chaing.ps1 -WorkspacePath "D:\Projects\MyWorkspace"
```

## 工作流程範例

### 情境 1：首次設定工作區
1. 啟動腳本：`.\start_j_chaing.ps1`
2. 選擇 `1` - 設定互動工作區
3. 確認環境配置正確

### 情境 2：查看和認可變更
1. 選擇 `2` - 讀取作業區最新變更
2. 檢視所有待處理的變更
3. 選擇 `4` - 認可變更
4. 輸入提交訊息
5. 確認提交

### 情境 3：完整部署流程
1. 選擇 `6` - 認可變更 + 委派至雲端代理程式
2. 確認認可變更
3. 輸入提交訊息
4. 確認推送到雲端
5. 等待雲端代理程式處理

### 情境 4：自動化部署（CI/CD）
```powershell
# 在自動化腳本中使用
.\start_j_chaing.ps1 -AutoApprove -DelegateToCloud
```

## 前置需求

1. **PowerShell** - 需要 PowerShell 5.1 或更高版本
2. **Git** - 必須安裝並配置 Git
3. **遠端倉庫** - 需要設定 Git 遠端倉庫（用於雲端代理程式）
4. **權限** - 需要有推送到遠端倉庫的權限

## 檢查前置需求

```powershell
# 檢查 PowerShell 版本
$PSVersionTable.PSVersion

# 檢查 Git 安裝
git --version

# 檢查遠端倉庫
git remote -v
```

## 安全性考量

1. **認證** - 確保 Git 認證已正確配置（HTTPS token 或 SSH key）
2. **權限** - 僅授權用戶可以推送到雲端代理程式
3. **審查** - 在認可變更前仔細審查所有變更

## 錯誤處理

### 常見錯誤及解決方法

#### 錯誤：「當前目錄不是 Git 倉庫」
**解決方法**：確認在正確的 Git 倉庫目錄中執行腳本，或使用 `-WorkspacePath` 參數指定路徑。

#### 錯誤：「未設定遠端倉庫」
**解決方法**：
```powershell
git remote add origin <repository-url>
```

#### 錯誤：「推送失敗」
**解決方法**：
1. 檢查網路連接
2. 確認 Git 認證
3. 檢查是否有推送權限
4. 嘗試手動推送：`git push origin <branch-name>`

#### 錯誤：「沒有需要認可的變更」
**說明**：這不是錯誤，表示工作區是乾淨的，沒有待提交的變更。

## 與其他工具整合

此腳本與倉庫中的其他工具腳本協同工作：

- **uts/move_bluestacks_to_j_drive.ps1** - BlueStacks 移動工具
- **uts/cleanup_and_compress_virtual_disks.ps1** - 虛擬磁碟清理工具
- **uts/compress_docker_disk.ps1** - Docker 磁碟壓縮工具
- **uts/remove_virtualbox_completely.ps1** - VirtualBox 移除工具

可以在互動模式中選擇「執行命令或腳本」來運行這些工具。

## 最佳實踐

1. **定期檢查狀態** - 使用選項 7 定期檢查工作區狀態
2. **有意義的提交訊息** - 在認可變更時提供清晰的提交訊息
3. **審查後再委派** - 在委派到雲端代理程式前，先審查所有變更
4. **保持工作區乾淨** - 定期清理不需要的檔案
5. **備份重要資料** - 在進行大規模變更前備份重要資料

## 進階用法

### 在其他腳本中調用
```powershell
# 從其他腳本呼叫
& ".\start_j_chaing.ps1" -AutoApprove -DelegateToCloud
```

### 排程任務
```powershell
# 建立排程任務，每天自動認可和委派
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"C:\Path\To\start_j_chaing.ps1`" -AutoApprove -DelegateToCloud"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AutoDelegateToCloud"
```

## 疑難排解

如果遇到問題：

1. 檢查 PowerShell 執行原則：
   ```powershell
   Get-ExecutionPolicy
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. 檢查 Git 配置：
   ```powershell
   git config --list
   ```

3. 啟用詳細輸出（修改腳本添加 `-Verbose` 支援）

## 支援

如有問題或建議，請在 GitHub 倉庫中開啟 issue。

## 版本歷史

- **v1.0.0** (2026-02-07)
  - 初始版本
  - 支援互動工作區設定
  - 支援變更認可
  - 支援雲端代理程式委派
  - 支援自動化模式

## 授權

此工具是五常雲端空間專案的一部分，依照專案授權條款使用。
