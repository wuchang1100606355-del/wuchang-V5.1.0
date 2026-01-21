# 路由器 SSH 金鑰設定指南

## 📋 SSH 金鑰資訊

### 金鑰位置
- **私鑰**: `C:\Users\o0930\.ssh\id_ed25519_router`
- **公鑰**: `C:\Users\o0930\.ssh\id_ed25519_router.pub`
- **專案備份**: `certs\ssh\router_public_key.pub`

### 公鑰內容
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIO8c7tZLL0OsCwa0L1CWhACnGWpTpYthAEHJBusLUImi wuchang-router-ssh-20260122
```

## 🔧 設定步驟

### 1. 將公鑰添加到路由器

#### 方法一：通過路由器 Web 介面
1. 登入路由器管理介面（通常是 `https://192.168.1.1` 或 `https://coffeeLofe.asuscomm.com:8443`）
2. 進入「系統管理」→「系統設定」→「SSH 服務」
3. 找到「授權金鑰」或「Authorized Keys」選項
4. 複製以下公鑰內容並貼上：
   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIO8c7tZLL0OsCwa0L1CWhACnGWpTpYthAEHJBusLUImi wuchang-router-ssh-20260122
   ```
5. 儲存設定

#### 方法二：通過 SSH 命令（如果已能登入）
```bash
# 連接到路由器（使用現有密碼）
ssh admin@192.168.1.1

# 在路由器上執行（將公鑰添加到授權列表）
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIO8c7tZLL0OsCwa0L1CWhACnGWpTpYthAEHJBusLUImi wuchang-router-ssh-20260122" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 2. 測試 SSH 連線

#### Windows PowerShell
```powershell
# 使用指定私鑰連線
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_router" admin@192.168.1.1

# 或使用路由器 IP/域名
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_router" admin@220.135.21.74
```

#### 設定 SSH Config（選用）
在 `C:\Users\o0930\.ssh\config` 檔案中添加：
```
Host router
    HostName 192.168.1.1
    User admin
    IdentityFile ~/.ssh/id_ed25519_router
    Port 22

Host router-external
    HostName 220.135.21.74
    User admin
    IdentityFile ~/.ssh/id_ed25519_router
    Port 22
```

設定後可直接使用：
```powershell
ssh router
# 或
ssh router-external
```

## 🔒 安全注意事項

1. **私鑰保護**
   - 私鑰檔案 (`id_ed25519_router`) 必須保密，不要分享給他人
   - 建議設定適當的檔案權限（Windows 會自動處理）

2. **公鑰分享**
   - 只有公鑰 (`id_ed25519_router.pub`) 可以安全地分享
   - 公鑰可以添加到多個伺服器/路由器

3. **備份**
   - 私鑰已備份在專案目錄：`certs\ssh\router_public_key.pub`（僅公鑰）
   - 建議將私鑰備份到安全位置（加密儲存）

## 📝 使用範例

### Python 腳本中使用
```python
import subprocess
import os

# SSH 連線命令
ssh_key = os.path.expanduser("~/.ssh/id_ed25519_router")
router_host = "192.168.1.1"
router_user = "admin"

# 執行 SSH 命令
cmd = f'ssh -i "{ssh_key}" {router_user}@{router_host} "ls -la"'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
```

### 使用 paramiko 庫（Python）
```python
import paramiko
import os

# 載入私鑰
private_key_path = os.path.expanduser("~/.ssh/id_ed25519_router")
private_key = paramiko.Ed25519Key.from_private_key_file(private_key_path)

# 建立 SSH 連線
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname="192.168.1.1",
    username="admin",
    pkey=private_key
)

# 執行命令
stdin, stdout, stderr = ssh.exec_command("ls -la")
print(stdout.read().decode())
ssh.close()
```

## 🛠️ 故障排除

### 問題：連線被拒絕
- 確認路由器已啟用 SSH 服務
- 檢查路由器防火牆設定
- 確認 SSH 端口（預設為 22）未被阻擋

### 問題：權限被拒絕
- 確認公鑰已正確添加到路由器的 `authorized_keys`
- 檢查路由器上的 `.ssh` 目錄權限（應為 700）
- 檢查 `authorized_keys` 檔案權限（應為 600）

### 問題：找不到私鑰
- 確認私鑰路徑正確：`C:\Users\o0930\.ssh\id_ed25519_router`
- 使用 `-i` 參數明確指定私鑰路徑

## 📅 建立日期
2026-01-22

## 🔑 金鑰指紋
SHA256:xoCJKyN6USToRwIN6EV3Yrie46jdILDUNtulxIjBQ+Y
