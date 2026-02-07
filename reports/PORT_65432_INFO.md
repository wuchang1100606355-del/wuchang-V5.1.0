# 端口 65432 使用情況

## 📊 當前狀態

### 使用情況
- **協議**: UDP
- **綁定地址**: `0.0.0.0:65432`（監聽所有網路介面）
- **進程 ID**: 6092
- **進程名稱**: `MSI.CentralServer.exe`
- **服務類型**: MSI 硬體管理服務

### 相關服務
以下 MSI 相關服務正在運行：
- **MSI Foundation Service** - Running
- **MSI Center Service** - Running
- **MSI_Companion_Service** - Running
- **Sensor dev service** - Running

## 🔍 說明

### MSI.CentralServer 用途
- MSI 硬體管理中央伺服器
- 用於 MSI Dragon Center / MSI Center 等軟體
- 管理 MSI 產品（主機板、顯示卡等）的硬體監控和控制

### 端口衝突處理

如果您的應用程式需要使用端口 65432，有以下選項：

#### 選項 1：停止 MSI 服務（不建議）
```powershell
# 停止 MSI Central Server 進程
Stop-Process -Id 6092 -Force

# 或停止相關服務（可能影響 MSI 軟體功能）
Stop-Service -Name "MSI_Center_Service" -Force
```

**注意**：停止這些服務可能會影響：
- MSI Dragon Center / MSI Center 功能
- 硬體監控（溫度、風扇轉速等）
- RGB 燈效控制
- 效能模式切換

#### 選項 2：使用其他端口（建議）
如果您的應用程式可以配置端口，建議使用其他端口，例如：
- `65433` - 65432 的下一個端口
- `65431` - 65432 的上一個端口
- `50000-65535` 範圍內的其他可用端口

#### 選項 3：檢查端口是否真的需要
- UDP 端口通常用於廣播或發現服務
- 如果只是單向通訊，可能不需要綁定特定端口
- 檢查您的應用程式是否真的需要這個特定端口

## 🔧 檢查可用端口

### PowerShell 命令
```powershell
# 檢查特定端口是否被使用
Get-NetTCPConnection -LocalPort 65432 -ErrorAction SilentlyContinue
Get-NetUDPEndpoint -LocalPort 65432 -ErrorAction SilentlyContinue

# 查找可用端口範圍
$usedPorts = Get-NetTCPConnection | Select-Object -ExpandProperty LocalPort
$availablePorts = 50000..65535 | Where-Object { $usedPorts -notcontains $_ }
$availablePorts | Select-Object -First 10
```

### Python 檢查腳本
```python
import socket

def check_port(port, protocol='TCP'):
    """檢查端口是否可用"""
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM if protocol == 'TCP' else socket.SOCK_DGRAM
    )
    try:
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except OSError:
        return False

# 檢查 65432
if check_port(65432):
    print("端口 65432 可用（TCP）")
else:
    print("端口 65432 已被使用（TCP）")

# 檢查替代端口
for port in [65431, 65433, 65434]:
    if check_port(port):
        print(f"端口 {port} 可用")
        break
```

## 📝 路由器 SSH 端口設定

如果您需要為路由器 SSH 設定端口轉發或使用端口 65432：

### 路由器端口轉發設定
1. 登入路由器管理介面
2. 進入「進階設定」→「NAT 轉發」→「虛擬伺服器」
3. 新增規則：
   - **服務名稱**: SSH (或自訂名稱)
   - **外部端口**: 65432
   - **內部 IP**: 路由器 IP（如 192.168.1.1）
   - **內部端口**: 22 (SSH 預設端口)
   - **協議**: TCP

### SSH 連線使用自訂端口
```powershell
# 使用自訂端口連線到路由器
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_router" -p 65432 admin@220.135.21.74
```

### 更新 SSH Config
在 `~/.ssh/config` 中添加：
```
Host router-custom
    HostName 220.135.21.74
    User admin
    IdentityFile ~/.ssh/id_ed25519_router
    Port 65432
```

## ⚠️ 注意事項

1. **MSI 服務影響**：如果停止 MSI 服務，可能影響硬體管理功能
2. **防火牆設定**：如果使用端口 65432，確保 Windows 防火牆允許該端口
3. **路由器設定**：如果要在路由器上使用，需要設定端口轉發規則
4. **安全性**：使用非標準端口可以增加安全性（安全透過隱蔽性）

## 📅 記錄時間
2026-01-22
