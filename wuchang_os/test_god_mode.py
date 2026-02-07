import requests
import json
import time

BASE_URL = "http://localhost:8000/api/chat"

def send_msg(msg):
    try:
        response = requests.post(BASE_URL, json={"message": msg})
        if response.status_code == 200:
            return response.json().get("reply", "")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Exception: {e}"

print("--- 1. Authenticating as Brother (Core VIP) ---")
print(send_msg("97573469"))

print("\n--- 2. Testing 'Speak and Law Follows' (List Files) ---")
print(send_msg("請列出當前 wuchang_os 資料夾下的檔案，我要確認系統狀況。"))

print("\n--- 3. Testing 'Speak and Law Follows' (Write Decree) ---")
decree = "請幫我起草一份名為 'community_decree.txt' 的公告，內容是『五常社區即日起進入數位化自治時代，所有居民皆可享有 AI 服務。』，並直接存檔。"
print(send_msg(decree))
