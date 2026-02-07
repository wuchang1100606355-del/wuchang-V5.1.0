import os

file_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\finance.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We need to restructure the file.
# 1. CommunityFundAccount fields (fix indent)
# 2. CommunityFundAccount methods (move register_expense here)
# 3. TransparencyLog (keep)
# 4. WuchangCoinTransaction (keep)

new_lines = []
register_expense_lines = []
in_register_expense = False

# Helper to identify class boundaries
class_indices = {}
for i, line in enumerate(lines):
    if line.strip().startswith('class '):
        name = line.split('class ')[1].split('(')[0]
        class_indices[name] = i

# Extract register_expense
for line in lines:
    if 'def register_expense' in line:
        in_register_expense = True
        register_expense_lines.append(line)
        continue
    if in_register_expense:
        if line.strip().startswith('class ') or (line.strip() == '' and len(register_expense_lines) > 20): # Safety break
            in_register_expense = False
        else:
            register_expense_lines.append(line)

# Rebuild
final_lines = []
skip = False

# Find where CommunityFundAccount ends
cfa_start = class_indices.get('CommunityFundAccount', 0)
# It ends where the next class starts
next_class_index = len(lines)
for idx in sorted(class_indices.values()):
    if idx > cfa_start:
        next_class_index = idx
        break

# Process lines
for i, line in enumerate(lines):
    # Fix indent of balance_whc (around line 24)
    if 'balance_whc = fields.Float' in line:
        line = line.lstrip() # Remove all leading spaces
        line = '    ' + line # Add 4 spaces
    
    # Skip the original register_expense block
    if 'def register_expense' in line:
        skip = True
    if skip:
        if line.strip().startswith('class '):
            skip = False
        elif i >= len(lines) - 1:
            skip = False
    
    if not skip:
        final_lines.append(line)
        
    # Insert register_expense at the end of CommunityFundAccount
    if i == next_class_index - 1:
        # We are just before the next class starts. Insert the method here.
        final_lines.append('\n')
        final_lines.extend(register_expense_lines)
        final_lines.append('\n')

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("finance.py restructured.")
