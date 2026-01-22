# 使用 Docker 執行 Cloudflare Tunnel 設定

**原因：** 不需要在系統上安裝 cloudflared，直接使用 Docker 容器執行所有命令

---

## 🐳 為什麼使用 Docker？

- ✅ **不需要安裝 cloudflared**
- ✅ **已確認 Docker 可用**
- ✅ **所有容器統一管理**
- ✅ **避免環境配置問題**

---

## 📋 使用 Docker 執行 Cloudflare 命令

### 基本語法

所有 `cloudflared` 命令都可以用 Docker 執行：

**原本的命令：**
```powershell
cloudflared tunnel login
```

**使用 Docker：**
```powershell
docker run --rm -it `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel login
```

---

## 🚀 快速設定（使用自動化腳本）

### 方法 1: 使用自動化腳本（推薦）

```powershell
.\setup_dns_with_docker.ps1
```

這個腳本會自動：
1. 登入 Cloudflare
2. 建立隧道
3. 配置 DNS 路由
4. 複製憑證檔案
5. 更新配置檔案
6. 重啟容器

---

## 📝 手動執行步驟（使用 Docker）

### 步驟 1: 登入 Cloudflare

```powershell
docker run --rm -it `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel login
```

**說明：**
- 會開啟瀏覽器讓您登入
- 選擇網域：**wuchang.org.tw**
- 憑證會儲存在 `%USERPROFILE%\.cloudflared`

---

### 步驟 2: 建立命名隧道

```powershell
docker run --rm -it `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel create wuchang-tunnel
```

**重要：** 記下產生的 **Tunnel ID**！

---

### 步驟 3: 列出隧道（確認 ID）

```powershell
docker run --rm `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel list
```

---

### 步驟 4: 配置 DNS 路由

```powershell
# Odoo ERP 系統
docker run --rm `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel app.wuchang.org.tw

# Open WebUI
docker run --rm `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel ai.wuchang.org.tw

# Portainer
docker run --rm `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel admin.wuchang.org.tw

# Uptime Kuma
docker run --rm `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel monitor.wuchang.org.tw
```

**驗證 DNS 路由：**
```powershell
docker run --rm `
    -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" `
    cloudflare/cloudflared:latest tunnel route dns list
```

---

### 步驟 5: 複製憑證檔案

```powershell
# 替換 <tunnel-id> 為步驟 2 記下的實際 ID
Copy-Item "${env:USERPROFILE}\.cloudflared\<tunnel-id>.json" "cloudflared\credentials.json"
```

---

### 步驟 6: 更新配置檔案

編輯 `cloudflared/config.yml`，將 `<tunnel-id>` 替換為實際 ID。

**或使用 PowerShell：**
```powershell
# 替換 <實際-tunnel-id> 為步驟 2 的 ID
(Get-Content cloudflared\config.yml -Encoding UTF8) -replace '<tunnel-id>', '<實際-tunnel-id>' | Set-Content cloudflared\config.yml -Encoding UTF8
```

---

### 步驟 7: 重啟容器

```powershell
docker restart wuchangv510-cloudflared-1
```

**查看日誌：**
```powershell
docker logs wuchangv510-cloudflared-1 --tail 20
```

---

## 🔧 常用 Docker 命令對照表

| 原本命令 | Docker 命令 |
|---------|------------|
| `cloudflared --version` | `docker run --rm cloudflare/cloudflared:latest --version` |
| `cloudflared tunnel login` | `docker run --rm -it -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" cloudflare/cloudflared:latest tunnel login` |
| `cloudflared tunnel list` | `docker run --rm -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" cloudflare/cloudflared:latest tunnel list` |
| `cloudflared tunnel create wuchang-tunnel` | `docker run --rm -it -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" cloudflare/cloudflared:latest tunnel create wuchang-tunnel` |
| `cloudflared tunnel route dns list` | `docker run --rm -v "${env:USERPROFILE}\.cloudflared:/home/nonroot/.cloudflared" cloudflare/cloudflared:latest tunnel route dns list` |

---

## ⚠️ 注意事項

1. **憑證檔案位置**
   - Docker 容器中的路徑：`/home/nonroot/.cloudflared`
   - 映射到主機：`%USERPROFILE%\.cloudflared`

2. **互動式命令**
   - 需要 `-it` 參數（例如：`tunnel login`、`tunnel create`）
   - 非互動式命令不需要 `-it`（例如：`tunnel list`）

3. **臨時容器**
   - 使用 `--rm` 參數，命令執行完後自動刪除容器
   - 不會留下殘留容器

---

## ✅ 優勢

使用 Docker 執行 Cloudflare 命令的優勢：

1. ✅ **不需要安裝額外軟體**
2. ✅ **統一使用 Docker 管理**
3. ✅ **避免版本衝突**
4. ✅ **環境一致性**
5. ✅ **易於維護和更新**

---

**建議：** 使用 `setup_dns_with_docker.ps1` 自動化腳本，會自動處理所有步驟！
