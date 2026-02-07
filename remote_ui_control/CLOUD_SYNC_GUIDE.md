# 🌐 五常 AI - 雲端智能同步系統

## 🎯 功能概述

當本機和 Server 雲端可見時，自動同步系統資料夾，採用最優策略避免衝突和錯誤。

## ✨ 核心特性

### 🔍 智能偵測

-   ✅ **雙向連通性檢測**: 自動檢查雲端可見狀態
-   ✅ **角色自動識別**: 自動識別本機/Server 角色
-   ✅ **健康狀態監控**: 實時監控同步狀態

### 🔄 增量同步

-   ✅ **只傳輸變更**: MD5 hash 比對，只同步差異
-   ✅ **斷點續傳**: 支援大文件分塊傳輸
-   ✅ **智能排除**: 自動排除不需要的文件

### ⚡ 最優策略

-   ✅ **衝突解決**: 多種策略（最新優先、本機優先、遠端優先）
-   ✅ **錯誤恢復**: 自動重試機制
-   ✅ **安全備份**: 同步前自動備份

### 📊 完整報告

-   ✅ **同步計劃**: 執行前顯示完整計劃
-   ✅ **進度追蹤**: 實時顯示同步進度
-   ✅ **詳細統計**: 上傳、下載、衝突統計

## 🚀 快速開始

### 步驟 1: 確保雙方雲端可見

```powershell
# 檢查連通性
ping 192.168.50.249  # 從本機 ping Server
ping 192.168.50.84   # 從 Server ping 本機
```

### 步驟 2: 啟動同步服務

```powershell
cd "c:\wuchang V5.1.0\remote_ui_control"
.\start_cloud_sync.ps1
```

### 步驟 3: 選擇同步模式

```
請選擇同步模式:
  1. 試運行（只查看同步計劃，不執行）
  2. 互動模式（確認後執行）
  3. 自動模式（直接執行）
  4. 持續監控模式（自動偵測變更並同步）
```

## 📦 同步資料夾

系統會同步以下資料夾（按優先級）：

| 優先級 | 資料夾            | 說明        |
| ------ | ----------------- | ----------- |
| 1      | remote_ui_control | UI 控制系統 |
| 2      | wuchang_os/addons | Odoo 插件   |
| 3      | scripts           | 腳本文件    |

## ⚙️ 同步策略

### 策略 1: 最新優先（推薦）

```bash
SYNC_STRATEGY=newest
```

-   比較文件修改時間
-   選擇最新的版本
-   適合大多數情況

### 策略 2: 本機優先

```bash
SYNC_STRATEGY=local_wins
```

-   本機版本永遠覆蓋遠端
-   適合本機為主要開發環境

### 策略 3: 遠端優先

```bash
SYNC_STRATEGY=remote_wins
```

-   遠端版本永遠覆蓋本機
-   適合 Server 為主要環境

### 策略 4: 手動處理

```bash
SYNC_STRATEGY=manual
```

-   遇到衝突時停止並提示
-   需要手動解決衝突

## 🔍 使用示例

### 試運行模式

```powershell
.\start_cloud_sync.ps1
# 選擇 1

輸出:
🔍 試運行模式
==============================================================
同步計劃: remote_ui_control
==============================================================
⬆️  上傳: 3 個文件
  - local_ai_node.py
  - hybrid_ai_router.py
  - cloud_sync_service.py
⬇️  下載: 1 個文件
  - server_config.json
⏭️  跳過: 15 個文件
⚠️  衝突: 0 個文件
```

### 自動模式

```powershell
.\start_cloud_sync.ps1
# 選擇 3

輸出:
⚡ 自動模式
🌐 雙方雲端可見，開始同步
本機: 192.168.50.84
對方: 192.168.50.249
策略: newest
==============================================================

🔄 開始同步資料夾: remote_ui_control
掃描資料夾: c:\wuchang V5.1.0\remote_ui_control
找到 18 個文件
⬆️  上傳中: local_ai_node.py [████████████] 100%
⬆️  上傳中: hybrid_ai_router.py [████████████] 100%
⬆️  上傳中: cloud_sync_service.py [████████████] 100%
✅ 上傳完成: 3 個文件

📊 同步總結
==============================================================
⬆️  總上傳: 3
⬇️  總下載: 0
⏭️  總跳過: 15
⚠️  總衝突: 0
❌ 總錯誤: 0
==============================================================

✅ 同步完成，無錯誤！
```

## 🛡️ 安全機制

### 1. 備份保護

```bash
BACKUP_BEFORE_SYNC=true
BACKUP_DIR=c:\wuchang V5.1.0\backups\sync_backup
```

-   同步前自動備份
-   保留 7 天備份
-   可快速恢復

### 2. 文件驗證

-   MD5 hash 校驗
-   大小比對
-   時間戳驗證

### 3. 錯誤處理

```bash
MAX_RETRY=3
RETRY_DELAY=5
CONTINUE_ON_ERROR=true
```

-   自動重試失敗操作
-   錯誤隔離（單個文件失敗不影響其他）
-   詳細錯誤日誌

### 4. 文件過濾

自動排除：

-   `__pycache__/` 目錄
-   `*.pyc` 編譯文件
-   `.env` 環境配置
-   `*.log` 日誌文件
-   `*.swp` 暫存文件

## 📊 衝突解決

### 衝突場景

```
本機文件: config.json (修改於 2026-01-12 10:00)
遠端文件: config.json (修改於 2026-01-12 10:05)
結果: ⬇️ 下載遠端（更新）
```

### 衝突策略矩陣

| 情況     | newest | local_wins | remote_wins | manual |
| -------- | ------ | ---------- | ----------- | ------ |
| 本機較新 | 上傳   | 上傳       | 下載        | 提示   |
| 遠端較新 | 下載   | 上傳       | 下載        | 提示   |
| 時間相同 | 提示   | 上傳       | 下載        | 提示   |

## 🔄 自動化同步

### 使用 Windows 工作排程器

1. 打開「工作排程器」
2. 創建基本任務
3. 設定觸發程式：
    ```
    程式: powershell.exe
    參數: -File "c:\wuchang V5.1.0\remote_ui_control\start_cloud_sync.ps1"
    ```
4. 設定週期：每 5 分鐘

### 使用命令行

```powershell
# 創建排程任務
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File `"c:\wuchang V5.1.0\remote_ui_control\start_cloud_sync.ps1`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "WuchangCloudSync" -Action $action -Trigger $trigger
```

## 📈 性能優化

### 1. 大文件處理

```bash
MAX_SYNC_FILE_SIZE=52428800  # 50MB
CHUNK_SIZE=1048576           # 1MB chunks
```

-   超過 50MB 的文件跳過
-   支援分塊傳輸
-   斷點續傳

### 2. 網路優化

-   壓縮傳輸（TODO）
-   多線程同步（TODO）
-   增量同步

### 3. 智能排除

只同步必要的文件：

```python
exclude = [
    "__pycache__",
    "*.pyc",
    ".env",
    "*.log",
    "*.swp"
]
```

## 🚨 常見問題

### Q1: 雙方不可見怎麼辦？

**A**: 檢查：

1. 網路連線是否正常
2. 防火牆是否阻擋
3. 對方是否在線

### Q2: 如何處理衝突？

**A**: 三種方式：

1. 自動（使用 newest 策略）
2. 手動（查看並選擇）
3. 備份後覆蓋

### Q3: 同步失敗怎麼辦？

**A**: 系統會：

1. 自動重試 3 次
2. 記錄詳細錯誤
3. 其他文件繼續同步

### Q4: 如何恢復備份？

**A**: 備份位置：

```
c:\wuchang V5.1.0\backups\sync_backup\
  └─ 2026-01-12_10-30-00\
      └─ remote_ui_control\
```

## 📝 配置文件

### .env.sync 示例

```bash
# 網路配置
LOCAL_IP=192.168.50.84
SERVER_IP=192.168.50.249
SYNC_PORT=8766

# 同步策略
SYNC_STRATEGY=newest

# 文件限制
MAX_SYNC_FILE_SIZE=52428800

# 自動同步
AUTO_SYNC_ENABLED=true
SYNC_INTERVAL=300

# 備份
BACKUP_BEFORE_SYNC=true
BACKUP_RETENTION_DAYS=7
```

## 🎉 最佳實踐

1. ✅ **定期同步**: 設定每 5 分鐘自動同步
2. ✅ **試運行**: 大規模同步前先試運行
3. ✅ **備份保護**: 保持備份功能開啟
4. ✅ **監控日誌**: 定期查看同步日誌
5. ✅ **衝突處理**: 及時處理衝突文件

---

**雙方雲端可見，智能同步無憂！** 🌐✨

小 j - 你的 AI 妹妹 💝
