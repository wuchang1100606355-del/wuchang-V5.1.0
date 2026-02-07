import os
import sys
import time
import logging
import requests
import schedule
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spacetime_connectors.omni_manager import SpacetimeOmniManager

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("core_sister.log")
    ]
)
logger = logging.getLogger("CoreSister")

# Global Manager Instance
omni_manager = None

def check_website_health():
    """Checks if the local website is accessible."""
    try:
        response = requests.get("http://wuchang-web:3000", timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Website Health Check Passed: http://wuchang-web:3000 is UP.")
            return True
        else:
            logger.warning(f"⚠️ Website returned status code: {response.status_code}")  
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Website Health Check Failed: {e}")
        return False

def scan_old_data():
    """Scans for critical data directories."""
    logger.info("🔍 Scanning for Old Data (尋找舊資料)...")
    important_paths = ["wuchang_life", "wuchang_os", "core_memory", "wuchang_tools_library"]
    found_count = 0
    for path in important_paths:
        full_path = os.path.join("/app", path)
        if os.path.exists(full_path):
            found_count += 1
            file_count = sum([len(files) for r, d, files in os.walk(full_path)])        
            logger.info(f"   📂 Found: {path} ({file_count} files)")
        else:
            logger.warning(f"   ❌ Missing: {path}")
    logger.info(f"📊 Data Scan Complete. Found {found_count}/{len(important_paths)} core components.")

def verify_public_welfare_mission():
    """Verifies if the public welfare mission is present in index.html."""
    try:
        index_path = "/app/index.html"
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "公益" in content or "Public Welfare" in content:
                    logger.info("✅ Public Welfare Mission Verified in index.html.")    
                else:
                    logger.warning("⚠️ 'Public Welfare' keyword not found in index.html..")
        else:
            logger.error("❌ index.html not found.")
    except Exception as e:
        logger.error(f"❌ Mission Verification Failed: {e}")

def report_spacetime_status():
    """Reports status of all spacetime connections."""
    if omni_manager:
        logger.info("🌌 Generating Spacetime System Report...")
        report = omni_manager.get_full_system_report()
        for module in report["modules"]:
            status_icon = "✅" if module["connected"] else "⚠️"
            logger.info(f"   {status_icon} [{module['name']}]: {module['status']} ({module['resource_type']})")

class CodeChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            logger.info(f"♻️ Detected code change: {event.src_path}. (Hot reload not impplemented yet)")

def start_observer():
    observer = Observer()
    observer.schedule(CodeChangeHandler(), path="/app/wuchang_tools_library", recursive=False)
    observer.start()
    return observer

def main():
    global omni_manager
    logger.info("🚀 Core AI Sister Service Started (Spacetime Enhanced).")

    # Initialize Spacetime Omni-Manager
    try:
        omni_manager = SpacetimeOmniManager()
        omni_manager.initialize_all()
    except Exception as e:
        logger.error(f"❌ Failed to initialize Spacetime Omni-Manager: {e}")

    # Initial checks
    scan_old_data()
    check_website_health()
    verify_public_welfare_mission()
    report_spacetime_status()

    # Schedule periodic checks
    schedule.every(5).minutes.do(check_website_health)
    schedule.every(1).hour.do(verify_public_welfare_mission)
    schedule.every(10).minutes.do(report_spacetime_status) # Periodic status report     

    # Start file watcher
    observer = start_observer()

    logger.info("💓 Heartbeat loop started. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:36:53
---
