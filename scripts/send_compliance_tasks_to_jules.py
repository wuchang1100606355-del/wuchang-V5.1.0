#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_compliance_tasks_to_jules.py

將合規任務傳送給 JULES

功能：
- 讀取合規任務清單
- 使用 Google Tasks API 建立任務給 JULES
- 記錄任務建立狀態
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def load_compliance_tasks() -> List[Dict[str, Any]]:
    """載入合規任務清單"""
    # 尋找最新的合規任務檔案
    task_files = list(BASE_DIR.glob("compliance_tasks_*.json"))
    if not task_files:
        print("❌ 找不到合規任務檔案，請先執行 dual_j_compliance_work.py")
        return []
    
    # 使用最新的檔案
    latest_file = max(task_files, key=lambda p: p.stat().st_mtime)
    print(f"📋 載入任務檔案: {latest_file.name}")
    
    try:
        tasks = json.loads(latest_file.read_text(encoding="utf-8"))
        print(f"✅ 已載入 {len(tasks)} 個合規任務")
        return tasks
    except Exception as e:
        print(f"❌ 載入任務失敗: {e}")
        return []


def create_google_task_for_jules(task: Dict[str, Any]) -> Dict[str, Any]:
    """為 JULES 建立 Google Task"""
    try:
        # 嘗試使用 google_tasks_integration.py
        from google_tasks_integration import create_task
        
        # 建立任務標題和描述
        title = f"[合規] {task.get('title', 'N/A')}"
        description = f"""
優先級: {task.get('priority', 'N/A')}
類別: {task.get('category', 'N/A')}

{task.get('description', '')}

資料來源:
- compliance_data.json
- website_content_data.json
- 雙J協作合規作業報告
        """.strip()
        
        # 建立任務
        result = create_task(
            title=title,
            notes=description,
            due_date=None,  # 可以設定截止日期
        )
        
        return {
            "success": True,
            "task_id": result.get("id"),
            "task_title": title,
            "google_task": result,
        }
    
    except ImportError:
        # 如果無法導入，使用替代方法
        print("⚠️  無法使用 Google Tasks API，使用替代方法")
        return {
            "success": False,
            "method": "alternative",
            "task": task,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "task": task,
        }


def main():
    """主函數"""
    print("=" * 70)
    print("將合規任務傳送給 JULES")
    print("=" * 70)
    print()
    
    # 載入合規任務
    tasks = load_compliance_tasks()
    if not tasks:
        return 1
    
    # 建立任務給 JULES
    print()
    print("=" * 70)
    print("建立 Google Tasks 給 JULES")
    print("=" * 70)
    print()
    
    results = []
    for task in tasks:
        print(f"📝 建立任務: {task.get('title', 'N/A')}")
        result = create_google_task_for_jules(task)
        results.append(result)
        
        if result.get("success"):
            print(f"  ✅ 任務已建立: {result.get('task_id', 'N/A')}")
        else:
            print(f"  ⚠️  使用替代方法記錄任務")
        print()
    
    # 儲存結果
    results_file = BASE_DIR / f"compliance_tasks_sent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.write_text(
        json.dumps({
            "timestamp": datetime.now().isoformat(),
            "tasks_sent": len([r for r in results if r.get("success")]),
            "tasks_total": len(tasks),
            "results": results,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print("=" * 70)
    print("任務傳送完成")
    print("=" * 70)
    print()
    print(f"總任務數: {len(tasks)}")
    print(f"成功建立: {len([r for r in results if r.get('success')])}")
    print(f"結果已儲存至: {results_file.name}")
    print()
    
    # 如果無法使用 Google Tasks API，提供替代方案
    if not any(r.get("success") for r in results):
        print("💡 替代方案：")
        print("1. 手動將任務複製到 Google Tasks")
        print("2. 使用 local_control_center.py 的 UI 介面建立任務")
        print("3. 直接執行相關腳本完成合規作業")
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
