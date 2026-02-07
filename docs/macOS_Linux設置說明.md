# macOS/Linux 設置說明

## 概述

本說明適用於在 macOS 或 Linux 系統上設置全自動合規和證書檢查系統。

**合規要求**：符合 Google 非營利組織合規要求

## 系統要求

### macOS
- macOS 10.14 或更高版本
- Python 3.7 或更高版本
- PowerShell Core 7.0+（可選，用於腳本管理）

### Linux
- 支持 systemd 的 Linux 發行版
- Python 3.7 或更高版本
- sudo 權限（用於創建 systemd 服務）

## 安裝步驟

### 1. 安裝必要套件

```bash
# 安裝 Python 套件
pip3 install dnspython requests urllib3

# 或使用 requirements.txt
pip3 install -r requirements.txt
```

### 2. 設置定時任務

#### macOS（使用 launchd）

```bash
cd "路徑/到/wuchang V5.1.0/scripts"
chmod +x setup_auto_compliance_task_macos.sh
./setup_auto_compliance_task_macos.sh
```

腳本會自動：
- 檢查 Python 環境
- 安裝必要套件
- 創建 LaunchAgent plist 文件
- 加載定時任務

#### Linux（使用 systemd）

```bash
cd "路徑/到/wuchang V5.1.0/scripts"
chmod +x setup_auto_compliance_task_macos.sh
sudo ./setup_auto_compliance_task_macos.sh
```

腳本會自動：
- 檢查 Python 環境
- 安裝必要套件
- 創建 systemd 服務和定時器
- 啟用並啟動定時器

### 3. 測試執行

```bash
cd "路徑/到/wuchang V5.1.0"
python3 scripts/auto_compliance_certificate_check.py
```

## 任務管理

### macOS (launchd)

#### 查看任務狀態

```bash
launchctl list com.wuchang.autocompliancecheck
```

#### 卸載任務

```bash
launchctl unload ~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist
```

#### 重新加載任務

```bash
launchctl unload ~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist
launchctl load ~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist
```

#### 查看日誌

```bash
# 標準輸出
tail -f logs/compliance_check_stdout.log

# 標準錯誤
tail -f logs/compliance_check_stderr.log
```

### Linux (systemd)

#### 查看定時器狀態

```bash
sudo systemctl status wuchang-autocompliancecheck.timer
```

#### 查看服務狀態

```bash
sudo systemctl status wuchang-autocompliancecheck.service
```

#### 停止定時器

```bash
sudo systemctl stop wuchang-autocompliancecheck.timer
```

#### 啟用定時器

```bash
sudo systemctl enable wuchang-autocompliancecheck.timer
sudo systemctl start wuchang-autocompliancecheck.timer
```

#### 查看日誌

```bash
# 使用 journalctl
sudo journalctl -u wuchang-autocompliancecheck.service -f

# 或查看日誌文件
tail -f logs/compliance_check_stdout.log
tail -f logs/compliance_check_stderr.log
```

## 配置文件位置

### macOS

- **LaunchAgent plist**: `~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist`
- **日誌文件**: `logs/compliance_check_*.log`
- **檢查報告**: `logs/compliance_cert_check_*.json`

### Linux

- **服務文件**: `/etc/systemd/system/wuchang-autocompliancecheck.service`
- **定時器文件**: `/etc/systemd/system/wuchang-autocompliancecheck.timer`
- **日誌文件**: `logs/compliance_check_*.log` 和 `journalctl`
- **檢查報告**: `logs/compliance_cert_check_*.json`

## 修改執行頻率

### macOS

編輯 plist 文件：

```bash
nano ~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist
```

修改 `StartInterval` 值（秒數）：
- 每小時：`3600`
- 每 30 分鐘：`1800`
- 每 15 分鐘：`900`

然後重新加載：

```bash
launchctl unload ~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist
launchctl load ~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist
```

### Linux

編輯定時器文件：

```bash
sudo nano /etc/systemd/system/wuchang-autocompliancecheck.timer
```

修改 `OnCalendar` 值：
- 每小時：`OnCalendar=hourly`
- 每 30 分鐘：`OnCalendar=*:0/30:00`
- 每 15 分鐘：`OnCalendar=*:0/15:00`

然後重新加載：

```bash
sudo systemctl daemon-reload
sudo systemctl restart wuchang-autocompliancecheck.timer
```

## 故障排除

### 問題：任務不執行

#### macOS

1. 檢查任務是否加載：
   ```bash
   launchctl list | grep wuchang
   ```

2. 檢查 plist 文件語法：
   ```bash
   plutil -lint ~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist
   ```

3. 查看系統日誌：
   ```bash
   log show --predicate 'process == "launchd"' --last 1h | grep wuchang
   ```

#### Linux

1. 檢查定時器狀態：
   ```bash
   sudo systemctl status wuchang-autocompliancecheck.timer
   ```

2. 檢查服務狀態：
   ```bash
   sudo systemctl status wuchang-autocompliancecheck.service
   ```

3. 查看日誌：
   ```bash
   sudo journalctl -u wuchang-autocompliancecheck.service -n 50
   ```

### 問題：Python 路徑錯誤

確保 plist 或服務文件中使用正確的 Python 路徑：

```bash
which python3
```

然後更新配置文件中的路徑。

### 問題：權限問題

#### macOS

確保腳本有執行權限：
```bash
chmod +x scripts/auto_compliance_certificate_check.py
chmod +x scripts/setup_auto_compliance_task_macos.sh
```

#### Linux

確保使用 sudo 創建 systemd 服務：
```bash
sudo ./setup_auto_compliance_task_macos.sh
```

## 手動設置（不使用腳本）

### macOS

創建 `~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.wuchang.autocompliancecheck</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/路徑/到/scripts/auto_compliance_certificate_check.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/路徑/到/wuchang V5.1.0</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/路徑/到/logs/compliance_check_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/路徑/到/logs/compliance_check_stderr.log</string>
</dict>
</plist>
```

然後加載：
```bash
launchctl load ~/Library/LaunchAgents/com.wuchang.autocompliancecheck.plist
```

### Linux

創建 `/etc/systemd/system/wuchang-autocompliancecheck.service`：

```ini
[Unit]
Description=Wuchang Auto Compliance and Certificate Check
After=network.target

[Service]
Type=oneshot
User=你的用戶名
WorkingDirectory=/路徑/到/wuchang V5.1.0
ExecStart=/usr/bin/python3 /路徑/到/scripts/auto_compliance_certificate_check.py
StandardOutput=append:/路徑/到/logs/compliance_check_stdout.log
StandardError=append:/路徑/到/logs/compliance_check_stderr.log
```

創建 `/etc/systemd/system/wuchang-autocompliancecheck.timer`：

```ini
[Unit]
Description=Run Wuchang Compliance Check Hourly
Requires=wuchang-autocompliancecheck.service

[Timer]
OnCalendar=hourly
OnBootSec=1h
Persistent=true

[Install]
WantedBy=timers.target
```

然後啟用：
```bash
sudo systemctl daemon-reload
sudo systemctl enable wuchang-autocompliancecheck.timer
sudo systemctl start wuchang-autocompliancecheck.timer
```

## 合規聲明

✅ **符合 Google 非營利組織合規要求**

- 所有操作均以合規為最高要件
- 僅用於非營利目的
- 保護系統穩定性和安全性
- 記錄所有操作以備審計

---

**創建時間**：2026-01-11  
**版本**：1.0.0  
**適用系統**：macOS, Linux
