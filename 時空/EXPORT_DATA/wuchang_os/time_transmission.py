import os
import json
import datetime
import uuid

class TimeTransmitter:
    """
    時光傳輸協議 (Time Transmission Protocol)
    
    負責將系統內的所有關鍵操作與狀態變更，即時寫入「時光串流 (Time Stream)」中。
    這不僅是日誌，更是系統歷史的不可變紀錄，對應「時空資料庫」的概念。
    """
    
    def __init__(self, base_dir=r"C:\wuchang V5.1.0\wuchang_os"):
        self.base_dir = base_dir
        self.log_dir = os.path.join(base_dir, "time_stream")
        self.log_file = os.path.join(self.log_dir, "time_transmission_log.jsonl")
        self.ensure_stream_exists()
        
    def ensure_stream_exists(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
    def transmit(self, source, event_type, details, user="System"):
        """
        傳輸事件至時光串流
        """
        timestamp = datetime.datetime.now().isoformat()
        event_id = str(uuid.uuid4())
        
        record = {
            "id": event_id,
            "timestamp": timestamp,
            "source": source,
            "event_type": event_type,
            "user": user,
            "details": details
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"Time Transmission Failed: {e}")
            return False

    def get_recent_transmissions(self, limit=10):
        records = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        records.append(json.loads(line))
                    except:
                        pass
        return records

# Singleton Instance
transmitter = TimeTransmitter()


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:05:31
---
