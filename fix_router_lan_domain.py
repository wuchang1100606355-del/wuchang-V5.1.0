import requests
import base64
import sys
import time

ROUTER_IP = "192.168.50.1"
USERNAME = "coffeeboss"
PASSWORD = "977349"

def login_and_fix():
    s = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"http://{ROUTER_IP}/Main_Login.asp"
    }

    # Method 1: login_username / login_passwd
    print("Trying Login Method 1 (username/password)...")
    payload1 = {
        "group_id": "",
        "action_mode": "",
        "action_script": "",
        "action_wait": "5",
        "current_page": "Main_Login.asp",
        "next_page": "index.asp",
        "login_username": USERNAME,
        "login_passwd": PASSWORD
    }
    
    try:
        r = s.post(f"http://{ROUTER_IP}/login.cgi", data=payload1, headers=headers, timeout=5)
        if "asus_token" in s.cookies or "sys_token" in s.cookies or "index.asp" in r.url:
            print("Login Method 1 Successful!")
            return change_domain(s)
    except Exception as e:
        print(f"Method 1 failed: {e}")

    # Method 2: login_authorization
    print("Trying Login Method 2 (login_authorization)...")
    s = requests.Session() # Reset session
    auth_str = f"{USERNAME}:{PASSWORD}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    payload2 = {
        "group_id": "",
        "action_mode": "",
        "action_script": "",
        "action_wait": "5",
        "current_page": "Main_Login.asp",
        "next_page": "index.asp",
        "login_authorization": auth_b64
    }
    
    try:
        r = s.post(f"http://{ROUTER_IP}/login.cgi", data=payload2, headers=headers, timeout=5)
        if "asus_token" in s.cookies or "sys_token" in s.cookies or "index.asp" in r.url:
            print("Login Method 2 Successful!")
            return change_domain(s)
        else:
            print("Login Method 2 failed. Response content preview:")
            # print(r.text[:200])
    except Exception as e:
        print(f"Method 2 failed: {e}")

    print("All login methods failed.")

def change_domain(s):
    print("Attempting to change LAN domain...")
    
    # 1. Get current settings to confirm
    try:
        r = s.get(f"http://{ROUTER_IP}/Advanced_LAN_Content.asp", timeout=5)
        if "wuchang.life" in r.text:
            print("Confirmed: 'wuchang.life' found in settings.")
        else:
            print("Note: 'wuchang.life' NOT found in current settings page text.")
    except Exception as e:
        print(f"Failed to read settings: {e}")

    # 2. Apply new settings
    payload = {
        "productid": "RT-AX86U", # Generic, might not matter or might need real one
        "current_page": "Advanced_LAN_Content.asp",
        "next_page": "Advanced_LAN_Content.asp",
        "modified": "0",
        "action_mode": " Apply ",
        "action_script": "restart_net_and_phy",
        "action_wait": "5",
        "first_time": "",
        "preferred_lang": "CN",
        "firmver": "3.0.0.4",
        "lan_domain": "wuchang.local", # THE FIX
        # Add other necessary fields if known, usually ASUS ignores missing ones or uses defaults
    }
    
    # We might need to scrape the 'token' from the page if the router uses CSRF tokens
    # But often session cookie is enough for ASUS
    
    try:
        r = s.post(f"http://{ROUTER_IP}/start_apply.htm", data=payload, headers={"Referer": f"http://{ROUTER_IP}/Advanced_LAN_Content.asp"}, timeout=10)
        print(f"Apply Response: {r.status_code}")
        if r.status_code == 200:
            print("Settings applied successfully! (Router might restart services)")
            return True
        else:
            print("Failed to apply settings.")
            return False
    except Exception as e:
        print(f"Apply request failed: {e}")
        return False

if __name__ == "__main__":
    login_and_fix()
