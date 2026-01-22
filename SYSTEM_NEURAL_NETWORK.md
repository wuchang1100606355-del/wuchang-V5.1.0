# 系統神經網路運作機制

## 📋 概述

系統神經網路是五常系統的核心感知機制，模擬生物神經網路結構，為 AI 小本體（Little J）提供即時系統感知能力。

## 🧠 架構設計

### 五層架構

```
┌─────────────────────────────────────┐
│  決策層 (Decision Layer)            │  ← AI 小本體查詢介面
│  - 統一感知 API                     │
│  - 狀態摘要與分析                   │
└─────────────────────────────────────┘
           ↑
┌─────────────────────────────────────┐
│  記憶層 (Memory Layer)              │  ← 歷史狀態記錄
│  - 感知讀數歷史                     │
│  - 事件佇列                         │
└─────────────────────────────────────┘
           ↑
┌─────────────────────────────────────┐
│  傳播層 (Propagation Layer)         │  ← 狀態變化通知
│  - 回調機制                         │
│  - 事件觸發                         │
└─────────────────────────────────────┘
           ↑
┌─────────────────────────────────────┐
│  處理層 (Processing Layer)          │  ← 數據聚合與分析
│  - 狀態判斷                         │
│  - 置信度計算                       │
└─────────────────────────────────────┘
           ↑
┌─────────────────────────────────────┐
│  感知層 (Sensor Layer)              │  ← 原始數據收集
│  - 服務節點                         │
│  - 網路節點                         │
│  - 資源節點                         │
│  - 健康檢查節點                     │
└─────────────────────────────────────┘
```

## 🔌 感知節點類型

### 1. 服務節點 (SERVICE)
監控服務運行狀態：
- 本機中控台 (port 8788)
- Little J Hub (port 8799)
- 其他自訂服務

### 2. 健康檢查節點 (HEALTH)
監控遠端服務健康狀態：
- 伺服器健康檢查端點
- 可配置健康檢查 URL

### 3. 資源節點 (RESOURCE)
監控系統資源使用：
- CPU 使用率
- 記憶體使用率
- 磁碟空間

### 4. 任務節點 (JOB)
監控任務狀態：
- 任務收件匣數量
- 任務執行狀態

### 5. 網路節點 (NETWORK)
監控網路連通性：
- DNS 解析狀態
- 網路介面狀態

### 6. 安全節點 (SECURITY)
監控安全事件：
- 稽核事件
- 異常行為

## 🚀 使用方式

### 啟動神經網路

```python
from system_neural_network import get_neural_network

nn = get_neural_network()
nn.start()
```

### 查詢系統感知

```python
# 獲取系統感知摘要（供 AI 使用）
perception = nn.get_system_perception()
print(perception)
```

輸出範例：
```json
{
  "timestamp": 1705123456.789,
  "overall_health": "healthy",
  "status_summary": {
    "healthy": 4,
    "warning": 1,
    "error": 0
  },
  "critical_nodes": {
    "service_control_center": {
      "name": "本機中控台",
      "status": "healthy",
      "value": {"running": true, "port": 8788}
    },
    "service_little_j_hub": {
      "name": "Little J Hub",
      "status": "healthy",
      "value": {"running": true, "port": 8799}
    }
  },
  "recent_events_count": 5,
  "total_nodes": 5
}
```

### 查詢特定節點

```python
# 獲取特定節點狀態
node_status = nn.get_node_status("service_control_center")
print(node_status)
```

### 獲取最近事件

```python
# 獲取最近 10 個事件
events = nn.get_recent_events(limit=10)
for event in events:
    print(f"事件: {event['event_type']}, 節點: {event['node_id']}")
```

### 註冊自訂節點

```python
from system_neural_network import NeuralNode, SensorType

# 創建自訂節點
custom_node = NeuralNode(
    node_id="custom_service",
    name="自訂服務",
    sensor_type=SensorType.SERVICE,
    check_interval=5.0,
    metadata={"port": 8080, "url": "http://127.0.0.1:8080/"}
)

# 註冊節點
nn.register_node(custom_node)
```

### 添加狀態變化回調

```python
def on_status_change(reading):
    print(f"節點 {reading.sensor_id} 狀態變化: {reading.status.value}")

# 為節點添加回調
nn.add_callback("service_control_center", on_status_change)
```

## 🌐 HTTP API

神經網路提供 HTTP API 供 Little J 查詢：

### 獲取系統感知摘要

```http
GET /api/neural/perception
```

回應：
```json
{
  "ok": true,
  "perception": {
    "timestamp": 1705123456.789,
    "overall_health": "healthy",
    "status_summary": {...},
    "critical_nodes": {...}
  }
}
```

### 獲取所有節點狀態

```http
GET /api/neural/status
```

### 獲取特定節點狀態

```http
GET /api/neural/node?id=service_control_center
```

### 獲取最近事件

```http
GET /api/neural/events?limit=50
```

### 啟動/停止神經網路

```http
POST /api/neural/start
POST /api/neural/stop
```

## 🔧 配置

神經網路配置儲存在 `neural_network_config.json`：

```json
{
  "nodes": [
    {
      "node_id": "service_control_center",
      "name": "本機中控台",
      "sensor_type": "service",
      "check_interval": 5.0,
      "enabled": true,
      "metadata": {
        "port": 8788,
        "url": "http://127.0.0.1:8788/"
      }
    }
  ]
}
```

## 📊 記憶儲存

所有感知讀數會自動記錄到 `neural_network_memory.jsonl`：

```json
{"timestamp": "2026-01-15T12:00:00+0800", "sensor_id": "service_control_center", "sensor_type": "service", "status": "healthy", "value": {...}}
{"timestamp": "2026-01-15T12:00:05+0800", "sensor_id": "service_control_center", "sensor_type": "service", "status": "healthy", "value": {...}}
```

## 🔗 整合到現有系統

### 整合到 local_control_center.py

```python
from system_neural_network import get_neural_network
from neural_network_api import NeuralNetworkAPIHandler

# 在 Handler 中添加路由
if parsed.path == "/api/neural/perception":
    nn = get_neural_network()
    if not nn.running:
        nn.start()
    perception = nn.get_system_perception()
    _json(self, HTTPStatus.OK, {"ok": True, "perception": perception})
```

### 整合到 little_j_hub_server.py

```python
# 在 Handler 中添加神經網路端點
if parsed.path == "/api/hub/neural/perception":
    from system_neural_network import get_neural_network
    nn = get_neural_network()
    if not nn.running:
        nn.start()
    perception = nn.get_system_perception()
    _json(self, HTTPStatus.OK, {"ok": True, "perception": perception})
```

## 🎯 AI 小本體使用範例

Little J 可以透過以下方式獲取系統感知：

```python
# 透過 HTTP API
import requests

response = requests.get("http://127.0.0.1:8788/api/neural/perception")
perception = response.json()["perception"]

# 判斷系統健康狀態
if perception["overall_health"] == "healthy":
    print("系統運行正常")
elif perception["overall_health"] == "degraded":
    print("系統狀態異常，需要關注")
    
# 檢查關鍵服務
for node_id, node_info in perception["critical_nodes"].items():
    if node_info["status"] != "healthy":
        print(f"警告: {node_info['name']} 狀態異常")
```

## 🔍 故障排除

### 節點無法讀取

1. 檢查節點配置是否正確
2. 確認節點是否啟用 (`enabled: true`)
3. 查看錯誤日誌

### 記憶檔案過大

定期清理 `neural_network_memory.jsonl`：

```python
# 只保留最近 1000 條記錄
with open("neural_network_memory.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()
    
with open("neural_network_memory.jsonl", "w", encoding="utf-8") as f:
    f.writelines(lines[-1000:])
```

### 性能問題

1. 調整節點檢查間隔 (`check_interval`)
2. 減少歷史記錄長度 (`history.maxlen`)
3. 禁用不必要的節點

## 📝 擴展開發

### 添加新的感知類型

1. 在 `SensorType` 中添加新類型
2. 在 `_read_sensor` 方法中添加讀取邏輯
3. 實現對應的 `_read_xxx_sensor` 方法

### 添加自訂處理邏輯

```python
def custom_processor(reading: SensorReading) -> None:
    # 自訂處理邏輯
    if reading.status == SensorStatus.ERROR:
        # 發送告警
        send_alert(reading)

# 添加處理器
nn.add_callback("service_control_center", custom_processor)
```

## 🔐 安全考量

1. **永久授權的讀取操作**：系統感知為永久授權的讀取權限，不需要額外權限檢查或授權請示
2. **敏感資訊**：避免在感知讀數中包含敏感資訊（如密碼、API 金鑰等）
3. **記憶檔案**：定期清理，避免洩漏歷史狀態
4. **只讀操作**：感知功能僅提供讀取，不執行任何修改操作

## 🔑 權限設計

### 永久授權的讀取操作

系統感知功能被設計為**永久授權的讀取操作**，這意味著：

- ✅ **不需要登入**：即使未登入也可以查詢系統感知
- ✅ **不需要授權請示**：不會觸發授權請示單流程
- ✅ **不需要權限檢查**：所有感知 API 端點都跳過權限檢查
- ✅ **AI 小本體可用**：Little J 可以隨時查詢系統狀態

### 設計理由

1. **系統健康監控**：感知功能用於監控系統健康狀態，屬於基礎設施層級
2. **只讀操作**：感知功能僅讀取狀態，不執行任何修改操作
3. **即時性需求**：AI 小本體需要即時獲取系統狀態，不應被權限流程阻擋
4. **安全邊界**：所有修改操作仍需通過正常的權限檢查流程

---

**最後更新**: 2026-01-15
