# 智生活系統：MVP 導入與佈署檢查清單

## MVP 功能
- 管理費線上繳費（既有支付串接）
- 包裹到貨通知與夜間自取
- 訪客預登記與 QR 憑證
- 工單報修與派工流程

## 佈署前檢查
- DNS 指向、SSL 憑證（Caddy/Cloudflared）
- 容器編排（system/ui profiles）： [docker-compose.yml](file:///c:/wuchang%20V5.1.0/docker-compose.yml)
- 健康檢查：/api/deploy/diag 至少一項可用（google_ok/ollama_ok/webui_ok）
- 資料庫初始化與管理帳號可登入

## 佈署後驗證
- 執行佈署健檢： [sanity_deploy_tests.ps1](file:///c:/wuchang%20V5.1.0/scripts/sanity_deploy_tests.ps1)
- VM 前置檢查頁：/ui/vm/precheck（就緒徽章）
- 公告推播/包裹通知/訪客預登記/工單派工端到端測試

## 安全與稽核
- 權限分層（住戶/物業/管委/訪客）
- 操作稽核與資料保留（交接不斷層）
- 設備憑證與韌體更新策略

