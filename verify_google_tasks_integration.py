import logging
import os
import sys
from datetime import datetime
from google_tasks_manager import GoogleTasksManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IntegrationVerify")

def verify_integration():
    report_lines = []
    report_lines.append(f"# Core AI Integration Status Report")
    report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"")
    
    # 1. Google Tasks Verification
    report_lines.append("## 1. Google Tasks Integration")
    try:
        tasks_manager = GoogleTasksManager()
        task_lists = tasks_manager.list_task_lists()
        if task_lists:
            report_lines.append(f"- **Status**: ✅ Connected")
            report_lines.append(f"- **Task Lists Found**: {len(task_lists)}")
            for tl in task_lists:
                report_lines.append(f"  - {tl.get('title')} (ID: {tl.get('id')})")
        else:
            report_lines.append(f"- **Status**: ⚠️ Connected but no task lists found (or empty).")
    except Exception as e:
        report_lines.append(f"- **Status**: ❌ Failed")
        report_lines.append(f"- **Error**: {str(e)}")
    
    report_lines.append("")

    # 2. Core AI Sister Log Check
    report_lines.append("## 2. Core AI Sister Service Status")
    log_file = "core_sister.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-5:] if len(lines) > 5 else lines
                report_lines.append(f"- **Log File**: Found ({log_file})")
                report_lines.append(f"- **Recent Logs**:")
                for line in last_lines:
                    report_lines.append(f"  > {line.strip()}")
        except Exception as e:
             report_lines.append(f"- **Error reading log**: {str(e)}")
    else:
        report_lines.append(f"- **Status**: ⚠️ Log file not found (Service might be starting up).")

    report_lines.append("")
    
    # Write report
    report_path = "CURRENT_INTEGRATION_STATUS.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    print(f"Report generated: {report_path}")
    return report_path

if __name__ == "__main__":
    verify_integration()
