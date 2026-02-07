# Docker Desktop 遠程同步指南

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**目標**: 讓 UI 筆電和 VM 伺服器透過網際網路或區域網路同步，雙方可以看到和讀寫相同的容器

---

## 🎯 方案選擇

### 方案 A：Docker Context（推薦）
**優點**：
- ✅ 簡單易用，無需修改 Docker daemon 設定
- ✅ 安全（使用 SSH 或 TLS）
- ✅ 支援雙向訪問
- ✅ 可以切換不同的 Docker 環境

**適用場景**：UI 筆電遠程管理 VM 伺服器的 Docker

### 方案 B：Docker Remote API
**優點**：
- ✅ 直接訪問 Docker daemon
- ✅ 功能完整

**缺點**：
- ⚠️ 需要開啟 Docker daemon 的 TCP 端口（安全風險）
- ⚠️ 需要配置 TLS 證書

**適用場景**：需要直接訪問 Docker API 的場景

### 方案 C：共享 Docker Socket（不推薦）
**缺點**：
- ❌ 安全風險高
- ❌ 不適合跨網路使用

---

## 🚀 推薦方案：Docker Context（SSH）

### 架構圖

```
┌─────────────────────┐         SSH/TLS          ┌─────────────────────┐
│   UI 筆電            │ ◄──────────────────────► │   VM 伺服器          │
│   (192.168.50.84)   │                         │   (192.168.50.249)   │
│                     │                         │                     │
│  Docker Desktop     │                         │  Docker Desktop     │
│  (Docker Context)   │                         │  (Docker Daemon)    │
└─────────────────────┘                         └─────────────────────┘
```

---

## 📋 設定步驟

### Step 1: 在 VM 伺服器上啟用 Docker Remote API（可選）

如果需要使用 TCP 連接（不推薦，僅用於測試）：

```powershell
# 在 VM 伺服器上（192.168.50.249）
# 編輯 Docker daemon 設定
# 路徑：C:\ProgramData\Docker\config\daemon.json

{
  "hosts": ["tcp://0.0.0.0:2376", "npipe://"],
  "tls": true,
  "tlsverify": true,
  "tlscacert": "C:\\ProgramData\\Docker\\certs\\ca.pem",
  "tlscert": "C:\\ProgramData\\Docker\\certs\\server-cert.pem",
  "tlskey": "C:\\ProgramData\\Docker\\certs\\server-key.pem"
}
```

**⚠️ 注意**：此方法有安全風險，建議使用 SSH 方式。

### Step 2: 使用 Docker Context（SSH 方式，推薦）

#### 2.1 在 UI 筆電上建立遠程 Context

```powershell
# 在 UI 筆電上執行
docker context create vm-server --docker "host=ssh://user@192.168.50.249"
```

或使用 TLS：

```powershell
docker context create vm-server-tls --docker "host=tcp://192.168.50.249:2376" --docker "tls=true"
```

#### 2.2 切換到遠程 Context

```powershell
# 切換到 VM 伺服器的 Docker
docker context use vm-server

# 驗證連接
docker ps

# 切換回本地
docker context use default
```

### Step 3: 使用 Docker Compose 遠程操作

```powershell
# 使用遠程 Context 執行 docker compose
docker context use vm-server
docker compose -f docker-compose.yml up -d

# 或指定 Context
docker --context vm-server compose up -d
```

---

## 🔧 進階設定：雙向同步

### 方案 1：共享 Docker Compose 檔案

兩台機器使用相同的 `docker-compose.yml` 檔案，透過網路共享：

```yaml
# docker-compose.yml
services:
  shared-service:
    image: nginx:latest
    volumes:
      - shared-data:/data  # 使用命名卷
    networks:
      - shared-network

volumes:
  shared-data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=192.168.50.249,vers=4
      device: ":/mnt/shared-docker-data"

networks:
  shared-network:
    driver: bridge
```

### 方案 2：使用 Portainer Agent（推薦）

Portainer 可以管理多個 Docker 環境：

1. **在 VM 伺服器上安裝 Portainer Agent**：
```powershell
docker run -d -p 9001:9001 --name portainer_agent --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker/volumes:/var/lib/docker/volumes portainer/agent:latest
```

2. **在 UI 筆電上安裝 Portainer**：
```powershell
docker run -d -p 9000:9000 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer-ce:latest
```

3. **在 Portainer UI 中添加遠程環境**：
   - 訪問 `http://localhost:9000`
   - 添加環境 → Docker → 選擇 "Agent"
   - 輸入 VM 伺服器的 IP 和 Portainer Agent 端口（9001）

---

## 📊 實際操作範例

### 範例 1：從 UI 筆電管理 VM 的容器

```powershell
# 1. 建立 Context
docker context create vm-server --docker "host=ssh://administrator@192.168.50.249"

# 2. 切換 Context
docker context use vm-server

# 3. 查看 VM 上的容器
docker ps

# 4. 啟動/停止容器
docker start wuchangv510-wuchang-web-1
docker stop wuchangv510-wuchang-web-1

# 5. 查看日誌
docker logs wuchangv510-wuchang-web-1

# 6. 執行命令
docker exec -it wuchangv510-wuchang-web-1 bash
```

### 範例 2：同步 Docker Compose 操作

```powershell
# 在 UI 筆電上，使用遠程 Context 執行 compose
docker --context vm-server compose -f docker-compose.yml up -d

# 查看狀態
docker --context vm-server compose ps

# 查看日誌
docker --context vm-server compose logs -f
```

---

## 🔒 安全建議

1. **使用 SSH 而非 TCP**：
   - SSH 更安全，無需開啟 Docker daemon 的 TCP 端口
   - 使用 SSH 金鑰認證

2. **限制訪問**：
   - 僅允許特定 IP 訪問
   - 使用防火牆規則

3. **使用 TLS**（如果必須使用 TCP）：
   - 生成 TLS 證書
   - 啟用 TLS 驗證

---

## 🛠️ 故障排除

### 問題 1: 無法連接到遠程 Docker

**檢查項目**：
1. 確認 VM 伺服器的 IP 地址正確
2. 確認 SSH 服務正在運行
3. 確認防火牆未阻擋連接
4. 確認 SSH 金鑰已設定

**解決方案**：
```powershell
# 測試 SSH 連接
ssh user@192.168.50.249

# 測試 Docker Context
docker --context vm-server ps
```

### 問題 2: 權限不足

**解決方案**：
```powershell
# 確認用戶在 docker 群組中（Linux）
# 或在 Windows 上以管理員身份運行
```

---

## 💡 最佳實踐

1. **使用命名 Context**：
   - `vm-server` - VM 伺服器
   - `ui-laptop` - UI 筆電
   - `default` - 本地

2. **建立別名**：
   ```powershell
   # 建立 PowerShell 別名
   function docker-vm { docker --context vm-server $args }
   function docker-ui { docker --context default $args }
   ```

3. **使用 Portainer**：
   - 統一管理多個 Docker 環境
   - 圖形化介面，易於操作

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
