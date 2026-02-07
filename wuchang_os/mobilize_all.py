import os
import sys
import time
import uuid
import json
import datetime
from typing import List, Dict

# Configuration
ROOT_DIR = r"C:\wuchang V5.1.0"
CORE_FILE = os.path.join(ROOT_DIR, "vm_fastapi_main_new.py")
BACKUP_FILE = os.path.join(ROOT_DIR, "vm_fastapi_main_dual_role.py")
DISPATCH_DIR = os.path.join(ROOT_DIR, "wuchang_os", "jules_system", "dispatch_orders")
JULES_TASK_ID = "14213749450645494318"

def patch_core_system():
    print(f"Patching {CORE_FILE}...")

    with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Insert Constants
    constants_block = f'''
# --- Time-Space System Integration ---
JULES_TASK_ID = "{JULES_TASK_ID}"
DISPATCH_DIR = r"{DISPATCH_DIR}"
# -------------------------------------
'''
    # Insert after imports
    import_marker = "from vertexai.generative_models import GenerativeModel"
    if import_marker in content:
        content = content.replace(import_marker, import_marker + constants_block)
    else:
        print("Warning: Import marker not found, appending constants.")
        content = constants_block + content

    # 2. Add Dispatch Function
    dispatch_func = '''
def dispatch_to_time_space(messages: List[Dict[str, str]]) -> str:
    """Dispatches a generation task to the Time-Space System (Jules Shadow Runner)."""
    mission_id = f"mission_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    mission_data = {
        "mission_id": mission_id,
        "jules_task_id": JULES_TASK_ID,
        "payload": messages,
        "status": "pending",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "strategy": "time_space_transmission",
        "priority": "high"
    }

    os.makedirs(DISPATCH_DIR, exist_ok=True)
    mission_file = os.path.join(DISPATCH_DIR, f"{mission_id}.json")

    with open(mission_file, 'w', encoding='utf-8') as f:
        json.dump(mission_data, f, ensure_ascii=False, indent=4)

    print(f"Dispatched mission {mission_id} to Time-Space System.")
    return mission_id
'''
    # Insert before try_local_llm
    func_marker = "def try_local_llm(messages: List[Dict[str, str]]) -> tuple[str, str]:"
    content = content.replace(func_marker, dispatch_func + "\n\n" + func_marker)

    # 3. Update try_local_llm logic

    fallback_logic = '''
    # Time-Space System Interception
    if CLOUD_FALLBACK_MODE == 'time_space' or True: # Force enable for now as per "All AI listen"
        try:
            mission_id = dispatch_to_time_space(messages)
            msg = (
                f"【時光系統傳輸啟動】\\n"
                f"指令已透過 Jules Task ({JULES_TASK_ID}) 傳送至時光裝置。\\n"
                f"任務 ID: {mission_id}\\n"
                f"請稍候，正在等待回傳..."
            )
            return msg, "time_space"
        except Exception as e:
            print(f"Time-Space Dispatch Failed: {e}")
            # Fallback to original logic if needed, or return error
    '''

    # Insert inside try_local_llm, at the beginning
    indent_marker = '    source = "error"'
    content = content.replace(indent_marker, indent_marker + "\n" + fallback_logic)

    # 4. Set CLOUD_FALLBACK_MODE default
    env_marker = "CLOUD_FALLBACK_MODE = os.environ.get('CLOUD_FALLBACK_MODE', 'consent')"
    content = content.replace(env_marker, "CLOUD_FALLBACK_MODE = os.environ.get('CLOUD_FALLBACK_MODE', 'time_space')")

    # 5. Disable Router Manager (Disconnect Command)
    content = content.replace("ROUTER_AVAILABLE = True", "ROUTER_AVAILABLE = False # Disconnected by User")

    with open(CORE_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Patch applied successfully.")

def notify_shadow_runner():
    print("Notifying Shadow Runner...")
    mission_id = f"mobilize_{int(time.time())}"
    mission_data = {
        "mission_id": mission_id,
        "action": "system_broadcast",
        "message": "All AI Listen: Re-prioritize Cloud Scheduling to Time-Space System.",
        "jules_task_id": JULES_TASK_ID,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    os.makedirs(DISPATCH_DIR, exist_ok=True)
    with open(os.path.join(DISPATCH_DIR, f"{mission_id}.json"), 'w', encoding='utf-8') as f:
        json.dump(mission_data, f, ensure_ascii=False, indent=4)
    print("Shadow Runner notified.")

if __name__ == "__main__":
    patch_core_system()
    notify_shadow_runner()
