#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_document_meeting_system.py

驗證公文及會議系統

功能：
- 驗證 Google Workspace API 整合
- 驗證公文系統功能
- 驗證會議系統功能
- 驗證合規性
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
ASSOCIATION_DIR = BASE_DIR / "association_operational_files"


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


def verify_google_workspace_api():
    """驗證 Google Workspace API"""
    print("=" * 70)
    print("【驗證 Google Workspace API】")
    print("=" * 70)
    print()
    
    results = {
        "credentials": False,
        "token": False,
        "api_access": False
    }
    
    # 檢查憑證檔案
    credentials_file = BASE_DIR / "google_credentials.json"
    if credentials_file.exists():
        log("OAuth 憑證檔案存在", "OK")
        results["credentials"] = True
        try:
            with open(credentials_file, 'r', encoding='utf-8') as f:
                creds = json.load(f)
                if "installed" in creds or "web" in creds:
                    log("憑證格式正確", "OK")
                else:
                    log("憑證格式可能有問題", "WARN")
        except Exception as e:
            log(f"讀取憑證檔案失敗: {e}", "ERROR")
    else:
        log("OAuth 憑證檔案不存在", "WARN")
    
    # 檢查 Token 檔案
    token_file = BASE_DIR / "google_token.json"
    if token_file.exists():
        log("Token 檔案存在", "OK")
        results["token"] = True
        try:
            with open(token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                if "token" in token_data or "access_token" in token_data:
                    log("Token 格式正確", "OK")
                else:
                    log("Token 格式可能有問題", "WARN")
        except Exception as e:
            log(f"讀取 Token 檔案失敗: {e}", "ERROR")
    else:
        log("Token 檔案不存在", "WARN")
    
    # 檢查 API 可用性
    try:
        from google_tasks_integration import GoogleTasksIntegration
        integration = GoogleTasksIntegration()
        if integration.is_authenticated():
            log("Google API 認證成功", "OK")
            results["api_access"] = True
        else:
            log("Google API 認證失敗", "WARN")
    except ImportError:
        log("Google Tasks 整合模組未找到", "WARN")
    except Exception as e:
        log(f"API 驗證時發生錯誤: {e}", "WARN")
    
    print()
    return results


def verify_document_system():
    """驗證公文系統"""
    print("=" * 70)
    print("【驗證公文系統】")
    print("=" * 70)
    print()
    
    results = {
        "document_file": False,
        "process_defined": False,
        "integration": False
    }
    
    # 檢查公文處理文件
    doc_file = ASSOCIATION_DIR / "08_公文處理與行政營運組織.md"
    if doc_file.exists():
        log("公文處理文件存在", "OK")
        results["document_file"] = True
        
        content = doc_file.read_text(encoding="utf-8")
        
        # 檢查流程定義
        if "收文流程" in content and "發文流程" in content:
            log("公文處理流程已定義", "OK")
            results["process_defined"] = True
        else:
            log("公文處理流程定義不完整", "WARN")
        
        # 檢查系統整合
        if "系統整合" in content or "AI" in content:
            log("系統整合已定義", "OK")
            results["integration"] = True
        else:
            log("系統整合定義不完整", "WARN")
    else:
        log("公文處理文件不存在", "ERROR")
    
    print()
    return results


def verify_meeting_system():
    """驗證會議系統"""
    print("=" * 70)
    print("【驗證會議系統】")
    print("=" * 70)
    print()
    
    results = {
        "demo_script": False,
        "meeting_files": False,
        "format_correct": False
    }
    
    # 檢查會議系統程式
    demo_file = BASE_DIR / "association_meeting_demo.py"
    if demo_file.exists():
        log("會議系統程式存在", "OK")
        results["demo_script"] = True
    else:
        log("會議系統程式不存在", "ERROR")
    
    # 檢查會議記錄
    meetings_dir = ASSOCIATION_DIR / "meetings"
    if meetings_dir.exists():
        meeting_files = list(meetings_dir.glob("meeting_*.md"))
        if meeting_files:
            log(f"找到 {len(meeting_files)} 個會議記錄", "OK")
            results["meeting_files"] = True
            
            # 檢查格式
            sample_file = meeting_files[0]
            content = sample_file.read_text(encoding="utf-8")
            if "會議日期" in content and "議程" in content:
                log("會議記錄格式正確", "OK")
                results["format_correct"] = True
            else:
                log("會議記錄格式可能有問題", "WARN")
        else:
            log("未找到會議記錄檔案", "WARN")
    else:
        log("會議記錄目錄不存在", "WARN")
    
    print()
    return results


def verify_compliance():
    """驗證合規性"""
    print("=" * 70)
    print("【驗證合規性】")
    print("=" * 70)
    print()
    
    results = {
        "compliance_file": False,
        "pii_policy": False,
        "data_storage": False
    }
    
    # 檢查合規文件
    compliance_file = BASE_DIR / "COMPLIANCE_NO_PII.md"
    if compliance_file.exists():
        log("合規文件存在", "OK")
        results["compliance_file"] = True
        
        content = compliance_file.read_text(encoding="utf-8")
        
        # 檢查無個資政策
        if "無個資" in content or "PII" in content:
            log("無個資政策已定義", "OK")
            results["pii_policy"] = True
        else:
            log("無個資政策定義不完整", "WARN")
        
        # 檢查資料儲存
        if "Google Drive" in content or "同步資料夾" in content:
            log("資料儲存機制已定義", "OK")
            results["data_storage"] = True
        else:
            log("資料儲存機制定義不完整", "WARN")
    else:
        log("合規文件不存在", "ERROR")
    
    print()
    return results


def generate_report(all_results):
    """產生驗證報告"""
    print("=" * 70)
    print("【驗證報告】")
    print("=" * 70)
    print()
    
    total_checks = 0
    passed_checks = 0
    
    for category, results in all_results.items():
        for check, result in results.items():
            total_checks += 1
            if result:
                passed_checks += 1
    
    print(f"總檢查項目: {total_checks}")
    print(f"通過: {passed_checks} ✅")
    print(f"失敗: {total_checks - passed_checks} ❌")
    print()
    
    if passed_checks == total_checks:
        log("所有檢查項目通過！", "OK")
    else:
        log(f"有 {total_checks - passed_checks} 個檢查項目失敗", "WARN")
        print()
        print("【需要處理的項目】")
        for category, results in all_results.items():
            for check, result in results.items():
                if not result:
                    print(f"  ❌ {category}.{check}")


def main():
    """主函數"""
    print("=" * 70)
    print("公文及會議系統驗證")
    print("=" * 70)
    print()
    print(f"驗證時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_results = {}
    
    # 1. 驗證 Google Workspace API
    all_results["google_workspace"] = verify_google_workspace_api()
    
    # 2. 驗證公文系統
    all_results["document_system"] = verify_document_system()
    
    # 3. 驗證會議系統
    all_results["meeting_system"] = verify_meeting_system()
    
    # 4. 驗證合規性
    all_results["compliance"] = verify_compliance()
    
    # 產生報告
    generate_report(all_results)
    
    # 儲存報告
    report_file = BASE_DIR / "document_meeting_verification_report.json"
    try:
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "results": all_results
        }
        report_file.write_text(
            json.dumps(report_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        log(f"驗證報告已儲存: {report_file}", "OK")
    except Exception as e:
        log(f"儲存報告失敗: {e}", "WARN")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
