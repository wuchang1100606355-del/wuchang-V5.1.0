#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_google_apis_status.py

檢查 Google Workspace APIs 啟用狀態
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REQUIRED_APIS = [
    "drive.googleapis.com",
    "docs.googleapis.com",
    "sheets.googleapis.com",
    "gmail.googleapis.com",
    "calendar-json.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudbuild.googleapis.com"
]


def check_api_status():
    """檢查 API 啟用狀態"""
    print("=" * 70)
    print("Google Workspace APIs 狀態檢查")
    print("=" * 70)
    print()
    
    print("需要啟用的 API:")
    for i, api in enumerate(REQUIRED_APIS, 1):
        print(f"  {i}. {api}")
    
    print()
    print("檢查方式:")
    print("1. 前往: https://console.cloud.google.com/apis/library")
    print("2. 搜尋每個 API 名稱")
    print("3. 確認是否已啟用")
    print()
    print("或使用 gcloud CLI:")
    for api in REQUIRED_APIS:
        print(f"  gcloud services enable {api}")


if __name__ == "__main__":
    check_api_status()
