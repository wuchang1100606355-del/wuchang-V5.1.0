import requests
import base64
import sys

ROUTER_IP = "192.168.50.1"
USERNAME = "coffeeboss"
PASSWORD = "977349"

def probe_router():
    s = requests.Session()
    
    # 1. Try Basic Auth first (Unlikely for main interface but worth a shot)
    try:
        print("Probing Basic Auth...")
        r = s.get(f"http://{ROUTER_IP}/Advanced_LAN_Content.asp", auth=(USERNAME, PASSWORD), timeout=5)
        print(f"Basic Auth Response: {r.status_code}")
        if "lan_domain" in r.text:
            print("Basic Auth Success! Found lan_domain in page.")
            return "basic"
    except Exception as e:
        print(f"Basic Auth failed: {e}")

    # 2. Try Form Login (Standard ASUS)
    try:
        print("\nProbing Form Login...")
        # Get login page to see if we need a token
        r = s.get(f"http://{ROUTER_IP}/Main_Login.asp", timeout=5)
        
        # Prepare login payload
        # Modern ASUS often uses login_authorization which is base64(user:pass)
        auth_str = f"{USERNAME}:{PASSWORD}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        
        payload = {
            "group_id": "",
            "action_mode": "",
            "action_script": "",
            "action_wait": "5",
            "current_page": "Main_Login.asp",
            "next_page": "index.asp",
            "login_authorization": auth_b64
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": f"http://{ROUTER_IP}/Main_Login.asp"
        }
        
        r = s.post(f"http://{ROUTER_IP}/login.cgi", data=payload, headers=headers, timeout=5)
        print(f"Login POST Response: {r.status_code}")
        
        if "asus_token" in s.cookies:
            print("Login Success! asus_token found.")
            return "form"
        elif "sys_token" in s.cookies:
            print("Login Success! sys_token found.")
            return "form"
        else:
            print("Login cookies not found. Response content preview:")
            print(r.text[:200])
            
    except Exception as e:
        print(f"Form Login failed: {e}")
        
    return None

if __name__ == "__main__":
    method = probe_router()
    if method:
        print(f"\nDetected Login Method: {method}")
    else:
        print("\nCould not determine login method.")
