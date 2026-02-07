#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dual_j_compliance_improvement_planning.py

最高權限代理 - 招集雙J協作進行改善工作規劃

功能：
- 以系統創辦人最高權限代理身份
- 招集地端小J和雲端小J（JULES）協作
- 根據合規查驗結果規劃改善工作
- 建立 Google Tasks 任務給 JULES 執行
- 生成改善工作規劃報告
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
JULES_MEMORY_BANK_FILE = BASE_DIR / "jules_memory_bank.json"
COMPLIANCE_REPORT_FILE = BASE_DIR / "合規查驗詳細報告_20260123.md"
COMPLIANCE_CHECK_RESULTS_FILE = BASE_DIR / "compliance_check_results_20260123_040458.json"
PLANNING_REPORT_FILE = BASE_DIR / f"雙J協作改善工作規劃_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
TASKS_FILE = BASE_DIR / f"compliance_improvement_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# 最高權限代理資訊
AUTHORITY_INFO = {
    "grantor": "系統創辦人，本系統設計人",
    "permission_level": "階段三權限（權限解放）",
    "authority_type": "第一類可究責對象",
    "grant_time": datetime.now().isoformat(),
    "scope": "合規改善工作規劃與執行"
}

# 改善工作項目（根據合規查驗結果）
IMPROVEMENT_TASKS = {
    "P0_HTTPS_SSL": {
        "priority": "P0",
        "title": "修復 HTTPS/SSL 證書配置",
        "category": "技術基礎設施",
        "assigned_to": "JULES",
        "estimated_time": "2-4 小時",
        "description": "修復 HTTPS/SSL 證書配置問題，這是阻擋所有合規驗證的根本問題",
        "steps": [
            "檢查 Caddy 配置檔案（Caddyfile）",
            "確認 SSL 證書已正確安裝到 Caddy",
            "確認 Caddy 監聽 443 端口",
            "檢查防火牆規則是否允許 HTTPS 流量",
            "確認 DNS 記錄正確指向伺服器 IP（220.135.21.74）",
            "檢查 Cloudflare Tunnel 配置（如使用）",
            "測試 HTTPS 連線是否正常",
            "驗證 SSL 證書有效性"
        ],
        "dependencies": [],
        "expected_outcome": "HTTPS 連線正常，SSL 證書有效，可通過 HTTPS 訪問網站"
    },
    "P1_GA4_CONFIG": {
        "priority": "P1",
        "title": "配置 Google Analytics 4 測量 ID",
        "category": "轉換追蹤",
        "assigned_to": "地端小J",
        "estimated_time": "1-2 小時",
        "description": "建立 GA4 屬性，取得測量 ID，更新所有 HTML 檔案",
        "steps": [
            "建立 Google Analytics 4 屬性",
            "取得測量 ID（格式：G-XXXXXXXXXX）",
            "更新 index.html 中的 GA4 ID",
            "更新 about.html 中的 GA4 ID",
            "更新 mission.html 中的 GA4 ID",
            "更新 contact.html 中的 GA4 ID",
            "使用 Google Tag Assistant 驗證安裝",
            "配置轉換事件（聯絡表單提交、頁面瀏覽等）"
        ],
        "dependencies": [],
        "expected_outcome": "Google Analytics 4 正常運作，轉換追蹤已配置"
    },
    "P1_VERIFY_CONTENT": {
        "priority": "P1",
        "title": "驗證網站內容合規性",
        "category": "網站內容",
        "assigned_to": "JULES",
        "estimated_time": "1 小時",
        "description": "HTTPS 修復後，驗證所有頁面內容是否符合合規要求",
        "steps": [
            "確認 HTTPS 已修復",
            "訪問 https://wuchang.life/about.html 驗證關於我們頁面",
            "訪問 https://wuchang.life/mission.html 驗證使命與活動頁面",
            "訪問 https://wuchang.life/contact.html 驗證聯絡我們頁面",
            "檢查 index.html 中的組織資訊披露",
            "確認所有頁面內容完整且符合合規要求",
            "重新執行合規檢查驗證結果"
        ],
        "dependencies": ["P0_HTTPS_SSL"],
        "expected_outcome": "所有頁面內容通過合規檢查"
    },
    "P2_DNS_ACME": {
        "priority": "P2",
        "title": "配置 DNS _acme-challenge TXT 記錄（可選）",
        "category": "DNS 配置",
        "assigned_to": "JULES",
        "estimated_time": "30 分鐘",
        "description": "如使用 Let's Encrypt，需要添加 _acme-challenge TXT 記錄",
        "steps": [
            "確認證書管理方式（Let's Encrypt / Cloudflare Tunnel / 其他）",
            "如使用 Let's Encrypt，添加 _acme-challenge TXT 記錄",
            "如使用其他方式，可忽略此任務"
        ],
        "dependencies": [],
        "expected_outcome": "DNS 記錄完整（依證書管理方式決定）"
    }
}


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄",
        "AUTHORITY": "🔐"
    }
    icon = icons.get(level, "•")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{icon} [{timestamp}] [{level}] {message}"
    print(log_entry)


def load_memory_bank() -> Dict[str, Any]:
    """載入 JULES 記憶庫"""
    if JULES_MEMORY_BANK_FILE.exists():
        try:
            return json.loads(JULES_MEMORY_BANK_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"載入記憶庫失敗: {e}", "ERROR")
            return {}
    return {}


def load_compliance_results() -> Dict[str, Any]:
    """載入合規檢查結果"""
    if COMPLIANCE_CHECK_RESULTS_FILE.exists():
        try:
            return json.loads(COMPLIANCE_CHECK_RESULTS_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"載入合規檢查結果失敗: {e}", "ERROR")
            return {}
    return {}


def create_google_task(task_info: Dict[str, Any], task_list_id: str = None) -> Optional[str]:
    """建立 Google Tasks 任務給 JULES"""
    try:
        from google_tasks_integration import GoogleTasksManager, GoogleTask
        
        manager = GoogleTasksManager()
        
        # 建立任務
        task = GoogleTask(
            title=f"[{task_info['priority']}] {task_info['title']}",
            notes=format_task_notes(task_info),
            status="needsAction"
        )
        
        # 設定截止日期（根據優先級）
        if task_info['priority'] == 'P0':
            task.due = (datetime.now() + timedelta(days=1)).isoformat() + 'Z'
        elif task_info['priority'] == 'P1':
            task.due = (datetime.now() + timedelta(days=3)).isoformat() + 'Z'
        else:
            task.due = (datetime.now() + timedelta(days=7)).isoformat() + 'Z'
        
        # 建立任務
        created_task = manager.create_task(task, task_list_id=task_list_id)
        
        if created_task and created_task.id:
            log(f"已建立任務: {task_info['title']} (ID: {created_task.id})", "OK")
            return created_task.id
        else:
            log(f"建立任務失敗: {task_info['title']}", "ERROR")
            return None
            
    except ImportError:
        log("Google Tasks API 未安裝，將任務儲存到本地檔案", "WARN")
        return None
    except Exception as e:
        log(f"建立 Google Tasks 任務失敗: {e}", "ERROR")
        return None


def format_task_notes(task_info: Dict[str, Any]) -> str:
    """格式化任務備註"""
    notes = []
    notes.append(f"類別: {task_info['category']}")
    notes.append(f"分配給: {task_info['assigned_to']}")
    notes.append(f"預估時間: {task_info['estimated_time']}")
    notes.append("")
    notes.append("描述:")
    notes.append(task_info['description'])
    notes.append("")
    notes.append("執行步驟:")
    for i, step in enumerate(task_info['steps'], 1):
        notes.append(f"{i}. {step}")
    
    if task_info.get('dependencies'):
        notes.append("")
        notes.append("依賴任務:")
        for dep in task_info['dependencies']:
            notes.append(f"- {dep}")
    
    notes.append("")
    notes.append("預期結果:")
    notes.append(task_info['expected_outcome'])
    notes.append("")
    notes.append("---")
    notes.append(f"建立時間: {datetime.now().isoformat()}")
    notes.append(f"授權者: {AUTHORITY_INFO['grantor']}")
    notes.append(f"權限等級: {AUTHORITY_INFO['permission_level']}")
    
    return "\n".join(notes)


def generate_planning_report(tasks: Dict[str, Dict[str, Any]], task_ids: Dict[str, Optional[str]]) -> str:
    """生成改善工作規劃報告"""
    report = []
    report.append("# 雙J協作改善工作規劃")
    report.append("")
    report.append(f"**規劃時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**授權者**: {AUTHORITY_INFO['grantor']}")
    report.append(f"**權限等級**: {AUTHORITY_INFO['permission_level']}")
    report.append("")
    report.append("---")
    report.append("")
    
    # 授權資訊
    report.append("## 🔐 最高權限代理授權")
    report.append("")
    report.append("本規劃由**系統創辦人，本系統設計人**（第一類可究責對象）授權執行。")
    report.append("")
    report.append(f"- **授權者**: {AUTHORITY_INFO['grantor']}")
    report.append(f"- **權限等級**: {AUTHORITY_INFO['permission_level']}")
    report.append(f"- **授權時間**: {AUTHORITY_INFO['grant_time']}")
    report.append(f"- **授權範圍**: {AUTHORITY_INFO['scope']}")
    report.append("")
    report.append("---")
    report.append("")
    
    # 合規狀態摘要
    compliance_results = load_compliance_results()
    report.append("## 📊 合規狀態摘要")
    report.append("")
    report.append("**當前合規分數**: 10.0% (1/10 項目通過)")
    report.append("**合規狀態**: 🔴 不符合（需立即處理）")
    report.append("")
    report.append("### 主要問題")
    report.append("1. **HTTPS/SSL 證書配置失敗** - 阻擋所有驗證")
    report.append("2. **Google Analytics 未配置** - 待配置實際 ID")
    report.append("3. **網站內容合規性** - 已準備好，待 HTTPS 修復後驗證")
    report.append("")
    report.append("---")
    report.append("")
    
    # 改善工作規劃
    report.append("## 📋 改善工作規劃")
    report.append("")
    
    # 按優先級分組
    p0_tasks = {k: v for k, v in tasks.items() if v['priority'] == 'P0'}
    p1_tasks = {k: v for k, v in tasks.items() if v['priority'] == 'P1'}
    p2_tasks = {k: v for k, v in tasks.items() if v['priority'] == 'P2'}
    
    # P0 任務
    if p0_tasks:
        report.append("### 🔴 P0 - 立即處理（阻擋驗證）")
        report.append("")
        for task_id, task_info in p0_tasks.items():
            task_id_str = task_ids.get(task_id, "未建立")
            report.append(f"#### {task_info['title']}")
            report.append("")
            report.append(f"- **任務 ID**: {task_id}")
            report.append(f"- **Google Tasks ID**: {task_id_str}")
            report.append(f"- **分配給**: {task_info['assigned_to']}")
            report.append(f"- **預估時間**: {task_info['estimated_time']}")
            report.append(f"- **類別**: {task_info['category']}")
            report.append("")
            report.append("**描述**:")
            report.append(task_info['description'])
            report.append("")
            report.append("**執行步驟**:")
            for i, step in enumerate(task_info['steps'], 1):
                report.append(f"{i}. {step}")
            report.append("")
            report.append("**預期結果**:")
            report.append(task_info['expected_outcome'])
            report.append("")
    
    # P1 任務
    if p1_tasks:
        report.append("### 🟡 P1 - 高優先級（完成合規）")
        report.append("")
        for task_id, task_info in p1_tasks.items():
            task_id_str = task_ids.get(task_id, "未建立")
            report.append(f"#### {task_info['title']}")
            report.append("")
            report.append(f"- **任務 ID**: {task_id}")
            report.append(f"- **Google Tasks ID**: {task_id_str}")
            report.append(f"- **分配給**: {task_info['assigned_to']}")
            report.append(f"- **預估時間**: {task_info['estimated_time']}")
            report.append(f"- **類別**: {task_info['category']}")
            if task_info.get('dependencies'):
                report.append(f"- **依賴任務**: {', '.join(task_info['dependencies'])}")
            report.append("")
            report.append("**描述**:")
            report.append(task_info['description'])
            report.append("")
            report.append("**執行步驟**:")
            for i, step in enumerate(task_info['steps'], 1):
                report.append(f"{i}. {step}")
            report.append("")
            report.append("**預期結果**:")
            report.append(task_info['expected_outcome'])
            report.append("")
    
    # P2 任務
    if p2_tasks:
        report.append("### 🟢 P2 - 中優先級（優化）")
        report.append("")
        for task_id, task_info in p2_tasks.items():
            task_id_str = task_ids.get(task_id, "未建立")
            report.append(f"#### {task_info['title']}")
            report.append("")
            report.append(f"- **任務 ID**: {task_id}")
            report.append(f"- **Google Tasks ID**: {task_id_str}")
            report.append(f"- **分配給**: {task_info['assigned_to']}")
            report.append(f"- **預估時間**: {task_info['estimated_time']}")
            report.append(f"- **類別**: {task_info['category']}")
            report.append("")
            report.append("**描述**:")
            report.append(task_info['description'])
            report.append("")
            report.append("**執行步驟**:")
            for i, step in enumerate(task_info['steps'], 1):
                report.append(f"{i}. {step}")
            report.append("")
    
    # 協作機制
    report.append("---")
    report.append("")
    report.append("## 🤝 雙J協作機制")
    report.append("")
    report.append("### 地端小J 職責")
    report.append("- 監控改善工作進度")
    report.append("- 驗證改善結果")
    report.append("- 執行本地可完成的任務（如 GA4 配置）")
    report.append("- 記錄工作日誌")
    report.append("")
    report.append("### 雲端小J (JULES) 職責")
    report.append("- 接收 Google Tasks 任務")
    report.append("- 執行技術修復任務（如 HTTPS/SSL 配置）")
    report.append("- 回報執行結果")
    report.append("- 更新任務狀態")
    report.append("")
    report.append("### 協作流程")
    report.append("1. 地端小J 監控合規狀態")
    report.append("2. 發現問題並規劃改善工作")
    report.append("3. 建立 Google Tasks 任務給 JULES")
    report.append("4. JULES 執行任務並回報結果")
    report.append("5. 地端小J 驗證改善結果")
    report.append("6. 重新執行合規檢查確認改善效果")
    report.append("")
    
    # 預期改善效果
    report.append("---")
    report.append("")
    report.append("## 📈 預期改善效果")
    report.append("")
    report.append("### 當前狀態")
    report.append("- **合規分數**: 10.0% (1/10)")
    report.append("- **阻擋因素**: HTTPS/SSL 配置問題")
    report.append("")
    report.append("### HTTPS 修復後預期")
    report.append("- **合規分數**: 預計 40-50% (4-5/10)")
    report.append("- **新增通過項目**:")
    report.append("  - ✅ 關於我們頁面")
    report.append("  - ✅ 使命與活動頁面")
    report.append("  - ✅ 聯絡方式")
    report.append("  - ✅ 組織資訊披露")
    report.append("")
    report.append("### GA4 配置後預期")
    report.append("- **合規分數**: 預計 50-60% (5-6/10)")
    report.append("- **新增通過項目**:")
    report.append("  - ✅ Google Analytics")
    report.append("")
    report.append("### 最終目標")
    report.append("- **合規分數**: 80-90% (8-9/10)")
    report.append("- **剩餘問題**: HTTPS/SSL 配置（需技術修復）")
    report.append("")
    
    return "\n".join(report)


def main():
    """主函數"""
    log("="*60, "AUTHORITY")
    log("最高權限代理 - 招集雙J協作進行改善工作規劃", "AUTHORITY")
    log("="*60, "AUTHORITY")
    log("")
    log(f"授權者: {AUTHORITY_INFO['grantor']}", "AUTHORITY")
    log(f"權限等級: {AUTHORITY_INFO['permission_level']}", "AUTHORITY")
    log("")
    
    # 載入記憶庫
    memory_bank = load_memory_bank()
    log("已載入 JULES 記憶庫", "OK")
    
    # 載入合規檢查結果
    compliance_results = load_compliance_results()
    log("已載入合規檢查結果", "OK")
    
    # 建立任務
    log("開始建立改善工作任務", "PROGRESS")
    task_ids = {}
    tasks_data = []
    
    for task_id, task_info in IMPROVEMENT_TASKS.items():
        log(f"建立任務: {task_info['title']}", "PROGRESS")
        google_task_id = create_google_task(task_info)
        task_ids[task_id] = google_task_id
        
        task_data = {
            "task_id": task_id,
            "google_task_id": google_task_id,
            "task_info": task_info,
            "created_at": datetime.now().isoformat(),
            "authority": AUTHORITY_INFO
        }
        tasks_data.append(task_data)
    
    # 儲存任務資料
    TASKS_FILE.write_text(
        json.dumps(tasks_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"任務資料已儲存: {TASKS_FILE.name}", "OK")
    
    # 生成規劃報告
    log("生成改善工作規劃報告", "PROGRESS")
    report = generate_planning_report(IMPROVEMENT_TASKS, task_ids)
    PLANNING_REPORT_FILE.write_text(report, encoding="utf-8")
    log(f"規劃報告已儲存: {PLANNING_REPORT_FILE.name}", "OK")
    
    # 輸出摘要
    print()
    print("="*60)
    print("改善工作規劃完成")
    print("="*60)
    print()
    print("📋 已建立的任務:")
    for task_id, task_info in IMPROVEMENT_TASKS.items():
        google_task_id = task_ids.get(task_id, "未建立")
        status = "✅" if google_task_id else "⚠️"
        print(f"  {status} [{task_info['priority']}] {task_info['title']}")
        print(f"     分配給: {task_info['assigned_to']}")
        print(f"     Google Tasks ID: {google_task_id}")
    print()
    print("📁 生成的檔案:")
    print(f"  - {PLANNING_REPORT_FILE.name}")
    print(f"  - {TASKS_FILE.name}")
    print()
    print("🤝 雙J協作已啟動")
    print("  - 地端小J: 監控進度、驗證結果")
    print("  - 雲端小J (JULES): 執行任務、回報結果")
    print()
    print("="*60)


if __name__ == "__main__":
    main()
