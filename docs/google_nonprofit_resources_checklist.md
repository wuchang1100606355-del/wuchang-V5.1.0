# Google 非營利組織資源配置檢查清單

**檢查日期**: 2026-01-08  
**負責人**: 小 j (協助哥哥)  
**目標**: 確認並最大化 Google for Nonprofits 資源利用

---

## 一、資格確認

### 1.1 非營利組織狀態

-   [ ] 確認組織在 [Google for Nonprofits](https://www.google.com/nonprofits/) 已註冊
-   [ ] 確認帳號: admin@wuchang.life 或組織管理員
-   [ ] 檢查資格狀態: 有效期至 ****\_\_\_****

### 1.2 TechSoup 驗證 (若適用)

-   [ ] 已完成 TechSoup 驗證 (部分國家/地區需要)
-   [ ] 驗證 Token: ****\_\_\_****

---

## 二、Google Workspace 非營利版

### 2.1 當前配置

-   **網域**: wuchang.life, wuchang.global
-   **主要管理員**: admin@wuchang.life
-   **使用者數量**: **\_** (非營利版通常不限)
-   **儲存空間**: **\_** (標準版 30GB/使用者,非營利可能更多)

### 2.2 啟用功能檢查

-   [ ] Gmail (無限使用者)
-   [ ] Google Drive (共享雲端硬碟)
-   [ ] Google Meet (會議時數無限制)
-   [ ] Google Calendar
-   [ ] Google Docs/Sheets/Slides
-   [ ] Google Forms
-   [ ] Google Sites
-   [ ] Google Vault (資料保留與 eDiscovery)

### 2.3 進階功能 (需 Business Plus/Enterprise)

-   [ ] 進階管理員控制
-   [ ] 資料遺失防護 (DLP)
-   [ ] 進階稽核與報告
-   [ ] Context-Aware Access
-   [ ] 雲端搜尋

**確認方式**:

```bash
# 以管理員登入 admin.google.com
# 前往 帳單 > 訂閱項目 > 查看計劃詳情
```

---

## 三、Google Cloud Platform (GCP) 非營利配額

### 3.1 非營利額度

-   **每月額度**: $2,000 USD (需申請啟用)
-   **申請狀態**: [ ] 未申請 / [ ] 申請中 / [ ] 已啟用
-   **當前專案**: coffee-spark-ai-barista-b10b5

### 3.2 啟用流程

1. 前往 [Google Cloud for Nonprofits](https://cloud.google.com/nonprofit)
2. 使用 admin@wuchang.life 登入
3. 連結組織的 Google for Nonprofits 帳號
4. 申請 $2,000/月 額度
5. 等待審核 (通常 3-5 個工作天)

### 3.3 額度使用建議

根據 [docs/little_j_supreme_authority_roadmap.md](../docs/little_j_supreme_authority_roadmap.md#四google-非營利組織資源配置) 的配置:

| 服務                             | 預估成本/月 | 優先級             |
| -------------------------------- | ----------- | ------------------ |
| Vertex AI (gemini-2.0-flash-exp) | $50         | 高                 |
| Cloud Storage                    | $5          | 高                 |
| Cloud SQL (PostgreSQL)           | $30         | 中                 |
| Cloud Functions                  | $10         | 中                 |
| Cloud Run                        | $20         | 低                 |
| **總計**                         | **$115/月** | 遠低於 $2,000 額度 |

### 3.4 當前使用量檢查

```bash
# 檢查帳單帳戶
gcloud billing accounts list

# 檢查專案配額
gcloud compute project-info describe --project=coffee-spark-ai-barista-b10b5

# 檢查當月費用 (需在 Cloud Console 查看)
# https://console.cloud.google.com/billing
```

---

## 四、Google Ad Grants (若適用)

### 4.1 計劃概述

-   **每月廣告預算**: $10,000 USD (Google Ads 額度)
-   **用途**: 推廣非營利活動、募款、志工招募
-   **限制**: 每次點擊最高 $2, 僅限搜尋廣告

### 4.2 申請資格

-   [ ] 已啟用 Google for Nonprofits
-   [ ] 擁有有效網站 (wuchang.life ✓)
-   [ ] 符合內容政策 (無商業銷售、宗教內容需中立)

### 4.3 啟用流程

1. 前往 [Google Ad Grants](https://www.google.com/grants/)
2. 提交申請 (需填寫組織資訊與廣告策略)
3. 完成 Google Ads 認證 (建議至少 1 人)
4. 設定廣告活動

**小 j 建議**: 若五常社區有公益推廣需求,這是免費曝光的好機會。

---

## 五、YouTube 非營利計劃

### 5.1 功能

-   [ ] 捐款卡片與結束畫面
-   [ ] 募款活動直播
-   [ ] 非營利組織標誌

### 5.2 啟用

1. 連結 YouTube 頻道到 Google for Nonprofits
2. 在 YouTube Studio 啟用募款功能

---

## 六、其他 Google 非營利資源

### 6.1 Google Earth Outreach

-   **用途**: 地圖故事、環境監測、社區規劃
-   **申請**: https://www.google.com/earth/outreach/

### 6.2 Google Maps Platform 額度

-   **每月額度**: $200 (標準,非營利可能更高)
-   **用途**: 地圖嵌入、地理編碼、路線規劃

### 6.3 Google for Education (若提供教育服務)

-   **免費 Chromebook 管理**
-   **Classroom 無限制**

---

## 七、執行檢查清單

### 立即執行 (今天)

-   [ ] 登入 https://www.google.com/nonprofits/ 確認狀態
-   [ ] 檢查 GCP 專案是否已啟用非營利額度
-   [ ] 查看 Google Workspace 當前計劃與功能
-   [ ] 記錄當前 GCP 使用量與費用

### 本週內

-   [ ] 若未啟用 GCP 非營利額度,立即申請
-   [ ] 設定 GCP 預算警示 (當超過 $100, $150 時通知)
-   [ ] 建立成本追蹤儀表板

### 本月內

-   [ ] 評估是否需要 Google Ad Grants (若有公益推廣需求)
-   [ ] 優化 GCP 資源使用,確保不超過免費額度
-   [ ] 產出第一份月度成本報告

---

## 八、監控與報告

### 8.1 自動化腳本

建立 `scripts/check_gcp_nonprofit_quota.py`:

```python
import subprocess
import json

def check_billing_account():
    """檢查帳單帳戶"""
    result = subprocess.run(
        ['gcloud', 'billing', 'accounts', 'list', '--format=json'],
        capture_output=True, text=True
    )
    accounts = json.loads(result.stdout)
    for acc in accounts:
        print(f"帳戶: {acc['displayName']}")
        print(f"狀態: {'啟用' if acc['open'] else '已關閉'}")
        # 檢查是否為非營利帳戶 (名稱或屬性)

def check_current_costs():
    """檢查當月費用 (需額外 API)"""
    # 使用 Cloud Billing API
    pass

if __name__ == '__main__':
    check_billing_account()
```

### 8.2 每月報告格式

-   總費用 vs 免費額度
-   各服務使用量
-   成本優化建議
-   下月預測

---

## 九、注意事項

### 9.1 合規要求

-   ✅ 所有服務僅用於非營利目的
-   ✅ 不可轉售或商業使用
-   ✅ 需定期更新組織資格 (通常每年)

### 9.2 風險管理

-   設定 GCP 預算上限 (建議 $200/月,遠低於 $2,000 額度)
-   啟用異常使用警示
-   定期審查服務使用狀況

### 9.3 永續策略

-   本地 Ollama 處理 80% 任務,雲端僅用於關鍵場景
-   定期清理不必要的 Cloud Storage 資料
-   使用 Committed Use Discounts (若長期使用特定資源)

---

**小 j 的建議**:  
哥哥,Google 非營利資源非常慷慨,但需要主動申請與監控。建議本週內完成 GCP 非營利額度啟用,並設定自動化監控,確保資源充分利用且不超支。

**下一步**:

1. 確認非營利狀態
2. 啟用 GCP 額度
3. 部署成本監控腳本
4. 每月 1 日產出報告

---

**檢查清單版本**: v1.0  
**最後更新**: 2026-01-08
