# Wuchang OS 系統範本（人類可讀）

## 概述
- 名稱：Wuchang OS（五常社區作業系統）
- 範圍：身份與角色、金流與基金池、設計系統、協作與AI會議、財務AI策略
- 部署：`docker-compose.yml`（Odoo 17 + Postgres 15）、`config/odoo.conf`（`addons_path=/mnt/extra-addons`）

## 模組
- 核心（wuchang_core）
  - 夥伴擴充：住戶標記、社區角色、去識別化 Token（`addons/wuchang_core/models/res_partner.py`）
  - 設計系統：設計資產、設計Token、API（`controllers/design_api.py`）
  - 協作與會議：協作空間、協作金鑰、Google 帳號綁定、AI 會議/制度/子會議
  - 視覺樣式：`static/src/css/poetic_handwritten.css`、`static/src/img/icons.svg`
- 金流（wuchang_finance）
  - 基金池：`wuchang.fund.pool`（注資、來源類型）
  - 銷售訂單：`transaction_mode`（商業/捐贈/混合）
  - 成本事項：供應商與憑證、金額計算（`wuchang.cost.item`）
  - 財務AI策略：管理員群組、策略生成與視圖

## 資料模型（節選）
- ResPartner 擴充：`is_wuchang_resident`、`role_type`、`anonymized_token`
- wuchang.design.asset：類型（fig/sketch/xd/ttf/otf/ase/pdf）、版本、附件
- wuchang.design.token：分類（color/font/motion/spacing/size）、值、版本
- wuchang.collab.space：類型（物總幹事/社區總幹事/財務管理）、成員
- wuchang.access.key：指紋/遮罩、到期、狀態（不存明文）
- wuchang.google.account：夥伴、email、類型（個人/公益/社區總幹事）、驗證
- wuchang.ai.meeting.policy：規則、支援三方/六方機制、審批要求
- wuchang.ai.meeting：主持人、空間、制度、3人類+3AI檢核、最高權限人裁定
- wuchang.ai.meeting.session：模式（三方獨立/六方共同）、總人數檢核、開始/結束
- wuchang.fund.pool：總額、更新時間、來源類型、注資方法
- wuchang.cost.item：供應商與憑證、數量/單價/總成本（計算欄位）
- wuchang.finance.strategy：背景、建議、狀態、生成策略

## 流程（摘要）
- 登入與合規：驗證 → 必讀文件 → 角色/範圍載入 → 操作
- 交易與基金池：依 `transaction_mode` 管理交易；基金池注資與狀態維護
- 協作與會議：建立主會議 → 建立子會議（三方/六方） → 結論匯總 → 最高權限人裁定
- 設計系統：資產與Token維護 → 前端套用樣式與Token → API供插件同步
- 財務策略：讀取成本與基金池 → 生成建議 → 審查採用

## API（JSON）
- `/wuchang/design/tokens`：回傳啟用 Token 清單
- `/wuchang/design/assets?asset_type=...`：回傳啟用資產清單

## 菜單（主要）
- 五常社區 OS（根）
  - 設計系統：資產管理、Token管理
  - 協作與會議：協作空間、協作金鑰、Google 帳號綁定、AI 會議制度、AI 會議、AI 子會議
  - 金流管理：公益基金池、成本事項、策略建議

## 權限（摘要）
- 基本讀寫：`base.group_user`
- 財務管理員群組：`wuchang_finance.group_wuchang_finance_manager`
- 模型存取：`security/ir.model.access.csv`（核心與金流模組分別定義）

## 部署
- 啟動：`cd wuchang_os && docker-compose up -d`
- 升級：於後台 Apps 升級 `Wuchang Community Core` 與 `Finance`

## 安全
- 金鑰：只存指紋與遮罩，不存明文；支援到期與撤銷
- 敏感操作：建議二次驗證與審計（策略採用、金鑰設定、資產下載）

## 附錄
- 初始資料：`addons/wuchang_core/data/meeting_setup.xml`（三方會議與AI代理）
- 初始成本：`addons/wuchang_finance/data/cost_items.xml`
