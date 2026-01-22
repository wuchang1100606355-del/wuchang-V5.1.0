# 開發者容器設置

## 開發環境配置

### 環境變數
- `WUCHANG_DEV_MODE`: 開發模式開關
- `WUCHANG_DEBUG`: 除錯模式
- `WUCHANG_LOG_LEVEL`: 日誌級別
- `WUCHANG_DEV_WORKSPACE`: 開發工作區路徑
- `WUCHANG_DEV_LOGS`: 日誌目錄
- `WUCHANG_DEV_CACHE`: 快取目錄

### 目錄結構
```
dev/
├── logs/          # 日誌檔案
├── cache/         # 快取檔案
├── temp/          # 臨時檔案
├── backups/       # 備份檔案
├── scripts/       # 開發腳本
└── tests/         # 測試檔案
```

### 快速測試
```bash
python dev/scripts/quick_test.py
```

### 開發工具
- 快速測試腳本: `dev/scripts/quick_test.py`
- 配置檔案: `developer_container_config.json`

## 注意事項
- 開發環境預設關閉 PII 儲存功能
- 除錯模式會輸出詳細日誌
- 測試模式不會執行實際操作
