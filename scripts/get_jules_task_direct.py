#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
get_jules_task_direct.py

直接從 Google Tasks URL 獲取任務（不依賴控制中心）

使用方式：
  python get_jules_task_direct.py "https://jules.google.com/task/18167513009276525148"
"""

import sys
import json
import re
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def extract_task_id_from_url(url: str) -> str:
    """從 URL 中提取任務 ID"""
    # 支援兩種格式：
    # https://jules.google.com/task/18167513009276525148 (數字 ID)
    # https://jules.google.com/task/Qk9yME10U1RZSk9HdmNWMw (Base64 編碼 ID)
    match = re.search(r'/task/([^/?]+)', url)
    if match:
        return match.group(1)
    return ""


def get_task_via_api(task_id: str):
    """通過 Google Tasks API 獲取任務"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 嘗試從 URL 獲取
        task_url = f"https://jules.google.com/task/{task_id}"
        task = integration.get_task_by_url(task_url)
        
        if task:
            return {
                "ok": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "notes": task.notes,
                    "due": task.due,
                    "completed": task.completed,
                    "updated": task.updated,
                }
            }
        else:
            return {
                "ok": False,
                "error": "任務不存在或無法訪問"
            }
    except FileNotFoundError as e:
        return {
            "ok": False,
            "error": "OAuth 憑證未設定",
            "details": str(e),
            "solution": "請參考 GOOGLE_TASKS_QUICK_SETUP.md 設定 OAuth 憑證"
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("使用方式: python get_jules_task_direct.py <Google Tasks URL>")
        print("範例: python get_jules_task_direct.py \"https://jules.google.com/task/18167513009276525148\"")
        sys.exit(1)
    
    task_url = sys.argv[1]
    
    print("=" * 70)
    print("從 Google Tasks 獲取任務")
    print("=" * 70)
    print(f"任務 URL: {task_url}")
    print()
    
    # 提取任務 ID
    task_id = extract_task_id_from_url(task_url)
    if not task_id:
        print("✗ 無法從 URL 中提取任務 ID")
        print("請確認 URL 格式正確: https://jules.google.com/task/TASK_ID")
        sys.exit(1)
    
    print(f"任務 ID: {task_id}")
    print()
    
    # 獲取任務
    print("【獲取任務內容】")
    result = get_task_via_api(task_id)
    
    if result.get("ok"):
        print("✓ 任務獲取成功")
        print()
        print("【任務資訊】")
        task = result.get("task", {})
        print(f"  標題: {task.get('title', '無標題')}")
        print(f"  狀態: {task.get('status', '未知')}")
        if task.get('notes'):
            notes = task.get('notes', '')
            print(f"  備註長度: {len(notes)} 字元")
            print(f"  備註預覽:")
            print(f"    {notes[:500]}...")
        if task.get('due'):
            print(f"  到期: {task.get('due')}")
        if task.get('completed'):
            print(f"  完成時間: {task.get('completed')}")
        print()
        
        # 儲存任務內容
        output_file = BASE_DIR / f"jules_task_{task_id}.json"
        output_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"✓ 任務內容已儲存到: {output_file}")
        
        # 如果備註很長，也單獨儲存
        if task.get('notes') and len(task.get('notes', '')) > 100:
            notes_file = BASE_DIR / f"jules_task_{task_id}_notes.txt"
            notes_file.write_text(task.get('notes', ''), encoding="utf-8")
            print(f"✓ 任務備註已儲存到: {notes_file}")
    else:
        print("✗ 任務獲取失敗")
        print(f"  錯誤: {result.get('error', '未知錯誤')}")
        if result.get('details'):
            print(f"  詳情: {result.get('details')}")
        if result.get('solution'):
            print()
            print("【解決方案】")
            print(f"  {result.get('solution')}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
