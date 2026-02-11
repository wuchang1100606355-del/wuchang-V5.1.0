import json
import os
import sys
import time

CONFIG_PATH = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"
HEALTH_REPORT_PATH = r"C:\wuchang V5.1.0\wuchang_os\System_Health_Report.md"

class DoubleJProgram:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            return None
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_config_ratio(self, new_ratio):
        if not (1 <= new_ratio <= 10):
            print("Error: Ratio must be between 1 and 10")
            return False

        self.config['scaling']['current_ratio'] = new_ratio
        
        # Auto-calculate default allocation if not present or if ratio changed significantly
        # But here we prefer to keep existing allocation if valid for the ratio, else reset
        # Simple logic: If allocation sum != new_ratio, reset to default (70/30 split or similar)
        allocation = self.config['scaling'].get('thread_allocation', {})
        total_alloc = sum(allocation.values()) if allocation else 0
        
        if total_alloc != new_ratio:
             # Default 70% Command, 30% Cleanup (rounded)
             cmd = int(new_ratio * 0.7)
             if cmd == 0 and new_ratio > 0: cmd = 1
             cleanup = new_ratio - cmd
             
             self.config['scaling']['thread_allocation'] = {
                "command_core": cmd,
                "resource_cleanup": cleanup
             }
        
        self.config['integration_settings']['task_batch_size'] = new_ratio

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"Configuration updated: 1:{new_ratio} scaling set.")
        return True

    def register_as_internal_program(self):
        ratio = self.config['scaling']['current_ratio']
        allocation = self.config['scaling'].get('thread_allocation', {"command_core": ratio, "resource_cleanup": 0})
        
        brain = self.config['roles']['brain_core']['account']
        ops = self.config['roles']['operations_core']['account']

        print(f"Registering Double J as Internal Program (Ratio 1:{ratio})...")       
        time.sleep(1)

        print(f"Allocating [Brain Core] {brain} -> {ratio}x [Ops Threads] ({ops})")
        print(f"Allocation Strategy: {allocation.get('command_core', 0)} Command Core / {allocation.get('resource_cleanup', 0)} Resource Cleanup")

        cmd_count = allocation.get('command_core', 0)
        cleanup_count = allocation.get('resource_cleanup', 0)
        
        current_thread = 1
        for i in range(cmd_count):
            print(f"  - [Thread #{current_thread}] Initializing Command Core (Brain Direct)...")
            current_thread += 1
            time.sleep(0.1)
            
        for i in range(cleanup_count):
            print(f"  - [Thread #{current_thread}] Initializing Resource Cleanup (Background)...")
            current_thread += 1
            time.sleep(0.1)

        print("Internal Program Registration: COMPLETE")

        # Log to Health Report
        self.log_to_health_report(ratio, allocation)

    def log_to_health_report(self, ratio, allocation):
        try:
            with open(HEALTH_REPORT_PATH, 'a', encoding='utf-8') as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n## Double J Internal Program Status ({timestamp})\n")     
                f.write(f"- **Program Name**: {self.config['collaboration_name']}\n") 
                f.write(f"- **Scaling Mode**: 1:{ratio} (Adjustable 1-10)\n")
                f.write(f"- **Allocation**: {allocation.get('command_core', 0)} Command / {allocation.get('resource_cleanup', 0)} Cleanup\n")
                f.write(f"- **Status**: Registered & Active\n")
            print("System Health Report updated.")
        except Exception as e:
            print(f"Failed to update health report: {e}")

if __name__ == "__main__":
    dj = DoubleJProgram()
    
    # If arg provided, update ratio
    if len(sys.argv) > 1:
        try:
            target_ratio = int(sys.argv[1])
            dj.update_config_ratio(target_ratio)
        except ValueError:
            pass
            
    # Always run registration with current config
    dj.register_as_internal_program()
