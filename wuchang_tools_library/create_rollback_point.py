import os
import shutil
import time
import hashlib
import json
from datetime import datetime

class SpacetimeArchiver:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.archive_dir = os.path.join(root_dir, "SPACETIME_SNAPSHOTS")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.snapshot_id = f"SNAP-{self.timestamp}"
        
    def create_rollback_point(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💾 Initiating System Snapshot ({self.snapshot_id})...")
        
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
            
        snapshot_path = os.path.join(self.archive_dir, self.snapshot_id)
        os.makedirs(snapshot_path)
        
        # Define critical files to archive
        critical_files = [
            "core_sister_service.py",
            "core_sister_service.py.quantum",
            "start_spacetime_system.ps1",
            "INTELLIGENCE_CORE/double_j_config.json",
            "INTELLIGENCE_CORE/double_j_config.json.quantum",
            "wuchang_tools_library/quantum_ai_transformer.py",
            "wuchang_tools_library/quantum_sandbox_manager.py",
            "wuchang_tools_library/wuchang_firewall_guard.py"
        ]
        
        manifest = {
            "snapshot_id": self.snapshot_id,
            "created_at": self.timestamp,
            "creator": "Core AI Sister (Little J)",
            "files": []
        }
        
        success_count = 0
        
        for file_rel_path in critical_files:
            src_path = os.path.join(self.root_dir, file_rel_path)
            if os.path.exists(src_path):
                dest_path = os.path.join(snapshot_path, file_rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)
                
                # Calculate hash for integrity
                with open(src_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                manifest["files"].append({
                    "path": file_rel_path,
                    "hash": file_hash
                })
                success_count += 1
                print(f"   -> Archived: {file_rel_path}")
            else:
                print(f"   -> Warning: File not found {file_rel_path}")

        # Save manifest
        with open(os.path.join(snapshot_path, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Snapshot Complete. {success_count} critical files secured.")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📍 Rollback Point Set: {snapshot_path}")

if __name__ == "__main__":
    archiver = SpacetimeArchiver(r"J:\共用雲端硬碟\五常雲端空間")
    archiver.create_rollback_point()
