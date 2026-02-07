# 伺服器連線診斷報告

**診斷時間**: 2026-01-17  
**目標伺服器**: 192.168.50.249  
**診斷工具**: diagnose_server_connection.py

---

## 📊 診斷結果摘要

### ✅ 正常項目

1. **Ping 測試**: ✅ **通過**
   - 伺服器可以 ping 通
   - 延遲: 3-5ms（正常）
   - 說明: 網絡連線正常，伺服器正在運行

2. **網絡配置**: ✅ **正常**
   - 本機 IP: 192.168.50.84
   - 伺服器 IP: 192.168.50.249
   - 網段: 都在 192.168.50.x 網段
   - ARP 表: 找到伺服器 MAC 地址 (30-9c-23-4a-9b-1b)

3. **路由表**: ✅ **正常**
   - 找到到伺服器網段的路由
   - 閘道: 192.168.50.1

4. **SSH 端口**: ✅ **開啟**
   - 端口 22 可以連接
   - 說明: SSH 服務正在運行

5. **RDP 端口**: ✅ **開啟**
   - 端口 3389 可以連接
   - 說明: 遠端桌面服務正在運行

### ❌ 問題項目

1. **服務端口全部關閉**: ❌
   - 8069 (Odoo): 關閉
   - 8080 (AI/Web): 關閉
   - 8766 (Cloud Sync): 關閉
   - 3001 (Status Dashboard): 關閉
   - 5432 (PostgreSQL): 關閉
   - 80 (HTTP): 關閉
   - 443 (HTTPS): 關閉

2. **SSH 認證失敗**: ⚠️
   - SSH 端口開啟但無法認證
   - 嘗試的用戶名: admin, wuchang, user, ubuntu, debian, root
   - 所有用戶名都認證失敗

---

## 🔍 問題分析

### 主要問題: 服務端口未開啟

**可能原因**:

1. **服務未啟動**
   - Docker 容器未運行
   - 服務進程未啟動
   - 系統服務未啟動

2. **服務監聽在 localhost**
   - 服務只監聽 127.0.0.1 而非 0.0.0.0
   - 只能從本機訪問，無法從外部訪問

3. **防火牆阻擋**
   - 伺服器防火牆阻擋了端口
   - 只允許 SSH (22) 和 RDP (3389)

4. **服務配置錯誤**
   - 服務配置為監聽其他端口
   - 服務配置為監聽其他 IP

---

## 🛠️ 解決方案

### 方案 1: 檢查服務狀態（在伺服器上執行）

```bash
# 檢查 Docker 容器狀態
docker ps -a

# 檢查 Odoo 服務
docker ps | grep odoo
docker logs <container_name>

# 檢查服務監聽端口
netstat -tlnp | grep 8069
netstat -tlnp | grep 8080
netstat -tlnp | grep 8766

# 檢查系統服務
systemctl status docker
systemctl status <service_name>
```

### 方案 2: 啟動服務（在伺服器上執行）

```bash
# 啟動 Docker 容器
cd /path/to/wuchang/project
docker-compose up -d

# 或啟動特定服務
docker-compose --profile system up -d
docker-compose --profile ai up -d
```

### 方案 3: 檢查服務監聽地址

```bash
# 檢查服務監聽地址
netstat -tlnp | grep LISTEN

# 如果服務只監聽 127.0.0.1，需要修改配置
# 修改為監聽 0.0.0.0 才能從外部訪問
```

### 方案 4: 檢查防火牆（在伺服器上執行）

```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 8069/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 8766/tcp
sudo ufw reload

# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --add-port=8069/tcp --permanent
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --add-port=8766/tcp --permanent
sudo firewall-cmd --reload

# 檢查 iptables
sudo iptables -L -n | grep 8069
```

### 方案 5: 使用 SSH 連線到伺服器

由於 SSH 端口 (22) 已開啟，可以：

1. **使用正確的用戶名和密碼**
   ```bash
   ssh <username>@192.168.50.249
   ```

2. **使用 SSH 密鑰**
   ```bash
   ssh -i ~/.ssh/id_rsa <username>@192.168.50.249
   ```

3. **部署 SSH 密鑰**（使用現有腳本）
   ```powershell
   .\deploy_ssh_key.py
   # 或
   .\setup_ssh_auto.ps1
   ```

---

## 📋 檢查清單

在伺服器上執行以下檢查：

- [ ] 檢查 Docker 容器是否運行: `docker ps`
- [ ] 檢查服務日誌: `docker logs <container_name>`
- [ ] 檢查端口監聽: `netstat -tlnp | grep <port>`
- [ ] 檢查防火牆狀態: `sudo ufw status`
- [ ] 檢查服務配置: 確認監聽地址為 0.0.0.0
- [ ] 檢查系統資源: `top` 或 `htop`
- [ ] 檢查服務啟動腳本: 確認服務已啟動

---

## 🎯 下一步操作

1. **使用 RDP 連線到伺服器**（端口 3389 已開啟）
   - 使用遠端桌面連線到 192.168.50.249:3389
   - 在伺服器上檢查服務狀態

2. **使用 SSH 連線到伺服器**（需要正確的認證）
   - 確認用戶名和密碼
   - 或部署 SSH 密鑰

3. **檢查服務配置**
   - 確認服務監聽地址
   - 確認服務端口配置
   - 確認防火牆規則

4. **啟動服務**
   - 根據檢查結果啟動相應服務
   - 確認服務正常運行

---

## 📝 診斷結論

**伺服器狀態**: ✅ 正在運行（可以 ping 通）  
**網絡連線**: ✅ 正常（同網段，路由正常）  
**服務狀態**: ❌ 服務端口未開啟（8069, 8080, 8766 等）  
**SSH 狀態**: ⚠️ 端口開啟但認證失敗

**主要問題**: 服務未啟動或監聽地址配置錯誤

**建議**: 使用 RDP 或 SSH 連線到伺服器，檢查並啟動相應服務。
