# 智生活公寓大廈管理系統：功能與架構導入指南

## 功能總覽
- 管委會與住戶管理：戶別資料、權限分層、交接歷史留存
- 財務與收費：管理費開立、線上繳費、催繳與對帳報表
- 公告與投票：公告推播、線上投票、意見回饋
- 包裹與物品：收發登記、到貨通知、夜間自取流程
- 訪客與門禁：來訪預登記、QR/臨時憑證、出入稽核
- 設施與預約：公設預約、尖峰規則、公平性保障
- 維修與工單：報修、派工、進度回報、維保履歷
- 安防與巡檢：監控整合、消防/氣體偵測、巡檢紀錄、緊急通報
- 物業資產台帳：設備台帳、保固與維保排程、合規檢查
- 社區生活服務：快遞/洗衣/叫車/居家維修等一鍵申請
- 能資與永續：水電智慧表、漏水偵測、能源分析、垃圾管理優化

## 技術架構
- 前端層：行動 App + 住戶入口、管理後台 Web
- 整合層：API Gateway/SSO、事件與通知中介（Email/SMS/Push）
- 服務域：身份與授權、收費與帳務、公告與投票、工單與維修、訪客/包裹/預約、IoT/門禁整合、即時資料與告警
- 資料層：RDB（交易）、時間序列（IoT）、物件儲存（影像/附件）
- 基礎設施：容器化部署、監控可觀測、DNS/反向代理
- 安全與合規：ISO 27001、隱私與法遵、設備憑證管理

## 與現有程式的對應
- 部署與健康檢查：`/api/deploy/diag` 端點與 UI 前置檢查頁
  - 程式： [web_login_home.py](file:///c:/wuchang%20V5.1.0/wuchang_os/addons/wuchang_design_system/controllers/web_login_home.py#L2437-L2492)
  - 頁面： [vm_precheck_templates.xml](file:///c:/wuchang%20V5.1.0/wuchang_os/addons/wuchang_design_system/views/vm_precheck_templates.xml)
- 容器編排：Odoo/Web/Caddy/Ollama/OpenWebUI
  - Compose： [docker-compose.yml](file:///c:/wuchang%20V5.1.0/docker-compose.yml)
- VM 登入就緒檢查（GCP）：`/api/gcp/vm/login_readiness`
  - 程式： [web_login_home.py](file:///c:/wuchang%20V5.1.0/wuchang_os/addons/wuchang_design_system/controllers/web_login_home.py#L4141-L4331)

## Odoo 模組設計建議
- 核心模型（新建/擴充）：
  - 住戶戶別：`estate.household`（住戶、戶別、車位、權限）
  - 公告與投票：`estate.notice`, `estate.vote`
  - 包裹管理：`estate.parcel`（狀態、通知、領取記錄）
  - 訪客/門禁：`estate.visitor`（預登記、通行憑證、出入紀錄）
  - 設施預約：`estate.facility`, `estate.booking`
  - 維修工單：`estate.workorder`（派工、進度、耗材）
  - 資產台帳：`estate.asset`（保固、維保日程、合規項）
  - 能資資料：`estate.meter_reading`（水電/用量/告警）
- 整合模式：以 `wuchang_core` 為帳務/設定中心，新增 `wuchang_property_toolkits` 擴充物業域模型與頁面；以 `wuchang_design_system` 承載前置檢查頁/安全策略路由。

## API 介接規格草案（示例）
- 訪客預登記：`POST /api/estate/visitor/preauth`
  - 入參：`name`, `id_no`, `visit_time`, `host_unit`
  - 出參：`{ ok, pass_qr, expire_ts }`
- 包裹到貨通知：`POST /api/estate/parcel/arrive`
  - 入參：`carrier`, `tracking_no`, `unit`, `arrive_ts`
  - 出參：`{ ok, parcel_id, notify_sent }`
- 公設預約：`POST /api/estate/booking/create`
  - 入參：`facility_id`, `start_ts`, `end_ts`, `unit`
  - 出參：`{ ok, booking_id }`
- 能資告警：`POST /api/estate/meter/alert`
  - 入參：`meter_id`, `type`, `value`, `ts`
  - 出參：`{ ok }`

## MVP 落地與部署檢查
- MVP 功能：線上繳費（既有支付串接）、包裹通知、訪客預登記、工單派工
- 佈署前檢：`/api/deploy/diag` 必須 `google_ok/ollama_ok/webui_ok` 至少一項可用
- 佈署後檢：執行 [sanity_deploy_tests.ps1](file:///c:/wuchang%20V5.1.0/scripts/sanity_deploy_tests.ps1)
- VM 前置檢：使用頁面 [vm_precheck_templates.xml](file:///c:/wuchang%20V5.1.0/wuchang_os/addons/wuchang_design_system/views/vm_precheck_templates.xml) 的 `/ui/vm/precheck`

## 安全與隱私要點
- 單點登入與權限分層（管委/物業/住戶/訪客）
- 操作稽核與資料保留政策（交接不斷層）
- 設備韌體與憑證管理、事件溯源

## 參考與後續
- GCP 佈署：使用腳本 [deploy_gcp_full.ps1](file:///c:/wuchang%20V5.1.0/scripts/deploy_gcp_full.ps1)（支援 `system/ui` Profile）
- 反向代理與外網：Caddy/Cloudflared，見 [docker-compose.yml](file:///c:/wuchang%20V5.1.0/docker-compose.yml)

