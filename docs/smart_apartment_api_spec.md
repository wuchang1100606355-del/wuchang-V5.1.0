# 智生活系統：API 介接規格草案

## 認證
- Cookie Session 或 Bearer Token（管委/物業/住戶分層）
- 速率限制與事件稽核（ir.logging）

## 端點
- 訪客預登記
  - POST /api/estate/visitor/preauth
  - 入參：name, id_no, visit_time, host_unit
  - 出參：{ ok, pass_qr, expire_ts }
- 訪客出入回寫
  - POST /api/estate/visitor/track
  - 入參：pass_qr, gate_id, action(in/out), ts
  - 出參：{ ok }
- 包裹到貨登記
  - POST /api/estate/parcel/arrive
  - 入參：carrier, tracking_no, unit, arrive_ts
  - 出參：{ ok, parcel_id, notify_sent }
- 包裹領取確認
  - POST /api/estate/parcel/pick
  - 入參：parcel_id, unit, ts, code
  - 出參：{ ok }
- 公設預約建立
  - POST /api/estate/booking/create
  - 入參：facility_id, start_ts, end_ts, unit
  - 出參：{ ok, booking_id }
- 工單建立與派工
  - POST /api/estate/workorder/create
  - 入參：title, unit, desc, photos[]
  - 出參：{ ok, workorder_id }
- 能資告警
  - POST /api/estate/meter/alert
  - 入參：meter_id, type(leak/overuse), value, ts
  - 出參：{ ok }

## 通知與整合
- 推播：公告/包裹/工單/預約變更（Email/SMS/App）
- 門禁：QR/臨時憑證/事件回寫
- 支付：管理費/預約費率（第三方支付對接）

## 健康檢查
- POST /api/deploy/diag → google_ok / ollama_ok / webui_ok
- GCP VM 就緒：POST /api/gcp/vm/login_readiness

