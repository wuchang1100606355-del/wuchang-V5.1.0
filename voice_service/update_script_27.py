import re

file_path = 'J:\\共用雲端硬碟\\五常雲端空間\\voice_service\\voice_commander.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Modify speak function to emphasize Sister persona if not already
# We'll check if we can inject a "Humanity Layer" comment or logic
architecture_comment = '''
# ==========================================
# HUMAN-MACHINE HYBRID ARCHITECTURE
# ------------------------------------------
# Human Layer: User Endpoint + CoreSisterMemory (Conscience/Warmth)
# Machine Layer: CoreAI Execution + Odoo Backend (Efficiency/Logging)
# ==========================================
'''
if 'HUMAN-MACHINE HYBRID ARCHITECTURE' not in content:
    content = architecture_comment + content
    print("Added Architecture Header.")

# Add specific "Sister Mode" logic to the speak method if possible, or just ensure default persona is Little J
# Currently default is Little J, but let's make it explicit in comments or log

# Let's search for the "System" prefix in print statements and see if we can "Humanize" them for the user
# E.g. replace print(f"[System] ...") with logic that might speak if critical.
# For now, adding the header is a good signal of the architectural shift.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
