import json
import os
import datetime

def install_menu():
    print(f"[{datetime.datetime.now()}] Starting Menu Installation Process...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Delete Old Demo Transaction Info
    print("Step 1: Deleting old demo transaction info...")
    stats_file = os.path.join(base_dir, 'legacy_data', 'legacy_dashboard_stats.json')
    empty_stats = {
        "income_sources": {"third_party_platform": 0, "cash": 0, "credit_card": 0, "third_party_payment": 0},
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "platforms": [],
        "total_revenue": 0
    }
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(empty_stats, f, indent=2, ensure_ascii=False)
        print(" - Cleared legacy_dashboard_stats.json")
    except Exception as e:
        print(f" - Warning: Could not clear stats: {e}")

    # 2. Load Most Recent Menu Record
    print("Step 2: Loading most recent menu record...")
    source_file = os.path.join(base_dir, 'legacy_data', 'legacy_menu_full.json') # Using FULL record
    if not os.path.exists(source_file):
        print(f" - Error: Source file {source_file} not found!")
        return

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        print(f" - Found {len(items)} items in {os.path.basename(source_file)}")
    except Exception as e:
        print(f" - Error reading source file: {e}")
        return

    # 3. Install Menu (No Variants)
    print("Step 3: Installing menu items (Exact Copy, No Variants)...")
    target_file = os.path.join(base_dir, 'installed_menu.json')
    
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=4, ensure_ascii=False)
        print(f" - Successfully wrote {len(items)} items to {os.path.basename(target_file)}")
    except Exception as e:
        print(f" - Error writing target file: {e}")
        return

    print("Menu Installation Complete.")

if __name__ == '__main__':
    install_menu()
