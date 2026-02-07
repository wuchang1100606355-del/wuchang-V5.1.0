# 雲端代理程式委派與變更認可系統

## 概述

這個系統提供了一個互動式工作區，讓使用者能夠：
1. **認可變更** - 檢視並提交程式碼變更
2. **委派至雲端代理程式** - 將任務委派給雲端代理程式（如 GitHub Copilot）
3. **管理工作流程** - 追蹤任務狀態和工作區變更

## 快速開始

### 啟動工具

在 PowerShell 中執行：

```powershell
.\start_j_chaing.ps1
```

### 主要功能

#### 1. 檢視待認可的變更
- 顯示當前工作區中所有未提交的變更
- 使用 Git 追蹤變更狀態

#### 2. 認可變更
- 暫存所有變更 (`git add .`)
- 提交變更並附加提交訊息
- 確認變更後才執行

#### 3. 委派至雲端代理程式
- 輸入任務描述
- 記錄任務到 `cloud_agent_tasks.json`
- 追蹤任務狀態和時間戳記

#### 4. 認可變更並委派至雲端代理程式
- 組合功能 2 和 3
- 一次完成認可和委派
- 適用於需要雲端協助的變更

#### 5. 檢視工作區狀態
- 顯示當前 Git 分支
- 列出待認可的變更
- 顯示最近的雲端代理任務

#### 6. 設定互動工作區
- 啟用/停用互動模式
- 配置自動化選項
- 設定工作區偏好

#### 7. 執行自訂命令
- 執行任意 PowerShell 命令
- 適用於特殊操作需求

## 配置檔案

### cloud_agent_config.json

```json
{
  "cloudAgent": {
    "name": "五常雲端代理程式",
    "type": "GitHub Copilot",
    "enabled": true,
    "endpoint": "https://copilot.github.com"
  },
  "workspace": {
    "interactive": true,
    "autoCommit": false,
    "autoDelegate": false
  },
  "approval": {
    "requireConfirmation": true,
    "autoApproveMinorChanges": false
  }
}
```

#### 配置選項說明

**cloudAgent** - 雲端代理程式設定
- `name`: 代理程式名稱
- `type`: 代理程式類型（如 GitHub Copilot、Claude、GPT-4 等）
- `enabled`: 是否啟用
- `endpoint`: API 端點 URL

**workspace** - 工作區設定
- `interactive`: 啟用互動模式
- `autoCommit`: 自動提交變更
- `autoDelegate`: 自動委派任務

**approval** - 認可設定
- `requireConfirmation`: 需要確認才能認可
- `autoApproveMinorChanges`: 自動認可小變更

## 工作流程範例

### 情境 1：認可程式碼變更並委派測試

1. 修改程式碼檔案
2. 執行 `start_j_chaing.ps1`
3. 選擇「4. 認可變更並委派至雲端代理程式」
4. 輸入提交訊息：「實作新功能 X」
5. 輸入任務描述：「測試新功能 X 的所有情境」
6. 系統會：
   - 提交程式碼變更
   - 記錄任務到雲端代理程式
   - 顯示任務狀態

### 情境 2：檢視工作區狀態

1. 執行 `start_j_chaing.ps1`
2. 選擇「5. 檢視工作區狀態」
3. 系統顯示：
   - 當前 Git 分支
   - 待認可的變更
   - 最近的雲端代理任務

### 情境 3：設定互動工作區

1. 執行 `start_j_chaing.ps1`
2. 選擇「6. 設定互動工作區」
3. 選擇「Y」啟用互動模式
4. 工作區現在會：
   - 自動監控檔案變更
   - 即時顯示 Git 狀態
   - 提供快速認可和委派功能

## 任務記錄

所有委派的任務都會記錄在 `cloud_agent_tasks.json`：

```json
[
  {
    "Timestamp": "2026-02-07 15:30:00",
    "Description": "測試新功能 X 的所有情境",
    "Status": "已委派",
    "Agent": "雲端代理程式"
  }
]
```

## 與雙J重點記憶系統整合

此工具與 `DUAL_J_CRITICAL_MEMORY_SYSTEM.md` 整合：

- 啟動時自動檢查重點記憶系統
- 提醒檢查工作日誌
- 確保遵循系統標準

## 最佳實踐

### 1. 定期認可變更
- 完成一個功能後立即認可
- 使用清晰的提交訊息
- 避免累積過多未認可的變更

### 2. 適當委派任務
- 複雜任務委派給雲端代理程式
- 明確描述任務需求
- 追蹤任務完成狀態

### 3. 保持工作區整潔
- 定期檢視工作區狀態
- 清理不需要的變更
- 維護清晰的 Git 歷史

### 4. 配置適合的設定
- 根據工作習慣調整配置
- 啟用適當的自動化功能
- 保持配置檔案版本控制

## 故障排除

### 問題：Git 命令失敗
**解決方案：**
- 確認當前目錄在 Git 儲存庫中
- 檢查 Git 是否已安裝
- 驗證 Git 配置正確

### 問題：無法儲存任務記錄
**解決方案：**
- 檢查檔案寫入權限
- 確認磁碟空間足夠
- 驗證 JSON 格式正確

### 問題：配置檔案載入失敗
**解決方案：**
- 檢查 `cloud_agent_config.json` 是否存在
- 驗證 JSON 格式正確
- 使用預設配置作為範本

## 進階使用

### 自動化腳本

可以建立批次檔來自動執行特定操作：

```powershell
# auto_approve_and_delegate.ps1
# 自動認可並委派的腳本

$taskDescription = $args[0]

# 添加所有變更
git add .

# 提交變更
git commit -m "自動提交: $taskDescription"

# 記錄任務（調用主腳本的功能）
# ... 實作任務記錄邏輯
```

### 整合 CI/CD

可以將此工具整合到 CI/CD 流程中：

1. 在 CI 流程中執行變更檢查
2. 自動認可符合條件的變更
3. 委派測試任務給雲端代理程式
4. 追蹤任務完成狀態

## 安全注意事項

1. **不要將敏感資訊寫入任務記錄**
   - 避免在任務描述中包含密碼或金鑰
   - 使用環境變數存儲敏感配置

2. **保護配置檔案**
   - 不要將含有認證資訊的配置檔案提交到公開儲存庫
   - 使用 `.gitignore` 排除敏感配置

3. **驗證輸入**
   - 檢查使用者輸入的命令
   - 避免執行不信任的腳本

## 更新與維護

### 檢查更新
- 定期檢查工具的新版本
- 閱讀更新日誌了解新功能

### 備份
- 定期備份 `cloud_agent_tasks.json`
- 備份自訂配置檔案

### 報告問題
- 在 GitHub Issues 中報告錯誤
- 提供詳細的錯誤訊息和重現步驟

## 相關文件

- [雙J重點記憶系統](./DUAL_J_CRITICAL_MEMORY_SYSTEM.md)
- [README](./README.md)
- [GitHub Copilot 文件](https://docs.github.com/copilot)

## 版本歷史

### v1.0.0 (2026-02-07)
- 初始版本
- 實作基本的認可和委派功能
- 支援互動工作區
- 整合雙J重點記憶系統
