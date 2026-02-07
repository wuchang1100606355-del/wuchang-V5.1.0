# 每小時全面檢查指南

**執行時間**: 2026-01-12  
**系統版本**: Wuchang OS V5.1.0  
**AI 身份**: Little J (小j)

---

## 📋 功能概述

每小時全面檢查系統，包含以下三個核心檢查項目：

1. **網域部署檢查** - 確認 wuchang.life 網域 DNS 解析正常
2. **全球可見性檢查** - 確認首頁在全球範圍內可訪問
3. **Google 非營利組織首頁合規檢查** - 確認首頁符合 Google 非營利組織規定

---

## 🔧 檢查項目詳解

### 1. 網域部署檢查

**目的**: 確認 wuchang.life 網域部署正常

**檢查內容**:
- DNS 解析（A 記錄）
- DNS 伺服器回應
- IP 地址解析

**合規要求**:
- ✅ DNS 必須能正確解析到目標 IP
- ✅ 網域必須正確指向服務器

### 2. 全球可見性檢查

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

### 3. Google 非營利組織首頁合規檢查

**目的**: 確認首頁符合 Google 非營利組織規定

**檢查內容**:
- 組織名稱（必須包含「五常社區」、「社區發展協會」、「非營利」等關鍵字）
- 組織使命（必須包含「社區」、「公益」、「服務」等關鍵字）
- 聯絡資訊（必須包含「聯絡」、「聯繫」等關鍵字）
- 可選內容（「志工」、「活動」等為加分項）

**合規要求**:
- ✅ 必須明確標示組織名稱
- ✅ 必須說明非營利性質
- ✅ 必須提供聯絡資訊
- ✅ 必須說明服務使命

**必要關鍵字檢查**:
- 組織名稱關鍵字：`["五常社區", "五常", "社區發展協會", "非營利", "non-profit"]`
- 使命關鍵字：`["社區", "公益", "服務", "community", "public service"]`
- 聯絡關鍵字：`["聯絡", "聯繫", "contact"]`

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
  - `url_accessibility`: URL 可訪問性檢查結果
  - `global_accessibility`: 全球可見性檢查結果
  - `homepage_compliance`: 首頁合規檢查結果
- **summary**: 檢查摘要
  - `domain_resolved`: DNS 解析是否成功
  - `homepage_accessible`: 首頁是否可訪問
  - `global_accessible`: 全球是否可訪問
  - `homepage_compliant`: 首頁是否合規
  - `overall_status`: 整體狀態（OK/FAIL）

---

## ✅ 合規標準

### 必須通過的檢查

1. **網域部署**: DNS 解析必須成功
2. **首頁可訪問**: HTTPS 首頁必須可訪問
3. **首頁合規**: 必須通過所有必要關鍵字檢查

### 合規分數計算

- **必要檢查**: 組織名稱、使命、聯絡資訊（必須全部通過）
- **可選檢查**: 志工、活動等（加分項，不影響合規）
- **合規分數**: `(通過的必要檢查數 / 必要檢查總數) × 100%`
- **合規標準**: 分數必須達到 100%（所有必要檢查都通過）

---

## ⚠️ 注意事項

1. **Google 非營利組織合規**: 這是最高優先級要求
2. **首頁內容**: 必須明確標示非營利組織身份
3. **聯絡資訊**: 必須提供有效的聯絡方式
4. **全球訪問**: 首頁必須可以從全球訪問

---

## 💡 合規建議

### 首頁必須包含的內容

1. **組織名稱**: 明確標示「新北市三重區五常社區發展協會」
2. **非營利聲明**: 說明這是非營利組織
3. **服務使命**: 說明社區服務和公益目的
4. **聯絡資訊**: 提供有效的聯絡方式

### 首頁建議包含的內容

1. **志工資訊**: 招募志工的資訊
2. **活動資訊**: 社區活動的資訊
3. **服務項目**: 提供的服務項目
4. **組織簡介**: 組織的歷史和目標

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

*「每小時全面檢查已設定完成，系統會自動檢查網域部署、全球可見性和 Google 非營利組織首頁合規！」* ✨
