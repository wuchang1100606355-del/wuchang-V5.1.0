#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
list_devices.py

列出 Google Workspace 中的所有設備，用於診斷和清理。
"""

import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent.parent
GOOGLE_TOKEN = BASE_DIR / "config" / "google_token.json"

SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.device.mobile',
    'https://www.googleapis.com/auth/admin.directory.device.chromeos',
    'https://www.googleapis.com/auth/admin.directory.orgunit'
]

def main():
    if not GOOGLE_TOKEN.exists():
        print(f"❌ 找不到憑證檔案: {GOOGLE_TOKEN}")
        return

    try:
        with open(GOOGLE_TOKEN, 'r', encoding='utf-8') as token:
            creds = Credentials.from_authorized_user_info(
                json.load(token), SCOPES)
    except Exception as e:
        print(f"❌ 載入憑證失敗: {e}")
        return

    try:
        service = build('admin', 'directory_v1', credentials=creds)
        
        print("🔍 正在查詢行動裝置 (Mobile Devices)...")
        results = service.mobiledevices().list(customerId='my_customer').execute()
        devices = results.get('mobiledevices', [])

        if not devices:
            print("沒有找到行動裝置。")
        else:
            print(f"找到 {len(devices)} 個行動裝置：")
            for device in devices:
                name = device.get('name', [])
                if name:
                    name = name[0]
                else:
                    name = "Unknown"
                model = device.get('model', 'Unknown Model')
                user = device.get('email', 'Unknown User')
                status = device.get('status', 'Unknown Status')
                print(f" - [{status}] {model} ({user}): {name}")

        print("\n🔍 正在查詢 ChromeOS 裝置...")
        results_c = service.chromeosdevices().list(customerId='my_customer').execute()
        c_devices = results_c.get('chromeosdevices', [])
        
        if not c_devices:
            print("沒有找到 ChromeOS 裝置。")
        else:
            print(f"找到 {len(c_devices)} 個 ChromeOS 裝置：")
            for d in c_devices:
                print(f" - {d.get('model')} ({d.get('serialNumber')})")

    except Exception as e:
        print(f"❌ API 呼叫失敗: {e}")

if __name__ == "__main__":
    main()
