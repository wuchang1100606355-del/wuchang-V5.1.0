import json
import os
path = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "organizational_units" not in data:
        data["organizational_units"] = []
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Updated")
    else:
        print("Exists")
except Exception as e:
    print(e)
