#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
full_setup_and_authorization.py

完整設定與授權流程

功能：
- 自動尋找憑證檔案
- 設定憑證檔案
- 執行 OAuth 授權
- 進行後續作業
"""

import sys
import json
import shutil
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
TARGET_FILE = BASE_DIR / "google_credentials.json"
CREDENTIAL_FILENAME = "client_secret_581281764864-4eg0icu55pkmbcirheflhp7fgt7gk499.apps.googleusercontent.com.json"


def find_and_setup_credentials():
    """尋找並設定憑證檔案"""
    print("【階段 1：尋找並設定憑證檔案】")
    print()
    
    import os
    
    # 如果目標檔案已存在
    if TARGET_FILE.exists():
        try:
            content = json.loads(TARGET_FILE.read_text(encoding="utf-8"))
            if "installed" in content or "web" in content:
                print(f"  ✓ 憑證檔案已存在且格式正確: {TARGET_FILE}")
                print()
                return True
        except:
            pass
    
    # 搜尋憑證檔案
    print(f"  正在搜尋憑證檔案: {CREDENTIAL_FILENAME}")
    print()
    
    search_paths = []
    
    if os.name == 'nt':  # Windows
        user_profile = os.getenv("USERPROFILE", "")
        if user_profile:
            search_paths.extend([
                Path(user_profile) / "Downloads",
                Path(user_profile) / "下載",
                Path(user_profile) / "Desktop",
                Path(user_profile) / "桌面",
                Path(user_profile) / "Documents",
                Path(user_profile) / "文件",
            ])
    
    search_paths.append(BASE_DIR)
    
    found_file = None
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # 精確匹配
        exact_match = search_path / CREDENTIAL_FILENAME
        if exact_match.exists():
            found_file = exact_match
            print(f"  ✓ 找到憑證檔案: {found_file}")
            break
        
        # 模糊匹配
        for file_path in search_path.glob("*client_secret*.json"):
            if "581281764864" in file_path.name or "4eg0icu55pkmbcirheflhp7fgt7gk499" in file_path.name:
                found_file = file_path
                print(f"  ✓ 找到類似檔案: {found_file}")
                break
        
        if found_file:
            break
    
    if not found_file:
        print("  ✗ 未找到憑證檔案")
        print()
        print("  請確認：")
        print(f"    1. 檔案名稱包含: {CREDENTIAL_FILENAME[:30]}...")
        print("    2. 檔案在下載資料夾或其他可訪問位置")
        print()
        print("  如果檔案在其他位置，請手動複製到：")
        print(f"    {TARGET_FILE}")
        print()
        return False
    
    # 驗證檔案格式
    try:
        content = json.loads(found_file.read_text(encoding="utf-8"))
        if "installed" not in content and "web" not in content:
            print("  ✗ 檔案格式不正確（不是 OAuth 憑證）")
            return False
        print("  ✓ 檔案格式驗證通過")
    except Exception as e:
        print(f"  ✗ 檔案格式錯誤: {e}")
        return False
    
    # 複製檔案
    try:
        if TARGET_FILE.exists():
            # 備份現有檔案
            backup_file = BASE_DIR / f"google_credentials.json.backup_{int(__import__('time').time())}"
            try:
                shutil.copy2(TARGET_FILE, backup_file)
            except:
                pass
        
        shutil.copy2(found_file, TARGET_FILE)
        print(f"  ✓ 已複製到: {TARGET_FILE}")
        print()
        return True
    except Exception as e:
        print(f"  ✗ 複製失敗: {e}")
        print()
        return False


def perform_authorization():
    """執行 OAuth 授權"""
    print("【階段 2：執行 OAuth 授權】")
    print()
    
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        print("  正在初始化 Google Tasks 整合...")
        integration = get_google_tasks_integration()
        
        print("  正在執行授權流程...")
        print("  （如果首次使用，會自動開啟瀏覽器要求授權）")
        print()
        
        # 獲取任務列表（觸發授權）
        task_lists = integration.list_task_lists()
        
        if task_lists:
            print(f"  ✓ 授權成功！")
            print(f"    找到 {len(task_lists)} 個任務列表")
            print()
            print("  任務列表：")
            for task_list in task_lists[:5]:
                print(f"    - {task_list.title} (ID: {task_list.id})")
            if len(task_lists) > 5:
                print(f"    ... 還有 {len(task_lists) - 5} 個任務列表")
            print()
            return True
        else:
            print("  ✓ 授權成功（沒有任務列表是正常的）")
            print()
            return True
            
    except FileNotFoundError as e:
        print(f"  ✗ 憑證檔案問題: {e}")
        return False
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid_grant" in error_msg:
            print("  ⚠️  授權已過期")
            print("  請刪除 google_token.json 後重新執行")
        elif "user" in error_msg or "consent" in error_msg:
            print("  ⚠️  需要用戶授權")
            print("  請在自動開啟的瀏覽器中完成授權")
        else:
            print(f"  ✗ 授權失敗: {e}")
        return False


def perform_subsequent_tasks():
    """執行後續作業"""
    print("【階段 3：執行後續作業】")
    print()
    
    tasks = []
    
    # 作業 1: 檔案比對
    print("  作業 1: 檔案比對...")
    try:
        from compare_files_smart import compare_file_list, find_accessible_server_path
        from safe_sync_push import DEFAULT_FILES, RULE_FILES
        
        server_path = find_accessible_server_path()
        if server_path:
            kb_results = compare_file_list(DEFAULT_FILES, server_path)
            rules_results = compare_file_list(RULE_FILES, server_path)
            print(f"    ✓ 完成（KB: {kb_results['summary']['total']}, Rules: {rules_results['summary']['total']}）")
            tasks.append(("檔案比對", True))
        else:
            print(f"    ⚠️  伺服器不可訪問，跳過")
            tasks.append(("檔案比對", None))
    except Exception as e:
        print(f"    ✗ 失敗: {e}")
        tasks.append(("檔案比對", False))
    
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
            print(f"    ✓ 完成: {report_file.name}")
            tasks.append(("生成差異報告", True))
        else:
            print(f"    ✗ 失敗: {report.get('error')}")
            tasks.append(("生成差異報告", False))
    except Exception as e:
        print(f"    ✗ 失敗: {e}")
        tasks.append(("生成差異報告", False))
    
    # 作業 3: 上傳到 JULES
    print("  作業 3: 上傳報告到 JULES...")
    try:
        from upload_diff_to_jules import upload_to_google_tasks
        
        report_files = sorted(BASE_DIR.glob("file_diff_report_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if report_files:
            content = report_files[0].read_text(encoding="utf-8")
            if upload_to_google_tasks(content, "檔案比對差異報告"):
                print(f"    ✓ 完成")
                tasks.append(("上傳報告到 JULES", True))
            else:
                print(f"    ⚠️  跳過")
                tasks.append(("上傳報告到 JULES", None))
        else:
            print(f"    ⚠️  沒有報告檔案，跳過")
            tasks.append(("上傳報告到 JULES", None))
    except Exception as e:
        print(f"    ⚠️  跳過: {e}")
        tasks.append(("上傳報告到 JULES", None))
    
    print()
    
    # 總結
    completed = sum(1 for _, status in tasks if status is True)
    skipped = sum(1 for _, status in tasks if status is None)
    failed = sum(1 for _, status in tasks if status is False)
    
    print(f"  完成: {completed}, 跳過: {skipped}, 失敗: {failed}")
    print()
    
    return failed == 0


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="完整設定與授權流程")
    parser.add_argument("--skip-tasks", action="store_true", help="跳過後續作業")
    parser.add_argument("--credentials-path", default=None, help="指定憑證檔案路徑")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("完整設定與授權流程")
    print("=" * 70)
    print()
    
    # 階段 1: 尋找並設定憑證
    if args.credentials_path:
        # 使用指定的路徑
        src = Path(args.credentials_path)
        if src.exists():
            try:
                shutil.copy2(src, TARGET_FILE)
                print(f"✓ 已從指定路徑複製憑證檔案: {src}")
                print()
            except Exception as e:
                print(f"✗ 複製失敗: {e}")
                return 1
        else:
            print(f"✗ 檔案不存在: {src}")
            return 1
    else:
        if not find_and_setup_credentials():
            print("=" * 70)
            print("【失敗】")
            print("=" * 70)
            print()
            print("請先設定憑證檔案，或使用 --credentials-path 指定路徑")
            return 1
    
    # 階段 2: 執行授權
    if not perform_authorization():
        print("=" * 70)
        print("【授權失敗】")
        print("=" * 70)
        return 1
    
    # 階段 3: 執行後續作業
    if not args.skip_tasks:
        perform_subsequent_tasks()
    
    # 完成
    print("=" * 70)
    print("【完成】")
    print("=" * 70)
    print()
    print("✓ 憑證檔案已設定")
    print("✓ OAuth 授權已完成")
    if not args.skip_tasks:
        print("✓ 後續作業已完成")
    print()
    print("現在可以使用：")
    print("  - python get_jules_task_direct.py <task_url>")
    print("  - python upload_diff_to_jules.py --auto-upload")
    print("  - python sync_from_google_task.py <task_url> <target_file>")
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
