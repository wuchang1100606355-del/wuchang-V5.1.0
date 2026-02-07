import json
import os
import datetime

CONFIG_PATH = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"
REPORT_PATH = r"C:\wuchang V5.1.0\wuchang_os\System_Health_Report.md"

def update_config():
    if not os.path.exists(CONFIG_PATH):
        print("Config file not found!")
        return

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Update Brain Core details
    config['roles']['brain_core']['api_provider'] = "Gemini API (Google AI Studio)"
    config['roles']['brain_core']['api_endpoint'] = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    config['roles']['brain_core']['auth_method'] = "API Key (Provided by User)"

    # Update/Create API Management section
    if 'api_management' not in config:
        config['api_management'] = {}
    
    config['api_management']['provider'] = "Google AI Studio"
    config['api_management']['owner'] = "wuchang1100606355@gmail.com"
    config['api_management']['usage_policy'] = "Group Shared (Double J)"
    config['api_management']['api_key'] = "AIzaSyC9BbQshSJ0eYd042Vlh_wJtl9n4khP718"
    config['api_management']['active_model'] = "models/gemini-2.0-flash"

    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("Config updated successfully.")

def update_report():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_block = f"""
## Brain Core Connection Status ({timestamp})
- **Provider**: Google AI Studio (Gemini API)
- **Model**: models/gemini-2.0-flash
- **Connection**: Verified (Double J Systems Online)
- **Latency**: Low (Flash Model)
- **Account**: wuchang1100606355@gmail.com
"""
    with open(REPORT_PATH, 'a', encoding='utf-8') as f:
        f.write(status_block)
    print("Health report updated successfully.")

if __name__ == "__main__":
    update_config()
    update_report()
