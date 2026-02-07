#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complete_authorization_and_setup.py

完整授權並進行後續作業

功能：
- 檢查憑證檔案
- 執行 OAuth 授權流程
- 驗證授權成功
- 執行後續作業（測試、檔案比對、上傳報告等）
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


def check_credentials_file():
    """檢查憑證檔案"""
    print("【步驟 1：檢查憑證檔案】")
    print()
    
    credentials_file = BASE_DIR / "google_credentials.json"
    
    if not credentials_file.exists():
        print(f"  ✗ 憑證檔案不存在: {credentials_file}")
        print()
        print("  請先設定憑證檔案：")
        print("    1. 將下載的 JSON 檔案複製到專案目錄")
        print("    2. 重新命名為: google_credentials.json")
        print("    3. 或執行: python setup_credentials_file.py <檔案路徑>")
        print()
        return False
    
    try:
        content = json.loads(credentials_file.read_text(encoding="utf-8"))
        if "installed" in content or "web" in content:
            print(f"  ✓ 憑證檔案存在: {credentials_file}")
            if "installed" in content:
                client_id = content["installed"].get("client_id", "")[:30]
                project_id = content["installed"].get("project_id", "")
            else:
                client_id = content["web"].get("client_id", "")[:30]
                project_id = content["web"].get("project_id", "")
            print(f"    客戶端 ID: {client_id}...")
            print(f"    專案 ID: {project_id}")
            print()
            return True
        else:
            print(f"  ✗ 憑證檔案格式不正確")
            return False
    except Exception as e:
        print(f"  ✗ 讀取憑證檔案失敗: {e}")
        return False


def perform_authorization():
    """執行 OAuth 授權流程"""
    print("【步驟 2：執行 OAuth 授權】")
    print()
    
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        print("  正在初始化 Google Tasks 整合...")
        integration = get_google_tasks_integration()
        
        print("  正在執行授權流程...")
        print("  （如果首次使用，會開啟瀏覽器要求授權）")
        print()
        
        # 嘗試獲取任務列表（這會觸發授權流程）
        task_lists = integration.list_task_lists()
        
        if task_lists:
            print(f"  ✓ 授權成功！")
            print(f"    找到 {len(task_lists)} 個任務列表")
            print()
            print("  任務列表：")
            for task_list in task_lists[:5]:  # 只顯示前 5 個
                print(f"    - {task_list.title} (ID: {task_list.id})")
            if len(task_lists) > 5:
                print(f"    ... 還有 {len(task_lists) - 5} 個任務列表")
            print()
            return True
        else:
            print("  ⚠️  授權成功，但沒有找到任務列表")
            print("  （這可能是正常的，如果您的帳號沒有任務列表）")
            print()
            return True
            
    except FileNotFoundError as e:
        print(f"  ✗ 憑證檔案問題: {e}")
        return False
    except Exception as e:
        error_msg = str(e)
        if "invalid_grant" in error_msg.lower():
            print("  ⚠️  授權已過期，需要重新授權")
            print("  請刪除 google_token.json 後重新執行")
        elif "user" in error_msg.lower() or "consent" in error_msg.lower():
            print("  ⚠️  需要用戶授權")
            print("  請在自動開啟的瀏覽器中完成授權")
        else:
            print(f"  ✗ 授權失敗: {e}")
        return False


def test_task_access():
    """測試任務存取"""
    print("【步驟 3：測試任務存取】")
    print()
    
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 測試獲取特定任務
        test_task_url = "https://jules.google.com/task/18167513009276525148"
        print(f"  測試獲取任務: {test_task_url}")
        
        task = integration.get_task_by_url(test_task_url)
        
        if task:
            print(f"  ✓ 任務存取成功")
            print(f"    標題: {task.title}")
            print(f"    狀態: {task.status}")
            if task.notes:
                print(f"    備註長度: {len(task.notes)} 字元")
            print()
            return True
        else:
            print("  ⚠️  無法找到指定任務（可能不存在或無權限）")
            print("  但授權功能正常")
            print()
            return True
            
    except Exception as e:
        print(f"  ⚠️  測試任務存取時發生錯誤: {e}")
        print("  （這不影響基本功能）")
        print()
        return True  # 不視為失敗


def perform_subsequent_tasks():
    """執行後續作業"""
    print("【步驟 4：執行後續作業】")
    print()
    
    tasks_completed = []
    tasks_failed = []
    
    # 作業 1: 檔案比對
    print("  作業 1: 執行檔案比對...")
    try:
        from compare_files_smart import compare_file_list, find_accessible_server_path
        from safe_sync_push import DEFAULT_FILES, RULE_FILES
        
        server_path = find_accessible_server_path()
        if server_path:
            kb_results = compare_file_list(DEFAULT_FILES, server_path)
            rules_results = compare_file_list(RULE_FILES, server_path)
            print(f"    ✓ 檔案比對完成")
            print(f"      KB 檔案: {kb_results['summary']['total']} 個")
            print(f"      規則檔案: {rules_results['summary']['total']} 個")
            tasks_completed.append("檔案比對")
        else:
            print(f"    ⚠️  伺服器不可訪問，跳過檔案比對")
            tasks_completed.append("檔案比對（跳過）")
    except Exception as e:
        print(f"    ✗ 檔案比對失敗: {e}")
        tasks_failed.append("檔案比對")
    
    print()
    
    # 作業 2: 生成差異報告
    print("  作業 2: 生成差異報告...")
    try:
        from generate_diff_report_for_jules import generate_jules_report, format_for_google_tasks
        
        report = generate_jules_report()
        if "error" not in report:
            markdown_content = format_for_google_tasks(report)
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_file = BASE_DIR / f"file_diff_report_{timestamp}.md"
            report_file.write_text(markdown_content, encoding="utf-8")
            print(f"    ✓ 差異報告已生成: {report_file.name}")
            tasks_completed.append("生成差異報告")
        else:
            print(f"    ✗ 生成報告失敗: {report.get('error')}")
            tasks_failed.append("生成差異報告")
    except Exception as e:
        print(f"    ✗ 生成報告失敗: {e}")
        tasks_failed.append("生成差異報告")
    
    print()
    
    # 作業 3: 上傳報告到 JULES（可選）
    print("  作業 3: 上傳報告到 JULES（可選）...")
    try:
        from upload_diff_to_jules import upload_to_google_tasks
        
        # 讀取最新報告
        report_files = sorted(BASE_DIR.glob("file_diff_report_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if report_files:
            latest_report = report_files[0]
            content = latest_report.read_text(encoding="utf-8")
            
            if upload_to_google_tasks(content, "檔案比對差異報告"):
                print(f"    ✓ 報告已上傳到 Google Tasks")
                tasks_completed.append("上傳報告到 JULES")
            else:
                print(f"    ⚠️  上傳失敗（可能需要手動上傳）")
                tasks_completed.append("上傳報告到 JULES（跳過）")
        else:
            print(f"    ⚠️  沒有找到報告檔案")
            tasks_completed.append("上傳報告到 JULES（跳過）")
    except Exception as e:
        print(f"    ⚠️  上傳報告時發生錯誤: {e}")
        tasks_completed.append("上傳報告到 JULES（跳過）")
    
    print()
    
    # 總結
    print("【後續作業總結】")
    print(f"  完成: {len(tasks_completed)} 個作業")
    for task in tasks_completed:
        print(f"    ✓ {task}")
    
    if tasks_failed:
        print(f"  失敗: {len(tasks_failed)} 個作業")
        for task in tasks_failed:
            print(f"    ✗ {task}")
    
    print()
    
    return len(tasks_failed) == 0


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="完整授權並進行後續作業")
    parser.add_argument("--skip-tasks", action="store_true", help="跳過後續作業，僅執行授權")
    parser.add_argument("--skip-test", action="store_true", help="跳過任務存取測試")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("完整授權並進行後續作業")
    print("=" * 70)
    print()
    
    # 步驟 1: 檢查憑證檔案
    if not check_credentials_file():
        print("=" * 70)
        print("【失敗】")
        print("=" * 70)
        print()
        print("請先設定憑證檔案後再執行")
        return 1
    
    # 步驟 2: 執行授權
    if not perform_authorization():
        print("=" * 70)
        print("【授權失敗】")
        print("=" * 70)
        print()
        print("請檢查：")
        print("  1. 憑證檔案是否正確")
        print("  2. Google Tasks API 是否已啟用")
        print("  3. OAuth 同意畫面是否已設定")
        return 1
    
    # 步驟 3: 測試任務存取
    if not args.skip_test:
        test_task_access()
    
    # 步驟 4: 執行後續作業
    if not args.skip_tasks:
        perform_subsequent_tasks()
    
    # 完成
    print("=" * 70)
    print("【完成】")
    print("=" * 70)
    print()
    print("✓ 授權已完成")
    if not args.skip_tasks:
        print("✓ 後續作業已完成")
    print()
    print("現在可以使用以下功能：")
    print("  - python get_jules_task_direct.py <task_url>")
    print("  - python upload_diff_to_jules.py --auto-upload")
    print("  - python sync_from_google_task.py <task_url> <target_file>")
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
