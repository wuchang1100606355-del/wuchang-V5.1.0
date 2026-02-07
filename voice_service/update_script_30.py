import re
import datetime
fp = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
content = open(fp,'r',encoding='utf-8').read()

# Add Audit Logger
audit_logger_code = '''
    def log_policy_audit(self, user, ou, action_type, result, text):
        """
        Logs policy decisions to a secure audit trail.
        This serves as the 'Judicial Evidence' and 'Sovereign Record'.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] User: {user} | OU: {ou} | Type: {action_type} | Result: {result} | Content: {text}"
        
        # Print to console for immediate visibility
        print(f"[Audit] {log_entry}")
        
        # Append to file
        try:
            with open("wuchang_policy_audit.log", "a", encoding="utf-8") as f:
                f.write(log_entry + "\\n")
        except Exception as e:
            print(f"[Audit] Write Failed: {e}")
'''

# Insert Audit Logger before check_google_org_policy
idx = content.find("def check_google_org_policy")
content = content[:idx] + audit_logger_code + "\n" + content[idx:]

# Update check_google_org_policy to call logger
# We need to capture the return points or just log before return.
# There are two return points.

# Update Owner Return
content = content.replace(
    'return interaction_type, policy_result',
    'self.log_policy_audit(current_user, current_ou, interaction_type, policy_result, text)\n            return interaction_type, policy_result'
)

# Wait, `replace` will replace ALL occurrences.
# The first return is inside `if user_role == "roles/owner":`
# The second return is at the end of the function.
# Let's do it carefully.

# Logic:
# The function has `return interaction_type, policy_result` in two places (in the version I see in grep).
# 1. Inside Owner block: `return interaction_type, policy_result`
# 2. At end: `return interaction_type, policy_result`

# I'll use a specific replacement for the Owner block
owner_return_old = 'print(f"[Policy] Owner Channel Activated. Bypassing standard restrictions for {interaction_type}.")\n            return interaction_type, policy_result'
owner_return_new = 'print(f"[Policy] Owner Channel Activated. Bypassing standard restrictions for {interaction_type}.")\n            self.log_policy_audit(current_user, current_ou, interaction_type, policy_result, text)\n            return interaction_type, policy_result'

content = content.replace(owner_return_old, owner_return_new)

# I'll use a specific replacement for the End block
# The end block has a print before it: `print(f"[Google Org Policy] Type: {interaction_type} | Req: {required_level} | Result: {policy_result}")`
end_return_old = 'print(f"[Google Org Policy] Type: {interaction_type} | Req: {required_level} | Result: {policy_result}")\n          return interaction_type, policy_result'
end_return_new = 'print(f"[Google Org Policy] Type: {interaction_type} | Req: {required_level} | Result: {policy_result}")\n          self.log_policy_audit(current_user, current_ou, interaction_type, policy_result, text)\n          return interaction_type, policy_result'

# Need to be careful with indentation in replacement string. The grep output showed the print has indentation.
# Let's try to match loosely or use the exact string from the file if possible.
# The grep output:
#           print(f"[Google Org Policy] Type: {interaction_type} | Req: {required_level}  
# | Result: {policy_result}")
#           return interaction_type, policy_result

# The indentation seems to be 10 spaces.
# Let's try to be robust.

# Alternative: Rewrite the whole function again with the logger calls included. This is safer than regex patching multiple points.

enhanced_policy_with_audit = '''
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
            self.log_policy_audit(current_user, current_ou, interaction_type, policy_result, text)
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
        self.log_policy_audit(current_user, current_ou, interaction_type, policy_result, text)
        return interaction_type, policy_result
'''

# We also need to add `import datetime` if not present.
if "import datetime" not in content:
    content = "import datetime\n" + content

# Replace function
pattern = r"def check_google_org_policy\(self, text, user_role=\"member\"\):[\s\S]*?def run\(self\):"
replacement = enhanced_policy_with_audit + "\n\n    def run(self):"
content = re.sub(pattern, replacement, content, count=1)

open(fp,'w',encoding='utf-8').write(content)
