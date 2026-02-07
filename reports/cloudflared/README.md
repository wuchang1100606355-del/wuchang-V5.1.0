# Cloudflare Tunnel 設定說明

## 步驟 1：安裝 cloudflared

### Windows
下載並安裝：https://github.com/cloudflare/cloudflared/releases

### 或使用 Docker
```bash
docker pull cloudflare/cloudflared:latest
```

## 步驟 2：登入 Cloudflare

```bash
cloudflared tunnel login
```

這會開啟瀏覽器，讓您登入 Cloudflare 並授權。

## 步驟 3：建立隧道

```bash
cloudflared tunnel create wuchang-tunnel
```

## 步驟 4：配置 DNS

```bash
cloudflared tunnel route dns wuchang-tunnel app.wuchang.org.tw
```

## 步驟 5：複製憑證

憑證檔案位置：
- Windows: `%USERPROFILE%\.cloudflared\<tunnel-id>.json`
- Linux/Mac: `~/.cloudflared/<tunnel-id>.json`

複製到：`cloudflared/credentials.json`

## 步驟 6：更新配置

編輯 `config.yml`，將 `<tunnel-id>` 替換為實際的隧道 ID。

## 步驟 7：啟動服務

```bash
docker-compose -f docker-compose.cloud.yml up -d
```
