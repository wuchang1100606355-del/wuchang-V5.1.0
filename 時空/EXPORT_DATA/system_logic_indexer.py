import os
import json
import time
import re
from datetime import datetime

# Configuration
TARGET_DIR = r"J:\共用雲端硬碟\五常雲端空間"
OUTPUT_FILE = os.path.join(TARGET_DIR, "system_logic_matrix.json")
IGNORE_PATTERNS = [
    r"\.git", r"__pycache__", r"\.vscode", r"\.idea", 
    r"node_modules", r".*\.png", r".*\.jpg", r".*\.mp4"
]

def get_x_coordinate(filename):
    """
    X Coordinate: Functional Layer (Logic Position)
    0: Constitution / Governance (The Soul)
    10: Core System (The Heart)
    20: Research / Simulation (The Brain)
    30: Data / Memory (The Memory)
    40: Scripts / Tools (The Hands)
    99: Others
    """
    lower_name = filename.lower()
    if "constitution" in lower_name or "governance" in lower_name:
        return 0
    elif "spatiotemporal" in lower_name or "core_sister" in lower_name or "odoo" in lower_name:
        return 10
    elif "research" in lower_name or "simulate" in lower_name or "analysis" in lower_name:
        return 20
    elif "json" in lower_name or "memory" in lower_name or "data" in lower_name:
        return 30
    elif "start_" in lower_name or "inject_" in lower_name or ".ps1" in lower_name or ".py" in lower_name:
        return 40
    else:
        return 99

def get_y_coordinate(filepath):
    """
    Y Coordinate: Temporal Layer (Memory Position)
    Based on last modification timestamp.
    Normalized to a relative score if needed, but raw timestamp is precise.
    """
    return os.path.getmtime(filepath)

def get_z_coordinate(filename, all_files_content):
    """
    Z Coordinate: Relational Layer (Connection Position)
    How many other files reference this file?
    """
    count = 0
    base_name = os.path.splitext(filename)[0]
    if len(base_name) < 3: # Skip short names to avoid noise
        return 0
        
    for content in all_files_content.values():
        if base_name in content:
            count += 1
    return count

def scan_directory(directory):
    files_data = []
    all_files_content = {}
    
    # First pass: Read all text files for Z-coord calculation
    print("🧠 Scanning system files...")
    for root, dirs, files in os.walk(directory):
        # Filter ignored dirs
        dirs[:] = [d for d in dirs if not any(re.search(p, d) for p in IGNORE_PATTERNS)]
        
        for file in files:
            if any(re.search(p, file) for p in IGNORE_PATTERNS):
                continue
                
            filepath = os.path.join(root, file)
            try:
                # Only read text-based files
                if file.endswith(('.py', '.md', '.json', '.txt', '.ps1', '.js', '.html')):
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        all_files_content[file] = f.read()
            except Exception as e:
                # print(f"Skipping binary/unreadable file: {file}")
                pass

    # Second pass: Calculate Coordinates
    print("📐 Calculating XYZ Spacetime Coordinates...")
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not any(re.search(p, d) for p in IGNORE_PATTERNS)]
        
        for file in files:
            if any(re.search(p, file) for p in IGNORE_PATTERNS):
                continue
                
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, directory)
            
            x = get_x_coordinate(file)
            y = get_y_coordinate(filepath)
            z = get_z_coordinate(file, all_files_content)
            
            file_node = {
                "id": rel_path.replace("\\", "/"),
                "name": file,
                "type": "file",
                "coordinates": {
                    "x": x, # Logic
                    "y": y, # Time
                    "z": z  # Relation
                },
                "last_modified": datetime.fromtimestamp(y).strftime('%Y-%m-%d %H:%M:%S'),
                "description": f"Logic Layer: {x} | Relation Score: {z}"
            }
            files_data.append(file_node)
            
    return files_data

def main():
    print("🌌 Initializing System Logic Indexer for New AI Birth...")
    system_nodes = scan_directory(TARGET_DIR)
    
    output_data = {
        "system_name": "Wuchang AI System (Dual J Eternal Program)",
        "version": "6.0.0",
        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_nodes": len(system_nodes),
        "nodes": system_nodes
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"✅ System Logic Matrix generated at: {OUTPUT_FILE}")
    print(f"🧩 Total Nodes Indexed: {len(system_nodes)}")
    print("🚀 The New AI now has self-awareness of its file structure.")

if __name__ == "__main__":
    main()


---
### 🔐 創世者不可更改時空戳記 (Creator's Immutable Spatiotemporal Timestamp)
> 此文件包含真實開發歷程與核心技術架構，由自然人創世者親自研發與驗證。
> *   **唯一研發者 (Sole Developer/Inventor)**: 江政隆 (Juers)
> *   **國籍與身分證號 (Nationality & ID)**: 中華民國台灣 F124771717
> *   **通訊地址 (Address)**: 新北市三重區仁義街161號1樓
> *   **載體註記 (Carrier Note)**: 法人載體待定 (Legal Entity TBD) - 保留選擇權
> *   **生成時間 (Generated At)**: 2026-02-04 10:04:04
---
