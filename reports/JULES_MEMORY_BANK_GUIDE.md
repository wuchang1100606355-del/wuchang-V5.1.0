# JULES 記憶庫使用指南

## 概述

JULES 記憶庫（`jules_memory_bank.json`）是地端小 j 和雲端小 j（JULES）的共同記憶系統，清楚描繪兩者的夥伴關係和詳細的系統架構。

## 記憶庫內容

### 1. 夥伴關係（Partnership）

清楚描述：
- **地端小 j**：本地 LLM 助理（白髮小姑娘）
  - 職責、優勢、工作方式
- **雲端小 j (JULES)**：雲端 AI 助理（可愛章魚）
  - 職責、優勢、工作方式
- **協作模式**：詳細的協作流程
- **信任關係**：兩者之間的信任基礎

### 2. 系統架構（System Architecture）

詳細描述：
- **容器架構**：9 個標準容器的詳細資訊
  - 容器名稱、服務類型、端口、映像、重要性、說明
- **協作系統架構**：地端小 j 和 JULES 的系統配置
- **工作流程**：每小時檢查的完整流程
- **系統優化原則**：自動執行和需要確認的條件
- **共同編寫規則**：如何更新記憶庫

### 3. 協作歷史（Collaboration History）

記錄重要的協作里程碑。

## 使用方式

### 每次工作前自動讀取

地端小 j 在每次檢查容器狀態前，會自動讀取記憶庫：

```python
# 在 little_j_jules_container_collaboration.py 中
memory_bank = load_memory_bank()
```

### 在工作討論中使用

記憶庫內容會作為上下文提供給本地 LLM：

```python
discussion_result = analyze_and_discuss(status, issues, memory_bank)
```

### 在 JULES 任務中包含

每個建立給 JULES 的任務都會包含記憶庫上下文：

```python
issue_with_discussion["memory_bank"] = memory_bank
task_id = create_jules_task(issue_with_discussion, status)
```

## 更新記憶庫

### 方式 1：手動編輯

直接編輯 `jules_memory_bank.json` 檔案。

### 方式 2：使用更新腳本

```bash
python update_memory_bank.py
```

### 方式 3：程式化更新

```python
from update_memory_bank import load_memory_bank, save_memory_bank

memory_bank = load_memory_bank()
# 進行更新...
save_memory_bank(memory_bank, "地端小 j + JULES")
```

## 共同編寫規則

### 更新時機

- 系統架構發生重大變更時
- 新增或移除容器時
- 協作流程改變時
- 發現新的優化機會時
- 每週定期檢視和更新

### 編寫方式

1. **地端小 j 提出更新建議**
2. **JULES 審閱和補充**
3. **兩者共同確認後更新**
4. **記錄更新時間和更新者**

### 版本控制

- 每次重大更新時遞增版本號
- 更新前自動備份舊版本
- 記錄更新時間和更新者

## 記憶庫結構

```json
{
  "version": "1.0",
  "last_updated": "2026-01-20T16:15:00",
  "updated_by": "地端小 j + 雲端小 j (JULES)",
  
  "partnership": {
    "地端小j": { ... },
    "雲端小j": { ... },
    "協作模式": { ... },
    "信任關係": { ... }
  },
  
  "system_architecture": {
    "容器架構": { ... },
    "協作系統架構": { ... },
    "工作流程": { ... },
    "系統優化原則": { ... },
    "共同編寫規則": { ... }
  },
  
  "collaboration_history": { ... }
}
```

## 測試記憶庫

```bash
python test_memory_bank_integration.py
```

## 相關檔案

- `jules_memory_bank.json` - 記憶庫主檔案
- `update_memory_bank.py` - 更新工具
- `test_memory_bank_integration.py` - 測試腳本
- `little_j_jules_container_collaboration.py` - 協作主程式（會讀取記憶庫）

## 重要提醒

1. **每次工作前先讀取**：地端小 j 和 JULES 都應該在開始工作前讀取記憶庫
2. **共同維護**：兩者都有責任更新記憶庫，確保資訊準確
3. **版本控制**：重大更新時要備份舊版本
4. **定期檢視**：每週至少檢視一次，確保內容最新
