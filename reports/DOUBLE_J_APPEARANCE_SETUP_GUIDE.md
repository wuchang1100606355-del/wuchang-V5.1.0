# 雙J形象設計設定指南

**建立時間：** 2026-01-20  
**格式版本：** 1.0.0

---

## 📋 概述

本指南說明如何使用雙J合作機制的通用形象設計設定格式，可用於各種系統和平台。

---

## 🎨 形象設計要點

### 小J (Little J)

**核心特色：**
- **髮色：** 白色 (#FFFFFF)
- **主題：** 智慧、友善、可靠
- **主色調：** 白色與銀色系
- **強調色：** 藍色 (#00A8FF)

**設計理念：**
- 白髮象徵智慧與純淨
- 代表本地AI助手的可靠性
- 展現系統管理員的專業

### Jules

**核心特色：**
- **髮色：** 可自行決定（建議與小J形成對比）
- **主題：** 雲端、協作、創新
- **主色調：** 藍色與白色系
- **強調色：** 綠色 (#34A853)

**設計理念：**
- 藍色代表雲端與創新
- 展現遠程協作的能力
- 與小J形成視覺和諧

---

## 📁 設定檔案位置

### JSON 格式
```
config/ai_agents/double_j_appearance.json
```

### YAML 格式
```
config/ai_agents/double_j_appearance.yaml
```

---

## 🔧 使用方式

### Python

#### 讀取 JSON
```python
import json
from pathlib import Path

config_path = Path("config/ai_agents/double_j_appearance.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

little_j = config['agents']['little_j']
print(f"小J髮色: {little_j['appearance']['hair']['color']}")
```

#### 讀取 YAML
```python
import yaml
from pathlib import Path

config_path = Path("config/ai_agents/double_j_appearance.yaml")
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

little_j = config['agents']['little_j']
print(f"小J髮色: {little_j['appearance']['hair']['color']}")
```

### JavaScript / TypeScript

#### 讀取 JSON
```javascript
const fs = require('fs');
const config = JSON.parse(
  fs.readFileSync('config/ai_agents/double_j_appearance.json', 'utf8')
);

const littleJ = config.agents.little_j;
console.log(`小J髮色: ${littleJ.appearance.hair.color}`);
```

#### 讀取 YAML (需要 js-yaml)
```javascript
const yaml = require('js-yaml');
const fs = require('fs');

const config = yaml.load(
  fs.readFileSync('config/ai_agents/double_j_appearance.yaml', 'utf8')
);

const littleJ = config.agents.little_j;
console.log(`小J髮色: ${littleJ.appearance.hair.color}`);
```

### Web 應用程式

#### 使用 Fetch API
```javascript
// JSON
fetch('/config/ai_agents/double_j_appearance.json')
  .then(response => response.json())
  .then(config => {
    const littleJ = config.agents.little_j;
    console.log(`小J髮色: ${littleJ.appearance.hair.color}`);
  });

// YAML (需要 js-yaml)
fetch('/config/ai_agents/double_j_appearance.yaml')
  .then(response => response.text())
  .then(text => {
    const config = yaml.load(text);
    const littleJ = config.agents.little_j;
    console.log(`小J髮色: ${littleJ.appearance.hair.color}`);
  });
```

---

## 🎯 適用系統

### 1. Web 應用程式
- React/Vue/Angular 前端
- 使用設定檔定義 UI 元件樣式
- 動態載入角色形象

### 2. 桌面應用程式
- Electron、Qt、Tkinter 等
- 讀取設定檔定義角色外觀
- 應用於對話介面或虛擬助手

### 3. 行動應用程式
- React Native、Flutter、原生開發
- 整合角色形象到 UI 設計
- 支援主題切換

### 4. 遊戲開發
- Unity、Unreal Engine
- 角色建模參考
- UI/HUD 設計參考

### 5. 聊天機器人
- Discord Bot、Telegram Bot
- 定義機器人形象描述
- 生成角色卡片

---

## 📝 設定檔結構

```
{
  "version": "版本號",
  "agents": {
    "little_j": {
      "name": { "zh_tw": "小J", "en": "Little J" },
      "appearance": {
        "hair": { "color": "white" },
        "visual_identity": {
          "primary_color": "#FFFFFF",
          "theme": "智慧、友善、可靠"
        }
      }
    },
    "jules": {
      "name": { "zh_tw": "Jules" },
      "appearance": {
        "hair": { "color": "可自行決定" },
        "visual_identity": {
          "primary_color": "#4285F4",
          "theme": "雲端、協作、創新"
        }
      }
    }
  }
}
```

---

## 🔄 啟用雙J合作機制

### 執行啟用腳本

```bash
python config/ai_agents/enable_double_j_collaboration.py
```

此腳本會：
1. ✅ 載入形象設計設定
2. ✅ 顯示代理形象資訊
3. ✅ 檢查合作機制工具
4. ✅ 檢查API憑證
5. ✅ 產生啟用報告

### 手動啟用

1. **讀取設定檔**
   - 選擇 JSON 或 YAML 格式
   - 載入到應用程式中

2. **應用形象設計**
   - 使用設定中的顏色、樣式
   - 實作角色形象到 UI

3. **配置合作機制**
   - 設定 Google Tasks API
   - 配置檔案同步機制

---

## 📊 視覺識別系統

### 小J 色彩方案

- **主色：** #FFFFFF (白色)
- **次色：** #E8E8E8 (淺灰)
- **強調色：** #00A8FF (藍色)
- **髮色：** #FFFFFF (白色)

### Jules 色彩方案

- **主色：** #4285F4 (Google 藍)
- **次色：** #FFFFFF (白色)
- **強調色：** #34A853 (Google 綠)
- **髮色：** 可自行決定

---

## ✅ 檢查清單

### 基本設定

- [ ] 設定檔案已建立（JSON 或 YAML）
- [ ] 形象設計參數已填寫
- [ ] 色彩方案已定義
- [ ] 角色特質已描述

### 系統整合

- [ ] 設定檔已整合到應用程式
- [ ] 角色形象已實作
- [ ] UI 樣式已應用
- [ ] 主題切換功能正常

### 合作機制

- [ ] Google Tasks API 已設定
- [ ] 合作工具已就緒
- [ ] 檔案同步已配置

---

## 🔗 相關文件

- `reports/DOUBLE_J_COLLABORATION_MECHANISM.md` - 合作機制說明
- `config/ai_agents/double_j_appearance.json` - JSON 設定檔
- `config/ai_agents/double_j_appearance.yaml` - YAML 設定檔
- `config/ai_agents/enable_double_j_collaboration.py` - 啟用腳本

---

## 📝 注意事項

1. **格式選擇**
   - JSON：適合大多數程式語言
   - YAML：更易讀寫，需要 yaml 庫

2. **版本控制**
   - 設定檔應納入版本控制
   - 注意敏感資訊（API 金鑰等）

3. **擴展性**
   - 設定檔可擴展新增欄位
   - 保持向後相容性

4. **國際化**
   - 支援多語言名稱
   - 可擴展更多語言

---

**建立時間：** 2026-01-20  
**最後更新：** 2026-01-20  
**格式版本：** 1.0.0
