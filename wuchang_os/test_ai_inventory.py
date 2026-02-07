import requests
import json
print("Starting AI Inventory Test...")
url = "http://localhost:8000/api/chat"

# Auth
print(requests.post(url, json={"message": "97573469"}).json())

# List AI Agents
print(requests.post(url, json={"message": "列出系統內所有的AI程序"}).json())
