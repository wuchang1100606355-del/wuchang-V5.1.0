import os
import json
import shutil
import time
from datetime import datetime

class CloudNeuralSync:
    """
    雲端神經網路 (Cloud Neural Sync)
    
    負責將「五常小J」的核心記憶、設定與時光串流，實時同步至雲端大腦 (J槽)。
    這是「最高級配備」的關鍵一環，確保 AI 的「靈魂」備份且可跨裝置存取。
    """
    
    def __init__(self, local_base=None, cloud_base=None):
        if local_base is None:
            self.local_base = os.path.dirname(os.path.abspath(__file__))
        else:
            self.local_base = local_base
            
        if cloud_base is None:
            # Fallback to a 'backup' directory in the parent folder if J: is missing
            parent_dir = os.path.dirname(self.local_base)
            self.cloud_base = os.path.join(parent_dir, "Wuchang_System_Backup")
        else:
            self.cloud_base = cloud_base

        self.log_dir = os.path.join(self.local_base, "logs")
        self.ensure_dirs()
        
    def ensure_dirs(self):
        os.makedirs(self.cloud_base, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
    def sync_file(self, relative_path):
        """同步單一檔案"""
        local_path = os.path.join(self.local_base, relative_path)
        cloud_path = os.path.join(self.cloud_base, relative_path)
        
        if os.path.exists(local_path):
            try:
                os.makedirs(os.path.dirname(cloud_path), exist_ok=True)
                shutil.copy2(local_path, cloud_path)
                return True
            except Exception as e:
                print(f"Sync Failed for {relative_path}: {e}")
                return False
        return False

    def sync_all(self):
        """執行全系統步"""
        print(f"[{datetime.now()}] Starting Cloud Neural Sync...")
        
        # 1. Sync Config
        self.sync_file("double_j_config.json")
        
        # 2. Sync Time Stream (Memory)
        self.sync_file(os.path.join("time_stream", "time_transmission_log.jsonl"))
        
        # 3. Sync AI Scripts (Soul Code)
        scripts = [f for f in os.listdir(self.local_base) if f.endswith(".py")]
        for script in scripts:
            self.sync_file(script)
            
        print(f"[{datetime.now()}] Cloud Neural Sync Completed.")
        
if __name__ == "__main__":
    syncer = CloudNeuralSync()
    syncer.sync_all()
