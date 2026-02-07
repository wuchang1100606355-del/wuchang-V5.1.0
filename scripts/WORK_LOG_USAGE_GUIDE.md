# 系統工作日誌使用指南

**建立時間：** 2026-01-20  
**檔案位置：** `reports/SYSTEM_WORK_LOGS.md`

---

## 📋 說明

所有系統工作都必須記錄到 `reports/SYSTEM_WORK_LOGS.md` 檔案中。如果檔案不存在，系統會自動建立。

---

## 🔧 使用方式

### 方式 1：使用工作日誌管理器（推薦）

```python
from work_log_manager import WorkLogManager

manager = WorkLogManager()

# 記錄工作
manager.log_work(
    work_type="系統維護",
    work_content="執行容器健康檢查",
    agent="little_j",  # 或 "jules"
    status="完成",
    result="檢查了 10 個容器，全部正常運行",
    related_files=["scripts/double_j_maintenance_workflow.py"]
)
```

### 方式 2：使用工作執行工具（自動記錄）

```python
from execute_work_with_logging import execute_work

def my_work():
    # 執行實際工作
    return "工作結果"

result = execute_work(
    work_type="系統維護",
    work_content="執行某項維護工作",
    work_function=my_work,
    agent="little_j"
)
```

### 方式 3：執行腳本並自動記錄

```python
from execute_work_with_logging import execute_script

result = execute_script(
    script_path=Path("scripts/my_script.py"),
    work_type="系統配置",
    work_content="更新系統配置檔案",
    agent="jules",
    args=["--param", "value"]
)
```

---

## 📝 日誌格式

### 工作記錄包含：

- **時間戳記**：自動記錄
- **工作類型**：系統維護、配置更新、安全檢查等
- **工作內容**：詳細描述
- **負責代理**：little_j 或 jules
- **執行狀態**：
  - 🔄 進行中
  - ✅ 完成
  - ❌ 失敗
  - ⏳ 待開始
- **執行結果**：成功時的詳細結果
- **相關檔案**：涉及的腳本或配置檔案
- **錯誤訊息**：失敗時的錯誤資訊

---

## 📊 日誌範例

```
#### 2026-01-20 15:30:00 - 系統維護

- **負責代理：** little_j (小J)
- **工作內容：** 執行每小時自動維護工作
- **狀態：** ✅ 完成
- **執行結果：** 檢查了 10 個容器，維護任務完成率 100%
- **相關檔案：** scripts/double_j_maintenance_workflow.py

---
```

---

## ✅ 整合到現有腳本

### 在維護腳本中整合

```python
# 在腳本開頭
from work_log_manager import WorkLogManager
log_manager = WorkLogManager()

# 工作開始時
log_manager.log_work(
    work_type="系統維護",
    work_content="執行維護工作",
    agent="little_j",
    status="進行中"
)

# 工作完成時
log_manager.log_work(
    work_type="系統維護",
    work_content="執行維護工作",
    agent="little_j",
    status="完成",
    result="工作執行成功"
)
```

---

## 🎯 重要提醒

1. **所有系統工作都必須記錄**
   - 維護工作
   - 配置變更
   - 安全檢查
   - 系統優化
   - 故障修復

2. **記錄要即時**
   - 工作開始時記錄「進行中」
   - 工作完成時更新為「完成」或「失敗」

3. **記錄要詳細**
   - 包含執行結果
   - 包含相關檔案
   - 失敗時包含錯誤訊息

4. **負責代理要正確**
   - `little_j`：本地 AI，執行實際操作
   - `jules`：雲端 AI，負責規劃和決策

---

**建立時間：** 2026-01-20  
**維護者：** 雙J工作小組
