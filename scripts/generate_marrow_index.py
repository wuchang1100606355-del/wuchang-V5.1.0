import os
import json
import hashlib
import datetime

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        # print(f"Error hashing {file_path}: {e}")
        return None

def get_file_category(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.md', '.txt', '.pdf', '.docx', '.html']:
        return 'Documentation'
    elif ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cs']:
        return 'Source Code'
    elif ext in ['.ps1', '.sh', '.bat', '.cmd']:
        return 'Scripts'
    elif ext in ['.json', '.xml', '.yaml', '.yml', '.ini', '.conf', '.env']:
        return 'Configuration'
    elif ext in ['.zip', '.tar', '.gz', '.7z', '.rar']:
        return 'Archive'
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg']:
        return 'Assets'
    else:
        return 'Other'

def generate_index(root_dir, output_file):
    project_index = {
        "project_name": "Wuchang V5.1.0",
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root_directory": root_dir,
        "files": []
    }

    # Added 'downloads' to ignore list to avoid clogging the index with runtime logs/data if they are huge
    # If user needs them, we can remove it. But for "Marrow" (Core), usually data is excluded.
    ignore_dirs = ['.git', '.venv', 'node_modules', '__pycache__', '.idea', '.vscode', 'dist', 'build', 'downloads', 'wuchang_backup']

    print(f"Scanning directory: {root_dir}...")
    count = 0

    for root, dirs, files in os.walk(root_dir):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, root_dir)
            
            try:
                stats = os.stat(file_path)
                file_size = stats.st_size
                last_modified = datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Calculate Hash 
                file_hash = calculate_sha256(file_path)

                file_info = {
                    "path": relative_path,
                    "category": get_file_category(file_path),
                    "size_bytes": file_size,
                    "last_modified": last_modified,
                    "sha256": file_hash
                }
                
                project_index["files"].append(file_info)
                count += 1
                if count % 100 == 0:
                    print(f"Indexed {count} files...", end='\r')

            except Exception as e:
                pass # print(f"Error processing {file_path}: {e}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(project_index, f, indent=4, ensure_ascii=False)
    
    print(f"\nIndex generation complete. Total {count} files indexed. Saved to {output_file}")

if __name__ == "__main__":
    root_directory = "c:\\wuchang V5.1.0"
    output_filename = "wuchang_marrow_index.json"
    generate_index(root_directory, output_filename)
