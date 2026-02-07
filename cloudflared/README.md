# Cloudflare Tunnel 配置目錄

此目錄用於存放 Cloudflare Tunnel 相關配置檔案。

## 檔案說明

### `config.yml`
Cloudflare Tunnel 的主要配置檔案，包含：
- Tunnel 路由規則
- 服務配置
- 安全設定

### `credentials.json`
Tunnel 的認證憑證檔案，用於連接到 Cloudflare。

## 建立方式

1. 在 Cloudflare Dashboard 建立 Tunnel
2. 下載憑證檔案到此目錄
3. 建立或更新 `config.yml`

## 注意事項

- 憑證檔案包含敏感資訊，請妥善保管
- 不要將憑證檔案提交到公開版本控制系統
