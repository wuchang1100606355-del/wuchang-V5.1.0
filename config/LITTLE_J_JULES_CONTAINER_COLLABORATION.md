# 地端小 j 與雲端小 j（JULES）容器維護協作機制

## 架構概述

**地端小 j（本地 LLM）** + **雲端小 j（JULES）** 共同維護 Docker 容器：

```
地端小 j（監控） → 發現問題 → 通知 JULES → JULES 執行修復 → 地端小 j 驗證結果
```

## 角色分工

### 地端小 j（本地 LLM - Little J）

**職責**：
- ✅ 持續監控容器狀態
- ✅ 偵測容器問題（停止、重啟、異常）
- ✅ 建立 JULES 任務
- ✅ 驗證修復結果
- ✅ 記錄協作日誌

**優勢**：
- 本地運行，即時監控
- 無需網路即可檢查容器狀態
- 可以快速響應本地問題

### 雲端小 j（JULES）

**職責**：
- ✅ 接收地端小 j 的任務
- ✅ 執行容器修復操作
- ✅ 回報執行結果
- ✅ 處理複雜的容器管理任務

**優勢**：
- 雲端處理，不受本地限制
- 可以執行複雜的修復流程
- 可以整合多個系統的資訊

## 協作流程

### 1. 監控階段（地端小 j）

地端小 j **每小時**檢查容器狀態：

```bash
python little_j_jules_container_collaboration.py --interval 3600
```

**檢查項目**：
- 標準容器是否都在運行（9個）
- 是否有容器異常重啟
- 是否有非標準容器需要清理

### 1.5. 工作討論階段（地端小 j）

每次檢查後，地端小 j 會：

1. **呼叫本地 LLM（Ollama）**進行工作討論
2. **分析系統狀態**並提供優化建議
3. **識別可立即執行的安全優化**
4. **自動執行小變動**（不涉及巨大變動）

### 2. 問題偵測（地端小 j）

當發現問題時，地端小 j 會：

1. **記錄問題**：記錄問題類型、嚴重程度、容器名稱
2. **加入討論結果**：將工作討論結果包含在任務中
3. **建立任務**：在 Google Tasks 中建立任務給 JULES
4. **追蹤狀態**：追蹤任務狀態，避免重複報告

### 2.5. 優化建議處理（地端小 j）

地端小 j 會：

1. **提取優化建議**：從 LLM 討論中提取優化建議
2. **評估風險**：判斷是否為低風險、可立即執行
3. **自動執行**：執行安全的優化（如清理、日誌管理）
4. **儲存記錄**：將所有建議儲存到 `container_optimization_suggestions.json`

**問題類型**：
- `standard_container_stopped` - 標準容器停止（高嚴重度）
- `container_restarting` - 容器異常重啟（中嚴重度）
- `non_standard_containers` - 非標準容器（低嚴重度）

### 3. 任務執行（JULES）

JULES 收到任務後：

1. **解析任務**：讀取任務內容和建議操作
2. **執行修復**：執行 docker 或 docker-compose 命令
3. **回報結果**：將執行結果附加到任務備註

**執行指令範例**：

```json
{
  "type": "execute",
  "command": "docker restart wuchangv510-db-1",
  "description": "重啟資料庫容器",
  "working_dir": "C:\\wuchang V5.1.0\\wuchang-V5.1.0"
}
```

### 4. 結果驗證（地端小 j）

地端小 j 定期驗證修復結果：

1. **重新檢查**：檢查之前報告的問題是否已解決
2. **驗證狀態**：確認容器是否恢復正常
3. **更新記錄**：更新驗證結果到協作狀態

## 使用方式

### 單次檢查（包含工作討論）

```bash
python little_j_jules_container_collaboration.py --once
```

**功能**：
- 檢查容器狀態
- 進行工作討論（使用本地 LLM）
- 生成優化建議
- 自動執行安全的小優化

### 持續監控（每小時檢查一次）

```bash
# 每小時檢查一次（預設 3600 秒）
python little_j_jules_container_collaboration.py

# 自訂檢查間隔
python little_j_jules_container_collaboration.py --interval 1800  # 30分鐘
```

### Windows 背景運行

使用批次檔啟動：

```batch
start_container_collaboration_hourly.bat
```

或手動啟動：

```bash
start "地端小j-容器協作" /min python little_j_jules_container_collaboration.py --interval 3600
```

### Windows 背景運行

建立批次檔 `start_container_collaboration.bat`：

```batch
@echo off
cd /d "C:\wuchang V5.1.0\wuchang-V5.1.0"
start "地端小j-容器協作" /min python little_j_jules_container_collaboration.py --interval 300
```

## 狀態檔案

### `container_collaboration_state.json`

記錄協作狀態：
- `last_check` - 最後檢查時間
- `issues_reported` - 已報告的問題 ID
- `jules_tasks_created` - 建立的 JULES 任務
- `verification_results` - 驗證結果

### `container_collaboration.log`

協作日誌：
- 檢查記錄
- 問題偵測記錄
- 工作討論記錄
- 任務建立記錄
- 驗證結果記錄

### `container_optimization_suggestions.json`

優化建議記錄：
- 建議類型
- 描述
- 風險等級
- 是否可立即執行
- 執行結果（如果有）

## 標準容器配置

系統標準配置應有 **9 個容器**：

1. **wuchangv510-caddy-1** - Web 伺服器
2. **wuchangv510-caddy-ui-1** - Caddy 管理介面
3. **wuchangv510-cloudflared-1** - Cloudflare Tunnel
4. **wuchangv510-db-1** - PostgreSQL 資料庫
5. **wuchangv510-ollama-1** - AI 模型服務
6. **wuchangv510-open-webui-1** - AI 介面
7. **wuchangv510-portainer-1** - 容器管理介面
8. **wuchangv510-uptime-kuma-1** - 監控工具
9. **wuchangv510-wuchang-web-1** - Odoo ERP 系統

## 問題處理範例

### 範例 1：資料庫容器停止

**地端小 j 偵測**：
```
[WARN] 偵測到問題: 標準容器 wuchangv510-db-1 未運行
```

**建立 JULES 任務**：
```
標題：容器維護：standard_container_stopped - 2026-01-20 16:10:00
內容：包含問題描述和建議操作
```

**JULES 執行**：
```json
{
  "type": "execute",
  "command": "docker start wuchangv510-db-1",
  "description": "啟動資料庫容器"
}
```

**地端小 j 驗證**：
```
[INFO] ✅ 容器 wuchangv510-db-1 已恢復運行
```

### 範例 2：容器異常重啟

**地端小 j 偵測**：
```
[WARN] 偵測到問題: 標準容器 wuchangv510-wuchang-web-1 正在重啟（可能異常）
```

**建立 JULES 任務**：
```
標題：容器維護：container_restarting - 2026-01-20 16:15:00
內容：建議檢查容器日誌
```

**JULES 執行**：
```json
{
  "type": "execute",
  "command": "docker logs wuchangv510-wuchang-web-1 --tail 50",
  "description": "查看容器日誌"
}
```

## 整合到系統

### 1. 整合到地端小 j（local_control_center.py）

可以在控制中心加入容器協作狀態顯示：

```python
# 在控制中心 API 中加入
@app.route("/api/container/collaboration/status")
def container_collaboration_status():
    # 讀取協作狀態
    # 返回當前狀態和最近問題
    pass
```

### 2. 整合到 JULES 任務執行器

確保 JULES 任務執行器可以處理容器管理指令：

```python
# 在 auto_jules_task_executor.py 中
if task_type == "container_maintenance":
    # 執行容器管理指令
    execute_container_command(task)
```

## 優勢

### 1. 即時監控
- 地端小 j 持續監控，快速發現問題

### 2. 自動化修復
- JULES 自動執行修復，無需人工介入

### 3. 結果驗證
- 地端小 j 自動驗證修復結果，確保問題解決

### 4. 協作記錄
- 完整的協作日誌，方便追蹤和除錯

## 注意事項

1. **權限**：確保地端小 j 和 JULES 都有執行 docker 命令的權限
2. **網路**：JULES 需要可以訪問 Google Tasks API
3. **日誌**：定期檢查協作日誌，確認運作正常
4. **狀態**：定期清理舊的協作狀態記錄

## 相關檔案

- `little_j_jules_container_collaboration.py` - 協作主程式
- `check_container_status.py` - 容器狀態檢查
- `create_container_management_task_for_jules.py` - 建立 JULES 任務
- `auto_jules_task_executor.py` - JULES 任務執行器
- `CONTAINER_MANAGEMENT_GUIDE.md` - 容器管理指南

## 下一步

1. ✅ 建立協作機制
2. ⏳ 整合到地端小 j 控制中心
3. ⏳ 整合到 JULES 任務執行器
4. ⏳ 測試完整協作流程
5. ⏳ 設定自動啟動
