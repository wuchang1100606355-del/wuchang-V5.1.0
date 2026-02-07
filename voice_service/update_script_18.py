import re

file_path = r"J:\共用雲端硬碟\五常雲端空間\voice_service\voice_commander.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix indentation and duplicate blocks issue found in previous check
# It seems there are duplicate "elif action_type == 'monitor_space_check_init':" blocks and bad indentation.

# The bad indentation was around:
# >                                 elif action_type == "monitor_space_check_init":

# Let's remove the extra indentation and the duplicate block if present.

lines = content.splitlines()
new_lines = []
seen_space_check = False

for line in lines:
    stripped = line.strip()
    if stripped.startswith('elif action_type == "monitor_space_check_init":'):
        if seen_space_check:
            continue # Skip duplicate
        else:
            seen_space_check = True
            new_lines.append('            elif action_type == "monitor_space_check_init":')
    elif stripped.startswith('elif action_type == "monitor_space_check_init":') is False:
        # Check if this line belongs to a skipped duplicate block
        # This is hard without parsing.
        # But looking at the output, the duplicate seems to be a copy-paste error.
        
        # Let's try a regex replace to clean up the specific known bad pattern if possible.
        pass
        new_lines.append(line)

# The indentation error reported was "unexpected indent".
# It usually means one line is indented more than it should be relative to previous.
# The `type` output showed a very deep indent for one occurrence.

# Let's use regex to fix the specific bad indent line.
content = re.sub(r'^\s+elif action_type == "monitor_space_check_init":', '            elif action_type == "monitor_space_check_init":', content, flags=re.MULTILINE)

# Also check for duplicate blocks. The output showed TWO occurrences.
# Let's verify if they are identical or if one is the "bad" one.
# It seems both were present in the grep output.

# I'll simply deduplicate by reading the whole file and ensuring the logic block appears once.
# But since I can't see the whole file easily, I'll rely on the fact that I just fixed the indentation.
# If there are two blocks, python might just execute the first one (or fail if inside another block).

# Let's try to remove the duplicate if it exists right after another.
# It seems the previous `fix_logic_block.py` might have left artifacts.

# Let's read the file again after the indent fix to be sure.
# For now, just writing the indent fix.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
