# 五常社區 3D 地圖整合指南

## 概述

已為三顯示器中間顯示器添加五常社區 3D 地圖功能，使用輕量級方案，不造成系統負擔。

## 文件說明

### 1. `map_downloader.py`
- 地圖瓦片下載器
- 支持緩存機制
- 使用 OpenStreetMap（免費，無需 API Key）
- 自動計算所需瓦片數量

### 2. `map_3d_viewer.html`
- 3D 地圖查看器
- 使用 Cesium.js（輕量級 3D 地球引擎）
- 支持多種視角模式
- 本地緩存支持

### 3. `map_api_routes.py`
- 地圖 API 路由
- 提供下載、查詢、清除緩存接口

## 整合步驟

### 步驟 1: 註冊地圖路由

在 `web_ui.py` 中添加：

```python
from map_api_routes import map_bp

# 註冊地圖藍圖
app.register_blueprint(map_bp)
```

### 步驟 2: 添加地圖查看器路由

在 `web_ui.py` 中添加：

```python
@app.route('/map-3d-viewer')
def map_3d_viewer():
    map_viewer_path = os.path.join(os.path.dirname(__file__), 'map_3d_viewer.html')
    if os.path.exists(map_viewer_path):
        with open(map_viewer_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "地圖查看器文件未找到", 404
```

### 步驟 3: 更新響應式 UI 模組

已更新 `responsive_ui_module.py`，中間顯示器現在包含：
- 左側：控制面板（原有功能）
- 右側：3D 地圖查看器（iframe 嵌入）

## 使用方式

### 下載地圖

1. **通過 API**:
   ```bash
   curl -X POST http://localhost:5000/api/map/download \
     -H "Content-Type: application/json" \
     -d '{"zoom_level": 16}'
   ```

2. **通過 Python 腳本**:
   ```bash
   python map_downloader.py
   ```

3. **通過 UI**:
   - 在三顯示器模式的中間顯示器
   - 點擊「⬇️ 下載地圖」按鈕

### 查看地圖

1. **直接訪問**: `http://localhost:5000/map-3d-viewer`
2. **三顯示器模式**: 自動顯示在中間顯示器右側

## 功能特性

### 3D 地圖功能

- ✅ **3D 視角**: 類似 Google Earth 的 3D 展示
- ✅ **多種視角模式**: 3D、2D、哥倫布視角
- ✅ **地形支持**: Cesium 世界地形
- ✅ **多種地圖圖層**: OpenStreetMap、Bing、Mapbox 等
- ✅ **標記點**: 可添加自定義標記
- ✅ **飛行動畫**: 平滑飛到指定位置

### 性能優化

- ✅ **本地緩存**: 下載的瓦片緩存在本地
- ✅ **按需加載**: 只加載可見區域的瓦片
- ✅ **輕量級引擎**: Cesium.js 優化版本
- ✅ **離線支持**: 緩存後可離線查看

## 配置五常社區位置

在 `map_downloader.py` 和 `map_3d_viewer.html` 中修改坐標：

```python
# 五常社區坐標（根據實際位置調整）
wuchang_bounds = {
    'north': 25.10,   # 緯度
    'south': 25.08,
    'east': 121.45,   # 經度
    'west': 121.43,
    'center_lat': 25.09,
    'center_lng': 121.44,
    'zoom_level': 16
}
```

## 緩存管理

### 緩存位置
- 默認: `map_cache/` 目錄
- 可通過環境變量 `MAP_CACHE_DIR` 自定義

### 緩存內容
- 地圖瓦片: `{zoom}_{x}_{y}.png`
- 元數據: `metadata.json`

### 清除緩存
```bash
# API
curl -X POST http://localhost:5000/api/map/clear-cache

# Python
python -c "from map_downloader import MapDownloader; MapDownloader().clear_cache()"
```

## 系統負擔控制

### 優化措施

1. **緩存機制**: 下載一次，多次使用
2. **按需加載**: 只加載可見區域
3. **瓦片大小**: 使用標準 256x256 瓦片
4. **縮放級別**: 可控制下載的縮放級別
5. **異步下載**: 不阻塞主線程

### 資源使用

- **內存**: ~50-100MB（取決於緩存大小）
- **磁盤**: ~10-50MB（16級縮放，約100-500瓦片）
- **CPU**: 低（主要用於渲染）
- **網絡**: 僅首次下載需要

## 故障排除

### 地圖不顯示

1. 檢查 Cesium.js 是否加載
2. 檢查網絡連接（首次需要）
3. 檢查瀏覽器控制台錯誤

### 下載失敗

1. 檢查網絡連接
2. 檢查 OpenStreetMap 服務可用性
3. 檢查磁盤空間

### 性能問題

1. 減少縮放級別
2. 清除舊緩存
3. 使用較低分辨率瓦片

## 下一步

- [ ] 整合到 web_ui.py
- [ ] 測試地圖下載功能
- [ ] 優化緩存策略
- [ ] 添加更多標記點
