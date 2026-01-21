# 詩意手寫風格設計系統

## 風格定義
- 字體：自然流暢之手寫字體為主視覺；標題採手寫，正文採易讀襯線/無襯線備援
- 色彩：柔和大地色系與自然色調（紙色、墨黑、土棕、森林綠、天空藍、陶紅）
- 紋理：水墨筆觸、紙張質感融入卡片與背景
- 動畫：模擬手寫過程的漸進描繪與流暢落筆

## 標準化控制
- Typography：標題`hw-title`、正文`hw-body`、色彩`ink-brush`
- Color System：CSS Token（`--paper-ivory`、`--ink-black`、`--earth-brown`等）
- Icon Set：手繪風線性圖標，使用`static/src/img/icons.svg`
- Component Library：`paper-card`、`motion-write`等基礎元件類別
- Motion Guidelines：`@keyframes handwriting`以描邊揭露方式呈現

## 設計Token管理
- 於後台「設計系統 > Token管理」維護鍵值，並同步供前端讀取
- 插件可呼叫`/wuchang/design/tokens`取得JSON以套入設計工具

## 檔案管理
- 於後台「設計系統 > 資產管理」上傳`fig/sketch/xd/ttf/otf/ase/pdf`
- 使用版本欄位維持一致性；`is_latest`標記最新版本

## 運行驗證
- UI頁面使用`poetic_handwritten.css`樣式
- 構件需遵循類別與Token命名規範

## 應用流程
1. 設計師提交資產與Token
2. 系統審核並標記最新版本
3. 前端套用樣式庫與Token
4. 定期一致性檢查與培訓
