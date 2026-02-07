#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_push_work_progress_to_server.py

全自動無人值守工作進度推送工具（最高授權）

功能：
- 自動生成工作進度摘要
- 使用最高授權（系統創辦人，第一類可究責對象）
- 全自動推送工作進度到伺服器
- 可究責對象無安全顧慮

授權：
- 操作者：系統創辦人，本系統設計人
- 授權等級：階段三權限解放（最高授權）
- 安全顧慮：無（可究責對象無安全顧慮）
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

try:
    from safe_sync_push import main as safe_push_main
    from risk_gate import now_iso, append_audit_jsonl
except ImportError as e:
    print(f"錯誤: 無法導入必要模組: {e}", file=sys.stderr)
    sys.exit(1)


# 可究責對象資訊（硬編碼）
ACCOUNTABLE_PERSON = {
    "name": "系統創辦人，本系統設計人",
    "role": "系統創辦人，本系統設計人",
    "accountability_priority": 1,
    "permission_stage": 3,  # 階段三權限解放
    "security_concern": False,  # 可究責對象無安全顧慮
}


def get_work_progress_summary() -> Dict[str, Any]:
    """
    生成工作進度摘要（自動化）
    """
    summary_file = Path("工作進度摘要_伺服器接手_20260123.md")
    
    if not summary_file.exists():
        return {
            "error": "工作進度摘要檔案不存在",
            "file": str(summary_file),
        }
    
    return {
        "file": str(summary_file),
        "exists": True,
        "size": summary_file.stat().st_size,
        "modified": datetime.fromtimestamp(summary_file.stat().st_mtime).isoformat(),
    }


def push_to_server(
    health_url: str = None,
    copy_to: str = None,
    files: List[str] = None,
    actor: str = None,
) -> Dict[str, Any]:
    """
    推送工作進度到伺服器（使用 safe_sync_push.py）
    
    Args:
        health_url: 伺服器健康檢查 URL
        copy_to: 推送目標資料夾
        files: 要推送的檔案清單
        actor: 操作者（預設為系統創辦人）
    """
    if actor is None:
        actor = ACCOUNTABLE_PERSON["name"]
    
    if files is None:
        files = [
            "工作進度摘要_伺服器接手_20260123.md",
            "合規查驗改善前後對比報告_20260123.md",
            "合規查驗詳細報告_20260123.md",
            "合規項目查驗報告_20260123.md",
        ]
    
    # 檢查檔案是否存在
    missing_files = []
    for f in files:
        if not Path(f).exists():
            missing_files.append(f)
    
    if missing_files:
        return {
            "ok": False,
            "error": "部分檔案不存在",
            "missing_files": missing_files,
        }
    
    # 使用 safe_sync_push.py 推送
    # 注意：safe_sync_push.py 需要 --health-url 和 --copy-to
    # 如果未提供，則使用環境變數或返回錯誤
    health_url = health_url or os.getenv("WUCHANG_HEALTH_URL")
    copy_to = copy_to or os.getenv("WUCHANG_COPY_TO")
    
    if not health_url or not copy_to:
        return {
            "ok": False,
            "error": "缺少必要參數",
            "hint": "請提供 --health-url 和 --copy-to，或設定環境變數 WUCHANG_HEALTH_URL 和 WUCHANG_COPY_TO",
            "health_url": health_url,
            "copy_to": copy_to,
        }
    
    # 構建 safe_sync_push.py 的命令行參數
    import sys as sys_module
    original_argv = sys_module.argv
    
    try:
        # 準備參數
        push_args = [
            "--health-url", health_url,
            "--copy-to", copy_to,
            "--actor", actor,
            "--files",
        ] + files
        
        # 調用 safe_sync_push.py
        sys_module.argv = ["safe_sync_push.py"] + push_args
        result_code = safe_push_main(push_args)
        
        return {
            "ok": result_code == 0,
            "result_code": result_code,
            "actor": actor,
            "files": files,
            "health_url": health_url,
            "copy_to": copy_to,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "actor": actor,
            "files": files,
        }
    finally:
        sys_module.argv = original_argv


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="全自動無人值守工作進度推送工具（最高授權）"
    )
    parser.add_argument(
        "--health-url",
        default=None,
        help="伺服器健康檢查 URL（無回應即中止）。亦可用環境變數 WUCHANG_HEALTH_URL"
    )
    parser.add_argument(
        "--copy-to",
        default=None,
        help="推送目標資料夾（可為 SMB/掛載磁碟）。亦可用環境變數 WUCHANG_COPY_TO"
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="自訂要推送的檔案清單（預設為工作進度摘要和合規報告）"
    )
    parser.add_argument(
        "--actor",
        default=None,
        help="操作者（預設為系統創辦人，本系統設計人）"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="僅檢查，不實際推送"
    )
    
    args = parser.parse_args()
    
    # 顯示授權資訊
    print("=" * 60)
    print("全自動無人值守工作進度推送工具（最高授權）")
    print("=" * 60)
    print(f"操作者: {ACCOUNTABLE_PERSON['name']}")
    print(f"授權等級: 階段三權限解放（最高授權）")
    print(f"可究責優先級: {ACCOUNTABLE_PERSON['accountability_priority']}")
    print(f"安全顧慮: 無（可究責對象無安全顧慮）")
    print("=" * 60)
    print()
    
    # 檢查工作進度摘要
    print("📋 檢查工作進度摘要...")
    summary_info = get_work_progress_summary()
    if "error" in summary_info:
        print(f"❌ 錯誤: {summary_info['error']}")
        return 1
    
    print(f"✅ 工作進度摘要檔案存在: {summary_info['file']}")
    print(f"   檔案大小: {summary_info['size']} bytes")
    print(f"   修改時間: {summary_info['modified']}")
    print()
    
    # 如果是 dry-run，只檢查不推送
    if args.dry_run:
        print("🔍 乾跑模式：僅檢查，不實際推送")
        print()
        print("📤 準備推送的檔案:")
        files = args.files or [
            "工作進度摘要_伺服器接手_20260123.md",
            "合規查驗改善前後對比報告_20260123.md",
            "合規查驗詳細報告_20260123.md",
            "合規項目查驗報告_20260123.md",
        ]
        for f in files:
            if Path(f).exists():
                print(f"  ✅ {f}")
            else:
                print(f"  ❌ {f} (不存在)")
        print()
        return 0
    
    # 執行推送
    print("📤 開始推送工作進度到伺服器...")
    result = push_to_server(
        health_url=args.health_url,
        copy_to=args.copy_to,
        files=args.files,
        actor=args.actor or ACCOUNTABLE_PERSON["name"],
    )
    
    print()
    if result.get("ok"):
        print("✅ 推送成功")
        print(f"   操作者: {result.get('actor')}")
        print(f"   推送檔案數: {len(result.get('files', []))}")
        print(f"   健康檢查 URL: {result.get('health_url')}")
        print(f"   目標資料夾: {result.get('copy_to')}")
        return 0
    else:
        print("❌ 推送失敗")
        if "error" in result:
            print(f"   錯誤: {result['error']}")
        if "hint" in result:
            print(f"   提示: {result['hint']}")
        if "missing_files" in result:
            print(f"   缺少檔案: {result['missing_files']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
