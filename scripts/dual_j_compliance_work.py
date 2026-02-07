#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dual_j_compliance_work.py

雙J協作合規作業系統

功能：
- 讀取雙J工作日誌
- 載入合規資料
- 啟動雙J協作進行合規作業
- 生成合規作業報告
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
WORK_LOG_DIR = BASE_DIR / "dual_j_work_logs"
COMPLIANCE_DATA_FILE = BASE_DIR / "compliance_data.json"
WEBSITE_CONTENT_FILE = BASE_DIR / "website_content_data.json"


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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{icon} [{timestamp}] [{level}] {message}")


def load_work_logs() -> List[Dict[str, Any]]:
    """載入工作日誌"""
    log("讀取雙J工作日誌...", "PROGRESS")
    
    all_logs_file = WORK_LOG_DIR / "all_logs.json"
    if not all_logs_file.exists():
        log("工作日誌檔案不存在", "WARN")
        return []
    
    try:
        logs = json.loads(all_logs_file.read_text(encoding="utf-8"))
        log(f"已載入 {len(logs)} 筆工作日誌", "OK")
        return logs
    except Exception as e:
        log(f"載入工作日誌失敗: {e}", "ERROR")
        return []


def load_compliance_data() -> Dict[str, Any]:
    """載入合規資料"""
    log("載入合規資料...", "PROGRESS")
    
    if not COMPLIANCE_DATA_FILE.exists():
        log("合規資料檔案不存在，請先執行 compliance_data_integration.py", "ERROR")
        return {}
    
    try:
        data = json.loads(COMPLIANCE_DATA_FILE.read_text(encoding="utf-8"))
        log("合規資料載入成功", "OK")
        return data
    except Exception as e:
        log(f"載入合規資料失敗: {e}", "ERROR")
        return {}


def load_website_content_data() -> Dict[str, Any]:
    """載入網站內容資料"""
    log("載入網站內容資料...", "PROGRESS")
    
    if not WEBSITE_CONTENT_FILE.exists():
        log("網站內容資料檔案不存在", "WARN")
        return {}
    
    try:
        data = json.loads(WEBSITE_CONTENT_FILE.read_text(encoding="utf-8"))
        log("網站內容資料載入成功", "OK")
        return data
    except Exception as e:
        log(f"載入網站內容資料失敗: {e}", "ERROR")
        return {}


def analyze_compliance_gaps(compliance_data: Dict[str, Any], work_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析合規缺口"""
    log("分析合規缺口...", "PROGRESS")
    
    gaps = {
        "missing_contact_info": [],
        "missing_content_pages": [],
        "missing_tracking": [],
        "technical_issues": [],
    }
    
    # 檢查聯絡資訊
    contact = compliance_data.get("contact", {})
    if not contact.get("phone"):
        gaps["missing_contact_info"].append("電話號碼")
    if not contact.get("email"):
        gaps["missing_contact_info"].append("電子郵件")
    if not contact.get("address", {}).get("street") or "待補充" in str(contact.get("address", {}).get("street", "")):
        gaps["missing_contact_info"].append("詳細地址")
    
    # 檢查網站內容
    website_content = load_website_content_data()
    if website_content:
        if not website_content.get("about_us", {}).get("description"):
            gaps["missing_content_pages"].append("關於我們頁面內容")
        if not website_content.get("mission", {}).get("main_activities"):
            gaps["missing_content_pages"].append("使命與活動頁面內容")
        if not website_content.get("contact", {}).get("phone"):
            gaps["missing_content_pages"].append("聯絡方式頁面內容")
    
    # 檢查追蹤設定（從工作日誌中查找）
    has_ga = False
    for log_entry in work_logs:
        if "Google Analytics" in str(log_entry.get("description", "")) or "GA" in str(log_entry.get("description", "")):
            has_ga = True
            break
    
    if not has_ga:
        gaps["missing_tracking"].append("Google Analytics 未安裝")
        gaps["missing_tracking"].append("轉換追蹤未配置")
    
    # 檢查技術問題（從工作日誌中查找）
    for log_entry in work_logs:
        description = str(log_entry.get("description", "")).lower()
        if any(keyword in description for keyword in ["ssl", "證書", "https", "dns", "訪問", "連接"]):
            if log_entry.get("status") != "completed":
                gaps["technical_issues"].append({
                    "issue": log_entry.get("description", ""),
                    "status": log_entry.get("status", ""),
                    "timestamp": log_entry.get("timestamp", ""),
                })
    
    return gaps


def create_compliance_tasks(gaps: Dict[str, Any], compliance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """建立合規任務"""
    log("建立合規任務...", "PROGRESS")
    
    tasks = []
    
    # P0 任務：技術基礎設施
    if gaps.get("technical_issues"):
        tasks.append({
            "priority": "P0",
            "category": "技術基礎設施",
            "title": "修復技術基礎設施問題",
            "description": "解決 HTTPS/SSL、DNS、網站可訪問性等技術問題",
            "issues": gaps["technical_issues"],
        })
    
    # P1 任務：聯絡資訊
    if gaps.get("missing_contact_info"):
        tasks.append({
            "priority": "P1",
            "category": "聯絡資訊",
            "title": "補充聯絡資訊",
            "description": "補充缺失的聯絡資訊以符合 Google 非營利組織要求",
            "missing_items": gaps["missing_contact_info"],
        })
    
    # P1 任務：網站內容
    if gaps.get("missing_content_pages"):
        tasks.append({
            "priority": "P1",
            "category": "網站內容",
            "title": "建立合規網站頁面",
            "description": "使用整合的合規資料建立關於我們、使命與活動、聯絡我們等頁面",
            "missing_pages": gaps["missing_content_pages"],
            "data_source": "website_content_data.json",
        })
    
    # P1 任務：追蹤設定
    if gaps.get("missing_tracking"):
        tasks.append({
            "priority": "P1",
            "category": "轉換追蹤",
            "title": "安裝 Google Analytics 並配置轉換追蹤",
            "description": "安裝 GA4 並配置至少一個轉換事件",
            "missing_items": gaps["missing_tracking"],
        })
    
    return tasks


def generate_compliance_work_report(
    work_logs: List[Dict[str, Any]],
    compliance_data: Dict[str, Any],
    gaps: Dict[str, Any],
    tasks: List[Dict[str, Any]]
) -> str:
    """生成合規作業報告"""
    report = []
    report.append("# 雙J協作合規作業報告")
    report.append("")
    report.append(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**工作日誌筆數**: {len(work_logs)}")
    report.append("")
    report.append("---")
    report.append("")
    
    # 工作日誌摘要
    report.append("## 📋 工作日誌摘要")
    report.append("")
    
    recent_logs = work_logs[-10:] if len(work_logs) > 10 else work_logs
    report.append(f"最近 {len(recent_logs)} 筆工作日誌：")
    report.append("")
    
    for log_entry in recent_logs:
        agent = log_entry.get("agent", "未知")
        work_type = log_entry.get("work_type", "")
        description = log_entry.get("description", "")
        status = log_entry.get("status", "")
        timestamp = log_entry.get("timestamp", "")
        
        status_icon = "✅" if status == "completed" else "🔄" if status == "in_progress" else "❌"
        report.append(f"- {status_icon} **{agent}** - {work_type}")
        report.append(f"  - {description}")
        report.append(f"  - 時間: {timestamp}")
        report.append("")
    
    # 合規資料摘要
    report.append("---")
    report.append("")
    report.append("## 📊 合規資料摘要")
    report.append("")
    
    org_info = compliance_data.get("organization", {})
    report.append(f"- **組織名稱**: {org_info.get('name', 'N/A')}")
    report.append(f"- **使命**: {compliance_data.get('mission', {}).get('mission', 'N/A')}")
    report.append(f"- **服務區域**: {compliance_data.get('service_area', {}).get('jurisdiction', 'N/A')}")
    report.append(f"- **Google for Nonprofits 驗證**: {'✅ 已通過' if org_info.get('google_nonprofit_verified') else '❌ 未通過'}")
    report.append("")
    
    # 合規缺口分析
    report.append("---")
    report.append("")
    report.append("## 🔍 合規缺口分析")
    report.append("")
    
    total_gaps = (
        len(gaps.get("missing_contact_info", [])) +
        len(gaps.get("missing_content_pages", [])) +
        len(gaps.get("missing_tracking", [])) +
        len(gaps.get("technical_issues", []))
    )
    
    report.append(f"**總缺口數**: {total_gaps}")
    report.append("")
    
    if gaps.get("missing_contact_info"):
        report.append("### 缺失的聯絡資訊")
        for item in gaps["missing_contact_info"]:
            report.append(f"- ❌ {item}")
        report.append("")
    
    if gaps.get("missing_content_pages"):
        report.append("### 缺失的網站內容")
        for item in gaps["missing_content_pages"]:
            report.append(f"- ❌ {item}")
        report.append("")
    
    if gaps.get("missing_tracking"):
        report.append("### 缺失的追蹤設定")
        for item in gaps["missing_tracking"]:
            report.append(f"- ❌ {item}")
        report.append("")
    
    if gaps.get("technical_issues"):
        report.append("### 技術問題")
        for issue in gaps["technical_issues"]:
            report.append(f"- ❌ {issue.get('issue', 'N/A')}")
            report.append(f"  - 狀態: {issue.get('status', 'N/A')}")
            report.append(f"  - 時間: {issue.get('timestamp', 'N/A')}")
        report.append("")
    
    # 合規任務
    report.append("---")
    report.append("")
    report.append("## 📋 合規任務清單")
    report.append("")
    
    if tasks:
        # 按優先級分組
        p0_tasks = [t for t in tasks if t.get("priority") == "P0"]
        p1_tasks = [t for t in tasks if t.get("priority") == "P1"]
        p2_tasks = [t for t in tasks if t.get("priority") == "P2"]
        
        if p0_tasks:
            report.append("### 🔴 P0 - 立即處理（阻擋基本合規）")
            report.append("")
            for i, task in enumerate(p0_tasks, 1):
                report.append(f"{i}. **{task.get('title', 'N/A')}**")
                report.append(f"   - 類別: {task.get('category', 'N/A')}")
                report.append(f"   - 說明: {task.get('description', 'N/A')}")
                if task.get("issues"):
                    report.append("   - 問題:")
                    for issue in task["issues"]:
                        report.append(f"     - {issue.get('issue', 'N/A')}")
                report.append("")
        
        if p1_tasks:
            report.append("### 🟡 P1 - 高優先級（阻擋 Google Ad Grants 合規）")
            report.append("")
            for i, task in enumerate(p1_tasks, 1):
                report.append(f"{i}. **{task.get('title', 'N/A')}**")
                report.append(f"   - 類別: {task.get('category', 'N/A')}")
                report.append(f"   - 說明: {task.get('description', 'N/A')}")
                if task.get("missing_items"):
                    report.append("   - 缺失項目:")
                    for item in task["missing_items"]:
                        report.append(f"     - {item}")
                report.append("")
        
        if p2_tasks:
            report.append("### 🟢 P2 - 中優先級（優化與完善）")
            report.append("")
            for i, task in enumerate(p2_tasks, 1):
                report.append(f"{i}. **{task.get('title', 'N/A')}**")
                report.append(f"   - 類別: {task.get('category', 'N/A')}")
                report.append(f"   - 說明: {task.get('description', 'N/A')}")
                report.append("")
    else:
        report.append("✅ 沒有發現合規缺口，所有項目都符合要求！")
        report.append("")
    
    # 建議行動
    report.append("---")
    report.append("")
    report.append("## 💡 建議行動")
    report.append("")
    report.append("### 1. 使用整合的合規資料")
    report.append("")
    report.append("已整合的合規資料檔案：")
    report.append("- `compliance_data.json` - 完整合規資料")
    report.append("- `website_content_data.json` - 網站內容資料")
    report.append("")
    report.append("可以使用這些資料建立合規網站頁面。")
    report.append("")
    
    report.append("### 2. 啟動雙J協作執行任務")
    report.append("")
    report.append("可以透過以下方式啟動雙J協作：")
    report.append("- 使用 `local_control_center.py` 的 UI 介面")
    report.append("- 使用 Google Tasks API 建立任務給 JULES")
    report.append("- 直接執行相關腳本")
    report.append("")
    
    report.append("### 3. 定期檢查合規狀態")
    report.append("")
    report.append("建議每週執行一次合規檢查：")
    report.append("```bash")
    report.append("python google_nonprofit_compliance_check.py")
    report.append("```")
    report.append("")
    
    report.append("---")
    report.append("")
    report.append("**報告生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return "\n".join(report)


def create_jules_task_for_compliance(task: Dict[str, Any]) -> Dict[str, Any]:
    """為 JULES 建立合規任務"""
    log(f"為 JULES 建立任務: {task.get('title', 'N/A')}", "PROGRESS")
    
    # 這裡可以整合 Google Tasks API 或直接建立任務檔案
    task_data = {
        "title": task.get("title", ""),
        "description": task.get("description", ""),
        "priority": task.get("priority", "P1"),
        "category": task.get("category", ""),
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "compliance_related": True,
    }
    
    return task_data


def main():
    """主函數"""
    print("=" * 70)
    print("雙J協作合規作業系統")
    print("=" * 70)
    print()
    
    # 1. 載入工作日誌
    work_logs = load_work_logs()
    
    # 2. 載入合規資料
    compliance_data = load_compliance_data()
    if not compliance_data:
        log("無法載入合規資料，請先執行 compliance_data_integration.py", "ERROR")
        return 1
    
    # 3. 分析合規缺口
    gaps = analyze_compliance_gaps(compliance_data, work_logs)
    
    # 4. 建立合規任務
    tasks = create_compliance_tasks(gaps, compliance_data)
    
    # 5. 生成報告
    print()
    print("=" * 70)
    print("生成合規作業報告")
    print("=" * 70)
    print()
    
    report = generate_compliance_work_report(work_logs, compliance_data, gaps, tasks)
    
    # 儲存報告
    report_file = BASE_DIR / f"雙J協作合規作業報告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding="utf-8")
    
    print(report)
    print()
    print(f"報告已儲存至: {report_file.name}")
    print()
    
    # 6. 建立 JULES 任務（可選）
    if tasks:
        print("=" * 70)
        print("建立 JULES 任務")
        print("=" * 70)
        print()
        
        jules_tasks = []
        for task in tasks:
            if task.get("priority") in ["P0", "P1"]:
                jules_task = create_jules_task_for_compliance(task)
                jules_tasks.append(jules_task)
                log(f"已建立任務: {task.get('title', 'N/A')}", "OK")
        
        if jules_tasks:
            tasks_file = BASE_DIR / f"compliance_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            tasks_file.write_text(
                json.dumps(jules_tasks, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print()
            print(f"任務清單已儲存至: {tasks_file.name}")
            print()
            print("💡 提示：可以使用 Google Tasks API 或 local_control_center.py 將這些任務傳送給 JULES")
    
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
