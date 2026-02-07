import sys
import requests
import json

def test_api(api_key, model_name):
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": "Hello, are you active? Reply with 'Double J Systems Online'."}]
        }]
    }
    
    print(f"\nTesting {model_name}...")
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("SUCCESS: API Call Successful!")
            try:
                text = response.json()['candidates'][0]['content']['parts'][0]['text']
                print(f"Response: {text}")
            except:
                print("Response format unexpected (but 200 OK).")
            return True
        else:
            print(f"FAILED: Status Code {response.status_code}")
            print("Error:", response.text)
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        key = sys.argv[1]
        test_api(key, "gemini-2.0-flash")
    else:
        print("Usage: python test_gemini_api.py YOUR_API_KEY")
