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

print("--- 1. Testing Default (Trial) ---")
# Reset session by not sending cookies (simulated by IP in server, so we might get existing session)
# Since server uses IP, and I'm localhost, I might need to restart server to clear or just assume state.
# I'll just check current state.
reply = send_msg("你好，我是新居民")
print(f"Reply: {reply[:100]}...")

print("\n--- 2. Testing VIP Upgrade (Ultra/Brother) ---")
reply = send_msg("97573469")
print(f"Reply: {reply}")

print("\n--- 3. Testing Ultra Capabilities (Gemini 3.0 Pro) ---")
reply = send_msg("請自我介紹並說明你的核心模型版本")
print(f"Reply: {reply[:150]}...")
