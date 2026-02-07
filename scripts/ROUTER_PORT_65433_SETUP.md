# 路由器 SSH 端口 65433 設定指南

## 📊 端口狀態

### 端口 65433 檢查結果
- **UDP 65433**: 被 MSI.CentralServer 使用（進程 6092）
- **TCP 65433**: ✅ 可用（未發現 TCP 連線）

### 說明
- UDP 和 TCP 是獨立的協議，可以同時使用相同端口號
- SSH 使用 TCP 協議，所以 65433 可以用於 SSH
- MSI 服務只使用 UDP，不會與 SSH 衝突

## 🔧 設定步驟

### 1. 路由器端口轉發設定

#### 步驟
1. 登入路由器管理介面
   - 本地：`https://192.168.1.1`
   - 遠端：`https://coffeeLofe.asuscomm.com:8443`

2. 進入端口轉發設定
   - 路徑：**進階設定** → **NAT 轉發** → **虛擬伺服器**

3. 新增端口轉發規則
   - **服務名稱**: `SSH-65433`（或自訂名稱）
   - **外部端口**: `65433`
   - **內部 IP**: `192.168.1.1`（路由器本身）或目標設備 IP
   - **內部端口**: `22`（SSH 預設端口）
   - **協議**: `TCP`
   - **啟用**: ✅ 是

4. 儲存設定

### 2. 本機 SSH Config 設定

SSH Config 已自動更新，包含以下設定：

```
Host router-65433
    HostName 220.135.21.74
    User admin
    IdentityFile ~/.ssh/id_ed25519_router
    Port 65433
```

### 3. 測試連線

#### 方法一：使用 SSH Config 別名
```powershell
ssh router-65433
```

#### 方法二：直接指定端口
```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_router" -p 65433 admin@220.135.21.74
```

#### 方法三：使用本地 IP
```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_router" -p 65433 admin@192.168.50.84
```

## 🔒 安全優勢

使用非標準端口（65433）的優點：
1. **降低掃描風險**：大多數自動掃描工具只檢查常見端口（22, 2222 等）
2. **隱蔽性**：非標準端口不易被發現
3. **減少攻擊面**：減少針對標準 SSH 端口的自動化攻擊

## 📝 完整 SSH Config 內容

```
Host router
    HostName 192.168.50.84
    User admin
    IdentityFile ~/.ssh/id_ed25519_router
    Port 22

Host router-external
    HostName 220.135.21.74
    User admin
    IdentityFile ~/.ssh/id_ed25519_router
    Port 22

Host router-65433
    HostName 220.135.21.74
    User admin
    IdentityFile ~/.ssh/id_ed25519_router
    Port 65433
```

## ⚠️ 注意事項

1. **防火牆設定**
   - 確保路由器防火牆允許端口 65433 的 TCP 連線
   - 如果使用 Windows 防火牆，確保允許 SSH 客戶端連線

2. **端口衝突**
   - UDP 65433 被 MSI 服務使用，但不影響 TCP SSH 連線
   - 如果未來需要 TCP 65433，可以考慮其他端口

3. **備用方案**
   - 如果 65433 不可用，可以使用其他端口（如 65434, 65435）
   - 標準 SSH 端口 22 仍然可用

## 🔍 故障排除

### 問題：連線被拒絕
- 檢查路由器端口轉發設定是否正確
- 確認路由器 SSH 服務已啟用
- 檢查防火牆規則

### 問題：連接超時
- 確認外部 IP 地址正確（220.135.21.74）
- 檢查網路連線
- 確認路由器 DDNS 設定正確

### 問題：權限被拒絕
- 確認 SSH 公鑰已正確添加到路由器
- 檢查 `authorized_keys` 檔案權限
- 確認使用者名稱正確（通常是 `admin`）

## 📅 設定日期
2026-01-22

## 🔑 相關檔案
- SSH 私鑰：`~/.ssh/id_ed25519_router`
- SSH 公鑰：`~/.ssh/id_ed25519_router.pub`
- SSH Config：`~/.ssh/config`
- 設定指南：`ROUTER_SSH_SETUP.md`
