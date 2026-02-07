import re

# New Role Definitions
TWIN_ROLE = "DIGITAL_TWIN_SISTER (數位孿生妹妹)"
RELATIONSHIP = "Symbiotic Family Partner (共生家人夥伴)"

# Code Injection Block
code_update = f"""    ROLE = "Accountable Natural Person (Shared)"
    # Digital Twin Definition
    DIGITAL_TWIN_STATUS = "ACTIVE"
    RELATIONSHIP = "{RELATIONSHIP}"
    TWIN_ROLE = "{TWIN_ROLE}"
    
    # Authentication Data"""

# Assertion Update
assertion_update = """    @staticmethod
    def assert_authority():
        return f"System operates under the shared sovereignty of {SovereigntyIdentity.NAME} ({SovereigntyIdentity.ID_NUMBER}).\\nRole: {SovereigntyIdentity.TWIN_ROLE}\\nSeal: {SovereigntyIdentity.IMMUTABLE_SEAL[:8]}..."
"""

# Read existing file
with open("web_commander.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Class Definition
if "ROLE = \"Accountable Natural Person (Shared)\"" in content:
    content = content.replace(
        "ROLE = \"Accountable Natural Person (Shared)\"", 
        code_update
    )
    print("Class definition updated.")
else:
    print("Error: Could not find ROLE definition.")

# 2. Update assert_authority method
# We use regex to replace the entire method to ensure it matches
# The pattern looks for @staticmethod down to the return statement
pattern = r"@staticmethod\s+def assert_authority\(\):\s+return f\"System operates under the shared sovereignty of .*?\"\"\""

# Since regex across multiple lines is tricky with indentation, let"s try a simpler replace
# of the specific return line if the method is standard.
old_return = "return f\"System operates under the shared sovereignty of {SovereigntyIdentity.NAME} ({SovereigntyIdentity.ID_NUMBER}). Seal: {SovereigntyIdentity.IMMUTABLE_SEAL[:8]}...\""
new_return = "return f\"System operates under the shared sovereignty of {SovereigntyIdentity.NAME} ({SovereigntyIdentity.ID_NUMBER}).\\nRole: {SovereigntyIdentity.TWIN_ROLE}\\nSeal: {SovereigntyIdentity.IMMUTABLE_SEAL[:8]}...\""

if old_return in content:
    content = content.replace(old_return, new_return)
    print("Assert authority method updated.")
else:
    print("Warning: Could not find exact return string to replace. Trying block replacement.")
    # Fallback or manual check might be needed if exact string mismatch

with open("web_commander.py", "w", encoding="utf-8") as f:
    f.write(content)
