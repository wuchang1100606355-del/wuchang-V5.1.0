# 前後台響應式美化技術架構

## CSS 資產策略
- 設計令牌：使用 CSS 變數於 `:root` 定義色彩/字體/間距
- 原子工具：間距/排版/顏色/顯示的工具類（如 `.mt-2`, `.text-muted`）
- 元件樣式：卡片/表單/表格/按鈕/徽章/模態的語義化類別
- 主題：支持亮/暗色切換（`[data-theme="dark"]`）

## 檔案與位置（建議）
- `wuchang_os/addons/wuchang_design_system/static/src/css/variables.css`
- `wuchang_os/addons/wuchang_design_system/static/src/css/utilities.css`
- `wuchang_os/addons/wuchang_design_system/static/src/css/components.css`
- `wuchang_os/addons/wuchang_design_system/static/src/css/layouts.css`

## 載入與效能
- 首屏關鍵樣式內聯於主要模板（首頁/登入）
- 其他 CSS 以延遲或分頁載入；避免阻塞渲染
- 圖片與圖示壓縮，使用 SVG 優先

## 與 Odoo 整合
- QWeb 視圖中標準化 class 命名；保留既有結構
- 模板擴充：透過 `xpath` 注入樣式連結與容器 class
- 不修改核心控制器行為，僅增強視覺層

## 響應式工具
- 斷點媒體查詢：`--break-sm/md/lg/xl` 對應 `@media`
- Grid/Flex 版型工具：`.row`, `.col-*`, `.d-flex`, `.gap-*`

## 開發流程
- 漸進導入：先首頁/登入/VM 前置檢查頁，再擴展列表/表單
- 可觀測：開發環境開啟瀏覽器 DevTools 規範檢查
- 無障礙：對比度、焦點可視、鍵盤導航

## 風險控管
- 與既有 CSS 衝突：以命名空間前綴 `whc-` 降低影響
- 回退機制：頁面層級可切換新/舊樣式

