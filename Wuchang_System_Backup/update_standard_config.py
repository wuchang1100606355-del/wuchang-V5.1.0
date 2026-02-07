import json
import os

CONFIG_PATH = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 1. Set as Standard Equipment
    config['system_info'] = config.get('system_info', {})
    config['system_info']['standard_equipment'] = "Double J Collaboration (1:10)"
    config['system_info']['is_standard_active'] = True

    # 2. Add Dynamic Policy
    config['scaling']['dynamic_policy'] = {
        "enabled": True,
        "mode": "Efficiency & Host Status",
        "standard_ratio": 10,
        "standard_allocation": {"command_core": 7, "resource_cleanup": 3},
        "thresholds": {
            "cpu_high": 80.0,
            "memory_high": 80.0,
            "latency_max_ms": 2000
        }
    }

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("Config updated: Standard Equipment & Dynamic Policy Set")
else:
    print("Config file not found.")
