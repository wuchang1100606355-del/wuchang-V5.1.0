# 五常社區 OS - 設計系統 (Design System)

**版本**: 1.0.0  
**日期**: 2026-01-08  
**設計師**: Claude Haiku 4.5 AI  
**品牌**: 新北市五常社區發展協會

---

## 📐 設計原則

### 核心理念

-   **信任第一** - 透明、可信任的視覺設計
-   **易用性優先** - 簡潔清晰，減少認知負荷
-   **社區溫度** - 既現代又親近，科技與人文平衡
-   **無障礙設計** - 考慮所有使用者（視覺、聽覺、運動障礙）

---

## 🎨 色彩系統 (Color System)

### 主色板 (Primary Palette)

```css
/* 品牌主色：深藍綠 - 代表信任、穩定、智慧 */
--color-primary-dark: #0f4c3a; /* RGB(15, 76, 58) */
--color-primary: #1b5e5d; /* RGB(27, 94, 93) - 主用色 */
--color-primary-light: #2a7a77; /* RGB(42, 122, 119) */
--color-primary-lighter: #4aaea8; /* RGB(74, 174, 168) */

/* 輔助色：生活綠 - 代表成長、活力、社區 */
--color-accent-dark: #2e7d54;
--color-accent: #4caf50; /* RGB(76, 175, 80) - 確認、成功 */
--color-accent-light: #81c784;
--color-accent-lighter: #c8e6c9;

/* 強調色：金色 - 代表價值、榮耀、認可 */
--color-highlight-dark: #b8860b;
--color-highlight: #ffb700; /* RGB(255, 183, 0) - 特色、推薦 */
--color-highlight-light: #ffd54f;

/* 中性色 - 文字、背景、邊框 */
--color-neutral-900: #1a1a1a; /* 最深 - 主文字 */
--color-neutral-800: #2e2e2e; /* 副文字 */
--color-neutral-700: #424242; /* 標籤、小字 */
--color-neutral-600: #616161; /* 禁用狀態 */
--color-neutral-500: #757575; /* 提示文字 */
--color-neutral-400: #bdbdbd; /* 邊框、分隔線 */
--color-neutral-300: #e0e0e0; /* 淺邊框 */
--color-neutral-200: #f5f5f5; /* 背景色 */
--color-neutral-100: #fafafa; /* 淺背景 */
--color-white: #ffffff; /* 純白 */

/* 語義色 */
--color-success: #4caf50; /* 成功 - 綠 */
--color-warning: #ff9800; /* 警告 - 橙 */
--color-error: #f44336; /* 錯誤 - 紅 */
--color-info: #2196f3; /* 資訊 - 藍 */
```

### 色彩使用規則

-   **主色 (#1B5E5D)**: 品牌元素、主標題、按鈕、導覽
-   **輔色 (#4CAF50)**: 成功狀態、確認按鈕、積極行動
-   **強調色 (#FFB700)**: 推薦項目、優先內容、特殊標記
-   **中性色**: 文字、背景、邊框、禁用狀態

### 色彩無障礙檢查

所有文字與背景的對比度需達到 WCAG AA 標準：

-   正文: 最低 4.5:1 對比度
-   大字體 (18pt+): 最低 3:1 對比度

---

## 🔤 字體系統 (Typography)

### 字體堆棧

```css
/* 中文優先字體堆棧 */
--font-sans: "Noto Sans TC", "Microsoft JhengHei", "Segoe UI", system-ui,
    sans-serif;
--font-serif: "Noto Serif TC", "Georgia", serif;
--font-mono: "Monaco", "Courier New", monospace;

/* Google Fonts 引入 */
@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700;900&family=Roboto+Mono:wght@400;700&display=swap");
```

### 字體尺寸與行距 (Typographic Scale)

```css
/* 標題 (Headings) */
--text-h1: {
    font-size: 48px;
    line-height: 1.2;
    font-weight: 700;
} /* 64px mobile */
--text-h2: {
    font-size: 36px;
    line-height: 1.25;
    font-weight: 700;
} /* 48px mobile */
--text-h3: {
    font-size: 28px;
    line-height: 1.3;
    font-weight: 600;
} /* 32px mobile */
--text-h4: {
    font-size: 24px;
    line-height: 1.33;
    font-weight: 600;
} /* 28px mobile */
--text-h5: {
    font-size: 20px;
    line-height: 1.4;
    font-weight: 600;
} /* 24px mobile */
--text-h6: {
    font-size: 16px;
    line-height: 1.5;
    font-weight: 600;
} /* 18px mobile */

/* 本文 (Body) */
--text-body-lg: {
    font-size: 18px;
    line-height: 1.6;
    font-weight: 400;
} /* 大本文 */
--text-body: {
    font-size: 16px;
    line-height: 1.6;
    font-weight: 400;
} /* 標準本文 */
--text-body-sm: {
    font-size: 14px;
    line-height: 1.57;
    font-weight: 400;
} /* 小本文 */

/* 標籤與小文字 (Labels & Small) */
--text-label: {
    font-size: 12px;
    line-height: 1.33;
    font-weight: 600;
} /* 標籤 */
--text-caption: {
    font-size: 12px;
    line-height: 1.33;
    font-weight: 400;
} /* 說明文字 */
--text-xsmall: {
    font-size: 11px;
    line-height: 1.45;
    font-weight: 400;
} /* 極小文字 */
```

### 字體權重使用

-   **300 (Light)**: 副標題、次要文字
-   **400 (Regular)**: 本文、說明
-   **500 (Medium)**: 標籤、特色文字
-   **600 (Semibold)**: 標題、強調
-   **700 (Bold)**: 大標題、品牌文字
-   **900 (Black)**: 極少使用、特殊強調

---

## 📏 間距系統 (Spacing System)

```css
/* 8px 基準間距系統 */
--space-xs: 4px; /* 0.25rem */
--space-sm: 8px; /* 0.5rem */
--space-md: 16px; /* 1rem */
--space-lg: 24px; /* 1.5rem */
--space-xl: 32px; /* 2rem */
--space-xxl: 48px; /* 3rem */
--space-xxxl: 64px; /* 4rem */
--space-huge: 96px; /* 6rem */

/* 使用規則 */
--padding-card: var(--space-lg); /* 卡片內邊距 */
--padding-section: var(--space-xxl); /* 區塊內邊距 */
--margin-component: var(--space-md); /* 組件外邊距 */
--margin-section: var(--space-huge); /* 區塊外邊距 */
```

---

## 🎯 圓角與邊框 (Radius & Borders)

```css
/* 圓角 */
--radius-none: 0px; /* 無圓角 */
--radius-sm: 4px; /* 小圓角 - 按鈕、輸入框 */
--radius-md: 8px; /* 中圓角 - 卡片、標籤 */
--radius-lg: 12px; /* 大圓角 - 模態框 */
--radius-xl: 16px; /* 特大圓角 - 英雄區角落 */
--radius-full: 9999px; /* 完全圓形 - 徽章、頭像 */

/* 邊框 */
--border-thin: 1px solid var(--color-neutral-300);
--border-standard: 1px solid var(--color-neutral-400);
--border-thick: 2px solid var(--color-neutral-600);
--border-primary: 2px solid var(--color-primary);
--border-accent: 2px solid var(--color-accent);
```

---

## 💨 陰影系統 (Shadow System)

```css
/* 陰影層級 */
--shadow-none: none;
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* 應用規則 */
--shadow-card: var(--shadow-md); /* 卡片 */
--shadow-hover: var(--shadow-lg); /* 懸停狀態 */
--shadow-modal: var(--shadow-2xl); /* 模態框 */
--shadow-input-focus: 0 0 0 3px rgba(27, 94, 93, 0.1); /* 輸入框焦點 */
```

---

## 🔀 過渡與動畫 (Transitions & Animations)

```css
/* 過渡時間 */
--transition-fast: 150ms ease-in-out;
--transition-normal: 250ms ease-in-out;
--transition-slow: 350ms ease-in-out;

/* 常見過渡 */
--transition-color: color var(--transition-normal), background-color var(--transition-normal);
--transition-shadow: box-shadow var(--transition-normal);
--transition-transform: transform var(--transition-fast);
```

---

## 🎨 組件設計規範

### 按鈕 (Buttons)

```css
/* 主按鈕 */
.btn-primary {
    background-color: var(--color-primary);
    color: white;
    padding: 12px 24px;
    border-radius: var(--radius-sm);
    font-size: 16px;
    font-weight: 600;
    transition: var(--transition-color), var(--transition-shadow);
    box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
    background-color: var(--color-primary-dark);
    box-shadow: var(--shadow-md);
}

.btn-primary:active {
    transform: scale(0.98);
}

/* 次按鈕 */
.btn-secondary {
    background-color: transparent;
    color: var(--color-primary);
    border: var(--border-primary);
    padding: 11px 23px; /* 視覺平衡 */
}

/* 輔助按鈕 */
.btn-tertiary {
    background-color: var(--color-neutral-200);
    color: var(--color-neutral-900);
}

/* 危險按鈕 */
.btn-danger {
    background-color: var(--color-error);
    color: white;
}

/* 按鈕大小 */
.btn-lg {
    padding: 16px 32px;
    font-size: 18px;
}
.btn-md {
    padding: 12px 24px;
    font-size: 16px;
}
.btn-sm {
    padding: 8px 16px;
    font-size: 14px;
}
```

### 卡片 (Cards)

```css
.card {
    background-color: white;
    border-radius: var(--radius-md);
    border: var(--border-thin);
    padding: var(--padding-card);
    box-shadow: var(--shadow-sm);
    transition: var(--transition-shadow), var(--transition-transform);
}

.card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
}

.card-header {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: var(--space-md);
    color: var(--color-primary);
}

.card-content {
    font-size: 14px;
    line-height: 1.6;
    color: var(--color-neutral-700);
}

.card-footer {
    margin-top: var(--space-md);
    padding-top: var(--space-md);
    border-top: var(--border-thin);
}
```

### 輸入框 (Form Inputs)

```css
.input {
    width: 100%;
    padding: 12px 16px;
    border: var(--border-standard);
    border-radius: var(--radius-sm);
    font-size: 16px;
    font-family: var(--font-sans);
    transition: var(--transition-color), var(--transition-shadow);
}

.input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: var(--shadow-input-focus);
}

.input:disabled {
    background-color: var(--color-neutral-100);
    color: var(--color-neutral-600);
    cursor: not-allowed;
}

.input-error {
    border-color: var(--color-error);
    box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.1);
}

.input-success {
    border-color: var(--color-success);
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}
```

---

## 📱 響應式斷點 (Breakpoints)

```css
--breakpoint-xs: 320px; /* 超小手機 */
--breakpoint-sm: 480px; /* 手機 */
--breakpoint-md: 768px; /* 平板 */
--breakpoint-lg: 1024px; /* 桌面 */
--breakpoint-xl: 1280px; /* 大桌面 */
--breakpoint-2xl: 1536px; /* 超大桌面 */

/* 媒體查詢示例 */
@media (max-width: 768px) {
    /* 平板及以下 */
}

@media (min-width: 769px) and (max-width: 1023px) {
    /* 僅平板 */
}

@media (min-width: 1024px) {
    /* 桌面及以上 */
}
```

---

## ♿ 無障礙設計 (Accessibility)

### WCAG 2.1 AA 標準

-   ✅ 色彩對比度: 正文 4.5:1, 大字體 3:1
-   ✅ 焦點指示器: 清晰可見（最少 2px）
-   ✅ 鍵盤導覽: 所有互動元素可用 Tab 鍵訪問
-   ✅ 讀屏器支持: 使用語義 HTML + ARIA 屬性
-   ✅ 動畫考慮: 提供 `prefers-reduced-motion` 選項

### 實作範例

```html
<!-- 按鈕 -->
<button aria-label="關閉選單" onclick="closeMenu()">
    <span aria-hidden="true">×</span>
</button>

<!-- 表單標籤 -->
<label for="email">電子郵件 <span aria-label="必填">(必填)</span></label>
<input id="email" type="email" required />

<!-- 跳過連結 -->
<a href="#main-content" class="skip-link">跳過導覽，進入主要內容</a>
```

---

## 🖼️ 圖片與媒體指南

### 圖片規格

-   **英雄區背景**: 1920×600px (桌面), 768×400px (平板), 360×300px (手機)
-   **卡片圖片**: 400×300px (16:9 比例)
-   **圖示**: 24×24px, 32×32px, 48×48px (SVG 優先)
-   **頭像**: 64×64px, 128×128px (圓形, 1:1 比例)

### 圖片優化

-   格式: WebP (主), PNG (備用)
-   壓縮: 保持質量的同時盡量減小檔案大小
-   延遲載入: 使用 `loading="lazy"` 屬性

---

## 📊 網格系統 (Grid System)

```css
/* 12 列網格系統 */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-lg);
}

.grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: var(--space-lg);
}

/* 響應式列數 */
@media (max-width: 768px) {
    .grid {
        grid-template-columns: repeat(6, 1fr);
    }
}

@media (max-width: 480px) {
    .grid {
        grid-template-columns: 1fr;
    }
}

/* 欄位跨度 */
.col-1 {
    grid-column: span 1;
}
.col-2 {
    grid-column: span 2;
}
.col-3 {
    grid-column: span 3;
}
.col-4 {
    grid-column: span 4;
}
.col-6 {
    grid-column: span 6;
}
.col-12 {
    grid-column: span 12;
}
```

---

## 🚀 效能考量 (Performance)

-   **CSS 檔案**: 壓縮後 < 50KB
-   **圖片優化**: WebP 格式, 平均 < 200KB
-   **載入時間**: 首屏 < 2 秒 (LCP), FID < 100ms, CLS < 0.1
-   **懶加載**: 視口外的圖片和組件延遲載入

---

## 📚 參考資源

-   [Google Material Design 3](https://m3.material.io/)
-   [WCAG 2.1 無障礙指南](https://www.w3.org/WAI/WCAG21/quickref/)
-   [Web Vitals](https://web.dev/vitals/)

---

**設計系統文件版本控制**: 由 Claude Haiku 4.5 自動化生成與維護  
**最後更新**: 2026-01-08
