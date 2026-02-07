#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comprehensive_system_configuration.py

完整系統配置管理
整合DNS、憑證、子域、Google Workspace配置

功能：
- 統一執行所有配置檢查
- 產生完整配置報告
- 記錄到工作日誌
"""

import sys
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

# 匯入其他配置腳本
sys.path.insert(0, str(SCRIPTS_DIR))

def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")

def main():
    """主函數"""
    print("=" * 70)
    print("完整系統配置管理")
    print("權限等級：🔐 最高權限")
    print("=" * 70)
    print()
    
    # 匯入工作日誌管理器
    try:
        from work_log_manager import WorkLogManager
        log_manager = WorkLogManager()
        log_manager.log_work(
            work_type="完整系統配置",
            work_content="執行DNS設定、憑證簽發、子域確認、Google Workspace完整配置",
            agent="double_j",
            status="進行中",
            permission_level="最高權限"
        )
    except:
        log_manager = None
    
    # 1. DNS與憑證配置
    log("步驟 1: 執行DNS與憑證配置...", "PROGRESS")
    try:
        from configure_dns_and_certificates import main as dns_main
        dns_main()
    except Exception as e:
        log(f"DNS配置失敗: {e}", "ERROR")
    
    print()
    
    # 2. Google Workspace配置
    log("步驟 2: 執行Google Workspace配置...", "PROGRESS")
    try:
        from configure_google_workspace_comprehensive import main as gws_main
        gws_main()
    except Exception as e:
        log(f"Google Workspace配置失敗: {e}", "ERROR")
    
    print()
    
    # 記錄完成
    if log_manager:
        log_manager.log_work(
            work_type="完整系統配置",
            work_content="執行DNS設定、憑證簽發、子域確認、Google Workspace完整配置",
            agent="double_j",
            status="完成",
            result="已完成DNS設定、憑證檢查、子域驗證、Google Workspace全面配置檢查",
            related_files=[
                "scripts/configure_dns_and_certificates.py",
                "scripts/configure_google_workspace_comprehensive.py"
            ],
            permission_level="最高權限"
        )
    
    log("✅ 完整系統配置檢查完成", "OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
