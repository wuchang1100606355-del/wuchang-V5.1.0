# 未運行容器排查報告

**排查時間：** 2026-01-21  
**排查者：** little_j (小J)  
**權限等級：** 🔐 最高權限

---

## 🔍 問題診斷

### 未運行的容器

| 容器名稱 | 狀態 | 錯誤類型 |
|---------|------|---------|
| wuchang-caddy-1 | Created | 配置錯誤 |
| wuchang-cloudflared-1 | Created | 依賴問題 |

---

## ❌ 問題分析

### 1. Caddy 容器問題

**錯誤訊息：**
```
error mounting "/run/desktop/mnt/host/g/共用雲端硬碟/五常雲端空間/wuchang_os/Caddyfile" 
to rootfs at "/etc/caddy/Caddyfile": 
not a directory: Are you trying to mount a directory onto a file (or vice-versa)? 
Check if the specified host path exists and is the expected type
```

**根本原因：**
- Caddyfile 路徑掛載失敗
- 可能是檔案不存在或是路徑錯誤
- 或檔案存在但類型不匹配（目錄 vs 檔案）

**退出碼：** 127

**影響：**
- Caddy 容器無法啟動
- HTTP/HTTPS 反向代理服務不可用
- 外部訪問功能受影響

### 2. Cloudflare 容器問題

**狀態：** Created（已建立但未啟動）

**根本原因：**
- Cloudflare 容器依賴於 Caddy 容器
- 由於 Caddy 容器啟動失敗，Cloudflare 容器也無法正常啟動
- 配置中 `depends_on: - caddy` 使得 Cloudflare 等待 Caddy

**影響：**
- Cloudflare Tunnel 服務不可用
- 外網訪問功能不可用

---

## 🔧 解決方案

### 方案 1: 檢查並修復 Caddyfile 路徑

**步驟：**
1. 檢查 `wuchang_os/Caddyfile` 是否存在
2. 確認檔案類型正確（是檔案而非目錄）
3. 如果不存在，創建或從備份恢復
4. 確認其他掛載檔案存在：
   - `wuchang_os/command_center`
   - `control_center.html`
   - `wuchang_os/command_center_design_report.html`

### 方案 2: 修改 Docker Compose 配置

**選項 A：暫時移除 Caddyfile 掛載（測試用）**
```yaml
caddy:
  volumes:
    # - ./wuchang_os/Caddyfile:/etc/caddy/Caddyfile:ro  # 暫時註解
    - caddy-data:/data
```

**選項 B：創建最小 Caddyfile**
如果檔案不存在，創建一個基本的 Caddyfile：
```
localhost:80 {
    reverse_proxy wuchang-web:8069
}
```

### 方案 3: 分步啟動

1. 先修復並啟動 Caddy 容器
2. 確認 Caddy 運行正常
3. 再啟動 Cloudflare 容器

---

## 📋 檢查清單

### 需要檢查的檔案

- [ ] `wuchang_os/Caddyfile` - 必須是檔案，不是目錄
- [ ] `wuchang_os/command_center` - 檢查是否存在
- [ ] `control_center.html` - 檢查是否存在
- [ ] `wuchang_os/command_center_design_report.html` - 檢查是否存在

### 需要檢查的配置

- [ ] Docker Compose 配置中的路徑是否正確
- [ ] 檔案權限是否正確
- [ ] 掛載點配置是否正確

---

## 🛠️ 修復步驟

### 步驟 1: 檢查檔案
```bash
# 檢查 Caddyfile 是否存在
ls -la wuchang_os/Caddyfile

# 檢查其他掛載檔案
ls -la wuchang_os/command_center
ls -la control_center.html
```

### 步驟 2: 修復 Caddyfile
如果檔案不存在，創建基本配置：
```bash
# 創建 Caddyfile
cat > wuchang_os/Caddyfile << 'EOF'
localhost:80 {
    reverse_proxy wuchang-web:8069
}
EOF
```

### 步驟 3: 重新啟動容器
```bash
# 停止並移除舊容器
docker-compose -f docker-compose.unified.yml stop caddy cloudflared
docker-compose -f docker-compose.unified.yml rm -f caddy cloudflared

# 重新啟動
docker-compose -f docker-compose.unified.yml --profile system up -d caddy
docker-compose -f docker-compose.unified.yml --profile system up -d cloudflared
```

### 步驟 4: 驗證
```bash
# 檢查容器狀態
docker ps | grep -E "caddy|cloudflared"

# 檢查日誌
docker logs wuchang-caddy-1
docker logs wuchang-cloudflared-1
```

---

## ✅ 預期結果

修復後應該看到：
- ✅ Caddy 容器狀態：Up
- ✅ Cloudflare 容器狀態：Up
- ✅ HTTP/HTTPS 服務可用
- ✅ 外部訪問功能正常

---

## 📝 後續建議

1. **備份配置檔案**
   - 定期備份 Caddyfile
   - 備份其他重要的配置檔案

2. **監控容器狀態**
   - 定期檢查容器運行狀態
   - 設置告警機制

3. **改進配置管理**
   - 使用配置驗證腳本
   - 在啟動前檢查必要檔案

---

**排查完成時間：** 2026-01-21  
**狀態：** ⚠️ 需要修復  
**優先級：** 高（影響外部訪問功能）
