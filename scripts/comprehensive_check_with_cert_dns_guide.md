# 每小時全面檢查指南（包含憑證簽發和靜態DNS設定）

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 📋 功能概述

每小時全面檢查系統，包含以下五個核心檢查項目：

1. **網域部署檢查** - 確認 wuchang.life 網域 DNS 解析正常
2. **靜態DNS設定檢查** - 確認 DNS 記錄符合預期的靜態設定
3. **憑證簽發檢查** - 確認 Caddy 和 Let's Encrypt 憑證簽發狀態
4. **全球可見性檢查** - 確認首頁在全球範圍內可訪問
5. **Google 非營利組織首頁合規檢查** - 確認首頁符合 Google 非營利組織規定

---

## 🔧 檢查項目詳解

### 1. 網域部署檢查

**目的**: 確認 wuchang.life 網域部署正常

**檢查內容**:
- DNS 解析（A 記錄）
- DNS 伺服器回應
- IP 地址解析
- 是否符合預期的靜態DNS設定

**合規要求**:
- ✅ DNS 必須能正確解析到目標 IP
- ✅ DNS IP 應符合預期的靜態DNS設定

### 2. 靜態DNS設定檢查（新增）

**目的**: 確認 DNS 記錄符合預期的靜態設定

**檢查內容**:
- DNS A記錄檢查（主站和www）
- DNS MX記錄檢查（Google郵件服務）
- DNS記錄是否符合預期值

**預期值**:
- A記錄（@）: `["104.199.144.93"]`（主站 IP，請根據實際情況調整）
- A記錄（www）: `["104.199.144.93"]`
- MX記錄（@）: `[{"priority": 1, "server": "smtp.google.com"}]`

**合規要求**:
- ✅ DNS A記錄必須符合預期值
- ✅ DNS MX記錄應包含 Google 郵件服務
- ⚠ DNS TXT記錄（SPF, DKIM, DMARC）為建議項

### 3. 憑證簽發檢查（新增）

**目的**: 確認 Caddy 和 Let's Encrypt 憑證簽發狀態

**檢查內容**:
- Caddy 容器運行狀態
- Caddy 配置文件存在性
- 網域配置狀態（wuchang.life）
- Let's Encrypt 證書狀態
- Caddy 數據目錄（證書存儲位置）

**配置路徑**:
- Caddy配置文件: `wuchang_os/Caddyfile`
- Caddy數據目錄: `volumes/caddy-data`
- 證書目錄: `volumes/caddy-data/caddy/certificates/acme-v02.api.letsencrypt.org-directory`

**合規要求**:
- ✅ Caddy 容器必須運行
- ✅ Caddy 配置文件必須存在
- ✅ 網域 wuchang.life 必須在配置中
- ✅ Let's Encrypt 證書應該存在（首次運行可能需要申請）

### 4. 全球可見性檢查

**目的**: 確認首頁在全球範圍內可訪問

**檢查內容**:
- HTTPS 首頁可訪問性
- HTTP 首頁可訪問性（備用）
- 使用不同 User-Agent 模擬不同地區訪問
- 響應時間和狀態碼

**合規要求**:
- ✅ 首頁必須可以從全球訪問
- ✅ SSL 證書必須有效
- ✅ 響應時間應在合理範圍內

### 5. Google 非營利組織首頁合規檢查

**目的**: 確認首頁符合 Google 非營利組織規定

**檢查內容**:
- 組織名稱關鍵字（五常社區、社區發展協會、非營利等）
- 使命關鍵字（社區、公益、服務等）
- 聯絡資訊關鍵字（聯絡、聯繫等）
- 可選內容（志工、活動等為加分項）

**合規要求**:
- ✅ 必須明確標示組織名稱
- ✅ 必須說明非營利性質
- ✅ 必須提供聯絡資訊
- ✅ 必須說明服務使命

---

## 🚀 使用方式

### 手動執行

```powershell
# 執行全面檢查
python scripts/comprehensive_hourly_check.py

# 或使用批處理腳本
scripts\run_hourly_check.bat
```

### 排程執行

任務已設定為每小時自動執行：

```powershell
# 查看任務狀態
.\scripts\manage_hourly_task.ps1 -Action status

# 手動執行任務
.\scripts\manage_hourly_task.ps1 -Action run
```

---

## 📊 檢查報告

### 報告位置

檢查報告會儲存在：
```
logs/comprehensive_hourly_check_YYYYMMDD_HHMMSS.json
```

### 報告內容

- **timestamp**: 檢查時間
- **domain**: 檢查的網域（wuchang.life）
- **organization**: 組織名稱
- **compliance_required**: 是否需要合規檢查
- **checks**: 各項檢查結果
  - `domain_deployment`: 網域部署檢查結果
  - `static_dns_config`: 靜態DNS設定檢查結果
  - `certificate_status`: 憑證簽發檢查結果
  - `url_accessibility`: URL 可訪問性檢查結果
  - `global_accessibility`: 全球可見性檢查結果
  - `homepage_compliance`: 首頁合規檢查結果
- **summary**: 檢查摘要
  - `domain_resolved`: DNS 解析是否成功
  - `static_dns_compliant`: 靜態DNS設定是否合規
  - `certificate_ok`: 憑證簽發是否正常
  - `homepage_accessible`: 首頁是否可訪問
  - `global_accessible`: 全球是否可訪問
  - `homepage_compliant`: 首頁是否合規
  - `overall_status`: 整體狀態（OK/FAIL）

---

## ✅ 合規標準

### 必須通過的檢查

1. **網域部署**: DNS 解析必須成功
2. **靜態DNS設定**: DNS 記錄必須符合預期值
3. **憑證簽發**: Caddy 容器必須運行且網域已配置
4. **首頁可訪問**: HTTPS 首頁必須可訪問
5. **首頁合規**: 必須通過所有必要關鍵字檢查

### 合規分數計算

- **必要檢查**: 所有檢查項目（必須全部通過）
- **整體狀態**: 所有必要檢查都通過時為 "OK"，否則為 "FAIL"

---

## ⚠️ 注意事項

1. **Google 非營利組織合規**: 這是最高優先級要求
2. **靜態DNS設定**: 請根據實際情況調整 `REQUIRED_DNS_RECORDS` 中的預期值
3. **憑證簽發**: 首次運行時，證書可能需要申請，這屬於正常情況
4. **系統AI全權**: 系統AI擁有全權執行所有檢查，自動檢測和報告問題

---

## 💡 配置調整

### 調整靜態DNS預期值

編輯 `scripts/comprehensive_hourly_check.py`：

```python
REQUIRED_DNS_RECORDS = {
    "A": {
        "@": ["104.199.144.93"],  # 請根據實際情況調整
        "www": ["104.199.144.93"],
    },
    "MX": {
        "@": [{"priority": 1, "server": "smtp.google.com"}]
    }
}
```

### 調整Caddy配置路徑

編輯 `scripts/comprehensive_hourly_check.py`：

```python
CADDY_CONFIG_PATH = PROJECT_ROOT / "wuchang_os" / "Caddyfile"
CADDY_DATA_PATH = PROJECT_ROOT / "volumes" / "caddy-data"
```

---

## 🚀 快速開始

```powershell
# 1. 執行檢查
python scripts/comprehensive_hourly_check.py

# 2. 查看報告
Get-Content logs\comprehensive_hourly_check_*.json | ConvertFrom-Json | Format-List

# 3. 檢查任務狀態
.\scripts\manage_hourly_task.ps1 -Action status

# 4. 手動執行任務
.\scripts\manage_hourly_task.ps1 -Action run
```

---

**報告生成時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

*「每小時全面檢查已更新完成，系統會自動檢查網域部署、靜態DNS設定、憑證簽發、全球可見性和 Google 非營利組織首頁合規！系統AI具備全權執行所有檢查。」* ✨
