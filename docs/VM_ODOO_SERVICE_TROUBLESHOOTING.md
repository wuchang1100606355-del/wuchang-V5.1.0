# VM Odoo 服務無法訪問問題排查

**問題**: 無法訪問 VM 伺服器 (192.168.50.84) 的 Odoo 服務

---

## 🔍 診斷結果

根據連線測試：
- ❌ VM 伺服器 (192.168.50.84) 無法連線（ping 失敗）
- ❌ Odoo 服務端口 (8069) 無法訪問
- ✅ 本機在相同網段 (192.168.50.249)
- ✅ 路由表正常

---

## 🎯 可能原因與解決方案

### 原因 1: VM 伺服器未啟動

**檢查方式**:
```powershell
# 檢查 VM 是否運行
ping 192.168.50.84
```

**解決方案**:
1. 登入 VM 主機
2. 確認 VM 已啟動
3. 檢查 VM 網路設定

---

### 原因 2: Odoo 服務未在 VM 上啟動

**檢查方式** (在 VM 上執行):
```bash
# 檢查 Docker 容器狀態
docker ps

# 檢查 Odoo 服務日誌
docker logs wuchang-web

# 檢查端口監聽
netstat -tlnp | grep 8069
```

**解決方案** (在 VM 上執行):
```bash
# 啟動 Odoo 服務
cd /path/to/wuchang/project
docker-compose --profile system up -d

# 或使用啟動腳本
./scripts/startup_compose.sh system
```

---

### 原因 3: 防火牆阻擋

**檢查方式** (在 VM 上執行):
```bash
# Linux (Ubuntu/Debian)
sudo ufw status
sudo iptables -L -n | grep 8069

# 檢查防火牆規則
sudo firewall-cmd --list-all  # CentOS/RHEL
```

**解決方案** (在 VM 上執行):
```bash
# 開放端口 8069
sudo ufw allow 8069/tcp
sudo ufw reload

# 或使用 iptables
sudo iptables -A INPUT -p tcp --dport 8069 -j ACCEPT
```

---

### 原因 4: 網路設定問題

**檢查方式**:
```powershell
# 檢查 VM IP 設定
# 在 VM 上執行
ip addr show
# 或
ifconfig
```

**解決方案**:
1. 確認 VM IP 為 `192.168.50.84`
2. 確認子網路遮罩為 `255.255.255.0` (或 `/24`)
3. 確認閘道為 `192.168.50.1`
4. 確認 DNS 設定正確

---

### 原因 5: Docker 網路問題

**檢查方式** (在 VM 上執行):
```bash
# 檢查 Docker 網路
docker network ls
docker network inspect bridge

# 檢查容器網路設定
docker inspect wuchang-web | grep -A 20 NetworkSettings
```

**解決方案**:
```bash
# 重啟 Docker 服務
sudo systemctl restart docker

# 重啟 Odoo 容器
docker-compose restart wuchang-web
```

---

## 🚀 快速修復步驟

### Step 1: 確認 VM 運行

```powershell
# 在本機執行
ping 192.168.50.84
```

如果無法 ping 通，請：
1. 檢查 VM 主機是否開機
2. 檢查 VM 網路設定
3. 檢查路由器設定

---

### Step 2: 在 VM 上啟動 Odoo 服務

```bash
# SSH 到 VM
ssh user@192.168.50.84

# 進入專案目錄
cd /path/to/wuchang/project

# 啟動服務
docker-compose --profile system up -d

# 檢查服務狀態
docker ps
docker logs wuchang-web
```

---

### Step 3: 驗證服務可訪問

```powershell
# 在本機執行
Test-NetConnection -ComputerName 192.168.50.84 -Port 8069

# 或使用瀏覽器訪問
# http://192.168.50.84:8069
```

---

## 📋 檢查清單

- [ ] VM 伺服器已啟動
- [ ] VM IP 設定正確 (192.168.50.84)
- [ ] Docker 服務正在運行
- [ ] Odoo 容器正在運行
- [ ] 端口 8069 已開放
- [ ] 防火牆規則正確
- [ ] 網路連線正常

---

## 💡 替代方案

如果 VM 上的 Odoo 服務暫時無法啟動，可以：

1. **使用本機 Odoo 服務** (如果已運行):
   - 訪問: `http://localhost:8069`
   - 在 Odoo UI 中手動納管設備

2. **使用 SQL 直接納管**:
   - 在 Odoo 中執行 SQL 腳本
   - 見 `scripts/enroll_v3_mix_edla_gl_sql.sql`

3. **等待 VM 服務恢復後再納管**:
   - 使用 API 納管腳本
   - 見 `scripts/enroll_v3_mix_edla_gl.ps1`

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
