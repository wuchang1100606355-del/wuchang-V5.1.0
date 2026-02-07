import requests
import json
import os

def get_api_key():
    path = r"C:\wuchang V5.1.0\wuchang_os\double_j_config.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("api_management", {}).get("api_key")
    return None

key = get_api_key()
if key:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            for m in resp.json().get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    print(m["name"])
        else:
            print(f"Error: {resp.status_code}")
    except Exception as e:
        print(e)
