#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compliance_data_integration.py

合規資料整合工具

功能：
- 從各資料檔案中提取組織資訊
- 整合聯絡方式、使命說明等合規所需資料
- 生成合規作業用的統一資料結構
- 支援合規檢查和報告生成
"""

import sys
import json
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


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """載入 JSON 檔案"""
    try:
        if file_path.exists():
            return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️  無法載入 {file_path.name}: {e}")
    return {}


def load_markdown_file(file_path: Path) -> str:
    """載入 Markdown 檔案"""
    try:
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"⚠️  無法載入 {file_path.name}: {e}")
    return ""


def extract_organization_info() -> Dict[str, Any]:
    """提取組織資訊"""
    print("📋 提取組織資訊...")
    
    org_info = {
        "name": "新北市三重區五常社區發展協會",
        "name_en": "Wuchang Community Development Association, Sanchong District, New Taipei City",
        "country": "台灣",
        "country_en": "Taiwan",
        "region": "新北市三重區",
        "type": "社區發展協會",
        "legal_status": "合法註冊的非營利組織",
        "google_nonprofit_verified": True,
        "verification_date": "永久事實（依 AGENT_CONSTITUTION.md）",
        "registration_number": None,  # 待補充
        "founded_date": None,  # 待補充
    }
    
    # 從 jules_memory_bank.json 提取
    memory_bank = load_json_file(BASE_DIR / "jules_memory_bank.json")
    if memory_bank:
        community_info = memory_bank.get("community_info", {})
        if community_info:
            org_info["jurisdiction"] = community_info.get("title", "")
            org_info["service_area"] = community_info.get("service_area", {})
    
    # 從 accounts_policy.json 提取
    accounts_policy = load_json_file(BASE_DIR / "accounts_policy.json")
    if accounts_policy:
        accounts = accounts_policy.get("accounts", [])
        for account in accounts:
            if account.get("account_id") == "1001":
                org_name = account.get("design_responsibility", {}).get("natural_person", {}).get("organization")
                if org_name:
                    org_info["name"] = org_name
    
    return org_info


def extract_contact_info() -> Dict[str, Any]:
    """提取聯絡方式"""
    print("📞 提取聯絡方式...")
    
    contact_info = {
        "address": {
            "street": None,
            "district": "三重區",
            "city": "新北市",
            "postal_code": None,
            "country": "台灣",
        },
        "phone": None,
        "email": None,
        "website": "https://wuchang.life",
        "social_media": {},
    }
    
    # 從協會章程提取會址
    charter = load_markdown_file(BASE_DIR / "association_operational_files" / "01_協會章程.md")
    if charter:
        if "會址" in charter or "第四條" in charter:
            lines = charter.split('\n')
            for i, line in enumerate(lines):
                if "會址" in line or "第四條" in line:
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if "新北市三重區" in next_line:
                            # 嘗試提取地址
                            address_parts = next_line.split('新北市三重區')
                            if len(address_parts) > 1:
                                street = address_parts[1].strip()
                                if street and "待補充" not in street:
                                    contact_info["address"]["street"] = street
                            contact_info["address"]["city"] = "新北市"
                            contact_info["address"]["district"] = "三重區"
    
    # 從 internal_id_records.json 提取
    internal_records = load_json_file(BASE_DIR / "internal_id_records.json")
    if internal_records:
        records = internal_records.get("records", [])
        for record in records:
            if record.get("role") == "總幹事":
                if record.get("address"):
                    contact_info["address"]["street"] = record.get("address")
                if record.get("phone"):
                    contact_info["phone"] = record.get("phone")
                if record.get("email"):
                    contact_info["email"] = record.get("email")
    
    return contact_info


def extract_mission_statement() -> Dict[str, Any]:
    """提取使命說明"""
    print("🎯 提取使命說明...")
    
    mission = {
        "mission": "最大化商家及消費者利益，沒了私利就有眾利",
        "vision": None,
        "core_values": [],
        "main_activities": [],
        "objectives": [],
    }
    
    # 從 jules_personality_profile.json 提取
    personality = load_json_file(BASE_DIR / "jules_personality_profile.json")
    if personality:
        core_identity = personality.get("core_identity", {})
        if core_identity:
            mission["mission"] = core_identity.get("mission", mission["mission"])
    
    # 從協會章程提取宗旨
    charter = load_markdown_file(BASE_DIR / "association_operational_files" / "01_協會章程.md")
    if charter:
        # 提取宗旨
        if "宗旨" in charter:
            lines = charter.split('\n')
            for i, line in enumerate(lines):
                if "宗旨" in line and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if "促進社區發展" in next_line or "增進居民福祉" in next_line:
                        mission["mission"] = "促進社區發展、增進居民福祉、推動社區營造、提升生活品質"
                        break
        
        # 提取任務（主要活動）
        if "任務" in charter or "第六條" in charter:
            activities = []
            lines = charter.split('\n')
            in_tasks = False
            for line in lines:
                if "任務" in line or "第六條" in line:
                    in_tasks = True
                    continue
                if in_tasks and line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                    activity = line.strip().split('.', 1)[-1].strip()
                    if activity:
                        activities.append(activity)
                elif in_tasks and line.strip() and not line.strip().startswith('#'):
                    if activities:  # 如果已經開始收集活動，遇到空行或標題就停止
                        break
            if activities:
                mission["main_activities"] = activities[:8]  # 最多8個
    
    # 從 association_operational_files/02_年度工作計畫_2026.md 提取
    work_plan = load_markdown_file(BASE_DIR / "association_operational_files" / "02_年度工作計畫_2026.md")
    if work_plan:
        # 提取年度工作目標
        if "年度工作目標" in work_plan or "總體目標" in work_plan:
            objectives = []
            lines = work_plan.split('\n')
            in_objectives = False
            for line in lines:
                if "總體目標" in line or "年度工作目標" in line:
                    in_objectives = True
                    continue
                if in_objectives and line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    objective = line.strip().split('.', 1)[-1].strip()
                    if objective:
                        objectives.append(objective)
                elif in_objectives and line.strip().startswith('##'):
                    break
            if objectives:
                mission["objectives"] = objectives[:5]
    
    # 從 wuchang_community_analysis.json 提取
    community_analysis = load_json_file(BASE_DIR / "wuchang_community_analysis.json")
    if community_analysis:
        key_insights = community_analysis.get("key_insights", [])
        if key_insights:
            # 處理不同格式的 key_insights
            objectives = []
            for insight in key_insights[:5]:
                if isinstance(insight, dict):
                    objectives.append(insight.get("title", str(insight)))
                else:
                    objectives.append(str(insight))
            mission["objectives"] = objectives
    
    return mission


def extract_service_area() -> Dict[str, Any]:
    """提取服務區域"""
    print("🗺️  提取服務區域...")
    
    service_area = {
        "jurisdiction": "五常社區發展協會轄區",
        "districts": [],
        "boundaries": None,
        "description": "五常社區發展協會服務轄區包含三個里",
    }
    
    # 從 jules_memory_bank.json 提取
    memory_bank = load_json_file(BASE_DIR / "jules_memory_bank.json")
    if memory_bank:
        community_info = memory_bank.get("community_info", {})
        if community_info:
            service_area["jurisdiction"] = community_info.get("title", service_area["jurisdiction"])
            service_area["description"] = community_info.get("description", service_area["description"])
            
            districts = community_info.get("districts", [])
            for district in districts:
                service_area["districts"].append({
                    "name": district.get("name", ""),
                    "description": district.get("description", ""),
                })
    
    # 從 wuchang_community_boundary.geojson 提取地理邊界
    geojson_file = BASE_DIR / "wuchang_community_boundary.geojson"
    if geojson_file.exists():
        geojson_data = load_json_file(geojson_file)
        if geojson_data:
            service_area["boundaries"] = geojson_data
    
    return service_area


def extract_governance_info() -> Dict[str, Any]:
    """提取治理資訊"""
    print("⚖️  提取治理資訊...")
    
    governance = {
        "fund_pool": {
            "name": "五常社區發展基金",
            "carrier": "仁義店會計系統",
            "principles": [
                "獨立基金池",
                "無資本利得",
                "不得私領",
                "只能依規定支出",
                "進貨/銷貨等作業必須可稽核"
            ]
        },
        "sponsor": {
            "name": "重新店",
            "role": "只出不進",
            "restrictions": [
                "不得回收",
                "不得核銷",
                "不得以幸福幣折抵或兌回任何利益"
            ],
            "contributions": [
                "網路",
                "伺服器",
                "設備",
                "人力等基礎設施"
            ]
        },
        "compliance_principles": [
            "合規",
            "可究責",
            "可追溯留痕"
        ],
    }
    
    # 從 AGENT_CONSTITUTION.md 提取
    constitution = load_markdown_file(BASE_DIR / "AGENT_CONSTITUTION.md")
    if constitution:
        # 可以從憲法中提取更多治理資訊
        pass
    
    return governance


def extract_legal_documents() -> List[Dict[str, Any]]:
    """提取法律文件資訊"""
    print("📄 提取法律文件資訊...")
    
    documents = []
    
    # 協會章程
    charter_file = BASE_DIR / "association_operational_files" / "01_協會章程.md"
    if charter_file.exists():
        documents.append({
            "type": "協會章程",
            "file": str(charter_file.relative_to(BASE_DIR)),
            "description": "組織章程與治理規範",
        })
    
    # 年度工作計畫
    work_plan_file = BASE_DIR / "association_operational_files" / "02_年度工作計畫_2026.md"
    if work_plan_file.exists():
        documents.append({
            "type": "年度工作計畫",
            "file": str(work_plan_file.relative_to(BASE_DIR)),
            "description": "2026年度工作計畫",
            "year": 2026,
        })
    
    # 財務管理規範
    financial_file = BASE_DIR / "association_operational_files" / "04_財務管理規範.md"
    if financial_file.exists():
        documents.append({
            "type": "財務管理規範",
            "file": str(financial_file.relative_to(BASE_DIR)),
            "description": "財務管理與會計規範",
        })
    
    return documents


def generate_compliance_data() -> Dict[str, Any]:
    """生成合規資料結構"""
    print("=" * 70)
    print("合規資料整合")
    print("=" * 70)
    print()
    
    compliance_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generated_by": "compliance_data_integration.py",
            "version": "1.0",
            "purpose": "Google 非營利組織合規作業資料整合",
        },
        "organization": extract_organization_info(),
        "contact": extract_contact_info(),
        "mission": extract_mission_statement(),
        "service_area": extract_service_area(),
        "governance": extract_governance_info(),
        "legal_documents": extract_legal_documents(),
        "compliance_status": {
            "google_nonprofit_verified": True,
            "verification_evidence": [
                "AGENT_CONSTITUTION.md",
                "ASSET_INVENTORY.md",
            ],
            "compliance_score": None,  # 將由合規檢查更新
            "last_check": None,
        },
    }
    
    return compliance_data


def generate_website_content_data(compliance_data: Dict[str, Any]) -> Dict[str, Any]:
    """生成網站內容資料（用於建立合規頁面）"""
    print("🌐 生成網站內容資料...")
    
    website_content = {
        "about_us": {
            "title": "關於我們",
            "organization_name": compliance_data["organization"]["name"],
            "organization_name_en": compliance_data["organization"].get("name_en", ""),
            "type": compliance_data["organization"]["type"],
            "country": compliance_data["organization"]["country"],
            "region": compliance_data["organization"]["region"],
            "legal_status": compliance_data["organization"]["legal_status"],
            "google_nonprofit_status": "已通過 Google for Nonprofits 驗證",
            "description": compliance_data["service_area"]["description"],
        },
        "mission": {
            "title": "使命與活動",
            "mission_statement": compliance_data["mission"]["mission"],
            "vision": compliance_data["mission"].get("vision", ""),
            "main_activities": compliance_data["mission"].get("main_activities", []),
            "objectives": compliance_data["mission"].get("objectives", []),
        },
        "contact": {
            "title": "聯絡我們",
            "address": compliance_data["contact"]["address"],
            "phone": compliance_data["contact"].get("phone", "待補充"),
            "email": compliance_data["contact"].get("email", "待補充"),
            "website": compliance_data["contact"]["website"],
        },
        "service_area": {
            "title": "服務區域",
            "jurisdiction": compliance_data["service_area"]["jurisdiction"],
            "districts": compliance_data["service_area"]["districts"],
            "description": compliance_data["service_area"]["description"],
        },
    }
    
    return website_content


def main():
    """主函數"""
    print("=" * 70)
    print("合規資料整合工具")
    print("=" * 70)
    print()
    
    # 生成合規資料
    compliance_data = generate_compliance_data()
    
    # 生成網站內容資料
    website_content = generate_website_content_data(compliance_data)
    
    # 儲存合規資料
    compliance_file = BASE_DIR / "compliance_data.json"
    compliance_file.write_text(
        json.dumps(compliance_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print()
    print(f"✅ 合規資料已儲存至: {compliance_file.name}")
    
    # 儲存網站內容資料
    website_content_file = BASE_DIR / "website_content_data.json"
    website_content_file.write_text(
        json.dumps(website_content, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✅ 網站內容資料已儲存至: {website_content_file.name}")
    
    # 顯示摘要
    print()
    print("=" * 70)
    print("資料整合摘要")
    print("=" * 70)
    print()
    print(f"組織名稱: {compliance_data['organization']['name']}")
    print(f"使命: {compliance_data['mission']['mission']}")
    print(f"服務區域: {compliance_data['service_area']['jurisdiction']}")
    print(f"法律文件: {len(compliance_data['legal_documents'])} 個")
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
