import os
import json
import glob
from datetime import datetime, timedelta

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_LOG = os.path.join(BASE_DIR, "logs", "audit", "processed_research_files.json")
OUTPUT_REPORT = os.path.join(BASE_DIR, "reports", "collection_stats_report.md")

TARGET_DIRS = [
    os.path.join(BASE_DIR, "logs", "audit", "conversations"),
    os.path.join(BASE_DIR, "memory_store", "conversations"),
    os.path.join(BASE_DIR, "reports", "association_operational_files", "meetings"),
    os.path.join(BASE_DIR, "scripts", "association_operations", "meetings"),
    os.path.join(BASE_DIR, "decision_logs"),
    os.path.join(BASE_DIR, "xiaoj_auto_reports")
]

def get_file_info(path):
    try:
        stat = os.stat(path)
        return {
            'path': path,
            'size': stat.st_size,
            'mtime': datetime.fromtimestamp(stat.st_mtime)
        }
    except:
        return None

def main():
    print(f"Analyzing collection stats...")
    
    # 1. Load Processed Files
    processed_files = set()
    if os.path.exists(PROCESSED_LOG):
        with open(PROCESSED_LOG, 'r', encoding='utf-8') as f:
            processed_files = set(json.load(f))
            # Normalize paths to handle potential separator differences
            processed_files = {os.path.abspath(p) for p in processed_files}
    
    # 2. Scan Target Directories
    all_files = []
    total_size = 0
    
    for d in TARGET_DIRS:
        if not os.path.exists(d):
            continue
            
        # Find all relevant files
        for ext in ["*.txt", "*.md", "*.json"]:
            for fpath in glob.glob(os.path.join(d, "**", ext), recursive=True):
                # Skip the logs/reports themselves if they happen to be in the path
                if "processed_research_files.json" in fpath or "collection_stats_report.md" in fpath:
                    continue
                    
                abs_path = os.path.abspath(fpath)
                info = get_file_info(abs_path)
                if info:
                    all_files.append(info)
                    total_size += info['size']

    # 3. Calculate Stats
    total_count = len(all_files)
    processed_count = 0
    unprocessed_files = []
    recently_modified = [] # Last 24 hours
    
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)
    
    for f in all_files:
        if f['path'] in processed_files:
            processed_count += 1
        else:
            unprocessed_files.append(f)
            
        if f['mtime'] > one_day_ago:
            recently_modified.append(f)
            
    coverage_ratio = (processed_count / total_count * 100) if total_count > 0 else 0
    
    # 4. Generate Report
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as r:
        r.write(f"# 資料採集與異動分析報告\n")
        r.write(f"**分析時間**: {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        r.write(f"## 📊 總體統計\n")
        r.write(f"- **監控目錄數**: {len(TARGET_DIRS)}\n")
        r.write(f"- **總檔案數**: {total_count}\n")
        r.write(f"- **已採集檔案**: {processed_count}\n")
        r.write(f"- **未採集檔案**: {len(unprocessed_files)}\n")
        r.write(f"- **採集覆蓋率**: {coverage_ratio:.1f}%\n")
        r.write(f"- **24h內活躍檔案**: {len(recently_modified)}\n\n")
        
        r.write(f"## 📁 目錄詳情\n")
        r.write(f"| 目錄路徑 | 檔案數 | 已採集 | 未採集 |\n")
        r.write(f"| :--- | :---: | :---: | :---: |\n")
        
        dir_stats = {}
        for d in TARGET_DIRS:
            d_abs = os.path.abspath(d)
            d_files = [f for f in all_files if f['path'].startswith(d_abs)]
            d_processed = [f for f in d_files if f['path'] in processed_files]
            
            r.write(f"| `{os.path.basename(d)}` | {len(d_files)} | {len(d_processed)} | {len(d_files) - len(d_processed)} |\n")
        
        r.write(f"\n## 🆕 待採集清單 (Top 20)\n")
        if unprocessed_files:
            for f in unprocessed_files[:20]:
                r.write(f"- [{os.path.basename(f['path'])}]({f['path']}) ({f['mtime'].strftime('%Y-%m-%d %H:%M')})\n")
        else:
            r.write("*(無待採集檔案，系統同步率 100%)*\n")
            
        r.write(f"\n## 🔥 近期活躍檔案 (24h)\n")
        if recently_modified:
            for f in recently_modified:
                status = "✅ 已採集" if f['path'] in processed_files else "⭕ **未採集**"
                r.write(f"- {status} [{os.path.basename(f['path'])}]({f['path']}) - {f['mtime'].strftime('%H:%M')}\n")
        else:
            r.write("*(過去 24 小時內無檔案變更)*\n")

    print(f"Report generated: {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
