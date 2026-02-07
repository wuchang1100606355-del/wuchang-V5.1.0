# 新北市三重區五常社區 3D 空間邏輯系統

**系統版本**: 1.0.0  
**建立時間**: 2026-01-18  
**架構基礎**: Google Earth Engine / Google Maps 3D  
**核心區域**: 五常里、五順里、仁忠里

---

## 📋 系統概述

本系統以 Google Earth 的資料結構和架構為基礎，為新北市三重區五常社區的三個里（五常里、五順里、仁忠里）建立精緻的 3D 空間邏輯，提供：

- 🌍 **3D 地球視覺化**：類似 Google Earth 的沉浸式體驗
- 📍 **行政區域精細模型**：三個里的詳細 3D 模型
- 🏗️ **建築物 3D**：真實的 3D 建築物模型
- 🗺️ **道路網路**：詳細的道路系統
- 📊 **空間資料管理**：支援 KML/KMZ、GeoJSON 等格式
- 🔍 **空間查詢**：距離計算、範圍查詢、空間分析

---

## 🏗️ 系統架構

```
spatial_3d_system/
├── models/                  # 空間資料模型
│   ├── spatial_data.py     # 空間資料結構
│   ├── village_model.py    # 里別模型
│   └── building_model.py   # 建築物模型
├── data/                    # 地理資料
│   ├── villages/           # 三個里的邊界資料
│   │   ├── wuchang_li.kml  # 五常里邊界
│   │   ├── wushun_li.kml   # 五順里邊界
│   │   └── renzhong_li.kml # 仁忠里邊界
│   ├── roads/              # 道路資料
│   └── buildings/          # 建築物資料
├── frontend/               # 前端視覺化
│   ├── earth_3d_viewer.html # 3D 地球查看器
│   └── cesium_integration.js # Cesium.js 整合
├── api/                    # API 服務
│   └── spatial_api.py      # 空間查詢 API
└── utils/                  # 工具函數
    ├── kml_parser.py       # KML 解析器
    └── geojson_handler.py  # GeoJSON 處理
```

---

## 🎯 核心區域

### 五常里 (Wuchang Li)

- **位置**: 三重區東北部
- **特色**: 仁義重劃區主要區域
- **重要設施**: 上品聊國咖啡館、五常社區發展協會
- **道路**: 仁義街、五華街、環河北路

### 五順里 (Wushun Li)

- **位置**: 三重區中部
- **特色**: 傳統商業區
- **重要設施**: 五華街商業區
- **道路**: 五華街、仁義街

### 仁忠里 (Renzhong Li)

- **位置**: 三重區西部
- **特色**: 傳統住宅區
- **重要設施**: 仁愛街、自強路五段
- **道路**: 仁愛街、自強路五段

---

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 啟動服務

```bash
python spatial_3d_system/api/spatial_api.py
```

### 訪問 3D 查看器

```
http://localhost:8080/earth-3d-viewer
```

---

## 📚 詳細文檔

- [空間資料模型](./docs/spatial_data_model.md)
- [API 文檔](./docs/api_reference.md)
- [視覺化指南](./docs/visualization_guide.md)

---

## 🔗 相關資源

- [Google Earth Engine](https://earthengine.google.com/)
- [Cesium.js 文檔](https://cesium.com/learn/cesiumjs/)
- [KML 規範](https://developers.google.com/kml/documentation)
