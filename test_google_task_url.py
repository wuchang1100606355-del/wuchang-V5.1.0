#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_google_task_url.py

測試從 Google Tasks URL 獲取任務
"""

import sys
import json
from dataclasses import asdict

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

task_url = "https://jules.google.com/task/9554046612705221251"

print("=" * 60)
print("Google Tasks URL 測試")
print("=" * 60)
print(f"任務 URL: {task_url}")
print()

try:
    from google_tasks_integration import get_google_tasks_integration
    
    print("正在嘗試獲取任務...")
    print()
    
    integration = get_google_tasks_integration()
    task = integration.get_task_by_url(task_url)
    
    if task:
        print("【任務資訊】")
        print(f"  標題: {task.title}")
        print(f"  狀態: {task.status}")
        if task.notes:
            print(f"  備註: {task.notes}")
        if task.due:
            print(f"  到期: {task.due}")
        if task.completed:
            print(f"  完成時間: {task.completed}")
        print()
        print("【完整資料】")
        print(json.dumps(asdict(task), ensure_ascii=False, indent=2))
    else:
        print("無法找到任務（可能原因：")
        print("  1. 任務不存在")
        print("  2. 未授權存取")
        print("  3. URL 格式不正確")
        
except ImportError as e:
    print("錯誤：Google API Client Library 未安裝")
    print("請執行：pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print()
    print(f"詳細錯誤: {e}")
    
except FileNotFoundError as e:
    print("錯誤：找不到 OAuth 憑證檔案")
    print("請從 Google Cloud Console 下載 OAuth 2.0 憑證並儲存為 google_credentials.json")
    print()
    print(f"詳細錯誤: {e}")
    
except Exception as e:
    print(f"錯誤: {e}")
    print()
    print("【使用 API 端點】")
    print("如果控制中心正在運行，可以使用 API 端點：")
    print()
    print("POST http://127.0.0.1:8788/api/google-tasks/tasks/from-url")
    print("Content-Type: application/json")
    print()
    print(json.dumps({"url": task_url}, ensure_ascii=False, indent=2))

print()
print("=" * 60)
