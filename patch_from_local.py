#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_from_local.py

以本地檔案進行比對修補

功能：
- 使用 safe_sync_push.py 將本地變更推送到伺服器
- 以本地檔案為準進行修補
- 支援所有配置檔（kb, rules）
"""

import sys
import subprocess
import os
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def patch_profile(profile: str, dry_run: bool = False):
    """修補指定配置檔"""
    print(f"【修補 {profile} profile】")
    
    health_url = os.getenv("WUCHANG_HEALTH_URL", "").strip()
    copy_to = os.getenv("WUCHANG_COPY_TO", "").strip()
    
    if not copy_to:
        print("  ✗ 未設定 WUCHANG_COPY_TO 環境變數")
        return False
    
    print(f"  伺服器目錄: {copy_to}")
    print(f"  健康檢查 URL: {health_url or '(未設定)'}")
    print()
    
    if dry_run:
        print("  [模擬模式] 將執行以下操作：")
        print(f"    python safe_sync_push.py --profile {profile} --actor system")
        return True
    
    # 執行推送
    try:
        args = [
            sys.executable,
            "safe_sync_push.py",
            "--profile", profile,
            "--actor", "system"
        ]
        
        if health_url:
            args.extend(["--health-url", health_url])
        if copy_to:
            args.extend(["--copy-to", copy_to])
        
        print("  正在推送...")
        result = subprocess.run(
            args,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=180
        )
        
        if result.returncode == 0:
            print("  ✓ 推送成功")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print("  ✗ 推送失敗")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
            
    except Exception as e:
        print(f"  ✗ 執行失敗: {e}")
        return False


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="以本地檔案進行比對修補")
    parser.add_argument("--profile", choices=["kb", "rules", "all"], default="all", help="同步配置檔")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("以本地檔案進行比對修補")
    print("=" * 70)
    print()
    
    results = {}
    
    if args.profile == "all":
        profiles = ["kb", "rules"]
    else:
        profiles = [args.profile]
    
    for profile in profiles:
        success = patch_profile(profile, dry_run=args.dry_run)
        results[profile] = success
        print()
    
    # 摘要
    print("=" * 70)
    print("【執行摘要】")
    print("=" * 70)
    
    for profile, success in results.items():
        status = "✓ 成功" if success else "✗ 失敗"
        print(f"  {profile}: {status}")
    
    print()
    print("=" * 70)
    
    # 返回狀態碼
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
