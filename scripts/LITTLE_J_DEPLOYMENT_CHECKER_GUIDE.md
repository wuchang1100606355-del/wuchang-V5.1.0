# 小 J 定時檢查部署狀態指南

**目的：** 自動定時檢查系統部署狀態，確保商家和居民可以穩定訪問服務

---

## 📋 功能說明

### 檢查項目

小 J 會自動檢查以下項目：

1. **容器狀態**
   - 檢查所有容器的運行狀態
   - 識別重啟中的容器
   - 識別已停止的容器

2. **DNS 解析**
   - 檢查所有域名的 DNS 解析
   - 驗證域名是否可以解析到正確的 IP

3. **服務訪問**
   - 檢查所有服務是否可以訪問
   - 驗證 HTTPS 連接是否正常

4. **問題報告**
   - 自動識別問題並產生報告
   - 分類問題嚴重程度

---

## 🚀 快速設定

### 方法 1: 使用自動化腳本（推薦）

```powershell
.\setup_scheduled_deployment_check.ps1
```

這會自動：
1. 檢查 Python 環境
2. 設定 Windows 工作排程器任務
3. 設定檢查頻率

### 方法 2: 手動設定

#### 步驟 1: 測試檢查腳本

```powershell
python little_j_deployment_checker.py
```

確認腳本可以正常執行。

#### 步驟 2: 建立定時任務

使用 Windows 工作排程器建立任務：

1. 開啟 `taskschd.msc`
2. 建立基本任務
3. 設定觸發器（例如：每 4 小時）
4. 設定動作：執行 `python little_j_deployment_checker.py`
5. 完成

---

## ⏰ 建議檢查頻率

### 生產環境（推薦）

- **每 4 小時檢查一次**
  - 平衡檢查頻率和系統負載
  - 及時發現問題

- **每天檢查一次（上午 8 點）**
  - 低系統負載
  - 適合非關鍵系統

### 關鍵環境

- **每小時檢查一次**
  - 更及時發現問題
  - 適合關鍵業務系統

---

## 📊 報告格式

### 報告位置

- **JSON 報告：** `reports/deployment_status_latest.json`
- **Markdown 報告：** `reports/deployment_status_latest.md`
- **日誌檔案：** `logs/deployment_check_YYYYMMDD.log`

### 報告內容

```markdown
# 部署狀態報告

**檢查時間：** 2026-01-20 10:30:00
**健康分數：** 95%

---

## 📊 執行摘要

- **總容器數：** 9
- **運行中：** 9 ✅
- **重啟中：** 0 ⚠️
- **DNS 解析成功：** 4/4
- **服務可訪問：** 4/4

---

## 🔍 容器狀態

- ✅ **wuchangv510-wuchang-web-1**: Up 2 hours
- ✅ **wuchangv510-db-1**: Up 2 hours
...

---

## ⚠️ 發現的問題

- ❌ **container_restarting**: 容器 xxx 正在重啟
...
```

---

## 🔧 進階設定

### 自訂檢查項目

編輯 `little_j_deployment_checker.py`，修改：

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

### 自訂通知

可以在檢查腳本中加入通知功能：

```python
def send_notification(issues):
    """發送通知"""
    if issues:
        # 發送郵件、簡訊或其他通知
        pass
```

---

## 📈 監控儀表板

### 查看最新報告

```powershell
# 查看 Markdown 報告
cat reports\deployment_status_latest.md

# 查看 JSON 報告
cat reports\deployment_status_latest.json | ConvertFrom-Json | ConvertTo-Json
```

### 查看日誌

```powershell
# 查看今天的日誌
cat logs\deployment_check_$(Get-Date -Format 'yyyyMMdd').log

# 查看最近的日誌
Get-Content logs\deployment_check_*.log | Select-Object -Last 50
```

---

## 🔔 告警建議

### 設定告警規則

當健康分數低於閾值時自動通知：

1. **嚴重問題（健康分數 < 50%）**
   - 立即通知管理員
   - 發送郵件或簡訊

2. **警告問題（健康分數 < 80%）**
   - 記錄到日誌
   - 可選：發送通知

3. **一般問題（健康分數 < 95%）**
   - 記錄到日誌
   - 在報告中標記

---

## ✅ 檢查清單

設定完成後，確認：

- [ ] 檢查腳本可以正常執行
- [ ] 定時任務已建立
- [ ] 報告目錄存在（`reports/`）
- [ ] 日誌目錄存在（`logs/`）
- [ ] 檢查頻率設定合理
- [ ] 通知機制已設定（如果需要）

---

## 🛠️ 疑難排解

### 問題 1: 任務未執行

**檢查：**
1. 開啟 `taskschd.msc`
2. 查看任務狀態
3. 查看任務歷史記錄

**解決方案：**
- 確認任務已啟用
- 檢查任務的執行帳號權限
- 確認 Python 路徑正確

### 問題 2: 報告未產生

**檢查：**
```powershell
# 檢查目錄權限
Test-Path reports
Test-Path logs
```

**解決方案：**
- 確保目錄存在且有寫入權限
- 檢查 Python 執行權限

### 問題 3: 檢查時間過長

**優化建議：**
- 減少檢查的域名數量
- 減少檢查的服務數量
- 調整超時時間

---

## 📝 相關檔案

- `little_j_deployment_checker.py` - 檢查腳本
- `setup_scheduled_deployment_check.ps1` - 設定腳本
- `check_deployment.py` - 詳細檢查腳本
- `check_dns_status.py` - DNS 檢查腳本

---

## 🎯 最佳實踐

1. **定期檢查報告**
   - 每天查看一次報告
   - 及時處理發現的問題

2. **設定合理的檢查頻率**
   - 不要過於頻繁（增加系統負載）
   - 不要過於稀少（延遲問題發現）

3. **保留歷史報告**
   - 定期備份報告
   - 分析趨勢和模式

4. **整合到監控系統**
   - 與 Uptime Kuma 整合
   - 與其他監控工具整合

---

**設定指南產生時間：** 2026-01-20  
**目的：** 為商家和居民提供穩定可靠的服務監控
