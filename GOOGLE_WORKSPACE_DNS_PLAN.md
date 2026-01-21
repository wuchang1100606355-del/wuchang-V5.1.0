# Google Workspace DNS 規劃與 API 設置指南

## 📋 目錄

1. [概述](#概述)
2. [Google Workspace 網域規劃](#google-workspace-網域規劃)
3. [Google Cloud DNS API 設置](#google-cloud-dns-api-設置)
4. [權限配置](#權限配置)
5. [DNS 記錄規劃](#dns-記錄規劃)
6. [自動化腳本](#自動化腳本)
7. [驗證與測試](#驗證與測試)
8. [故障排除](#故障排除)

---

## 概述

本文檔提供完整的 Google Workspace 子域名規劃和 Google Cloud DNS API 設置方案，實現自動化 DNS 管理。

### 目標

- ✅ 規劃所有服務的子域名
- ✅ 設置 Google Cloud DNS API 權限
- ✅ 實現 DNS 記錄自動化管理
- ✅ 整合現有 Docker 容器服務
- ✅ 提供完整的 API 操作工具

### 前置需求

1. **Google Workspace 帳號**
   - 管理員權限
   - 已驗證的網域

2. **Google Cloud Platform (GCP)**
   - 已建立專案
   - 啟用 Cloud DNS API
   - 服務帳號權限

3. **網域註冊**
   - 網域已註冊
   - 可修改名稱伺服器（Nameservers）

---

## Google Workspace 網域規劃

### 主網域

假設主網域為：`wuchang.org.tw`

### 子域名規劃

根據網域部署規劃，建議以下子域名結構：

#### 1. 主要服務子域名

```
app.wuchang.org.tw          → Odoo ERP 系統
ai.wuchang.org.tw           → Open WebUI (AI 介面)
admin.wuchang.org.tw        → Portainer (容器管理)
monitor.wuchang.org.tw      → Uptime Kuma (監控)
caddy.wuchang.org.tw        → Caddy UI (管理介面)
api.wuchang.org.tw          → API 服務
www.wuchang.org.tw          → 主網站
```

#### 2. Google Workspace 服務子域名

```
mail.wuchang.org.tw         → Gmail (Google Workspace)
calendar.wuchang.org.tw    → Google Calendar
drive.wuchang.org.tw       → Google Drive
docs.wuchang.org.tw        → Google Docs
meet.wuchang.org.tw        → Google Meet
```

#### 3. 內部服務子域名

```
vpn.wuchang.org.tw         → VPN 服務（如需要）
db.wuchang.org.tw          → 資料庫管理（僅內部）
```

### 完整子域名列表

| 子域名 | 類型 | 用途 | 目標 | 備註 |
|--------|------|------|------|------|
| www | CNAME | 主網站 | Cloudflare Tunnel | 公開訪問 |
| app | CNAME | Odoo ERP | Cloudflare Tunnel | 公開訪問 |
| ai | CNAME | Open WebUI | Cloudflare Tunnel | 公開訪問 |
| admin | CNAME | Portainer | Cloudflare Tunnel | 需認證 |
| monitor | CNAME | Uptime Kuma | Cloudflare Tunnel | 需認證 |
| caddy | CNAME | Caddy UI | Cloudflare Tunnel | 需認證 |
| api | CNAME | API 服務 | Cloudflare Tunnel | API Key 認證 |
| mail | MX | Gmail | Google Workspace | Google 管理 |
| calendar | CNAME | Google Calendar | Google Workspace | Google 管理 |
| drive | CNAME | Google Drive | Google Workspace | Google 管理 |
| docs | CNAME | Google Docs | Google Workspace | Google 管理 |
| meet | CNAME | Google Meet | Google Workspace | Google 管理 |

---

## Google Cloud DNS API 設置

### 步驟 1: 啟用 Google Cloud DNS API

#### 方法一：透過 Google Cloud Console

1. **登入 Google Cloud Console**
   - 前往：https://console.cloud.google.com

2. **選擇或建立專案**
   - 點擊專案選擇器
   - 選擇現有專案或建立新專案

3. **啟用 Cloud DNS API**
   - 前往「API 和服務」→「程式庫」
   - 搜尋「Cloud DNS API」
   - 點擊「啟用」

#### 方法二：透過 gcloud CLI

```bash
# 安裝 gcloud CLI（如未安裝）
# Windows: 下載並安裝 Google Cloud SDK
# macOS: brew install google-cloud-sdk
# Linux: 參考官方文件

# 登入
gcloud auth login

# 選擇專案
gcloud config set project YOUR_PROJECT_ID

# 啟用 Cloud DNS API
gcloud services enable dns.googleapis.com
```

### 步驟 2: 建立服務帳號

#### 透過 Google Cloud Console

1. **建立服務帳號**
   - 前往「IAM 和管理」→「服務帳號」
   - 點擊「建立服務帳號」
   - 輸入名稱：`dns-manager`
   - 輸入說明：`DNS 記錄管理服務帳號`

2. **授予權限**
   - 角色：`DNS 管理員` (roles/dns.admin)
   - 或自訂角色：
     - `dns.managedZones.*`
     - `dns.resourceRecordSets.*`

3. **建立金鑰**
   - 點擊服務帳號
   - 前往「金鑰」標籤
   - 點擊「新增金鑰」→「建立新金鑰」
   - 選擇「JSON」
   - 下載金鑰檔案

#### 透過 gcloud CLI

```bash
# 建立服務帳號
gcloud iam service-accounts create dns-manager \
    --display-name="DNS Manager" \
    --description="DNS record management service account"

# 授予 DNS 管理員權限
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:dns-manager@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/dns.admin"

# 建立並下載金鑰
gcloud iam service-accounts keys create dns-manager-key.json \
    --iam-account=dns-manager@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 步驟 3: 建立 DNS 區域（Zone）

#### 透過 Google Cloud Console

1. **建立 DNS 區域**
   - 前往「網路服務」→「Cloud DNS」
   - 點擊「建立區域」
   - 區域類型：**公開區域**
   - 區域名稱：`wuchang-org-tw`
   - DNS 名稱：`wuchang.org.tw`
   - 說明：`Wuchang organization DNS zone`

2. **記錄名稱伺服器**
   - 建立後，Google 會提供 4 個名稱伺服器
   - 記錄這些名稱伺服器（稍後需要在網域註冊商設定）

#### 透過 gcloud CLI

```bash
# 建立公開 DNS 區域
gcloud dns managed-zones create wuchang-org-tw \
    --dns-name=wuchang.org.tw \
    --description="Wuchang organization DNS zone" \
    --visibility=public

# 查看名稱伺服器
gcloud dns managed-zones describe wuchang-org-tw \
    --format="value(nameServers)"
```

### 步驟 4: 更新網域註冊商的名稱伺服器

1. **登入網域註冊商控制台**
2. **找到 DNS 設定或名稱伺服器設定**
3. **更新為 Google Cloud DNS 提供的名稱伺服器**：
   ```
   ns-cloud-a1.googledomains.com
   ns-cloud-a2.googledomains.com
   ns-cloud-a3.googledomains.com
   ns-cloud-a4.googledomains.com
   ```
4. **等待 DNS 傳播**（通常 24-48 小時）

---

## 權限配置

### Google Workspace 管理員權限

確保您的帳號具有以下權限：

1. **Google Workspace 管理員**
   - 完整管理員權限
   - 或至少具有「網域管理員」權限

2. **Google Cloud Platform**
   - 專案擁有者或編輯者
   - 或具有以下 IAM 角色：
     - `roles/dns.admin`
     - `roles/iam.serviceAccountUser`

### 服務帳號權限

服務帳號需要以下權限：

```json
{
  "bindings": [
    {
      "role": "roles/dns.admin",
      "members": [
        "serviceAccount:dns-manager@PROJECT_ID.iam.gserviceaccount.com"
      ]
    }
  ]
}
```

### 驗證權限

```bash
# 檢查當前使用者權限
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:user:YOUR_EMAIL"

# 檢查服務帳號權限
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:dns-manager@YOUR_PROJECT_ID.iam.gserviceaccount.com"
```

---

## DNS 記錄規劃

### 記錄類型說明

#### A 記錄
用於將域名指向 IPv4 地址。

#### CNAME 記錄
用於將域名指向另一個域名（別名）。

#### MX 記錄
用於郵件服務，指向郵件伺服器。

#### TXT 記錄
用於驗證、SPF、DKIM 等。

### 初始 DNS 記錄配置

#### 1. 基本 A 記錄（如需要）

```
類型    名稱    值                TTL
A       @       <伺服器 IP>       300
A       www     <伺服器 IP>       300
```

#### 2. Cloudflare Tunnel CNAME 記錄

```
類型    名稱      值                                    TTL
CNAME   app       <tunnel-id>.cfargotunnel.com         300
CNAME   ai        <tunnel-id>.cfargotunnel.com         300
CNAME   admin     <tunnel-id>.cfargotunnel.com         300
CNAME   monitor   <tunnel-id>.cfargotunnel.com         300
CNAME   caddy     <tunnel-id>.cfargotunnel.com         300
CNAME   api       <tunnel-id>.cfargotunnel.com         300
```

#### 3. Google Workspace MX 記錄

```
類型    名稱    優先級    值                              TTL
MX      @       1         aspmx.l.google.com             3600
MX      @       5         alt1.aspmx.l.google.com        3600
MX      @       5         alt2.aspmx.l.google.com        3600
MX      @       10        alt3.aspmx.l.google.com        3600
MX      @       10        alt4.aspmx.l.google.com        3600
```

#### 4. Google Workspace TXT 記錄（驗證）

```
類型    名稱    值                                    TTL
TXT     @       google-site-verification=...           3600
TXT     @       v=spf1 include:_spf.google.com ~all   3600
```

#### 5. Google Workspace CNAME 記錄

```
類型    名稱      值                              TTL
CNAME   mail      ghs.googlehosted.com           3600
CNAME   calendar  ghs.googlehosted.com           3600
CNAME   drive     ghs.googlehosted.com           3600
CNAME   docs      ghs.googlehosted.com           3600
CNAME   meet      ghs.googlehosted.com           3600
```

---

## 自動化腳本

### 腳本功能

1. **DNS 記錄管理**
   - 建立記錄
   - 更新記錄
   - 刪除記錄
   - 列出記錄

2. **批量操作**
   - 批量建立子域名
   - 批量更新記錄
   - 匯入/匯出配置

3. **驗證與測試**
   - DNS 解析檢查
   - 記錄驗證
   - 傳播狀態檢查

---

## 驗證與測試

### 1. 驗證 DNS 區域

```bash
# 列出所有 DNS 區域
gcloud dns managed-zones list

# 查看特定區域詳情
gcloud dns managed-zones describe wuchang-org-tw
```

### 2. 驗證 DNS 記錄

```bash
# 列出區域內所有記錄
gcloud dns record-sets list --zone=wuchang-org-tw

# 查詢特定記錄
gcloud dns record-sets list --zone=wuchang-org-tw --name=app.wuchang.org.tw
```

### 3. 測試 DNS 解析

```bash
# 使用 dig 測試
dig app.wuchang.org.tw

# 使用 nslookup 測試
nslookup app.wuchang.org.tw

# 使用線上工具
# https://dnschecker.org/
```

---

## 故障排除

### 常見問題

#### 1. API 未啟用

**錯誤**：`API dns.googleapis.com is not enabled`

**解決方法**：
```bash
gcloud services enable dns.googleapis.com
```

#### 2. 權限不足

**錯誤**：`Permission denied`

**解決方法**：
- 檢查服務帳號權限
- 確認 IAM 角色設定正確

#### 3. DNS 記錄未生效

**可能原因**：
- DNS 傳播延遲（24-48 小時）
- 名稱伺服器未正確設定
- TTL 設定過長

**解決方法**：
- 等待 DNS 傳播
- 檢查名稱伺服器設定
- 降低 TTL 值（測試期間）

---

## 相關資源

- [Google Cloud DNS 文件](https://cloud.google.com/dns/docs)
- [Google Workspace 管理控制台](https://admin.google.com)
- [Google Cloud Console](https://console.cloud.google.com)
- [Cloud DNS API 參考](https://cloud.google.com/dns/docs/reference/v1)

---

## 更新記錄

| 日期 | 版本 | 更新內容 | 作者 |
|------|------|---------|------|
| 2026-01-19 | 1.0 | 初始版本 | System |
