import requests
import json
print("Starting Test...")
url = "http://localhost:8000/api/chat"
s = requests.Session()

# Auth
print(requests.post(url, json={"message": "97573469"}).json())

# Create Unit
print(requests.post(url, json={"message": "成立新單位 '數位發展部'，負責人 '王小明'"}).json())

# Create User
print(requests.post(url, json={"message": "新增使用者 '李大同'，角色 '居民'"}).json())
