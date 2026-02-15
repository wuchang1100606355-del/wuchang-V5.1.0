import requests
import sys

def check(url, method="GET", data=None):
    try:
        if method == "GET":
            r = requests.get(url, timeout=5)
        else:
            r = requests.post(url, json=data, timeout=5)
        status = "OK" if r.status_code == 200 else f"FAILED ({r.status_code})"
        print(f"[{method}] {url:40} -> {status}")
        return r.status_code == 200
    except Exception as e:
        print(f"[{method}] {url:40} -> ERROR: {e}")
        return False

print("--- 五常系統連結連通性排查報告 (Wuchang Link Diagnostic Report) ---")
targets = [
    ("http://localhost:6688/home.html", "GET"),
    ("http://localhost:6688/index.html", "GET"),
    ("http://localhost:6688/staff_voices.html", "GET"),
    ("http://localhost:6688/api/config", "GET"),
    ("http://localhost:8000/", "GET"),
    ("http://localhost:8000/manifest.json", "GET"),
    ("http://localhost:8000/api/chat", "POST", {"message": "hello"})
]

success_count = 0
for t in targets:
    if check(*t):
        success_count += 1

print(f"--- 總結: {success_count}/{len(targets)} 成功 ---")
if success_count == len(targets):
    print("✅ 系統全鏈路對齊完成。")
else:
    print("⚠️ 部分鏈路仍存在偏差。")
