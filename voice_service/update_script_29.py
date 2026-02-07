import re
fp = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
content = open(fp,'r',encoding='utf-8').read()

# Enhanced Policy Logic with Owner Channel
enhanced_policy = '''
    def check_google_org_policy(self, text, user_role="member"):
        """
        Consults Google Organization Policy for Wuchang Commercial Property.
        Structure:
          - Organization: Wuchang Commercial Property (id: wuchang_cp)
            - OU: Owner Office (User: Juers) -> Full Access
            - OU: Management (User: Admin) -> Restricted Access
            - OU: Public (User: Guest) -> Read Only
        """
        # 0. Identity & Role Resolution
        # Simulate Identity Check based on Keywords (Voice Biometrics placeholder)
        current_user = "guest"
        current_ou = "/wuchang_cp/public"
        
        if any(k in text for k in ["我", "本人", "哥", "老板", "owner", "juers"]):
             current_user = "Juers (Owner)"
             current_ou = "/wuchang_cp/owner_office"
             user_role = "roles/owner"
        elif "admin" in text:
             current_user = "System Admin"
             current_ou = "/wuchang_cp/management"
             user_role = "roles/admin"
             
        print(f"[Policy] Identity: {current_user} | OU: {current_ou} | Role: {user_role}")

        # 1. Interaction Type Analysis
        is_question = any(x in text for x in ["什麼", "如何", "多少", "嗎", "?", "？", "查", "問"])
        interaction_type = "QUESTION (提問)" if is_question else "COMMAND/ANSWER (指令/回答)"
        
        # 2. Permission Level & Policy Enforcement
        policy_result = "ALLOWED"
        required_level = "public"
        
        # Policy Rule: Owner Channel Override
        if user_role == "roles/owner":
            policy_result = "APPROVED_BY_OWNER_AUTHORITY"
            print(f"[Policy] Owner Channel Activated. Bypassing standard restrictions for {interaction_type}.")
            return interaction_type, policy_result

        # Standard Rules for Non-Owners
        if interaction_type.startswith("COMMAND"):
            required_level = "admin_ou"
            if user_role != "roles/admin":
                 if "開燈" in text or "點餐" in text:
                     required_level = "service_ou"
                 else:
                     policy_result = "RESTRICTED (Insufficient Permission)"
        
        print(f"[Google Org Policy] Type: {interaction_type} | Req: {required_level} | Result: {policy_result}")
        return interaction_type, policy_result
'''

# Replace the previous simple version with the enhanced version
# We need to find the previous definition and replace it.
# The previous definition started with "def check_google_org_policy(self, text, user_role="member"):"
# and ended before "def run(self):"

# Regex to capture the whole function body might be tricky, so let's match the start and assume it goes until "def run"
# Actually, we can just search for the start string and replace until `def run`.

pattern = r"def check_google_org_policy\(self, text, user_role=\"member\"\):[\s\S]*?def run\(self\):"
# We need to be careful not to delete "def run(self):"
# So we include it in the replacement or lookahead.

# Let's construct the replacement string which includes "def run(self):" at the end.
replacement = enhanced_policy + "\n\n    def run(self):"

# Use re.sub
content = re.sub(pattern, replacement, content, count=1)

open(fp,'w',encoding='utf-8').write(content)
