# Docker Desktop 雙向同步指南（正確版本）

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**目標**: 讓 UI 筆電 (192.168.50.84) 和 VM 伺服器 (192.168.50.249) 可以互相訪問對方的 Docker

---

## 🎯 架構說明

```
┌─────────────────────┐         SSH          ┌─────────────────────┐
│   UI 筆電            │ ◄──────────────────► │   VM 伺服器          │
│   (192.168.50.84)   │                       │   (192.168.50.249)  │
│                     │                       │                     │
│  Docker Context:    │                       │  Docker Context:    │
│  - default (本地)   │                       │  - default (本地)   │
│  - vm-server (→VM)  │                       │  - ui-laptop (→UI)  │
└─────────────────────┘                       └─────────────────────┘
```

---

## 📋 設定步驟

### Step 1: 在 VM 伺服器 (192.168.50.249) 上設定

執行以下腳本：

```powershell
cd "C:\wuchang V5.1.0"
.\scripts\setup_docker_bidirectional_sync_corrected.ps1
```

這會：
1. 建立 `ui-laptop` Context，讓 VM 可以連接到 UI 筆電的 Docker
2. 測試連接
3. 建立便利腳本

### Step 2: 在 UI 筆電 (192.168.50.84) 上設定

同樣執行腳本：

```powershell
cd "C:\wuchang V5.1.0"
.\scripts\setup_docker_bidirectional_sync_corrected.ps1
```

這會：
1. 建立 `vm-server` Context，讓 UI 筆電可以連接到 VM 的 Docker
2. 測試連接
3. 建立便利腳本

---

## 🔧 使用方式

### 在 VM 伺服器上操作 UI 筆電的 Docker

```powershell
# 切換到 UI 筆電的 Docker Context
.\scripts\docker-ui.ps1

# 查看 UI 筆電的容器
docker ps

# 啟動/停止 UI 筆電的容器
docker start <container_name>
docker stop <container_name>

# 查看日誌
docker logs <container_name>

# 切換回 VM 本地
.\scripts\docker-vm-local.ps1
```

### 在 UI 筆電上操作 VM 伺服器的 Docker

```powershell
# 切換到 VM 伺服器的 Docker Context
.\scripts\docker-vm.ps1

# 查看 VM 的容器
docker ps

# 啟動/停止 VM 的容器
docker start <container_name>
docker stop <container_name>

# 查看日誌
docker logs <container_name>

# 切換回 UI 本地
.\scripts\docker-ui-local.ps1
```

### 使用 Docker Compose 遠程操作

```powershell
# 在 VM 上操作 UI 筆電的 compose
docker --context ui-laptop compose -f docker-compose.yml up -d

# 在 UI 筆電上操作 VM 的 compose
docker --context vm-server compose -f docker-compose.yml up -d
```

---

## 🔒 SSH 設定要求

### 1. 啟用 SSH 服務

**Windows (兩台機器都需要)**：
```powershell
# 安裝 OpenSSH Server（如果尚未安裝）
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 啟動 SSH 服務
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 確認防火牆規則
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

### 2. 設定 SSH 金鑰認證（推薦）

**在 VM 伺服器上生成金鑰**：
```powershell
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa_vm_to_ui
```

**將公鑰複製到 UI 筆電**：
```powershell
type $env:USERPROFILE\.ssh\id_rsa_vm_to_ui.pub | ssh $UIUser@192.168.50.84 "mkdir -p .ssh; cat >> .ssh/authorized_keys"
```

**在 UI 筆電上生成金鑰**：
```powershell
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa_ui_to_vm
```

**將公鑰複製到 VM 伺服器**：
```powershell
type $env:USERPROFILE\.ssh\id_rsa_ui_to_vm.pub | ssh $VMUser@192.168.50.249 "mkdir -p .ssh; cat >> .ssh/authorized_keys"
```

---

## ✅ 驗證設定

### 測試 SSH 連接

**從 VM 到 UI**：
```powershell
ssh $UIUser@192.168.50.84 "docker ps"
```

**從 UI 到 VM**：
```powershell
ssh $VMUser@192.168.50.249 "docker ps"
```

### 測試 Docker Context

**在 VM 上**：
```powershell
docker --context ui-laptop ps
```

**在 UI 筆電上**：
```powershell
docker --context vm-server ps
```

---

## 💡 進階使用：共享容器和 Volume

### 方案 1：使用網路共享存儲

在 `docker-compose.yml` 中使用網路共享的 Volume：

```yaml
services:
  shared-service:
    volumes:
      - shared-data:/data

volumes:
  shared-data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=192.168.50.249,vers=4
      device: ":/mnt/shared-docker-data"
```

### 方案 2：使用 Portainer 統一管理

1. **在 VM 上啟動 Portainer Agent**：
```powershell
docker run -d -p 9001:9001 --name portainer_agent --restart=always -v /var/run/docker.sock:/var/run/docker.sock portainer/agent:latest
```

2. **在 UI 筆電上啟動 Portainer**：
```powershell
docker run -d -p 9000:9000 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer-ce:latest
```

3. **在 Portainer UI 中添加兩台機器**：
   - 訪問 `http://localhost:9000`
   - 添加環境 → Docker → Agent
   - VM Agent URL: `192.168.50.249:9001`
   - UI Agent URL: `192.168.50.84:9001`（如果 UI 也安裝了 Agent）

---

## 🛠️ 故障排除

### 問題 1: SSH 連接失敗

**檢查項目**：
1. SSH 服務是否運行：`Get-Service sshd`
2. 防火牆是否開放端口 22
3. SSH 金鑰是否正確設定

**解決方案**：
```powershell
# 檢查 SSH 服務狀態
Get-Service sshd

# 檢查防火牆規則
Get-NetFirewallRule -Name sshd

# 測試 SSH 連接
ssh user@192.168.50.84
```

### 問題 2: Docker Context 無法連接

**檢查項目**：
1. SSH 連接是否正常
2. Docker daemon 是否運行
3. 用戶是否有 Docker 權限

**解決方案**：
```powershell
# 測試 SSH
ssh user@192.168.50.84 "docker ps"

# 檢查 Context 設定
docker context inspect ui-laptop
```

---

## 📊 當前狀態

- ✅ **VM 伺服器 (192.168.50.249)**: 已檢測到 Docker 運行中
- ✅ **容器數量**: 8 個容器正在運行
- ⚠️ **UI 筆電連接**: 需要執行設定腳本並確認 SSH 連接

---

**文件版本**: 1.1  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
