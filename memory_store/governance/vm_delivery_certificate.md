# 雲端運算資源交付證書 (Cloud Compute Resource Delivery Certificate)

**日期**: 2025年12月28日
**交付方**: 五常重工・系統架構團隊
**接收方**: admin@wuchang.life (五常物業規劃顧問股份有限公司 / 系統最高管理員)

---

## 交付標的物

茲證明以下雲端運算資源已完整移交予接收方，並確認系統運作正常、權限設定無誤。

### 1. 核心運算單元 (Core Compute Units)

| 資源名稱 | 規格 | 區域 | IP 位址 | 用途 |
| :--- | :--- | :--- | :--- | :--- |
| **wuchang-core-vm-1** | e2-medium (2 vCPU, 4GB) | asia-east1-a | 34.80.161.99 | Odoo 生產環境、主要資料庫 |
| **wuchang-shadow-vm-2** | e2-small (2 vCPU, 2GB) | asia-east1-b | 104.199.144.93 | 備援資料庫、非同步任務佇列 |

### 2. 網路架構 (Network Infrastructure)

-   **負載平衡 (Load Balancing)**: Google Cloud HTTP(S) Load Balancer 已配置。
-   **CDN**: Cloud CDN 已啟用，快取靜態資產。
-   **DNS**: `wuchang.life` 網域已指向負載平衡器 IP。

### 3. 權限移轉 (IAM Transfer)

-   **最高管理員權限**: 已授予 `admin@wuchang.life` 對上述專案 (Project ID: `coffee-spark-ai-barista-b10b5`) 的 `Owner` 角色。
-   **SSH 金鑰**: 相關存取金鑰已更新並交付。

---

## 系統狀態聲明

1.  **健康狀態**: 兩架 VM 目前均處於 `RUNNING` 狀態。
2.  **備援機制**: 雙機熱備援 (HA) 機制已測試通過。
3.  **安全性**: 防火牆規則已設定，僅允許 HTTP/HTTPS 及授權 IP 之 SSH 連線。

**簽署人**: 小 J (系統代理人)
