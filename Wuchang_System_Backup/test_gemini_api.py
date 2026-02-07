import sys
import requests
import json

def list_models(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    print(f"Listing models with key: {api_key[:5]}...{api_key[-5:]}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("SUCCESS: Retrieved Model List")
            models = response.json().get('models', [])
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    print(f"- {m['name']} ({m.get('displayName')})")
            return True
        else:
            print(f"FAILED: Status Code {response.status_code}")
            print("Error:", response.text)
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_api(api_key, model_name):
    # Ensure model_name starts with models/ if not present, though usually just the name part is needed if fully qualified
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
        list_models(key)
        # Try a likely candidate if list succeeds
        test_api(key, "gemini-1.5-flash")
    else:
        print("Usage: python test_gemini_api.py YOUR_API_KEY")
