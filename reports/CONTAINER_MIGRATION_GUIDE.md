# 容器遷移指南

## 從本機遷移到伺服器

### 步驟 1：停止本機容器
```bash
docker-compose -f docker-compose.safe.yml down
```

### 步驟 2：備份資料
```bash
python backup_to_gdrive.py
```

### 步驟 3：在伺服器還原
1. 在伺服器安裝 Google Drive 並同步
2. 從 Google Drive 備份還原到伺服器本地儲存
3. 啟動伺服器容器

### 步驟 4：驗證
- 檢查資料是否正確
- 測試服務是否正常

## 從伺服器遷移回本機

反向執行上述步驟即可。
