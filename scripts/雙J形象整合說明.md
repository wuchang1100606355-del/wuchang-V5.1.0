# 雙J形象整合說明

## 概述

已建立工具用於生成和整合雙J（地端小J和雲端小J）的形象圖片到系統中。

## 工具說明

### 1. `generate_dual_j_images.py`
**功能**：生成雙J形象圖片

**生成的圖片**：
- `little_j_avatar.png` - 地端小J形象（白髮小姑娘）
- `jules_avatar.png` - 雲端小J (JULES) 形象
- `dual_j_collaboration.png` - 雙J協作形象

**使用方式**：
```bash
# 設定 API Key
$env:WUCHANG_LLM_API_KEY = "your-api-key-here"

# 執行生成
python generate_dual_j_images.py
```

**圖片規格**：
- 格式：PNG
- 尺寸：1024x1024 像素
- 背景：透明背景（適合頭像使用）
- 風格：現代動漫風格（地端小J）、專業數位藝術風格（雲端小J）

### 2. `integrate_dual_j_images.py`
**功能**：整合雙J形象圖片到系統中

**整合位置**：
- 首頁（`index.html`）- 新增「雙J協作系統」區塊
- 導航列 - 加入「雙J協作」連結
- 圖片索引 - 建立 `dual_j_images_index.json`

**使用方式**：
```bash
python integrate_dual_j_images.py
```

## 圖片存放位置

生成的圖片將存放在：
```
static/images/dual_j/
├── little_j_avatar.png          # 地端小J形象
├── jules_avatar.png             # 雲端小J形象
├── dual_j_collaboration.png     # 雙J協作形象
└── dual_j_images_index.json     # 圖片索引
```

## 形象設計說明

### 地端小J（Little J）
- **形象**：白髮小姑娘
- **身份**：本地 LLM 助理
- **特點**：
  - 可愛、友善的外觀
  - 現代、科技感風格
  - 專業但親近
  - 適合社區發展 AI 助理

### 雲端小J (JULES)
- **形象**：專業 AI 助理
- **身份**：雲端 LLM 執行者
- **特點**：
  - 現代、專業的 AI 助理外觀
  - 雲端、科技主題
  - 友善但專業的氣質
  - 適合雲端 AI 服務

### 雙J協作
- **形象**：兩個 AI 助理協作
- **主題**：協作、團隊合作
- **特點**：
  - 兩個 AI 助理角色（地端小J和雲端小J）
  - 協作主題：共同工作、分享資訊
  - 現代、專業風格
  - 適合橫幅或標題使用

## 整合到系統

### 首頁整合

已自動整合到 `index.html`，包含：
- 雙J協作系統區塊
- 地端小J介紹卡片
- 雲端小J (JULES) 介紹卡片
- 雙J協作介紹卡片

### UI 整合

可在以下位置使用雙J形象：
- 浮動圖示（`little_j_floating_icon.py`）
- 控制中心 UI（`wuchang_control_center.html`）
- 工作日誌頁面（`dual_j_work_log.html`）

## 使用步驟

### 步驟 1：生成圖片

1. 設定 API Key：
   ```powershell
   $env:WUCHANG_LLM_API_KEY = "your-api-key-here"
   ```

2. 執行生成：
   ```bash
   python generate_dual_j_images.py
   ```

3. 檢查生成的圖片：
   - `static/images/dual_j/little_j_avatar.png`
   - `static/images/dual_j/jules_avatar.png`
   - `static/images/dual_j/dual_j_collaboration.png`

### 步驟 2：整合到系統

1. 執行整合工具：
   ```bash
   python integrate_dual_j_images.py
   ```

2. 檢查整合結果：
   - 首頁是否包含「雙J協作系統」區塊
   - 導航列是否包含「雙J協作」連結
   - 圖片索引是否已建立

### 步驟 3：驗證

1. 開啟首頁：`http://localhost:5000` 或 `https://wuchang.life`
2. 檢查「雙J協作系統」區塊是否正常顯示
3. 確認圖片載入正常

## 圖片要求

### 地端小J頭像
- **檔案名**：`little_j_avatar.png`
- **尺寸**：至少 256x256 像素（建議 512x512）
- **格式**：PNG（透明背景）
- **風格**：現代動漫風格，白髮小姑娘

### 雲端小J頭像
- **檔案名**：`jules_avatar.png`
- **尺寸**：至少 256x256 像素（建議 512x512）
- **格式**：PNG（透明背景）
- **風格**：現代數位藝術風格，專業 AI 助理

### 雙J協作圖片
- **檔案名**：`dual_j_collaboration.png`
- **尺寸**：1024x512 或類似橫幅格式
- **格式**：PNG（透明或簡約背景）
- **風格**：現代數位插畫，展示協作主題

## 手動上傳圖片

如果不想使用 API 生成，可以手動上傳圖片：

1. 準備圖片檔案（符合上述規格）
2. 將圖片放入 `static/images/dual_j/` 目錄
3. 命名為：
   - `little_j_avatar.png`
   - `jules_avatar.png`
   - `dual_j_collaboration.png`
4. 執行 `python integrate_dual_j_images.py` 進行整合

## 注意事項

1. **API 費用**：使用 OpenAI DALL-E 3 會產生費用
2. **每日額度**：預設每日 10 次，可透過 `WUCHANG_IMAGE_DAILY_LIMIT` 調整
3. **圖片版權**：生成的圖片屬於使用者所有
4. **網路連線**：需要網路連線以下載圖片

## 故障排除

### 問題：未設定 API Key
**解決方案**：設定 `WUCHANG_LLM_API_KEY` 環境變數

### 問題：已達每日額度上限
**解決方案**：
- 等待明日自動重置
- 或調整 `WUCHANG_IMAGE_DAILY_LIMIT` 環境變數

### 問題：圖片未顯示
**解決方案**：
- 檢查圖片檔案是否存在
- 檢查檔案路徑是否正確
- 檢查瀏覽器控制台是否有錯誤

### 問題：整合失敗
**解決方案**：
- 檢查 `index.html` 檔案權限
- 檢查檔案編碼是否為 UTF-8
- 手動檢查 HTML 結構

## 下一步

1. 設定 API Key 並生成圖片
2. 執行整合工具
3. 驗證首頁顯示
4. 根據需要調整圖片和樣式
