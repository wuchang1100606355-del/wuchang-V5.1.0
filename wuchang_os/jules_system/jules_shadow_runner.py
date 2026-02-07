import os
import time
import json
import shutil
import glob
import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SHADOW UNIT] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("C:/wuchang V5.1.0/wuchang_os/jules_system/shadow_runner.log"),
        logging.StreamHandler()
    ]
)

DISPATCH_DIR = "C:/wuchang V5.1.0/wuchang_os/jules_system/dispatch_orders"
DATA_DIR = "C:/wuchang V5.1.0/wuchang_os/jules_system/jules_data"
SEARCH_ROOT = "J:/共用雲端硬碟/五常雲端空間"

def process_mission(mission_file):
    try:
        with open(mission_file, 'r', encoding='utf-8') as f:
            mission = json.load(f)
        
        if mission.get('status') == 'completed':
            return

        mission_id = mission['mission_id']
        logging.info(f"Processing Mission: {mission_id}")

        # Search in J Drive
        logging.info(f"Searching for {mission_id} in {SEARCH_ROOT}...")
        found_files = []
        # Recursive search might be slow, so we limit depth or use specific patterns if known
        # For now, we search for the ID in filenames
        for root, dirs, files in os.walk(SEARCH_ROOT):
            for file in files:
                if mission_id in file:
                    found_files.append(os.path.join(root, file))
        
        if found_files:
            logging.info(f"Found {len(found_files)} files.")
            target_dir = os.path.join(DATA_DIR, mission_id)
            os.makedirs(target_dir, exist_ok=True)
            
            for src in found_files:
                dst = os.path.join(target_dir, os.path.basename(src))
                shutil.copy2(src, dst)
                logging.info(f"Copied {src} to {dst}")
            
            mission['status'] = 'completed'
            mission['result'] = f"Found and synced {len(found_files)} files."
        else:
            logging.warning(f"No files found for {mission_id}.")
            mission['status'] = 'failed' # Or 'pending_retry'
            mission['result'] = "File not found in J Drive."

        # Update Mission File
        with open(mission_file, 'w', encoding='utf-8') as f:
            json.dump(mission, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        logging.error(f"Error processing {mission_file}: {e}")

def main():
    logging.info("Shadow Unit Activated. Watching Dispatch Orders...")
    os.makedirs(DATA_DIR, exist_ok=True)
    
    while True:
        mission_files = glob.glob(os.path.join(DISPATCH_DIR, "*.json"))
        for m_file in mission_files:
            process_mission(m_file)
        
        time.sleep(10) # Check every 10 seconds

if __name__ == "__main__":
    main()
