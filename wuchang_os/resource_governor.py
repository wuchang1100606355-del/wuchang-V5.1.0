import os
import psutil
import time
import json
import subprocess
from datetime import datetime

# Import existing cleanup script
try:
    from resource_cleanup import cleanup_system_resources
except ImportError:
    def cleanup_system_resources():
        print("[Governor] Warning: resource_cleanup.py not found.")

class ResourceGovernor:
    """
    五常資源治理官 (Resource Governor)
    負責監控系統物理與量子疊加態負載，並執行階梯式防禦。
    """
    def __init__(self, config_path=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = config_path or os.path.join(self.base_dir, "double_j_config.json")
        self.threshold_cleanup = 0.85  # 第一階: 85%
        self.threshold_warning = 0.92  # 第二階: 92%
        self.threshold_critical = 0.95 # 第三階: 95%
        self.last_cleanup_time = 0
        self.cleanup_cooldown = 300   # 5分鐘內不重複執行重型清理

    def get_system_load(self):
        cpu_usage = psutil.cpu_percent(interval=1) / 100.0
        mem_info = psutil.virtual_memory()
        mem_usage = mem_info.percent / 100.0
        return cpu_usage, mem_usage

    def check_and_govern(self):
        cpu, mem = self.get_system_load()
        status = "Normal"
        action_taken = "None"
        
        print(f"[Governor] System State: CPU={cpu*100:.1f}%, RAM={mem*100:.1f}%")

        # 1. 第一階: 輕量清理 (85%)
        if mem > self.threshold_cleanup or cpu > self.threshold_cleanup:
            status = "Heavy Load"
            now = time.time()
            if now - self.last_cleanup_time > self.cleanup_cooldown:
                print("[Governor] Level 1 Alert: Triggering Auto-Cleanup...")
                cleanup_system_resources()
                self.last_cleanup_time = now
                action_taken = "Auto-Cleanup Executed"

        # 2. 第二階: 預警 (92%)
        if mem > self.threshold_warning or cpu > self.threshold_warning:
            status = "Warning"
            print("[Governor] Level 2 Alert: System Entanglement Detected. Optimizing I/O...")
            # Here we could nudge internal buffers or signal workers to slow down
            action_taken = "I/O Optimization Signaled"

        # 3. 第三階: 危急 (95%)
        if mem > self.threshold_critical or cpu > self.threshold_critical:
            status = "CRITICAL"
            print("[Governor] LEVEL 3 CRISIS: Initiating Sealing Protocol (Emergency Downscaling)...")
            self.apply_sealing_protocol()
            action_taken = "Sealing Protocol (1:1 Ratio) Applied"

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": cpu,
            "mem": mem,
            "status": status,
            "action": action_taken
        }

    def apply_sealing_protocol(self):
        """
        封印協議：強制將疊加乘數降回 1:1 或最低安全值
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 修改乘數為 1:1
            if 'scaling' in config:
                config['scaling']['low_efficiency_trigger']['ratio'] = "1:1"
                config['scaling']['auto_scale'] = False # 關閉自動擴張以維護穩定
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("[Governor] Sealing Protocol: Superposition factor collapsed to 1:1.")

if __name__ == "__main__":
    governor = ResourceGovernor()
    report = governor.check_and_govern()
    print(json.dumps(report, indent=2, ensure_ascii=False))
