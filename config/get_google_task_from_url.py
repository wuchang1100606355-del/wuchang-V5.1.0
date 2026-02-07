#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
get_google_task_from_url.py

從 Google Tasks URL 獲取任務的便捷工具

使用方式：
  python get_google_task_from_url.py "https://jules.google.com/task/9554046612705221251"
"""

import sys
import json
from dataclasses import asdict
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

def main():
    if len(sys.argv) < 2:
        print("使用方式: python get_google_task_from_url.py <task_url>")
        print("範例: python get_google_task_from_url.py \"https://jules.google.com/task/9554046612705221251\"")
        sys.exit(1)
    
    task_url = sys.argv[1]
    
    print("=" * 70)
    print("Google Tasks 任務獲取工具")
    print("=" * 70)
    print(f"任務 URL: {task_url}")
    print()
    
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        print("正在連接到 Google Tasks API...")
        integration = get_google_tasks_integration()
        
        print("正在搜尋任務...")
        task = integration.get_task_by_url(task_url)
        
        if task:
            print()
            print("【任務資訊】")
            print(f"  標題: {task.title}")
            print(f"  狀態: {'✓ 已完成' if task.status == 'completed' else '○ 待處理'}")
            
            if task.notes:
                print(f"  備註: {task.notes}")
            
            if task.due:
                print(f"  到期時間: {task.due}")
            
            if task.completed:
                print(f"  完成時間: {task.completed}")
            
            if task.updated:
                print(f"  最後更新: {task.updated}")
            
            print()
            print("【完整 JSON 資料】")
            print(json.dumps(asdict(task), ensure_ascii=False, indent=2))
            
            # 儲存到檔案
            output_file = Path("google_task_output.json")
            output_file.write_text(
                json.dumps(asdict(task), ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print()
            print(f"【已儲存】任務資料已儲存到: {output_file}")
            
        else:
            print()
            print("❌ 無法找到任務")
            print()
            print("可能原因：")
            print("  1. 任務不存在或已被刪除")
            print("  2. 當前帳號沒有存取權限")
            print("  3. URL 格式不正確")
            print("  4. 任務不在任何任務列表中")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print()
        print("❌ 錯誤：找不到 OAuth 憑證檔案")
        print()
        print("請按照以下步驟設定：")
        print("  1. 前往 Google Cloud Console: https://console.cloud.google.com/")
        print("  2. 建立或選擇專案")
        print("  3. 啟用 Google Tasks API")
        print("  4. 建立 OAuth 2.0 憑證（桌面應用程式）")
        print("  5. 下載 JSON 憑證並儲存為 google_credentials.json")
        print()
        print(f"詳細錯誤: {e}")
        sys.exit(1)
        
    except ImportError as e:
        print()
        print("❌ 錯誤：Google API Client Library 未安裝")
        print()
        print("請執行：")
        print("  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        print()
        print(f"詳細錯誤: {e}")
        sys.exit(1)
        
    except Exception as e:
        print()
        print(f"❌ 錯誤: {e}")
        print()
        print("【替代方案】")
        print("如果控制中心正在運行，可以使用 API 端點：")
        print()
        print("  curl -X POST http://127.0.0.1:8788/api/google-tasks/tasks/from-url \\")
        print("    -H \"Content-Type: application/json\" \\")
        print(f"    -d '{{\"url\": \"{task_url}\"}}'")
        print()
        sys.exit(1)
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
