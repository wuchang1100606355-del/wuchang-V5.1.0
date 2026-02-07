import json
import os

CONFIG_PATH = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    config['scaling']['current_ratio'] = 10
    config['scaling']['thread_allocation'] = {
        "command_core": 7,
        "resource_cleanup": 3
    }

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("Config updated: Ratio 10, Command 7, Cleanup 3")
else:
    print("Config file not found.")
