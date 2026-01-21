# 伺服器端部署檢查設定指南

**目的：** 在伺服器上設定定時自動檢查部署狀態

---

## 📋 設定步驟

### 步驟 1: 上傳檔案到伺服器

將以下檔案上傳到伺服器：

1. `server_deployment_checker.py` - 檢查腳本
2. `setup_server_scheduled_check.sh` - 設定腳本

**上傳方法：**

**方法 A: 使用 SCP**
```bash
scp server_deployment_checker.py user@server:/path/to/deployment/
scp setup_server_scheduled_check.sh user@server:/path/to/deployment/
```

**方法 B: 使用 Git**
```bash
# 在伺服器上克隆或拉取
git pull
```

**方法 C: 直接編輯**
在伺服器上直接建立檔案

---

### 步驟 2: 設定執行權限

```bash
chmod +x server_deployment_checker.py
chmod +x setup_server_scheduled_check.sh
```

---

### 步驟 3: 安裝依賴套件

```bash
# 安裝 Python 依賴（如果需要）
pip3 install requests psutil
```

---

### 步驟 4: 測試腳本

```bash
python3 server_deployment_checker.py
```

確認腳本可以正常執行並產生報告。

---

### 步驟 5: 設定定時任務

**方法 A: 使用設定腳本（推薦）**

```bash
./setup_server_scheduled_check.sh
```

按照提示選擇檢查頻率。

**方法 B: 手動設定 Cron**

```bash
# 編輯 Cron 任務
crontab -e

# 新增以下行（每 4 小時檢查一次）
0 */4 * * * cd /path/to/deployment && /usr/bin/python3 server_deployment_checker.py >> /path/to/deployment/logs/server_deployment_check_cron.log 2>&1
```

---

## ⏰ Cron 時間格式

### 常用設定

| 說明 | Cron 格式 | 範例 |
|-----|----------|------|
| 每小時 | `0 * * * *` | 每小時的 0 分 |
| 每 2 小時 | `0 */2 * * *` | 每 2 小時的 0 分 |
| 每 4 小時 | `0 */4 * * *` | 每 4 小時的 0 分 |
| 每天 8 點 | `0 8 * * *` | 每天上午 8 點 |
| 每天 2 次 | `0 8,20 * * *` | 每天 8 點和 20 點 |

### Cron 格式說明

```
* * * * *
│ │ │ │ │
│ │ │ │ └── 星期幾 (0-7, 0 和 7 都代表星期日)
│ │ │ └──── 月份 (1-12)
│ │ └────── 日期 (1-31)
│ └──────── 小時 (0-23)
└────────── 分鐘 (0-59)
```

---

## 📊 報告位置

### 本地報告

- **JSON 報告：** `reports/server_deployment_status_latest.json`
- **Markdown 報告：** `reports/server_deployment_status_latest.md`
- **日誌檔案：** `logs/server_deployment_check_YYYYMMDD.log`

### Google Drive 同步

如果伺服器可以訪問 Google Drive，報告會自動同步到：
- `J:/共用雲端硬碟/五常雲端空間/reports/server_deployment/` (Windows)
- `/mnt/gdrive/reports/server_deployment/` (Linux)

---

## 🔍 檢查項目

伺服器檢查腳本會檢查：

1. **容器狀態**
   - 檢查所有容器的運行狀態
   - 識別重啟中的容器
   - 識別已停止的容器

2. **DNS 解析**
   - 檢查所有域名的 DNS 解析
   - 驗證域名是否可以解析

3. **服務訪問**
   - 檢查所有服務的 HTTPS 連接
   - 驗證服務是否可訪問

4. **伺服器資源**
   - CPU 使用率
   - 記憶體使用率
   - 磁碟使用率

---

## 🔧 進階設定

### 自訂檢查項目

編輯 `server_deployment_checker.py`，修改：

```python
# 要檢查的域名
domains = [
    "app.wuchang.org.tw",
    "ai.wuchang.org.tw",
    # 新增其他域名...
]

# 要檢查的服務
services = {
    "app.wuchang.org.tw": "https://app.wuchang.org.tw",
    # 新增其他服務...
}
```

### 設定通知

可以在檢查腳本中加入通知功能：

```python
def send_notification(issues):
    """發送通知"""
    if issues:
        # 發送郵件、簡訊或其他通知
        # 例如：使用 SMTP 發送郵件
        pass
```

---

## 📈 查看報告

### 查看最新報告

```bash
# Markdown 報告
cat reports/server_deployment_status_latest.md

# JSON 報告
cat reports/server_deployment_status_latest.json | jq .

# 查看最近的日誌
tail -f logs/server_deployment_check_$(date +%Y%m%d).log
```

### 查看 Cron 日誌

```bash
tail -f logs/server_deployment_check_cron.log
```

---

## ✅ 驗證設定

### 檢查 Cron 任務

```bash
# 列出所有 Cron 任務
crontab -l

# 應該看到類似：
# 0 */4 * * * cd /path/to/deployment && /usr/bin/python3 server_deployment_checker.py ...
```

### 手動執行測試

```bash
python3 server_deployment_checker.py
```

確認報告正常產生。

### 查看任務歷史

```bash
# 查看 Cron 執行記錄（如果系統有設定）
grep CRON /var/log/syslog | grep server_deployment_checker
```

---

## 🔔 告警設定

### 設定資源閾值

編輯 `server_deployment_checker.py`，修改資源檢查閾值：

```python
# 調整閾值
if resources["cpu_percent"] > 90:  # CPU 使用率超過 90%
if resources["memory_percent"] > 90:  # 記憶體使用率超過 90%
if resources["disk_percent"] > 90:  # 磁碟使用率超過 90%
```

### 整合通知系統

可以整合到：
- 郵件通知（SMTP）
- Slack/Teams 通知
- Telegram 通知
- 簡訊通知（SMS API）

---

## 🛠️ 疑難排解

### 問題 1: Cron 任務未執行

**檢查：**
```bash
# 確認 Cron 服務運行中
systemctl status cron

# 查看 Cron 日誌
grep CRON /var/log/syslog | tail -20
```

**解決方案：**
- 確認 Cron 服務已啟動
- 檢查腳本路徑是否正確
- 檢查 Python 路徑是否正確

### 問題 2: 報告未產生

**檢查：**
```bash
# 檢查目錄權限
ls -la reports/
ls -la logs/

# 檢查腳本執行權限
ls -la server_deployment_checker.py
```

**解決方案：**
- 確保目錄存在且有寫入權限
- 確保腳本有執行權限
- 檢查 Python 執行權限

### 問題 3: Docker 命令無法執行

**檢查：**
```bash
# 測試 Docker 命令
docker ps

# 檢查使用者是否有 Docker 權限
groups
```

**解決方案：**
- 將使用者加入 docker 群組：`sudo usermod -aG docker $USER`
- 或使用 `sudo` 執行（需要修改腳本）

---

## 📝 相關檔案

- `server_deployment_checker.py` - 伺服器檢查腳本
- `setup_server_scheduled_check.sh` - 設定腳本
- `little_j_deployment_checker.py` - 本機檢查腳本（參考）

---

**設定指南產生時間：** 2026-01-20  
**適用環境：** Linux 伺服器
