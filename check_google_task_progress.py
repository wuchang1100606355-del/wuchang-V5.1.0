#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_google_task_progress.py

檢查 Google Tasks 任務進度

使用方式：
  python check_google_task_progress.py "https://jules.google.com/task/9554046612705221251"
"""

import sys
import json
from datetime import datetime
from dataclasses import asdict

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass


def format_datetime(dt_str: str) -> str:
    """格式化日期時間"""
    if not dt_str:
        return "未設定"
    try:
        # RFC3339 格式：2026-01-19T10:30:00.000Z
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str


def check_task_progress(task_url: str):
    """檢查任務進度"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        print("正在連接到 Google Tasks API...")
        integration = get_google_tasks_integration()
        
        print("正在搜尋任務...")
        task = integration.get_task_by_url(task_url)
        
        if not task:
            print("❌ 無法找到任務")
            return None
        
        return task
        
    except FileNotFoundError as e:
        print("❌ 錯誤：找不到 OAuth 憑證檔案")
        print("請從 Google Cloud Console 下載 OAuth 2.0 憑證並儲存為 google_credentials.json")
        print(f"詳細錯誤: {e}")
        return None
        
    except ImportError as e:
        print("❌ 錯誤：Google API Client Library 未安裝")
        print("請執行：pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        print(f"詳細錯誤: {e}")
        return None
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return None


def display_progress(task):
    """顯示任務進度"""
    print()
    print("=" * 70)
    print("任務進度資訊")
    print("=" * 70)
    print()
    
    # 基本資訊
    print("【基本資訊】")
    print(f"  標題: {task.title or '(無標題)'}")
    print(f"  狀態: {task.status}")
    
    # 狀態圖示
    if task.status == "completed":
        status_icon = "✓ 已完成"
        status_color = "已完成"
    else:
        status_icon = "○ 待處理"
        status_color = "進行中"
    
    print(f"  狀態圖示: {status_icon}")
    print()
    
    # 時間資訊
    print("【時間資訊】")
    if task.due:
        due_time = format_datetime(task.due)
        print(f"  到期時間: {due_time}")
        
        # 計算是否過期
        try:
            from datetime import datetime, timezone
            if task.due.endswith("Z"):
                due_dt = datetime.fromisoformat(task.due[:-1]).replace(tzinfo=timezone.utc)
            else:
                due_dt = datetime.fromisoformat(task.due.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if due_dt < now and task.status != "completed":
                print(f"  ⚠️  狀態: 已過期")
            elif due_dt >= now:
                days_left = (due_dt - now).days
                print(f"  ⏰ 剩餘時間: {days_left} 天")
        except:
            pass
    else:
        print("  到期時間: 未設定")
    
    if task.completed:
        completed_time = format_datetime(task.completed)
        print(f"  完成時間: {completed_time}")
    else:
        print("  完成時間: 未完成")
    
    if task.updated:
        updated_time = format_datetime(task.updated)
        print(f"  最後更新: {updated_time}")
    else:
        print("  最後更新: 未知")
    
    print()
    
    # 內容資訊
    print("【內容資訊】")
    if task.notes:
        notes_preview = task.notes[:200] if len(task.notes) > 200 else task.notes
        print(f"  備註長度: {len(task.notes)} 字元")
        print(f"  備註預覽: {notes_preview}")
        if len(task.notes) > 200:
            print("  ... (內容已截斷)")
    else:
        print("  備註: 無")
    
    print()
    
    # 進度摘要
    print("【進度摘要】")
    if task.status == "completed":
        print("  ✓ 任務已完成")
        if task.completed:
            print(f"  ✓ 完成時間: {format_datetime(task.completed)}")
    else:
        print("  ○ 任務進行中")
        if task.due:
            print(f"  ⏰ 到期時間: {format_datetime(task.due)}")
        else:
            print("  ⏰ 無到期時間限制")
    
    print()
    
    # 完整資料（JSON）
    print("【完整資料 (JSON)】")
    print(json.dumps(asdict(task), ensure_ascii=False, indent=2))
    
    print()
    print("=" * 70)


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方式: python check_google_task_progress.py <task_url>")
        print("範例: python check_google_task_progress.py \"https://jules.google.com/task/9554046612705221251\"")
        sys.exit(1)
    
    task_url = sys.argv[1]
    
    print("=" * 70)
    print("Google Tasks 任務進度檢查")
    print("=" * 70)
    print(f"任務 URL: {task_url}")
    print()
    
    # 檢查任務進度
    task = check_task_progress(task_url)
    
    if task:
        display_progress(task)
    else:
        print()
        print("【提示】")
        print("如果尚未設定 OAuth 憑證，請參考 GOOGLE_TASKS_QUICK_SETUP.md")
        print("或使用控制中心 API（如果已設定憑證）：")
        print()
        print("  POST http://127.0.0.1:8788/api/google-tasks/tasks/from-url")
        print(f"  Body: {{\"url\": \"{task_url}\"}}")
        sys.exit(1)


if __name__ == "__main__":
    main()
