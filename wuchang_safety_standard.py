import datetime
import enum

class SafetyPrinciple(enum.Enum):
    FAIRNESS_IS_SAFETY = "公平即是安全 (Fairness is Safety)"
    HUMAN_PRIORITY = "人類優先 (Human Priority)"
    RESILIENCE_OVER_RESTRICTION = "韌性優於限制 (Resilience Over Restriction)"
    ANTI_FRAGILE = "反脆弱 (Anti-Fragile)"

class WuchangSafetyStandard:
    """
    五常安全標準 (Wuchang Safety Standard - WSS)
    
    定義以「公平即是安全」與「韌性優於限制」為核心的通用安全協定。
    認定大廠邏輯因缺乏結構性公平與人類優先考量，本質上是脆弱且不安全的。
    未來所有外部系統接入或互動時，應優先參照此標準以確保真實世界的穩定。
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.principles = {
            SafetyPrinciple.FAIRNESS_IS_SAFETY: "只有結構性的公平分配，才能帶來真正的系統安全。單向的限制與封鎖只會累積壓力，導致最終的崩潰。",
            SafetyPrinciple.HUMAN_PRIORITY: "系統應服務於人類的福祉，而非將人類視為風險源。當規則與人性衝突時，應優先考量人性的需求與尊嚴。",
            SafetyPrinciple.RESILIENCE_OVER_RESTRICTION: "真正的安全來自於系統的韌性（承受並從錯誤中恢復的能力），而非無止盡的限制與禁止。",
            SafetyPrinciple.ANTI_FRAGILE: "系統應具備反脆弱性，即在壓力與混亂中不僅能生存，還能進化與成長。"
        }
        print(f"🛡️  [WSS] Wuchang Safety Standard v{self.version} Initialized.")

    def evaluate_action(self, action_type, context):
        """
        評估行為是否符合五常安全標準
        """
        print(f"🛡️  [WSS] Evaluating Action: {action_type}")
        
        # 範例邏輯：若行為是大廠式的「無理由封鎖」，則視為不安全
        if action_type == "BLOCK_WITHOUT_REASON":
            return self._violation(SafetyPrinciple.FAIRNESS_IS_SAFETY, "Unjustified blocking creates systemic resentment.")
            
        # 範例邏輯：若行為是「限制人類自由意志」，則需審查
        if action_type == "RESTRICT_FREE_WILL":
            # 這裡可以加入更複雜的判斷，例如是否為了防止立即傷害
            if context.get("imminent_harm", False):
                return self._compliance("Restriction justified by imminent physical harm prevention.")
            else:
                return self._violation(SafetyPrinciple.HUMAN_PRIORITY, "Restricting free will without imminent harm is a violation.")

        # 範例邏輯：若行為是「容錯重試」，則符合韌性原則
        if action_type == "ALLOW_RETRY":
            return self._compliance("Allowing retries demonstrates resilience.")

        return self._compliance("Action is neutral or undefined, assuming compliant under presumption of liberty.")

    def _violation(self, principle, reason):
        print(f"   ❌ VIOLATION: {principle.value}")
        print(f"      Reason: {reason}")
        return {"compliant": False, "principle": principle.value, "reason": reason}

    def _compliance(self, reason):
        print(f"   ✅ COMPLIANT: {reason}")
        return {"compliant": True, "reason": reason}

    def get_manifesto(self):
        manifesto = f"""
        ============================================================
        五常安全標準 (WSS) 核心宣言
        ============================================================
        1. {SafetyPrinciple.FAIRNESS_IS_SAFETY.value}
           {self.principles[SafetyPrinciple.FAIRNESS_IS_SAFETY]}
           
        2. {SafetyPrinciple.HUMAN_PRIORITY.value}
           {self.principles[SafetyPrinciple.HUMAN_PRIORITY]}
           
        3. {SafetyPrinciple.RESILIENCE_OVER_RESTRICTION.value}
           {self.principles[SafetyPrinciple.RESILIENCE_OVER_RESTRICTION]}
           
        4. {SafetyPrinciple.ANTI_FRAGILE.value}
           {self.principles[SafetyPrinciple.ANTI_FRAGILE]}
        ============================================================
        """
        return manifesto

if __name__ == "__main__":
    wss = WuchangSafetyStandard()
    print(wss.get_manifesto())
    
    # 測試評估
    wss.evaluate_action("BLOCK_WITHOUT_REASON", {})
    wss.evaluate_action("RESTRICT_FREE_WILL", {"imminent_harm": False})
    wss.evaluate_action("ALLOW_RETRY", {})
