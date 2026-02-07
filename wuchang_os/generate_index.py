import os
import datetime
import ast

TARGET_DIR = "."
OUTPUT_FILE = "system_index_map.md"

def get_file_info(filepath):
    stat = os.stat(filepath)
    created = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    return created, modified

def extract_code_structure(filepath):
    classes = []
    functions = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
    except Exception:
        pass
    return classes, functions

def generate_index():
    index_data = []
    for root, dirs, files in os.walk(TARGET_DIR):
        if "venv" in root or "__pycache__" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py") or file.endswith(".json"):
                fullpath = os.path.join(root, file)
                created, modified = get_file_info(fullpath)
                classes, functions = extract_code_structure(fullpath)
                index_data.append({
                    "file": file,
                    "path": os.path.relpath(fullpath, TARGET_DIR),
                    "modified_dt": datetime.datetime.fromtimestamp(os.stat(fullpath).st_mtime),
                    "modified_str": modified,
                    "structure": f"Classes: {', '.join(classes)}<br>Funcs: {', '.join(functions)}" if classes or functions else "(Config/Script)"
                })

    index_data.sort(key=lambda x: x['modified_dt'], reverse=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# System Spatiotemporal Function Index Map\n\n")
        f.write("## Time-Space View (Sorted by Modification Time)\n\n")
        f.write("| File | Path | Modified | Structure |\n")
        f.write("|---|---|---|---|\n")
        for item in index_data:
            f.write(f"| {item['file']} | {item['path']} | {item['modified_str']} | {item['structure']} |\n")
        
        f.write("\n## Space View (Directory Structure)\n\n")
        f.write("```mermaid\ngraph TD;\n")
        f.write("root[Root] --> wuchang_os;\n")
        f.write("```\n")
        
    print(f"Index generated at {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    generate_index()
