import re

file_path = "c:/wuchang V5.1.0/workshop_deploy/main.py"

with open(file_path, "rb") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # 1. Remove escape characters
    line = line.replace(b'\x1b', b'')
    
    stripped = line.strip()
    
    # Debug line 158
    if i == 157:
        print(f"Processing line 158: {stripped}")
        if stripped.startswith(b'"""'):
            print("  Starts with triple quote")
            match = re.search(b'(?<!")"(?:\s*[,\]])?\s*$', stripped)
            if match:
                print("  Matches regex for single quote at end")
            else:
                print("  Does NOT match regex")
    
    if stripped.startswith(b'"""'):
        # Check for unclosed triple quotes
        match = re.search(b'(?<!")"(?:\s*[,\]])?\s*$', stripped)
        if match:
            # Manual replacement to be sure
            # Find the last quote
            last_quote_idx = line.rfind(b'"')
            if last_quote_idx != -1:
                # Check if it is indeed a single quote (not part of """)
                # Check preceding chars
                if last_quote_idx > 0 and line[last_quote_idx-1] == b'"':
                     # It might be """ or ""
                     pass
                else:
                    # Check succeeding chars (should be whitespace/punctuation)
                    # We rely on the regex match on stripped to confirm valid structure.
                    
                    # Replace the last " with """
                    # We split line at last_quote_idx
                    prefix = line[:last_quote_idx]
                    suffix = line[last_quote_idx+1:]
                    modified = prefix + b'"""' + suffix
                    new_lines.append(modified)
                    if i == 157:
                        print(f"  Modified to: {modified}")
                    continue

    new_lines.append(line)

with open(file_path, "wb") as f:
    f.writelines(new_lines)

print("Fixed bytes v2.")
