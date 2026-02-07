"""
五常社區服務系統 - 統一責任與權限管理系統 (URPM)
Unified Responsibility & Permission Management System

原則:
- 所有權限使用者都是可究責自然人
- 權限範圍與責任範圍一一對應
- 所有操作均自動記錄與審計
- 責任追蹤與究責機制完整
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import json


class ResponsibilityDomain(str, Enum):
    """責任領域定義"""
    HARDWARE = "hardware"        # 硬體設備
    AI_DESIGN = "ai_design"      # AI 設計
    ORGANIZATION = "organization"  # 組織治理
    DOMAIN = "domain"             # 網域管理
    ERP = "erp"                  # ERP 系統
    POS = "pos"                  # POS 營運

身份: POS 營運 (POS Manager)
責任: 日常營業、庫存、財務結帳
可行使權限: 系統全部權限（在 POS 營運範圍內）
可究責對象: 營業操作、客戶服務、現金準確性、銷售記錄
class NaturalPersonAuthority:
    """可究責自然人權限與責任系統"""

    def __init__(self):
        self.authorities: Dict[str, Dict[str, Any]] = {}
        self.responsibility_log: List[Dict] = []
        self.audit_trail: List[Dict] = []

    def register_natural_person(
        self,
        person_id: str,
        person_name: str,
        responsibility_domain: ResponsibilityDomain,
        scope: str,
        contact_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """註冊可究責自然人"""

        authority_record = {
            "person_id": person_id,
            "person_name": person_name,
            "responsibility_domain": responsibility_domain.value,
            "scope": scope,
            "contact_info": contact_info,
            "registration_date": datetime.utcnow().isoformat(),
            "permissions": self._get_permissions_for_domain(responsibility_domain),
            "responsibilities": self._get_responsibilities_for_domain(responsibility_domain),
            "accountability_status": "active",
            "audit_scope": "all_operations_in_domain"
        }

        self.authorities[person_id] = authority_record

        # 記錄此註冊
        self._audit_log(
            action="natural_person_registered",
            person_id=person_id,
            details=authority_record
        )

        return authority_record

    def _get_permissions_for_domain(self, domain: ResponsibilityDomain) -> List[str]:
        """根據責任領域取得權限清單"""

        permission_map = {
            ResponsibilityDomain.HARDWARE: [
                "manage_devices",
                "network_configuration",
                "system_restart",
                "maintenance_approval",
                "hardware_inventory"
            ],
            ResponsibilityDomain.AI_DESIGN: [
                "ai_model_management",
                "algorithm_updates",
                "prompt_engineering",
                "ai_decision_review",
                "bias_mitigation",
                "ethics_review"
            ],
            ResponsibilityDomain.ORGANIZATION: [
                "nonprofit_compliance",
                "policy_creation",
                "budget_allocation",
                "strategic_planning",
                "external_audit",
                "governance"
            ],
            ResponsibilityDomain.DOMAIN: [
                "user_management",
                "domain_security",
                "email_administration",
                "access_control",
                "workspace_settings"
            ],
            ResponsibilityDomain.ERP: [
                "database_management",
                "module_configuration",
                "backup_management",
                "disaster_recovery",
                "business_process_design"
            ],
            ResponsibilityDomain.POS: [
                "daily_operations",
                "inventory_management",
                "customer_service",
                "financial_settlement",
                "sales_reporting"
            ]
        }

        return permission_map.get(domain, [])

    def _get_responsibilities_for_domain(self, domain: ResponsibilityDomain) -> List[str]:
        """根據責任領域取得責任清單"""

        responsibility_map = {
            ResponsibilityDomain.HARDWARE: [
                "物理設備維護與保護",
                "網路連接穩定性",
                "設備更新升級",
                "故障診斷與修復",
                "安全備份與冗餘"
            ],
            ResponsibilityDomain.AI_DESIGN: [
                "AI 決策邏輯正確性",
                "演算法無偏見性",
                "倫理合規性",
                "決策可解釋性",
                "持續學習與改進",
                "隱私與安全"
            ],
            ResponsibilityDomain.ORGANIZATION: [
                "非營利組織合規",
                "財務透明度",
                "戰略規劃執行",
                "外部審計配合",
                "社區利益保護",
                "政策制定與推行"
            ],
            ResponsibilityDomain.DOMAIN: [
                "使用者存取管理",
                "網域安全防護",
                "郵件系統穩定",
                "身份驗證安全",
                "工作區資源分配"
            ],
            ResponsibilityDomain.ERP: [
                "業務數據準確性",
                "系統備份完整性",
                "災難復原能力",
                "流程設計合理性",
                "數據庫效能"
            ],
            ResponsibilityDomain.POS: [
                "營業操作正確性",
                "客戶服務品質",
                "庫存記錄準確",
                "現金收納安全",
                "銷售報表真實性"
            ]
        }

        return responsibility_map.get(domain, [])

    def execute_action(
        self,
        person_id: str,
        action: str,
        resource: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """執行操作 - 自動記錄與究責"""

        if person_id not in self.authorities:
            return {
                "status": "error",
                "message": "未知的可究責自然人"
            }

        authority = self.authorities[person_id]
        action_id = f"action_{datetime.now().timestamp()}"

        # 記錄操作
        action_record = {
            "action_id": action_id,
            "person_id": person_id,
            "person_name": authority["person_name"],
            "responsibility_domain": authority["responsibility_domain"],
            "action": action,
            "resource": resource,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "executed"
        }

        self.responsibility_log.append(action_record)
        self._audit_log(
            action="action_executed",
            person_id=person_id,
            details=action_record
        )

        return {
            "status": "success",
            "action_id": action_id,
            "message": f"操作已執行並記錄，可究責ID: {action_id}"
        }

    def get_person_accountability_report(self, person_id: str) -> Dict[str, Any]:
        """產生個人究責報告"""

        if person_id not in self.authorities:
            return {"error": "未找到此自然人記錄"}

        authority = self.authorities[person_id]

        # 收集此人的所有操作
        person_actions = [
            log for log in self.responsibility_log if log["person_id"] == person_id]

        return {
            "person_id": person_id,
            "person_name": authority["person_name"],
            "responsibility_domain": authority["responsibility_domain"],
            "scope": authority["scope"],
            "accountability_status": "active",
            "total_actions_executed": len(person_actions),
            "permissions_granted": authority["permissions"],
            "responsibilities_assigned": authority["responsibilities"],
            "recent_actions": person_actions[-10:],  # 最近10個操作
            "contact_for_accountability": authority["contact_info"],
            "report_generated": datetime.utcnow().isoformat()
        }

    def _audit_log(self, action: str, person_id: str, details: Dict):
        """審計日誌"""
        audit_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "person_id": person_id,
            "details": details
        }
        self.audit_trail.append(audit_record)


# 系統初始化 - 登記所有可究責自然人
def initialize_responsibility_system() -> NaturalPersonAuthority:
    """初始化責任與權限系統"""

    system = NaturalPersonAuthority()

    # 註冊所有可究責自然人
    authorities_to_register = [
        {
            "person_id": "hardware_owner_001",
            "person_name": "系統地端硬體設備所有權人",
            "domain": ResponsibilityDomain.HARDWARE,
            "scope": "192.168.50.0/24 網段內所有硬體設備",
            "contact": {"phone": "", "email": ""}
        },
        {
            "person_id": "ai_designer_001",
            "person_name": "系統 AI 設計人（小 j）",
            "domain": ResponsibilityDomain.AI_DESIGN,
            "scope": "所有 AI 決策、模型、算法",
            "contact": {"phone": "", "email": ""}
        },
        {
            "person_id": "google_nonprofit_admin_001",
            "person_name": "Google 非營利組織超級管理員",
            "domain": ResponsibilityDomain.ORGANIZATION,
            "scope": "Google Workspace 整個組織",
            "contact": {"phone": "", "email": ""}
        },
        {
            "person_id": "workspace_admin_001",
            "person_name": "Workspace 超級管理員（wuchang.life 租用人）",
            "domain": ResponsibilityDomain.DOMAIN,
            "scope": "wuchang.life 網域及所有使用者",
            "contact": {"phone": "", "email": ""}
        },
        {
            "person_id": "odoo_admin_001",
            "person_name": "Odoo 最高權限帳號持有人",
            "domain": ResponsibilityDomain.ERP,
            "scope": "Odoo 18 整個 ERP 系統",
            "contact": {"phone": "", "email": ""}
        },
        {
            "person_id": "pos_manager_001",
            "person_name": "品啦國咖啡 POS 負責人",
            "domain": ResponsibilityDomain.POS,
            "scope": "POS 營運及日常商業管理",
            "contact": {"phone": "", "email": ""}
        }
    ]

    for auth in authorities_to_register:
        system.register_natural_person(
            person_id=auth["person_id"],
            person_name=auth["person_name"],
            responsibility_domain=auth["domain"],
            scope=auth["scope"],
            contact_info=auth["contact"]
        )

    return system


# API 整合
def add_accountability_endpoints(app, responsibility_system: NaturalPersonAuthority):
    """將究責系統端點加入 FastAPI"""

    @app.get('/accountability/person/{person_id}')
    async def get_person_report(person_id: str):
        """取得可究責自然人的責任與權限報告"""
        return responsibility_system.get_person_accountability_report(person_id)

    @app.get('/accountability/all-authorities')
    async def list_all_authorities():
        """列出所有可究責自然人"""
        return {
            "total_authorities": len(responsibility_system.authorities),
            "authorities": list(responsibility_system.authorities.values())
        }

    @app.post('/accountability/record-action')
    async def record_action(
        person_id: str,
        action: str,
        resource: str,
        details: Dict[str, Any]
    ):
        """記錄操作 - 建立究責軌跡"""
        return responsibility_system.execute_action(
            person_id=person_id,
            action=action,
            resource=resource,
            details=details
        )

    @app.get('/accountability/audit-trail')
    async def get_audit_trail(limit: int = 100):
        """查看審計軌跡"""
        return {
            "total_records": len(responsibility_system.audit_trail),
            "recent_audits": responsibility_system.audit_trail[-limit:]
        }


if __name__ == "__main__":
    print("五常社區服務系統 - 統一責任與權限管理系統")
    print("="*70)

    # 初始化系統
    system = initialize_responsibility_system()

    print("\n✓ 已註冊的可究責自然人：\n")
    for person_id, authority in system.authorities.items():
        print(f"【{authority['person_name']}】")
        print(f"  ID: {person_id}")
        print(f"  責任領域: {authority['responsibility_domain']}")
        print(f"  責任範圍: {authority['scope']}")
        print(f"  可行使權限數: {len(authority['permissions'])}")
        print(f"  承擔責任數: {len(authority['responsibilities'])}")
        print()

    print("="*70)
    print("所有自然人均獲得系統全部權限（在各自責任範圍內）")
    print("所有操作均自動記錄，可究責軌跡完整")
    print("="*70)
