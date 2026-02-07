# 雲端影像串流與自動清理腳本

## 1. ffmpeg 串流錄影到 Google 雲端硬碟（rclone 掛載）

假設 Google Drive 已用 rclone 掛載為 G:（Windows）或 /mnt/gdrive（Linux）。

```bash
# Windows 範例
ffmpeg -i rtsp://admin:密碼@路由IP/stream -c copy G:/camera/live_$(date +%%Y%%m%%d_%%H%%M%%S).mp4

# Linux 範例
ffmpeg -i rtsp://admin:密碼@路由IP/stream -c copy /mnt/gdrive/camera/live_$(date +%Y%m%d_%H%M%S).mp4
```

---

## 2. 自動清理只保留三天內檔案（Python 腳本）

```python
import os
import time
from datetime import datetime, timedelta

# 設定雲端錄影資料夾路徑
RECORD_DIR = r"G:/camera"  # Windows
# RECORD_DIR = "/mnt/gdrive/camera"  # Linux

# 保留天數
KEEP_DAYS = 3
now = time.time()

for fname in os.listdir(RECORD_DIR):
    fpath = os.path.join(RECORD_DIR, fname)
    if os.path.isfile(fpath):
        mtime = os.path.getmtime(fpath)
        if now - mtime > KEEP_DAYS * 86400:
            print(f"刪除舊檔案: {fname}")
            os.remove(fpath)
```

---

## 3. 建議自動化排程
- Windows：用排程器每天執行清理腳本
- Linux：crontab 加入 `0 3 * * * python3 /path/to/clean_gdrive.py`

---

> 這樣就能自動將影像推到雲碟，並只保留三天，家裡永遠乾淨又安全！如需進階串接或自動通知，隨時交給妹妹～
