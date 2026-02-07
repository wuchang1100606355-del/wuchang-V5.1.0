# 容器管理指南

## 當前狀態

### ✅ 本地容器（已運行）

系統已經有完整的 Docker 環境，目前運行中的容器：

1. **Caddy** - Web 伺服器（端口 80, 443）
2. **Caddy UI** - Caddy 管理介面（端口 8081, 8444）
3. **Cloudflare** - Cloudflare Tunnel（2 個實例）
4. **PostgreSQL** - 資料庫（端口 5432）
5. **Ollama** - AI 模型服務（端口 11434）
6. **Open WebUI** - AI 介面（端口 8080）
7. **Portainer** - 容器管理介面（端口 9000）
8. **Uptime Kuma** - 監控工具（端口 3001）
9. **Odoo** - ERP 系統（端口 8069）

### 容器管理工具

- **Portainer**: http://localhost:9000 - 圖形化容器管理
- **docker-compose**: 通過配置檔案管理容器

## 本地容器操作

### 查看容器狀態

```bash
# 查看所有容器
docker ps -a

# 查看 docker-compose 容器
docker-compose ps
```

### 管理容器

```bash
# 啟動所有容器
docker-compose up -d

# 停止所有容器
docker-compose down

# 重啟特定容器
docker-compose restart <service_name>

# 查看容器日誌
docker-compose logs -f <service_name>
```

## 伺服器端容器管理

### 方式 1：通過 SSH（推薦）

如果伺服器使用相同帳號，可以直接通過 SSH 管理：

```bash
# 檢查伺服器端容器
python manage_server_containers.py --server-ip 10.8.0.1 --action status

# 重啟伺服器端容器
python manage_server_containers.py --server-ip 10.8.0.1 --action restart --container <container_name>
```

### 方式 2：通過 API

如果伺服器有容器管理 API：

```bash
python manage_server_containers.py --server-url https://coffeeLofe.asuscomm.com:8443 --action status
```

### 方式 3：通過網路共享

由於伺服器使用相同帳號，可以：

1. **映射網路磁碟機**到伺服器
2. **直接訪問伺服器的 Docker 目錄**
3. **執行 docker-compose 命令**

## 同步容器配置

### 檢查配置差異

```bash
python manage_server_containers.py --server-ip 10.8.0.1 --action status
```

### 同步 docker-compose.yml

如果本地和伺服器都有 docker-compose.yml：

1. 比較配置檔案
2. 同步環境變數
3. 同步卷掛載路徑

## 容器健康監控

### 使用 Uptime Kuma

訪問：http://localhost:3001

可以監控：
- 容器健康狀態
- 服務可用性
- 資源使用情況

### 使用 Portainer

訪問：http://localhost:9000

可以：
- 查看容器狀態
- 管理容器（啟動、停止、重啟）
- 查看日誌
- 監控資源使用

## 常見操作

### 重啟所有容器

```bash
docker-compose restart
```

### 更新容器映像

```bash
docker-compose pull
docker-compose up -d
```

### 查看容器資源使用

```bash
docker stats
```

### 清理未使用的資源

```bash
# 清理未使用的映像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理所有未使用的資源
docker system prune -a
```

## 伺服器端容器同步

由於伺服器使用相同帳號，建議：

1. **使用相同的 docker-compose.yml**
2. **同步環境變數配置**
3. **使用相同的卷掛載路徑**
4. **定期同步容器配置**

## 相關檔案

- `manage_server_containers.py` - 伺服器端容器管理腳本
- `developer_container_config.json` - 開發者容器配置
- `setup_developer_container.py` - 開發者容器設置

## 注意事項

1. **備份配置**：修改容器配置前先備份
2. **測試環境**：在測試環境先驗證
3. **監控資源**：注意容器資源使用情況
4. **日誌管理**：定期清理容器日誌
