# 「重新店」硬體設備規劃書 v3.2

**文件狀態:** 草案
**更新日期:** 2025 年 12 月 21 日
**主要決策者:** 指揮官

## 1. 核心理念

本規劃旨在為「重新店」打造一套高效、穩定且具未來擴充性的 POS 與網路基礎設施。架構核心為「雲端 + 本地 AI」，確保結帳流程順暢，並透過創新的語音點餐提升員工效率。

---

## 2. POS 工作站架構

### 2.1. 主 POS 結帳工作站 (Station-01)

此工作站為店面核心，負責處理所有結帳、訂單輸入及會員管理。採用「單一平板，雙螢幕」架構。

-   **核心設備 (已決策):**
    -   **型號:** Samsung Galaxy Tab S9 Ultra
    -   **作業系統:** Android
    -   **理由:** 頂級處理效能，搭載 Samsung DeX 桌面模式，能穩定驅動雙螢幕及周邊，兼具效能與成本效益。
-   **擴充基座:**
    -   **型號:** CalDigit TS4 或同等級 Thunderbolt/USB4 擴充基座
    -   **用途:** 連接所有周邊設備，並為平板供電。
-   **顧客顯示螢幕:**
    -   **型號:** 10-14 吋 USB-C 便攜螢幕 (例如: Arzopa, Uperfect)
    -   **連接方式:** 透過擴充基座的 HDMI/DisplayPort 接口。
-   **周邊設備:**

    -   **收據印表機:** Epson TM-T88VII (乙太網路介面)
    -   **錢箱:** 標準 RJ11/RJ12 接口錢箱 (連接至印表機)
    -   **條碼掃描器:** USB 介面 2D 條碼掃描器

-   **[最高優先級任務] 相容性驗證:**
    -   **任務:** 驗證 Epson TM-T88VII 網路印表機在 Android DeX 環境下與 Odoo POS 的相容性。
    -   **目標:** 確認可透過 Odoo POS Box (或等效方案) 在 Android 上穩定驅動印表機與錢箱。

### 2.2. 員工專用語音點餐工作站 (Station-02)

此工作站專為員工設計，透過本地語音 AI 實現快速、免持的點餐輸入，提升內部運作效率。

-   **核心設備:**
    -   **型號:** 24 吋觸控一體機 (All-in-One PC) 或 Mini PC + 24 吋觸控螢幕
    -   **作業系統:** Windows 11 Pro
-   **語音輸入設備:**
    -   **麥克風:** 高品質 USB 降噪麥克風陣列 (例如: Anker PowerConf S3)
-   **軟體架構:**
    -   **前端:** 客製化 Python 應用程式 (PyQt/Tkinter)
    -   **語音轉文字 (STT):** 本地 Docker 容器 `wyoming-whisper`
    -   **自然語言理解 (NLU):** 本地 Docker 容器 `ollama`
    -   **後端通訊:** 直接呼叫 Odoo API

---

## 3. 網路基礎設施

採用 Ubiquiti UniFi 解決方案，建立穩定、安全且易於管理的網路環境。

-   **路由器/閘道器:** EdgeRouter X / UniFi Security Gateway
-   **交換器:** UniFi Switch 8 (PoE)
-   **無線網路基地台 (AP):** UniFi 6 Lite / Pro AP
-   **網路規劃:**
    -   **VLAN 10 (內部):** 供 POS、印表機、本地伺服器等核心設備使用。
    -   **VLAN 20 (訪客):** 供顧客使用，與內部網路完全隔離。

---

## 4. 設備管理 (MDM)

-   **管理框架:** Android Enterprise
-   **管理平台:** Samsung Knox Manage 或 Microsoft Intune for Android
-   **核心策略:**
    -   **零接觸註冊 (Zero-Touch Enrollment)**
    -   **專用設備鎖定 (Kiosk Mode)**
    -   **遠端網路與安全策略配置**
