
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace literal \n with actual newline
fixed_content = content.replace("\\n", "\n")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(fixed_content)

print("Fixed main.py formatting.")

