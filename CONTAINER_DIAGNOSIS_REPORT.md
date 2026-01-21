# 容器診斷報告

## 📋 問題容器資訊

**容器名稱：** `wuchangv510-cloudflared-named-1`  
**狀態：** Restarting（持續重啟）  
**重啟次數：** 466+ 次  
**映像檔：** `cloudflare/cloudflared:latest`

---

## 🔍 問題分析

### 根本原因

1. **缺少 Token 值**
   - 容器命令：`tunnel run --token`
   - 問題：`--token` 參數後面沒有提供 token 值
   - 結果：命令執行失敗，容器立即退出

2. **缺少配置檔案掛載**
   - 沒有掛載 `config.yml` 配置檔案
   - 沒有掛載 `credentials.json` 憑證檔案
   - 容器無法找到必要的配置

3. **重複的容器**
   - 已有另一個 Cloudflare Tunnel 容器運行：`wuchangv510-cloudflared-1`
   - 這個容器可能是測試或重複配置

---

## ✅ 解決方案

### 方案 1：移除容器（推薦）⭐

**原因：**
- 已有另一個正常運行的 cloudflared 容器
- 這個容器配置不完整
- 移除不會影響服務

**執行步驟：**
```bash
# 停止容器
docker stop wuchangv510-cloudflared-named-1

# 移除容器
docker rm wuchangv510-cloudflared-named-1
```

### 方案 2：修復配置（如果需要保留）

**如果確實需要這個容器，需要：**

1. **提供 Token 或配置檔案**
   ```bash
   # 方式 A：使用 Token
   docker run ... cloudflared tunnel run --token YOUR_TOKEN
   
   # 方式 B：使用配置檔案
   docker run ... -v ./cloudflared/config.yml:/etc/cloudflared/config.yml \
                  -v ./cloudflared/credentials.json:/etc/cloudflared/credentials.json \
                  cloudflared tunnel run
   ```

2. **檢查 docker-compose 配置**
   - 確認是否有對應的 docker-compose 檔案
   - 修復配置後重新啟動

---

## 📊 當前 Cloudflare Tunnel 狀態

### 正常運行的容器
- ✅ `wuchangv510-cloudflared-1` - 正常運行

### 異常容器
- ❌ `wuchangv510-cloudflared-named-1` - 持續重啟

**結論：** 只需要保留 `wuchangv510-cloudflared-1`，可以安全移除異常容器。

---

## 🛠️ 自動修復腳本

已建立 `fix_restarting_container.py` 腳本，可以：
- 自動診斷問題
- 提供修復建議
- 自動移除重複容器（如果確認不需要）

---

## 📝 建議操作

**立即執行：**
```bash
# 停止並移除異常容器
docker stop wuchangv510-cloudflared-named-1
docker rm wuchangv510-cloudflared-named-1

# 驗證其他容器正常
docker ps --filter "name=cloudflared"
```

**驗證：**
```bash
# 確認只有一個 cloudflared 容器運行
docker ps | findstr cloudflared

# 應該只看到 wuchangv510-cloudflared-1
```

---

## ✅ 修復後檢查

修復後執行：
```bash
python check_deployment.py
```

應該會顯示：
- ✅ 容器狀態檢查：通過
- ✅ 所有容器正常運行
