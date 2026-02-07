import re

file_path = 'web_commander.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix IndentationError and duplicate lines
# We see:
#         was_corrected = (normalized != text) or bool(notes)
#                 was_corrected = (normalized != text) or bool(notes)
#         return normalized, was_corrected, judgment_note

# This happened because my previous replacement logic matched a part but didn't consume the old 'was_corrected' line fully or something.
# Let's clean up the TranslatorAI end block.

pattern = r"if not judgment_note:.*?# --- AI Role: Core AI"
# We want to replace everything from "if not judgment_note:" down to "# --- AI Role: Core AI"
# with a clean block.

clean_block = """        if not judgment_note:
            judgment_note = '信心高 (High Confidence)'

        was_corrected = (normalized != text) or bool(notes)
        return normalized, was_corrected, judgment_note

# --- AI Role: Core AI"""

# Using re.DOTALL to match newlines
content = re.sub(pattern, clean_block, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Repaired web_commander.py indentation.")
