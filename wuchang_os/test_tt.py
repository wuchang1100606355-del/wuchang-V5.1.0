import requests
import json
print("Starting Time Transmission Test...")
url = "http://localhost:8000/api/chat"

# Auth
print(requests.post(url, json={"message": "97573469"}).json())

# Test Command
print(requests.post(url, json={"message": "請檢查系統狀態"}).json())
