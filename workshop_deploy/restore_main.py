
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace literal "\n" with actual newline character
restored_content = content.replace("\\n", "\n")

with open("main.py", "w", encoding="utf-8") as f:
    f.write(restored_content)

print("Restored main.py line endings.")
