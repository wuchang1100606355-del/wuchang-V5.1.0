# 智生活系統：Odoo 模組對應與資料模型

## 模組分工
- wuchang_core：系統設定、帳務/通知中介、基礎安權
- wuchang_property_toolkits：物業/社區域模型（新建/擴充）
- wuchang_design_system：前置檢查頁、路由與網站頁面

## 資料模型（建議）
- estate.household：住戶/戶別/車位/聯絡資訊/權限
- estate.notice：公告（狀態、受眾、推播紀錄）
- estate.vote：投票（議題、選項、投票紀錄、權重）
- estate.parcel：包裹（承運商、追蹤碼、到貨/領取、通知）
- estate.visitor：訪客（預登記、憑證、出入記錄）
- estate.facility：公設（名稱、規則、尖峰費率）
- estate.booking：預約（時段、戶別、費用、狀態）
- estate.workorder：工單（來源、派工、進度、耗材、照片）
- estate.asset：資產台帳（設備、保固、維保日程、合規）
- estate.meter_reading：能資（錶計、讀數、異常類型）

## 視圖與權限
- 後台樹/表單視圖：household/parcel/visitor/booking/workorder/asset
- 網站頁面：公告/投票/訪客預登記/包裹自取/公設預約
- 安權分層：住戶/物業/管委/訪客；操作稽核（ir.logging）

## 流程對應
- 包裹到貨→掃碼登記→推播→自取驗證→領取完成
- 訪客預登記→QR 憑證→通關→出入稽核→事件回寫
- 工單報修→派工→進度回報→完工驗收→成本核算
- 公設預約→規則校驗→支付處理→使用稽核→回饋

## 既有功能對接
- 佈署診斷：/api/deploy/diag（健康檢查）
  - 參考： [web_login_home.py](file:///c:/wuchang%20V5.1.0/wuchang_os/addons/wuchang_design_system/controllers/web_login_home.py#L2437-L2492)
- VM 前置檢查頁：/ui/vm/precheck
  - 參考： [vm_precheck_templates.xml](file:///c:/wuchang%20V5.1.0/wuchang_os/addons/wuchang_design_system/views/vm_precheck_templates.xml)

