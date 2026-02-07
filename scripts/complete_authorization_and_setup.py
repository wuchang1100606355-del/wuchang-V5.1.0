#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complete_authorization_and_setup.py

執行 Google OAuth 授權流程
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
GOOGLE_CREDENTIALS = BASE_DIR / "config" / "google_credentials.json"
GOOGLE_TOKEN = BASE_DIR / "config" / "google_token.json"

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("❌ 缺少必要的 Google API 套件")
    print("請執行: pip install google-auth google-auth-oauthlib")
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.device.mobile',
    'https://www.googleapis.com/auth/admin.directory.device.chromeos',
    'https://www.googleapis.com/auth/admin.directory.orgunit'
]


def main():
    print("=" * 70)
    print("Google Workspace OAuth 授權流程")
    print("=" * 70)
    print()
    
    if not GOOGLE_CREDENTIALS.exists():
        print(f"❌ 憑證檔案不存在: {GOOGLE_CREDENTIALS}")
        print("請先從 Google Cloud Console 下載憑證檔案")
        print("前往: https://console.cloud.google.com/apis/credentials")
        return
    
    creds = None
    
    # 檢查是否有已儲存的 token
    if GOOGLE_TOKEN.exists():
        try:
            with open(GOOGLE_TOKEN, 'r', encoding='utf-8') as token:
                creds = Credentials.from_authorized_user_info(
                    json.load(token), SCOPES)
            print("✓ 已載入儲存的認證資訊")
        except:
            pass
    
    # 如果沒有有效的認證，進行 OAuth 流程
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✓ 已重新整理認證資訊")
            except:
                creds = None
        
        if not creds:
            print("正在開啟瀏覽器進行 OAuth 授權...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(GOOGLE_CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0)
            print("✓ OAuth 認證成功")
        
        # 儲存認證資訊
        GOOGLE_TOKEN.parent.mkdir(parents=True, exist_ok=True)
        with open(GOOGLE_TOKEN, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
        print("✓ 已儲存認證資訊")
    
    print()
    print("✅ 授權完成！")


if __name__ == "__main__":
    main()
