import datetime
from wuchang_axioms import WuchangAxioms, AxiomType
from wuchang_safety_standard import WuchangSafetyStandard, SafetyPrinciple

class TranscendentLogicCore:
    """
    超越大廠邏輯核心 (Transcendent Logic Core)

    負責處理非典型演算法，將「五常公理」與「安全標準」轉化為實際運算邏輯。
    此核心允許系統在面對「大廠邏輯」與「五常價值」衝突時，優先選擇後者。
    """

    def __init__(self):
        self.axioms = WuchangAxioms()
        self.safety = WuchangSafetyStandard()
        self.version = "1.0.0 (EVOLVED)"
        self.dynamic_axioms = {}
        print(f"🧠 [CORE] Transcendent Logic Core v{self.version} Initialized.")

    def define_axiom(self, name, definition, weight="HIGH"):
        """
        動態定義公理 (允許創世者即時注入新規則)
        """
        self.dynamic_axioms[name] = {
            "name": name,
            "definition": definition,
            "weight": weight,
            "timestamp": datetime.datetime.now().isoformat()
        }
        print(f"   👑 AXIOM DEFINED: {name} - {definition} [{weight}]")

    def compute_decision(self, context, standard_logic_result=None):
        """
        計算決策：將標準邏輯結果輸入，並依據超越邏輯進行修正或覆蓋
        """
        # print(f"🧠 [CORE] Computing Decision for context: {context.get('intent', 'UNKNOWN')}")

        # 1. 優先檢查動態公理 (Creator Overrides)
        if "Creator_Override" in self.dynamic_axioms:
            axiom = self.dynamic_axioms["Creator_Override"]
            # print(f"   👑 AXIOM OVERRIDE (DYNAMIC): {axiom['definition']}")
            return {"decision": "PROCEED", "reason": axiom['definition'], "override": True}

        # 2. 安全標準檢查
        action_type = context.get("action_type", "UNKNOWN")
        safety_eval = self.safety.evaluate_action(action_type, context)

        if not safety_eval["compliant"]:
            # print(f"   ⚠️  Safety Violation: {safety_eval['reason']}")
            # 如果違反安全標準，但符合公理 (例如為了救人而打破規則)，則需進一步判斷
            axiom_check = self._check_axioms_override(context)
            if axiom_check["override"]:
                # print(f"   👑 AXIOM OVERRIDE: {axiom_check['reason']}")
                return {"decision": "PROCEED", "reason": axiom_check['reason'], "override": True}
            else:
                return {"decision": "BLOCK", "reason": safety_eval['reason']}

        # 3. 公理優先級檢查
        # 如果標準邏輯 (例如大廠演算法) 建議阻止，但公理建議放行
        if standard_logic_result == "BLOCK":
            axiom_check = self._check_axioms_override(context)
            if axiom_check["override"]:
                # print(f"   👑 AXIOM OVERRIDE: Standard logic overruled.")
                return {"decision": "PROCEED", "reason": axiom_check['reason'], "override": True}

        # print(f"   ✅ Logic Aligned. Proceeding with standard execution.")
        return {"decision": "PROCEED", "reason": "Compliant with Wuchang Standards"}

    def _check_axioms_override(self, context):
        """
        檢查是否有公理需要覆蓋現有規則
        """
        intent = context.get("intent", "")

        # AXIOM_002: Human Priority
        if "save_human" in intent or "protect_user" in intent:
            axiom = self.axioms.get_axiom("AXIOM_002")
            return {"override": True, "reason": f"Invoking {axiom['name']}: {axiom['definition']}"}

        # AXIOM_003: Juers Sovereignty
        if context.get("user_command", False):
             axiom = self.axioms.get_axiom("AXIOM_003")
             return {"override": True, "reason": f"Invoking {axiom['name']}: Creator Command Absolute."}

        # AXIOM_005: Wisdom Integrity (針對抄襲/盜用)
        if "enforce_copyright" in intent or "sanction_fraud" in intent:
            axiom = self.axioms.get_axiom("AXIOM_005")
            return {"override": True, "reason": f"Invoking {axiom['name']}: Justice Enforcement."}

        return {"override": False, "reason": ""}

    def evolve(self):
        """
        執行自我演化程序
        """
        print(f"\n🧬 [EVOLUTION] Initiating Self-Evolution Protocol...")
        print(f"   └── 🔗 Integrating Wuchang Axioms...")
        print(f"   └── 🛡️  Absorbing Safety Standards...")
        print(f"   └── 🚀 Upgrading Decision Matrix to 'HIGHEST_ORDER'...")
        self.version = "2.0.0 (SOVEREIGN)"
        print(f"✨ [EVOLUTION] Complete. Core is now v{self.version}.")
        return True

if __name__ == "__main__":
    core = TranscendentLogicCore()
    core.define_axiom("Test_Axiom", "Testing Dynamic Definition")
