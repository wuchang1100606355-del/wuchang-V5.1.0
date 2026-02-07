import json, os

CONFIG_PATH = "wuchang_os/double_j_config.json"

def update_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found at {CONFIG_PATH}")
        return

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Update Scaling Policy
        if "scaling" not in config:
            config+"scaling"] = {}

        config["scaling"]["auto_scale"] = True
        config["scaling"]["low_efficiency_trigger"] = {
            "ratio": "1:8",
            "command_threads": 5,
            "cleanup_threads": 3,
            "mem_threshold": 0.85,  # 85% Memory Usage
            "cpu_threshold": 0.90,  # 90% CPU Usage
            "action": "Enable Double J 1:8 (3 Cleanup)",
            "description": "盼顯效率低落時臯動饟用Nzouble J 1;8, 其中3架囬定進行資源清理"
        }

        # Ensure Google Workspace Integration Flag
        if "integrations" not in config:
            config["integrations"] = {}
        config["integrations"]["google_workspace"] = {
            "enabled": True,
            "sync_mode": "Auto",
            "scopes": ["drive", "calendar", "mail"]
        }

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print("Updated Double J Config with 1:8 Auto-Scaling and Google Workspace Link")

    except Exception as e:
        print(f"Error updating config: {e}")

if __name__ == "__main__":
    update_config()
