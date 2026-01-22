#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upload_diff_to_jules.py

將檔案差異報告上傳到 JULES (Google Tasks)

功能：
- 生成檔案差異報告
- 自動上傳到 Google Tasks
- 或輸出內容供手動複製
"""

import sys
import json
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def upload_to_google_tasks(content: str, title: str = "檔案比對差異報告") -> bool:
    """上傳到 Google Tasks"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 尋找或建立任務列表
        lists = integration.list_task_lists()
        target_list = None
        
        for task_list in lists:
            if "wuchang" in task_list.title.lower() or "sync" in task_list.title.lower():
                target_list = task_list
                break
        
        if not target_list:
            # 建立新列表
            target_list = integration.create_task_list("Wuchang File Sync")
        
        # 建立任務
        task = integration.create_task(
            task_list_id=target_list.id,
            title=title,
            notes=content
        )
        
        if task:
            print(f"✓ 已上傳到 Google Tasks")
            print(f"  任務列表: {target_list.title}")
            print(f"  任務標題: {task.title}")
            print(f"  任務 ID: {task.id}")
            if hasattr(task, 'self_link') and task.self_link:
                print(f"  任務連結: {task.self_link}")
            return True
        else:
            print("✗ 上傳失敗")
            return False
            
    except ImportError:
        print("⚠️  Google Tasks 整合模組不可用")
        print("   請確保已安裝 google-api-python-client 並設定 OAuth 憑證")
        return False
    except Exception as e:
        print(f"✗ 上傳時發生錯誤: {e}")
        return False


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="將檔案差異報告上傳到 JULES")
    parser.add_argument("--auto-upload", action="store_true", help="自動上傳到 Google Tasks")
    parser.add_argument("--title", default="檔案比對差異報告", help="任務標題")
    parser.add_argument("--report-file", default=None, help="使用現有的報告檔案")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("上傳檔案差異報告到 JULES")
    print("=" * 70)
    print()
    
    # 生成或讀取報告
    if args.report_file:
        report_file = Path(args.report_file)
        if not report_file.exists():
            print(f"✗ 報告檔案不存在: {report_file}")
            return 1
        content = report_file.read_text(encoding="utf-8")
    else:
        # 生成新報告
        from generate_diff_report_for_jules import generate_jules_report, format_for_google_tasks
        
        print("正在生成報告...")
        report = generate_jules_report()
        
        if "error" in report:
            print(f"✗ 生成報告失敗: {report['error']}")
            return 1
        
        content = format_for_google_tasks(report)
        
        # 儲存報告
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = BASE_DIR / f"file_diff_report_{timestamp}.md"
        report_file.write_text(content, encoding="utf-8")
        print(f"✓ 報告已儲存: {report_file}")
        print()
    
    # 上傳或顯示
    if args.auto_upload:
        print("正在上傳到 Google Tasks...")
        success = upload_to_google_tasks(content, args.title)
        if success:
            print()
            print("=" * 70)
            print("【完成】")
            print("=" * 70)
            return 0
        else:
            print()
            print("=" * 70)
            print("【上傳失敗】")
            print("請手動複製以下內容到 Google Tasks:")
            print("=" * 70)
            print()
            print(content)
            return 1
    else:
        print("=" * 70)
        print("報告內容（可複製到 Google Tasks）")
        print("=" * 70)
        print()
        print(content)
        print()
        print("=" * 70)
        print()
        print("提示: 使用 --auto-upload 參數可自動上傳到 Google Tasks")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    sys.exit(main())
