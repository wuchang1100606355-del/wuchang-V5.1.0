import requests
import json

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

print("--- Testing Trial Tier ---")
reply = send_msg("Hello, what is my tier?")
print(f"Reply: {reply[:100]}...")  # Truncate for brevity

print("\n--- Testing Registration (Core VIP) ---")
reply = send_msg("97573469")
print(f"Reply: {reply}")

print("\n--- Testing Core VIP Tier ---")
reply = send_msg("Who are you now?")
print(f"Reply: {reply[:100]}...")
