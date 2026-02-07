#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
execute_dual_j_full_deployment.py

執行雙J協作全面部署
"""

import sys
import os
import subprocess
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

def main():
    """執行雙J全面部署"""
    print("=" * 60)
    print("雙J協作全面部署")
    print("=" * 60)
    print()
    
    # 檢查環境變數
    server_dir = os.getenv("WUCHANG_COPY_TO", "")
    health_url = os.getenv("WUCHANG_HEALTH_URL", "https://wuchang.life/health")
    
    if not server_dir:
        print("⚠️  警告: WUCHANG_COPY_TO 環境變數未設定")
        print("   將使用模擬模式執行")
        print()
        dry_run = True
    else:
        print(f"✅ 伺服器目錄: {server_dir}")
        print(f"✅ 健康檢查URL: {health_url}")
        print()
        dry_run = False
    
    # 執行部署
    cmd = [sys.executable, str(BASE_DIR / "dual_j_full_deployment.py")]
    
    if server_dir:
        cmd.extend(["--server-dir", server_dir])
    if health_url:
        cmd.extend(["--health-url", health_url])
    
    if dry_run:
        cmd.append("--dry-run")
        print("【模擬模式】不會實際部署到伺服器")
        print()
    
    print("開始執行部署...")
    print()
    
    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, timeout=600)
        
        if result.returncode == 0:
            print()
            print("=" * 60)
            print("✅ 部署執行完成")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("⚠️  部署執行完成（有警告）")
            print("=" * 60)
    except subprocess.TimeoutExpired:
        print()
        print("=" * 60)
        print("❌ 部署執行超時")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 部署執行失敗: {e}")
        print("=" * 60)

if __name__ == "__main__":
    main()
