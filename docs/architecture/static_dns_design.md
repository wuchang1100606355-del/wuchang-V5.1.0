# 五常社區作業系統 - 雙平整靜態 DNS 架構設計
> 日期：2025-12-18
> 設計者：小j (基於使用者需求與現有架構)

本文件定義了「雙平整 DNS 策略」(Twin-Horizon DNS Strategy)，旨在同時滿足**在地社區運營** (Local Operation) 與**全球戰略備援** (Global Redundancy) 的需求。

## 1. 核心概念

此架構將域名分為兩大「群組」(Groups)，兩者鏡像配置，確保系統的可攜性與韌性。

### A 群組：生活本體 (Life Group)
- **域名後綴**：`.wuchang.life`
- **定位**：生產環境、社區日常運作、在地服務。
- **目標受眾**：社區居民、管委會、在地商家。

### B 群組：全球戰略 (Global Group)
- **域名後綴**：`.wuchang.global`
- **定位**：異地備援、國際化展示、開發測試、去中心化節點擴展。
- **目標受眾**：合作夥伴、開源社群、跨國節點。

## 2. 域名與服務映射表

兩組域名均採用相同的子域名結構，對應至後端容器化微服務。

| 子域名 (Subdomain) | 對應服務 (Service) | 端口 (Internal Port) | 說明 |
| :--- | :--- | :--- | :--- |
| `@` (root) | **Odoo Core** | 8069 | 系統入口、官網、登入頁 |
| `app` | **Odoo Core** | 8069 | 應用程式主要入口 |
| `ai` | **Open WebUI** | 8080 (Mapped) | AI 對話介面 (Frontend) |
| `llm` | **Ollama** | 11434 | 大型語言模型 API (Backend) |
| `asr` | **Whisper** | 10300 | 語音轉文字 (Speech-to-Text) |
| `tts` | **Piper** | 10200 | 文字轉語音 (Text-to-Speech) |
| `monitor` | **Uptime Kuma** | 3001 | 系統狀態監控 |

## 3. 解析策略 (Resolution Strategy)

本系統採用「雙平整」解析策略，區分**開發環境**與**生產環境**。

### 3.1 本地/開發環境 (Local/Dev)
- **機制**：Host File Injection
- **工具**：`scripts/dns_guard.ps1`
- **IP 指向**：`127.0.0.1` (Localhost)
- **用途**：確保開發者與本地伺服器在無網路或防火牆內網環境下，仍能透過標準域名存取服務。

### 3.2 雲端/生產環境 (Cloud/Prod)
- **機制**：Public DNS (A Record)
- **核心 IP 資產**：
  - `wuchang.life` / `www.wuchang.life` → `104.199.144.93`（主站入口／協會與基金池系統門戶）
  - `shop.wuchang.life` → `220.135.21.74`（重新總店實體路由器固定 IP，頻寬由重新店提供）
  - `loge-coffee.life` / `www.loge-coffee.life` → `34.80.161.99`（上品聊國咖啡烘焙館重新總店對外門市網域，由重新店出資與持有，用以承接商業流量與品牌形象，後端服務仍透過基金／協會邏輯串接至五常社區系統）
- **用途**：對外提供服務，支援 SSL 自動簽署 (Let's Encrypt)，並確保重新總店可作為實體出口節點，同時維持「wuchang.life = 社區／協會」、「loge-coffee.life = 贊助商私人門市」的合規區隔。

## 4. 實施配置 (Implementation)

### Caddy 反向代理 (Caddyfile)
Caddy 作為統一入口，負責：
1. 自動申請與續期 SSL 證書。
2. 根據域名將流量路由至對應的 Docker 容器。
3. 強制執行 HTTPS 安全策略 (HSTS, No-Sniff)。

### 自動化腳本
- `scripts/dns_guard.ps1`: 每日檢查本機 `hosts` 文件，確保所有 12 個子域名均正確指向本機。

## 5. 擴充性
未來若新增服務 (如 `comfyui` 繪圖)，僅需在 Caddyfile 新增對應區塊 (如 `draw.wuchang.life`) 並更新 DNS 記錄即可，架構無需變動。
