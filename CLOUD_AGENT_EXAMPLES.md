# 雲端代理程式委派系統使用範例

本文件展示如何使用雲端代理程式委派系統的常見情境。

## 情境 1：完成一個功能後認可變更

假設您剛完成了一個新功能的開發，需要認可變更並委派測試任務。

### 步驟：

1. **啟動工具**
   ```powershell
   .\start_j_chaing.ps1
   ```

2. **選擇選項 4** - "認可變更並委派至雲端代理程式"

3. **系統顯示待認可的變更**
   ```
   待認可的變更：
   M  router_connection.py
   A  new_feature.py
   M  README.md
   ```

4. **確認認可** - 輸入 `Y`

5. **輸入提交訊息**
   ```
   新增功能：支援多路由器連接
   ```

6. **輸入任務描述**
   ```
   測試多路由器連接功能，確保所有情境正常運作
   ```

7. **完成！** 系統會：
   - ✓ 提交變更到 Git
   - ✓ 記錄任務到 cloud_agent_tasks.json
   - ✓ 顯示雲端代理程式資訊

---

## 情境 2：檢查工作區狀態

在開始工作前，檢查當前工作區狀態和待處理任務。

### 步驟：

1. **啟動工具**
   ```powershell
   .\start_j_chaing.ps1
   ```

2. **選擇選項 5** - "檢視工作區狀態"

3. **系統顯示**
   ```
   【Git 狀態】
     當前分支: main
     待認可變更: 無

   【雲端代理任務】
     總任務數: 3
     最近任務:
       - [2026-02-07 14:30:00] 測試多路由器連接功能
       - [2026-02-07 13:15:00] 更新文件
       - [2026-02-07 12:00:00] 修復登錄錯誤
   ```

---

## 情境 3：只委派任務（不認可變更）

有時您只需要委派一個任務，而不涉及程式碼變更。

### 步驟：

1. **啟動工具**
   ```powershell
   .\start_j_chaing.ps1
   ```

2. **選擇選項 3** - "委派至雲端代理程式"

3. **輸入任務描述**
   ```
   分析系統性能瓶頸並提供優化建議
   ```

4. **完成！** 系統記錄任務並顯示代理程式資訊

---

## 情境 4：設定互動工作區

啟用互動模式以獲得更好的工作體驗。

### 步驟：

1. **啟動工具**
   ```powershell
   .\start_j_chaing.ps1
   ```

2. **選擇選項 6** - "設定互動工作區"

3. **確認啟用** - 輸入 `Y`

4. **獲得的功能**
   - ✓ 自動監控檔案變更
   - ✓ 即時顯示 Git 狀態
   - ✓ 快速認可和委派

---

## 情境 5：執行自訂 Git 命令

需要執行特定的 Git 操作。

### 步驟：

1. **啟動工具**
   ```powershell
   .\start_j_chaing.ps1
   ```

2. **選擇選項 7** - "執行自訂命令"

3. **輸入命令**
   ```
   git log --oneline -10
   ```

4. **查看輸出** - 系統執行命令並顯示結果

---

## 任務記錄範例

系統會將所有委派的任務記錄在 `cloud_agent_tasks.json`：

```json
[
  {
    "Timestamp": "2026-02-07 14:30:00",
    "Description": "測試多路由器連接功能，確保所有情境正常運作",
    "Status": "已委派",
    "Agent": "雲端代理程式"
  },
  {
    "Timestamp": "2026-02-07 13:15:00",
    "Description": "更新所有文件以反映新功能",
    "Status": "已委派",
    "Agent": "雲端代理程式"
  },
  {
    "Timestamp": "2026-02-07 12:00:00",
    "Description": "修復登錄驗證錯誤",
    "Status": "已委派",
    "Agent": "雲端代理程式"
  }
]
```

---

## 自訂配置範例

您可以編輯 `cloud_agent_config.json` 來自訂系統行為：

### 範例 1：啟用自動提交小變更

```json
{
  "approval": {
    "requireConfirmation": false,
    "autoApproveMinorChanges": true,
    "approvalThreshold": "auto"
  }
}
```

### 範例 2：配置不同的雲端代理

```json
{
  "cloudAgent": {
    "name": "自訂AI助手",
    "type": "Claude 3.5",
    "enabled": true,
    "endpoint": "https://api.anthropic.com"
  }
}
```

### 範例 3：啟用自動推送

```json
{
  "git": {
    "autoStage": true,
    "autoPush": true,
    "defaultBranch": "main"
  }
}
```

---

## 整合到工作流程

### 每日工作流程範例

1. **早上開始工作**
   - 啟動工具並檢視工作區狀態（選項 5）
   - 查看昨天委派的任務狀態

2. **開發過程中**
   - 完成一個小功能後，使用選項 4 認可並委派測試
   - 需要幫助時，使用選項 3 委派研究任務

3. **結束工作前**
   - 使用選項 1 檢視所有待認可變更
   - 使用選項 2 或 4 認可所有變更
   - 查看任務記錄確保沒有遺漏

### 團隊協作流程

1. **程式碼審查**
   ```powershell
   # 委派程式碼審查任務
   選項 3 → "審查最新的程式碼變更並提供建議"
   ```

2. **文件更新**
   ```powershell
   # 認可程式碼後委派文件更新
   選項 4 → 提交訊息："實作功能 X" → 任務："更新相關文件"
   ```

3. **測試驗證**
   ```powershell
   # 委派全面測試
   選項 3 → "執行所有單元測試和整合測試"
   ```

---

## 進階技巧

### 技巧 1：批次處理多個任務

建立一個腳本來批次委派任務：

```powershell
# batch_delegate.ps1
$tasks = @(
    "測試功能 A",
    "測試功能 B",
    "更新文件",
    "優化性能"
)

foreach ($task in $tasks) {
    # 這裡可以調用 start_j_chaing.ps1 的功能
    Write-Host "委派任務: $task"
}
```

### 技巧 2：整合到 Git Hooks

在 `.git/hooks/pre-commit` 中自動檢查：

```bash
#!/bin/bash
# 在提交前自動檢查工作區狀態
powershell -File ./start_j_chaing.ps1 -AutoCheck
```

### 技巧 3：定期報告

建立定期任務報告：

```powershell
# weekly_report.ps1
# 分析過去一週的任務記錄
$tasks = Get-Content cloud_agent_tasks.json | ConvertFrom-Json
$weekAgo = (Get-Date).AddDays(-7)
$recentTasks = $tasks | Where-Object { 
    [DateTime]::Parse($_.Timestamp) -gt $weekAgo 
}
Write-Host "本週委派任務數: $($recentTasks.Count)"
```

---

## 疑難排解範例

### 問題：忘記提交訊息格式

**解決方案：** 使用範本

編輯 `cloud_agent_config.json`：
```json
{
  "git": {
    "commitMessageTemplate": "[模組名稱] {description}"
  }
}
```

### 問題：任務記錄太多

**解決方案：** 定期清理舊任務

```powershell
# cleanup_old_tasks.ps1
$tasks = Get-Content cloud_agent_tasks.json | ConvertFrom-Json
$monthAgo = (Get-Date).AddDays(-30)
$recentTasks = $tasks | Where-Object { 
    [DateTime]::Parse($_.Timestamp) -gt $monthAgo 
}
$recentTasks | ConvertTo-Json | Set-Content cloud_agent_tasks.json
```

---

## 總結

這個系統提供了靈活的工作流程管理：
- ✓ 簡化變更認可流程
- ✓ 高效的任務委派機制
- ✓ 完整的任務追蹤記錄
- ✓ 與現有工具無縫整合

根據您的需求自訂配置，讓工作更有效率！
