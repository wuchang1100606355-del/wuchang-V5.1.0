#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_rollback_point.py

建立系統回滾點

功能：
- 建立系統快照
- 備份重要檔案和配置
- 建立回滾腳本
- 記錄系統狀態
"""

import sys
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
SNAPSHOT_METADATA = SNAPSHOTS_DIR / "snapshot_metadata.json"


def get_file_hash(file_path: Path) -> str:
    """計算檔案 SHA256 雜湊值"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return ""


def get_git_info() -> dict:
    """取得 Git 資訊"""
    git_info = {
        "branch": "",
        "commit": "",
        "status": "",
    }
    
    try:
        # 取得分支
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            git_info["branch"] = result.stdout.strip()
        
        # 取得 commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            git_info["commit"] = result.stdout.strip()[:12]
        
        # 取得狀態
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            git_info["status"] = result.stdout.strip()
    except:
        pass
    
    return git_info


def create_snapshot(purpose: str = "系統回滾點") -> tuple:
    """建立系統快照"""
    print("=" * 70)
    print("建立系統回滾點")
    print("=" * 70)
    print()
    
    # 建立快照目錄
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    
    # 生成快照 ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_id = f"snapshot_{timestamp}"
    snapshot_dir = SNAPSHOTS_DIR / snapshot_id
    snapshot_dir.mkdir(exist_ok=True)
    
    print(f"快照 ID: {snapshot_id}")
    print(f"快照目錄: {snapshot_dir}")
    print(f"目的: {purpose}")
    print()
    
    # 要備份的重要檔案和目錄
    important_files = [
        # 配置檔案
        "accounts_policy.json",
        "auto_auth_config.json",
        "network_interconnection_config.json",
        "jules_memory_bank.json",
        "little_j_permanent_permissions.json",
        "jules_personality_profile.json",
        "internal_id_records.json",
        "wuchang_community_boundary.geojson",
        "wuchang_community_knowledge_index.json",
        "wuchang_community_context_compact.md",
        
        # 憑證和認證
        "google_credentials.json",
        "google_token.json",
        ".secrets.json",
        
        # 核心規則檔案
        "AGENT_CONSTITUTION.md",
        "RISK_ACTION_SOP.md",
        "risk_gate.py",
        "safe_sync_push.py",
        "little_j_policy.py",
        
        # API 和整合
        "api_community_data.py",
        "local_control_center.py",
        
        # 環境和校準
        "environment_calibration_report.json",
        "env_vars.example.json",
    ]
    
    # 要備份的目錄（只備份特定檔案）
    important_dirs = {
        "cloudflared": ["config.yml", "credentials.json"],
        "certs/ssh": ["*.pub", "*.pem"],
        "wuchang_os/addons": ["**/__manifest__.py", "**/*.py"],
    }
    
    backed_up = []
    skipped = []
    file_hashes = {}
    
    print("正在備份檔案...")
    print()
    
    # 備份重要檔案
    for file_pattern in important_files:
        file_path = BASE_DIR / file_pattern
        if file_path.exists() and file_path.is_file():
            try:
                dest = snapshot_dir / file_path.name
                shutil.copy2(file_path, dest)
                file_hash = get_file_hash(file_path)
                file_hashes[file_pattern] = {
                    "path": str(file_path.relative_to(BASE_DIR)),
                    "hash": file_hash,
                    "size": file_path.stat().st_size,
                    "mtime": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                }
                backed_up.append(file_pattern)
                print(f"  ✓ {file_pattern}")
            except Exception as e:
                skipped.append(f"{file_pattern}: {e}")
                print(f"  ✗ {file_pattern}: {e}")
        else:
            skipped.append(f"{file_pattern}: 檔案不存在")
    
    # 備份重要目錄中的特定檔案
    for dir_name, patterns in important_dirs.items():
        dir_path = BASE_DIR / dir_name
        if dir_path.exists() and dir_path.is_dir():
            for pattern in patterns:
                for file_path in dir_path.rglob(pattern):
                    if file_path.is_file():
                        try:
                            rel_path = file_path.relative_to(BASE_DIR)
                            dest = snapshot_dir / rel_path
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, dest)
                            file_hash = get_file_hash(file_path)
                            file_hashes[str(rel_path)] = {
                                "path": str(rel_path),
                                "hash": file_hash,
                                "size": file_path.stat().st_size,
                                "mtime": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            }
                            backed_up.append(str(rel_path))
                            print(f"  ✓ {rel_path}")
                        except Exception as e:
                            skipped.append(f"{file_path}: {e}")
    
    # 建立環境變數快照
    env_snapshot = {}
    import os
    env_vars_to_snapshot = [
        "WUCHANG_HEALTH_URL",
        "WUCHANG_COPY_TO",
        "WUCHANG_HUB_URL",
        "WUCHANG_HUB_TOKEN",
        "WUCHANG_SYSTEM_DB_DIR",
        "WUCHANG_WORKSPACE_OUTDIR",
        "WUCHANG_PII_ENABLED",
        "WUCHANG_DEV_MODE",
        "PATH",
        "PYTHONPATH",
    ]
    
    for var in env_vars_to_snapshot:
        value = os.getenv(var, "")
        if value:
            # 隱藏敏感資訊
            if "TOKEN" in var or "SECRET" in var or "PASSWORD" in var:
                env_snapshot[var] = "***HIDDEN***"
            else:
                env_snapshot[var] = value
    
    env_file = snapshot_dir / "environment_variables.json"
    env_file.write_text(
        json.dumps(env_snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    # 取得 Git 資訊
    git_info = get_git_info()
    
    # 建立快照元數據
    metadata = {
        "snapshot_id": snapshot_id,
        "timestamp": timestamp,
        "created_at": datetime.now().isoformat(),
        "purpose": purpose,
        "backed_up_files": backed_up,
        "skipped_files": skipped,
        "file_count": len(backed_up),
        "file_hashes": file_hashes,
        "environment_variables": list(env_snapshot.keys()),
        "git_info": git_info,
        "system_info": {
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
        },
    }
    
    metadata_file = snapshot_dir / "metadata.json"
    metadata_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    # 更新全局元數據
    if SNAPSHOT_METADATA.exists():
        try:
            global_metadata = json.loads(SNAPSHOT_METADATA.read_text(encoding="utf-8"))
        except:
            global_metadata = {"snapshots": []}
    else:
        global_metadata = {"snapshots": []}
    
    global_metadata["snapshots"].append({
        "snapshot_id": snapshot_id,
        "timestamp": timestamp,
        "created_at": datetime.now().isoformat(),
        "purpose": purpose,
        "file_count": len(backed_up),
    })
    
    # 只保留最近 20 個快照記錄
    global_metadata["snapshots"] = global_metadata["snapshots"][-20:]
    global_metadata["last_updated"] = datetime.now().isoformat()
    
    SNAPSHOT_METADATA.write_text(
        json.dumps(global_metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print()
    print(f"✓ 已備份 {len(backed_up)} 個檔案")
    if skipped:
        print(f"⚠️  跳過 {len(skipped)} 個項目")
    print(f"✓ 環境變數已快照")
    print(f"✓ Git 資訊已記錄")
    print()
    
    return snapshot_id, snapshot_dir, metadata


def create_rollback_script(snapshot_id: str, snapshot_dir: Path, metadata: dict):
    """建立回滾腳本"""
    print("=" * 70)
    print("建立回滾腳本")
    print("=" * 70)
    print()
    
    rollback_script = BASE_DIR / f"rollback_{snapshot_id}.py"
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rollback_{snapshot_id}.py

回滾到快照: {snapshot_id}

建立時間: {metadata['created_at']}
目的: {metadata['purpose']}
"""

import sys
import json
import shutil
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOT_DIR = BASE_DIR / "snapshots" / "{snapshot_id}"

def rollback():
    """執行回滾"""
    print("=" * 70)
    print("回滾到快照: {snapshot_id}")
    print("=" * 70)
    print()
    
    if not SNAPSHOT_DIR.exists():
        print(f"✗ 快照目錄不存在: {{SNAPSHOT_DIR}}")
        return False
    
    # 讀取元數據
    metadata_file = SNAPSHOT_DIR / "metadata.json"
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        print("快照資訊：")
        print(f"  建立時間: {{metadata.get('created_at', 'N/A')}}")
        print(f"  目的: {{metadata.get('purpose', 'N/A')}}")
        print(f"  檔案數量: {{metadata.get('file_count', 0)}}")
        print()
    
    # 確認回滾
    print("⚠️  警告：此操作將覆蓋現有檔案！")
    print("按 Ctrl+C 取消，或按 Enter 繼續...")
    try:
        input()
    except KeyboardInterrupt:
        print("\\n已取消回滾")
        return False
    
    # 還原檔案
    restored = 0
    failed = 0
    
    print()
    print("正在還原檔案...")
    print()
    
    for file_path in SNAPSHOT_DIR.rglob("*"):
        if file_path.is_file() and file_path.name not in ["metadata.json", "environment_variables.json"]:
            try:
                rel_path = file_path.relative_to(SNAPSHOT_DIR)
                dest = BASE_DIR / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)
                print(f"  ✓ 已還原: {{rel_path}}")
                restored += 1
            except Exception as e:
                print(f"  ✗ 還原失敗 {{file_path.name}}: {{e}}")
                failed += 1
    
    print()
    print("=" * 70)
    print("回滾結果")
    print("=" * 70)
    print(f"已還原: {{restored}} 個檔案")
    if failed > 0:
        print(f"失敗: {{failed}} 個檔案")
    print()
    
    if failed == 0:
        print("✓ 回滾完成")
    else:
        print("⚠️  回滾完成，但有部分檔案還原失敗")
    
    print()
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = rollback()
    sys.exit(0 if success else 1)
'''
    
    rollback_script.write_text(script_content, encoding="utf-8")
    
    # 在 Windows 上設定執行權限
    import os
    try:
        os.chmod(rollback_script, 0o755)
    except:
        pass
    
    print(f"✓ 回滾腳本已建立: {rollback_script.name}")
    print()
    
    return rollback_script


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="建立系統回滾點")
    parser.add_argument(
        "--purpose",
        type=str,
        default="系統回滾點",
        help="回滾點目的說明"
    )
    
    args = parser.parse_args()
    
    # 建立快照
    snapshot_id, snapshot_dir, metadata = create_snapshot(args.purpose)
    
    # 建立回滾腳本
    rollback_script = create_rollback_script(snapshot_id, snapshot_dir, metadata)
    
    # 總結
    print("=" * 70)
    print("【完成】")
    print("=" * 70)
    print()
    print(f"快照 ID: {snapshot_id}")
    print(f"快照目錄: {snapshot_dir}")
    print(f"回滾腳本: {rollback_script.name}")
    print(f"備份檔案數: {metadata['file_count']}")
    print()
    print("【回滾方式】")
    print(f"  執行: python {rollback_script.name}")
    print()
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
