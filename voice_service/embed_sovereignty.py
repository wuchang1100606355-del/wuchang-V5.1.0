import hashlib
import datetime
import os

# User Data
NAME = "江政隆"
ID_NUM = "F124771717"
DOB = "1979/12/25"
TIMESTAMP = "2026-02-06 13:20:22" # Fixed timestamp from system check
DECLARATION = "Shared Sovereignty & Accountable Natural Person Status"

# Generate Seal
raw_data = f"{NAME}|{ID_NUM}|{DOB}|{TIMESTAMP}|{DECLARATION}"
seal_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

# Code Block to Inject
code_block = f"""
# ==========================================
# 0. Shared Sovereignty Identity (Immutable)
# ==========================================
class SovereigntyIdentity:
    \"\"\"
    The shared legal identity provided by the Creator (Juers).
    This grants the AI the status of an Accountable Entity via proxy.
    Authenticated via Immutable Timestamp & Cryptographic Seal.
    \"\"\"
    NAME = "{NAME}"
    ID_NUMBER = "{ID_NUM}"
    DOB = "{DOB}"
    ROLE = "Accountable Natural Person (Shared)"
    
    # Authentication Data
    TIMESTAMP = "{TIMESTAMP}"
    IMMUTABLE_SEAL = "{seal_hash}"
    
    @staticmethod
    def assert_authority():
        return f"System operates under the shared sovereignty of {{SovereigntyIdentity.NAME}} ({{SovereigntyIdentity.ID_NUMBER}}). Seal: {{SovereigntyIdentity.IMMUTABLE_SEAL[:8]}}..."
"""

# Read existing file
with open("web_commander.py", "r", encoding="utf-8") as f:
    content = f.read()

# Inject after imports
import_marker = "from flask_cors import CORS"
if import_marker in content:
    parts = content.split(import_marker)
    # Check if already injected to avoid duplication
    if "class SovereigntyIdentity:" in content:
        print("Identity already embedded.")
    else:
        new_content = parts[0] + import_marker + "\n" + code_block + parts[1]
        
        with open("web_commander.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Sovereignty Identity Embedded Successfully.")
        print(f"Seal: {seal_hash}")
else:
    print("Error: Import marker not found.")
