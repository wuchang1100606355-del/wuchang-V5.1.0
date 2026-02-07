import json
import os

path = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

if "system_protocols" not in data:
    data["system_protocols"] = {}

data["system_protocols"]["time_transmission"] = True
data["system_protocols"]["time_transmission_mode"] = "active"

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Updated config with Time Transmission enabled.")
