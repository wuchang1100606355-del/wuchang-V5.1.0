# 容器管理權限轉移給 JULES

## 任務目標

將 Docker 容器管理權限轉移給 JULES，讓 JULES 可以自動管理系統容器。

## 當前容器狀態

### 運行中的容器 (9 個)
- ✅ **wuchangv510-portainer-1** - Up 11 hours
  - 映像: portainer/portainer-ce:latest
- ✅ **wuchangv510-caddy-ui-1** - Up 11 hours
  - 映像: caddy:2
- ✅ **wuchangv510-caddy-1** - Up 11 hours
  - 映像: caddy:2
- ✅ **wuchangv510-wuchang-web-1** - Up 11 hours
  - 映像: odoo:17.0
- ✅ **wuchangv510-open-webui-1** - Up 11 hours (healthy)
  - 映像: ghcr.io/open-webui/open-webui:latest
- ✅ **wuchangv510-ollama-1** - Up 11 hours
  - 映像: ollama/ollama:latest
- ✅ **wuchangv510-db-1** - Up 11 hours
  - 映像: postgres:15
- ✅ **wuchangv510-uptime-kuma-1** - Up 11 hours (healthy)
  - 映像: louislam/uptime-kuma:latest
- ✅ **wuchangv510-cloudflared-1** - Up 11 hours
  - 映像: cloudflare/cloudflared:latest

## 標準容器配置

系統標準配置應有 **9 個容器**：

1. **wuchangv510-caddy-1** - Web 伺服器（端口 80, 443）
2. **wuchangv510-caddy-ui-1** - Caddy 管理介面（端口 8081, 8444）
3. **wuchangv510-cloudflared-1** - Cloudflare Tunnel
4. **wuchangv510-db-1** - PostgreSQL 資料庫（端口 5432）
5. **wuchangv510-ollama-1** - AI 模型服務（端口 11434）
6. **wuchangv510-open-webui-1** - AI 介面（端口 8080）
7. **wuchangv510-portainer-1** - 容器管理介面（端口 9000）
8. **wuchangv510-uptime-kuma-1** - 監控工具（端口 3001）
9. **wuchangv510-wuchang-web-1** - Odoo ERP 系統（端口 8069）

## JULES 容器管理指令格式

### 檢查容器狀態
```json
{
  "type": "execute",
  "command": "docker ps -a",
  "description": "檢查所有容器狀態"
}
```

### 啟動容器
```json
{
  "type": "execute",
  "command": "docker start <container_name>",
  "description": "啟動指定容器"
}
```

### 停止容器
```json
{
  "type": "execute",
  "command": "docker stop <container_name>",
  "description": "停止指定容器"
}
```

### 重啟容器
```json
{
  "type": "execute",
  "command": "docker restart <container_name>",
  "description": "重啟指定容器"
}
```

### 使用 docker-compose 管理
```json
{
  "type": "execute",
  "command": "docker-compose up -d",
  "description": "啟動所有服務",
  "working_dir": "C:\\wuchang V5.1.0\\wuchang-V5.1.0"
}
```

```json
{
  "type": "execute",
  "command": "docker-compose restart <service_name>",
  "description": "重啟指定服務",
  "working_dir": "C:\\wuchang V5.1.0\\wuchang-V5.1.0"
}
```

```json
{
  "type": "execute",
  "command": "docker-compose ps",
  "description": "查看服務狀態",
  "working_dir": "C:\\wuchang V5.1.0\\wuchang-V5.1.0"
}
```

### 查看容器日誌
```json
{
  "type": "execute",
  "command": "docker logs <container_name> --tail 50",
  "description": "查看容器日誌"
}
```

### 檢查容器健康
```json
{
  "type": "execute",
  "command": "python check_container_status.py",
  "description": "檢查容器健康狀態",
  "working_dir": "C:\\wuchang V5.1.0\\wuchang-V5.1.0"
}
```

## 自動化管理建議

### 1. 定期健康檢查
- 每小時檢查一次容器狀態
- 如果容器異常，自動重啟
- 記錄異常情況

### 2. 容器監控
- 監控容器資源使用（CPU、記憶體）
- 監控容器日誌錯誤
- 自動清理舊日誌

### 3. 自動備份
- 定期備份容器配置
- 備份資料庫
- 備份重要資料

## 需要 JULES 執行的操作

1. **確認容器管理權限**
   - [ ] 確認 JULES 可以執行 docker 命令
   - [ ] 確認 JULES 可以訪問 docker-compose 配置
   - [ ] 測試基本容器管理命令

2. **設定自動檢查**
   - [ ] 建立定期容器健康檢查任務
   - [ ] 設定異常容器自動重啟機制
   - [ ] 設定日誌記錄

3. **整合到 JULES 任務系統**
   - [ ] 將容器管理指令加入 JULES 可執行指令列表
   - [ ] 測試容器管理指令執行
   - [ ] 確認結果回報機制

## 相關檔案

- `check_container_status.py` - 容器狀態檢查腳本
- `check_standard_containers.py` - 標準容器檢查腳本
- `docker-compose.unified.yml` - Docker Compose 配置
- `CONTAINER_MANAGEMENT_GUIDE.md` - 容器管理指南

## 優先級

**中優先級** - 提升系統自動化管理能力

## 備註

請 JULES 協助：
1. 確認容器管理權限和指令格式
2. 建立定期健康檢查機制
3. 整合容器管理到 JULES 任務系統
