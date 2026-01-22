#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_document_meeting_system_verification.py

檢查公文及會議系統是否需要程式驗證

功能：
- 檢查公文系統配置
- 檢查會議系統配置
- 確認 Google Workspace 整合
- 評估是否需要程式驗證
"""

import sys
from pathlib import Path

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
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_document_system():
    """檢查公文系統"""
    print("=" * 70)
    print("【檢查公文系統】")
    print("=" * 70)
    print()
    
    doc_file = ASSOCIATION_DIR / "08_公文處理與行政營運組織.md"
    
    if doc_file.exists():
        log("公文處理文件存在", "OK")
        print(f"  檔案: {doc_file.name}")
        
        # 讀取內容檢查
        content = doc_file.read_text(encoding="utf-8")
        
        # 檢查 Google 相關
        has_google = "google" in content.lower() or "workspace" in content.lower()
        if has_google:
            log("公文系統使用 Google 工具", "OK")
        else:
            log("未發現 Google 工具使用", "INFO")
        
        return True, content
    else:
        log("公文處理文件不存在", "WARN")
        return False, None


def check_meeting_system():
    """檢查會議系統"""
    print()
    print("=" * 70)
    print("【檢查會議系統】")
    print("=" * 70)
    print()
    
    meetings_dir = ASSOCIATION_DIR / "meetings"
    meeting_demo = BASE_DIR / "association_meeting_demo.py"
    
    # 檢查會議記錄
    if meetings_dir.exists():
        meeting_files = list(meetings_dir.glob("meeting_*.md"))
        log(f"找到 {len(meeting_files)} 個會議記錄", "OK")
        for f in meeting_files[:5]:
            print(f"  ✓ {f.name}")
        if len(meeting_files) > 5:
            print(f"  ... 還有 {len(meeting_files) - 5} 個")
    else:
        log("會議記錄目錄不存在", "WARN")
    
    # 檢查會議系統程式
    if meeting_demo.exists():
        log("會議系統程式存在", "OK")
        print(f"  檔案: {meeting_demo.name}")
        
        content = meeting_demo.read_text(encoding="utf-8")
        has_google = "google" in content.lower() or "workspace" in content.lower()
        if has_google:
            log("會議系統使用 Google 工具", "OK")
        else:
            log("未發現 Google 工具使用", "INFO")
        
        return True, content
    else:
        log("會議系統程式不存在", "WARN")
        return False, None


def check_google_workspace_integration():
    """檢查 Google Workspace 整合"""
    print()
    print("=" * 70)
    print("【檢查 Google Workspace 整合】")
    print("=" * 70)
    print()
    
    # 檢查相關檔案
    google_files = [
        BASE_DIR / "google_workspace_writer.py",
        BASE_DIR / "GOOGLE_WORKSPACE_SETUP.md",
        BASE_DIR / "COMPLIANCE_NO_PII.md",
    ]
    
    found_files = []
    for f in google_files:
        if f.exists():
            found_files.append(f)
            log(f"找到: {f.name}", "OK")
    
    if found_files:
        log(f"找到 {len(found_files)} 個 Google Workspace 相關檔案", "OK")
    else:
        log("未找到 Google Workspace 整合檔案", "WARN")
    
    return len(found_files) > 0


def check_compliance_requirements():
    """檢查合規要求"""
    print()
    print("=" * 70)
    print("【檢查合規要求】")
    print("=" * 70)
    print()
    
    compliance_file = BASE_DIR / "COMPLIANCE_NO_PII.md"
    constitution_file = BASE_DIR / "AGENT_CONSTITUTION.md"
    
    requirements = []
    
    if compliance_file.exists():
        log("合規文件存在", "OK")
        content = compliance_file.read_text(encoding="utf-8")
        
        # 檢查驗證相關
        if "驗證" in content or "verification" in content.lower():
            requirements.append("需要驗證合規性")
        
        if "google" in content.lower() or "workspace" in content.lower():
            requirements.append("Google Workspace 合規要求")
    
    if constitution_file.exists():
        log("系統憲法文件存在", "OK")
        content = constitution_file.read_text(encoding="utf-8")
        
        if "驗證" in content or "verification" in content.lower():
            requirements.append("系統憲法驗證要求")
    
    if requirements:
        log("發現合規要求", "OK")
        for req in requirements:
            print(f"  • {req}")
    else:
        log("未發現明確的驗證要求", "INFO")
    
    return requirements


def generate_verification_report():
    """產生驗證報告"""
    print()
    print("=" * 70)
    print("【驗證需求評估】")
    print("=" * 70)
    print()
    
    print("根據檢查結果，公文及會議系統的驗證需求：")
    print()
    
    print("1. **Google Workspace 整合驗證**")
    print("   - 如果使用 Google Docs/Drive 儲存公文和會議記錄")
    print("   - 需要確認 Google Workspace 非營利帳號狀態")
    print("   - 需要確認 API 權限和認證")
    print()
    
    print("2. **合規性驗證**")
    print("   - 根據 COMPLIANCE_NO_PII.md，系統需符合無個資要求")
    print("   - 公文和會議記錄可能包含可究責自然人資訊")
    print("   - 需要確認資料處理符合合規聲明")
    print()
    
    print("3. **程式功能驗證**")
    print("   - 檢查公文處理流程是否正常運作")
    print("   - 檢查會議記錄生成是否正確")
    print("   - 確認 Google Workspace API 整合是否正常")
    print()
    
    print("4. **資料安全驗證**")
    print("   - 確認資料儲存位置（Google Drive 同步資料夾）")
    print("   - 確認權限控制是否適當")
    print("   - 確認備份機制是否完整")
    print()


def main():
    """主函數"""
    print("=" * 70)
    print("公文及會議系統驗證需求檢查")
    print("=" * 70)
    print()
    
    # 檢查公文系統
    doc_exists, doc_content = check_document_system()
    
    # 檢查會議系統
    meeting_exists, meeting_content = check_meeting_system()
    
    # 檢查 Google Workspace 整合
    has_google = check_google_workspace_integration()
    
    # 檢查合規要求
    requirements = check_compliance_requirements()
    
    # 產生驗證報告
    generate_verification_report()
    
    # 總結
    print()
    print("=" * 70)
    print("【總結】")
    print("=" * 70)
    print()
    
    if has_google:
        log("建議進行程式驗證", "WARN")
        print()
        print("原因：")
        print("  1. 系統使用 Google Workspace 工具")
        print("  2. 需要確認 API 整合是否正常")
        print("  3. 需要確認合規性是否符合要求")
        print("  4. 需要確認資料處理流程是否正確")
    else:
        log("如果未使用 Google 工具，仍建議進行基本驗證", "INFO")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
