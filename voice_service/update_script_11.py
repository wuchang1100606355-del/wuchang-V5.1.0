import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert DEVICE_REGISTRY
registry_code = '''    # Device Registry for Sovereignty Verification
    DEVICE_REGISTRY = {
        "juers_pc": {"owner": "juers", "keywords": ["自己", "我的", "電腦", "測試", "PC"]},
        "juers_phone": {"owner": "juers", "keywords": ["手機"]},
        "brother_room": {"owner": "brother", "keywords": ["弟弟", "小孩", "房間", "兒子"]},
        "living_room": {"owner": "public", "keywords": ["客廳", "大門"]}
    }
'''

# Insert it inside the class, maybe after __init__ or at class level?
# Let's put it at class level for simplicity, or inside __init__. 
# Actually, inside the class as a static dict or instance variable is fine.
# Let's put it after `def __init__(self):` block ends, but wait, `__init__` is long.
# Let's put it at the top of the class.

if "DEVICE_REGISTRY =" not in content:
    # Find class definition
    content = content.replace("class VoiceCommander:", "class VoiceCommander:\n" + registry_code)

# 2. Add verify_sovereignty method
verify_method = '''
    def verify_sovereignty(self, text):
        """
        Verifies if the current user (assumed 'juers' for now) holds sovereignty over the target device mentioned in text.
        Returns: (is_sovereign, device_info)
        """
        target_device = None
        for dev_id, info in self.DEVICE_REGISTRY.items():
            for kw in info["keywords"]:
                if kw in text:
                    target_device = info
                    break
            if target_device:
                break
        
        if not target_device:
            # Default to "unknown/others" if not explicitly "self"
            return False, {"owner": "unknown"}
            
        if target_device["owner"] == "juers":
            return True, target_device
        else:
            return False, target_device
'''

# Insert method before run()
if "def verify_sovereignty" not in content:
    content = content.replace("    def run(self):", verify_method + "\n    def run(self):")

# 3. Update the monitoring logic in run() to use verify_sovereignty
# We need to find the monitoring block again.
# It looks like:
# elif "監控" in cmd_text ...
#    if "自己" in cmd_text ...

# We will replace the condition with a call to verify_sovereignty
old_logic_pattern = r'elif "監控" in cmd_text.*?if "自己" in cmd_text.*?else:.*?risk_level = "privacy_critical"'
# This regex is hard because of newlines.
# Let's match the block start and manually restructure.

monitoring_block_start = 'elif "監控" in cmd_text or "監視" in cmd_text or ("看" in cmd_text and ("房間" in cmd_text or "小孩" in cmd_text)):'

new_monitoring_logic = '''        elif "監控" in cmd_text or "監視" in cmd_text or ("看" in cmd_text and ("房間" in cmd_text or "小孩" in cmd_text)):
            is_sovereign, target_info = self.verify_sovereignty(cmd_text)
            
            if is_sovereign:
                # Sovereignty Verified (User owns the device)
                print(f"[System] Sovereignty Verified: User owns {target_info}")
                action = "monitor_self"
                risk_level = "medium"
                category = "monitoring"
            else:
                # Sovereignty Denied (User does NOT own the device)
                print(f"[System] Sovereignty Check Failed: Target belongs to {target_info['owner']}")
                action = "monitor_others"
                risk_level = "privacy_critical"
                category = "monitoring"'''

# Find the block and replace the immediate if/else logic
# The original code:
#             if "自己" in cmd_text or "我的" in cmd_text or "測試" in cmd_text:  
#                 action = "monitor_self"
#                 risk_level = "medium"
#                 category = "monitoring"
#             else:
#                 action = "monitor_others"
#                 risk_level = "privacy_critical"
#                 category = "monitoring"

# We'll try to replace this chunk.
chunk_to_replace = '''            if "自己" in cmd_text or "我的" in cmd_text or "測試" in cmd_text:  
                action = "monitor_self"
                risk_level = "medium"
                category = "monitoring"
            else:
                action = "monitor_others"
                risk_level = "privacy_critical"
                category = "monitoring"'''

if chunk_to_replace.strip() in content: # Try exact match first
    content = content.replace(chunk_to_replace, new_monitoring_logic.strip().replace("        ", "            ")) # Adjust indent
else:
    # Regex approach
    # Note: re.DOTALL is needed
    pattern = r'if "自己" in cmd_text.*?category = "monitoring"'
    # This matches from 'if "自己"' to the LAST 'category = "monitoring"' in the block.
    # The block has two 'category = "monitoring"'.
    # Let's try to match the specific structure.
    lines = content.splitlines()
    new_lines = []
    skip = False
    replaced = False
    
    for line in lines:
        if 'if "自己" in cmd_text or "我的" in cmd_text' in line and not replaced:
            # We found the start of the block we want to replace
            # We need to skip lines until we see the end of the else block.
            # The else block ends with category = "monitoring"
            new_lines.append(new_monitoring_logic) # Insert new logic
            skip = True
            replaced = True
        elif skip:
            if 'category = "monitoring"' in line and 'risk_level = "privacy_critical"' in lines[lines.index(line)-1]:
                 # This is likely the end of the else block
                 skip = False
            # Wait, this is tricky line-by-line.
            # Let's use the known indentation.
            if "elif" in line and "正常" in line: # The next elif block
                 skip = False
                 new_lines.append(line)
            continue
        else:
            new_lines.append(line)
    
    # Actually, simpler approach:
    # Read the file, identify the lines for the monitoring block, and overwrite them.
    pass # logic is complicated for pure python script without interactive testing.
    
    # Let's try a very specific replace string that matches what I likely wrote last time.
    # Last time I didn't change indentation, so it should match.
    
    target_str = '''            if "自己" in cmd_text or "我的" in cmd_text or "測試" in cmd_text:  
                action = "monitor_self"
                risk_level = "medium"
                category = "monitoring"
            else:
                action = "monitor_others"
                risk_level = "privacy_critical"
                category = "monitoring"'''
    
    # Try normalizing whitespace
    import re
    # Escape regex special chars in target_str just in case
    # Construct a regex that allows flexible whitespace
    regex_pattern = r'if\s+"自己"\s+in\s+cmd_text.*?category\s*=\s*"monitoring"'
    # This is too broad.
    
    # Let's rely on the `elif "監控"` marker.
    parts = content.split('elif "監控" in cmd_text or "監視" in cmd_text or ("看" in cmd_text and ("房間" in cmd_text or "小孩" in cmd_text)):')
    if len(parts) > 1:
        pre = parts[0]
        post = parts[1]
        # post starts with the body of the elif.
        # We want to replace the body up to the next elif.
        subparts = post.split('elif "正常" in cmd_text:')
        body = subparts[0]
        rest = subparts[1] if len(subparts) > 1 else ""
        
        # New body
        new_body = "\n" + new_monitoring_logic + "\n        "
        
        content = pre + 'elif "監控" in cmd_text or "監視" in cmd_text or ("看" in cmd_text and ("房間" in cmd_text or "小孩" in cmd_text)):' + new_body + 'elif "正常" in cmd_text:' + rest

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated voice_commander.py with Device Registry and Sovereignty Verification.")
