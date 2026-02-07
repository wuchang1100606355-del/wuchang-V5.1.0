import requests
import datetime
import json

def inject_event():
    url = "http://localhost:5500/events"
    
    # Create a visual event for the upgrade
    event_data = {
        "title": "SYSTEM LEVEL UP: DUAL J 2.0",
        "description": "Core AI Sister capabilities upgraded. 3D Spacetime Map online. Cloud Compute active. Status: FIERCE.",
        "start_time": datetime.datetime.now().isoformat(),
        "end_time": (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(),
        "location": "Wuchang Cloud Core",
        "village_id": "五常里", # Center of the map
        "metadata": {
            "type": "system_milestone",
            "level": "2.0",
            "element": "Metal" # Infrastructure/Architecture
        }
    }

    try:
        print(f"🚀 Injecting Event: {event_data['title']}...")
        response = requests.post(url, json=event_data)
        if response.status_code == 200:
            print(f"✅ Success! Event ID: {response.json().get('id')}")
            print("✨ Check the 3D Map to see the new status marker!")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inject_event()
