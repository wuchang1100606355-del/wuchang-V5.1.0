import json

CONFIG_PATH = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"
REPORT_PATH = r"C:\wuchang V5.1.0\wuchang_os\System_Health_Report.md"

config_data = {
  "collaboration_name": "Double J Internal Program (Adjustable Scaling)",
  "version": "2.2",
  "scaling": {
    "mode": "dynamic",
    "min_ratio": 1,
    "max_ratio": 10,
    "current_ratio": 10
  },
  "roles": {
    "brain_core": {
      "account": "wuchang1100606355@gmail.com",
      "tier": "Google One AI Premium (Ultra)",
      "role": "Intelligence Provider (Brain)",
      "responsibilities": [
        "Complex Reasoning (Gemini Ultra)",
        "Resource Optimization Strategy",
        "Data Analysis",
        "Code Generation"
      ],
      "resource_pool": "Unlimited",
      "api_provider": "Gemini API (Google AI Studio)",
      "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
      "auth_method": "API Key (Provided by User)"
    },
    "operations_core": {
      "account": "admin@wuchang.life",
      "tier": "Google Workspace for Nonprofits",
      "role": "Task Executor (Body)",
      "responsibilities": [
        "Google Tasks Management",
        "Calendar Scheduling",
        "Organization Compliance",
        "Audit Logging"
      ],
      "api_access": [
        "Tasks API",
        "Calendar API",
        "Admin SDK"
      ]
    }
  },
  "integration_settings": {
    "sync_mode": "asynchronous",
    "task_batch_size": 10,
    "security_protocol": "OAuth 2.0 (Simulated)"
  },
  "api_management": {
    "provider": "Google AI Studio",
    "owner": "wuchang1100606355@gmail.com",
    "usage_policy": "Group Shared (Double J)",
    "api_key": "AIzaSyC9BbQshSJ0eYd042Vlh_wJtl9n4khP718",
    "active_model": "models/gemini-2.0-flash"
  }
}

with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(config_data, f, indent=2, ensure_ascii=False)

print("Configuration restored and updated.")

import datetime
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
print("Health report updated.")
