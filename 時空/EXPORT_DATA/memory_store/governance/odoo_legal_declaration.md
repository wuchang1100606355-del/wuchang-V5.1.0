# Odoo 系統法律聲明與組織信息整合

**整合日期**: 2026 年 1 月 8 日  
**責任人**: 江政隆  
**狀態**: Active - 應用於所有 Odoo 前後台頁面

---

## 整合範圍

### 1. 首頁與公開頁面 (wuchang_web_portal)

**檔案**: `wuchang_os/addons/wuchang_web_portal/views/portal_templates.xml`

新增「組織身份、資金來源與法律聲明」區塊，包含：

-   組織身份卡片（新北市五常社區發展協會 + 五常物業規劃顧問）
-   資金來源卡片（上品聊國咖啡館 Google 商家資訊超連結）
-   法律聲明卡片（無資本利得宣告 + 專利保護）

### 2. 登入頁面與品牌展示 (wuchang_design_system)

#### 登入頁面 HTML (web_login_templates.xml)

-   頂部 footer：組織身份、統一編號、資金來源、Google Maps 連結
-   品牌信息區塊：動態顯示組織信息與資金來源

#### 品牌 API 端點 (web_login.py)

**路由**: `/web/login/branding_info`

新增返回值：

```python
'organization_info': '新北市五常社區發展協會（立案字號：新北市社區補自第1100606355號）& 五常物業規劃顧問股份有限公司（統一編號：97573469，社會企業）'
'funding_source': '系統開發：上品聊國咖啡館全額捐助｜網路資源：Google非營利組織抵免額｜設備補助：新北市政府補助'
```

### 3. Odoo 設定管理 (wuchang_core)

#### 設定 UI (settings_views.xml)

新增「組織身份與資金來源聲明」設定區塊，包含欄位：

-   **branding_organization_info** (文本)：組織法律名稱與立案資訊
-   **branding_funding_source** (文本)：資金來源與合作夥伴信息
-   **branding_coffee_org_link** (字元)：Google Maps/官方網站連結
-   **branding_decision_maker** (字元)：核心決策人及身份資訊
-   **branding_nonprofit_declaration** (文本)：無資本利得宣告文本

#### 設定模型 (settings.py)

五個新欄位定義 + get_values()讀取 + set_values()保存

---

## 上品聊國咖啡館 Google 商家資訊超連結

### 連結設置方式

**完整地址**: 新北市三重區重新路三段 204 號  
**Google Maps 連結**: `https://www.google.com/maps/place/204,+Section+3,+Chongxin+Rd,+Sanchong+District,+New+Taipei+City/@25.0818,121.4898,15z`

### 出現位置

1. **portal_templates.xml** - 資金來源卡片

    ```html
    <a
        href="https://www.google.com/maps/search/上品聊國咖啡館"
        target="_blank"
        rel="noopener noreferrer"
        >上品聊國咖啡館重新總店</a
    >全額捐助
    ```

2. **web_login_templates.xml** - 頁面頂部 footer

    ```html
    <a
        href="https://www.google.com/maps/search/上品聊國咖啡館"
        target="_blank"
        rel="noopener noreferrer"
        style="color:#666;"
        >上品聊國咖啡館重新總店</a
    >
    ```

3. **web_login_templates.xml** - 動態品牌信息
    ```javascript
    if (co && d.coffee_org) {
        co.innerHTML =
            '系統開發支持：<a href="https://www.google.com/maps/search/上品聊國咖啡館" target="_blank" rel="noopener noreferrer">' +
            d.coffee_org +
            "</a>"
    }
    ```

### 設定位置

Odoo 後台 → 網站設定 → 組織身份與資金來源聲明 → 咖啡館 Google 商家資訊

---

## 組織信息默認值

若未在 Odoo 設定中配置，系統使用以下默認值：

| 項目       | 默認值                                                                                        |
| ---------- | --------------------------------------------------------------------------------------------- |
| 組織身份   | 新北市五常社區發展協會（立案字號：新北市社區補自第 1100606355 號）                            |
| 營運夥伴   | 五常物業規劃顧問股份有限公司（統一編號：97573469，社會企業）                                  |
| 資金來源   | 系統開發：上品聊國咖啡館全額捐助\|網路資源：Google 非營利組織抵免額\|設備補助：新北市政府補助 |
| 咖啡館連結 | https://www.google.com/maps/search/上品聊國咖啡館                                             |
| 決策人     | 江政隆（F124771717，1979-12-25）                                                              |

---

## 修改與同步

### Odoo 設定後同步方式

1. **即時顯示**：登入頁面、網站首頁會即時讀取 Odoo 設定
2. **API 端點**：所有前端 JavaScript 通過 `/web/login/branding_info` API 獲取信息
3. **記憶同步**：設定變更會自動保存到 `ir.config_parameter`

### 更新流程

```
管理員編輯設定 → Odoo保存到ir.config_parameter → API端點返回新值 → 前端頁面動態更新
```

---

## 法律效力

-   ✅ 上品聊國咖啡館 Google 商家資訊為公開連結，可供查證
-   ✅ 所有組織信息與立案字號均有正式文件備查
-   ✅ 無資本利得宣告符合中華民國民法與稅法規範
-   ✅ 所有更改記錄在 memory_store/governance/下，可供稽查

---

## 記憶指示

本文檔定義了 Odoo 系統內的所有法律聲明與組織信息的顯示邏輯。小 j 應確保：

1. 所有公開頁面準確反映這些信息
2. 首次初始化 Odoo 時，應在設定中填入相應信息
3. 任何組織信息變更應同時更新 Odoo 設定與 memory_store 文件
4. Google Maps 連結應保持有效且指向正確商家

---

**最後修改**: 2026-01-08  
**修改人**: 江政隆 / GitHub Copilot  
**驗證狀態**: 已整合至所有 Odoo 前後台


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:23:00
---
