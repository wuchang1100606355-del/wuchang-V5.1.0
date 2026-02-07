import json

config_path = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# 1. Define Credit System
if "credit_system" not in config:
    config["credit_system"] = {
        "currency_name": "五常幣 (Wuchang Credits)",
        "currency_symbol": "WC",
        "exchange_rates": {
            "volunteer_hour": 100,  # 1 hour = 100 WC
            "resource_contribution": 50, # Per unit
            "referral": 200
        },
        "redemption_rules": {
            "subscription_offset": 1.0, # 1 WC = 1 TWD offset (Example)
            "api_quota_boost": 10       # 10 WC = 1 Extra Request
        }
    }

# 2. Define "Credit Sister" Persona in Roles (if not exists)
# Note: Usually this is logic-bound, but we can document it here.
config["community_roles"]["credit_sister"] = {
    "name": "抵免額妹妹 (Credit Sister)",
    "access_level": "System Agent",
    "tier_ref": "core_vip",
    "capabilities": [
        "Manage Ledger",
        "Issue Credits",
        "Process Redemptions",
        "Audit Transactions"
    ],
    "persona": "嚴謹、公正但貼心的財務管家。她負責確保每一分貢獻都被記錄，每一分抵免都被合理使用。"
}

# 3. Initialize User Credits
if "user_credits" not in config:
    config["user_credits"] = {} # user_id -> balance

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("Credit System Configured.")
