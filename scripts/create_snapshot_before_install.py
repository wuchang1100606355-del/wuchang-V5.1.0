#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_snapshot_before_install.py

建立快照回滾點後執行安裝

功能：
- 建立系統快照
- 備份重要檔案
- 建立回滾點
- 執行 Google Tasks API 安裝
"""

import sys
import json
import shutil
import time
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


def create_snapshot():
    """建立系統快照"""
    print("【步驟 1：建立系統快照】")
    print()
    
    # 建立快照目錄
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    
    # 生成快照 ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_id = f"snapshot_{timestamp}"
    snapshot_dir = SNAPSHOTS_DIR / snapshot_id
    snapshot_dir.mkdir(exist_ok=True)
    
    print(f"  快照 ID: {snapshot_id}")
    print(f"  快照目錄: {snapshot_dir}")
    print()
    
    # 要備份的重要檔案和目錄
    important_items = [
        "google_credentials.json",
        "google_token.json",
        "network_interconnection_config.json",
        "auto_auth_config.json",
        "environment_calibration_report.json",
        "file_diff_report_*.json",
        "file_diff_report_*.md",
        "jules_task_*.json",
    ]
    
    # 備份配置檔案
    config_files = [
        "AGENT_CONSTITUTION.md",
        "RISK_ACTION_SOP.md",
        "risk_gate.py",
        "safe_sync_push.py",
        "api_community_data.py",
    ]
    
    backed_up = []
    skipped = []
    
    print("  正在備份檔案...")
    
    # 備份重要檔案
    for pattern in important_items:
        if "*" in pattern:
            # 使用 glob 搜尋
            for file_path in BASE_DIR.glob(pattern):
                try:
                    dest = snapshot_dir / file_path.name
                    shutil.copy2(file_path, dest)
                    backed_up.append(str(file_path.relative_to(BASE_DIR)))
                except Exception as e:
                    skipped.append(f"{file_path.name}: {e}")
        else:
            file_path = BASE_DIR / pattern
            if file_path.exists():
                try:
                    dest = snapshot_dir / file_path.name
                    shutil.copy2(file_path, dest)
                    backed_up.append(pattern)
                except Exception as e:
                    skipped.append(f"{pattern}: {e}")
    
    # 備份配置檔案
    for config_file in config_files:
        file_path = BASE_DIR / config_file
        if file_path.exists():
            try:
                dest = snapshot_dir / config_file
                shutil.copy2(file_path, dest)
                backed_up.append(config_file)
            except Exception as e:
                skipped.append(f"{config_file}: {e}")
    
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
    ]
    
    for var in env_vars_to_snapshot:
        value = os.getenv(var, "")
        if value:
            # 隱藏敏感資訊
            if "TOKEN" in var or "SECRET" in var:
                env_snapshot[var] = "***HIDDEN***"
            else:
                env_snapshot[var] = value
    
    env_file = snapshot_dir / "environment_variables.json"
    env_file.write_text(
        json.dumps(env_snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    # 建立快照元數據
    metadata = {
        "snapshot_id": snapshot_id,
        "timestamp": timestamp,
        "created_at": datetime.now().isoformat(),
        "backed_up_files": backed_up,
        "skipped_files": skipped,
        "environment_variables": list(env_snapshot.keys()),
        "purpose": "Before Google Tasks API installation",
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
        "purpose": metadata["purpose"],
    })
    
    # 只保留最近 10 個快照記錄
    global_metadata["snapshots"] = global_metadata["snapshots"][-10:]
    
    SNAPSHOT_METADATA.write_text(
        json.dumps(global_metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print(f"  ✓ 已備份 {len(backed_up)} 個檔案")
    if skipped:
        print(f"  ⚠️  跳過 {len(skipped)} 個檔案")
    print(f"  ✓ 環境變數已快照")
    print()
    
    return snapshot_id, snapshot_dir


def create_rollback_script(snapshot_id: str, snapshot_dir: Path):
    """建立回滾腳本"""
    print("【步驟 2：建立回滾腳本】")
    print()
    
    rollback_script = BASE_DIR / f"rollback_{snapshot_id}.py"
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rollback_{snapshot_id}.py

回滾到快照: {snapshot_id}

建立時間: {datetime.now().isoformat()}
"""

import sys
import shutil
from pathlib import Path

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
        import json
        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        print("快照資訊：")
        print(f"  建立時間: {{metadata.get('created_at', 'N/A')}}")
        print(f"  目的: {{metadata.get('purpose', 'N/A')}}")
        print()
    
    # 還原檔案
    restored = 0
    failed = 0
    
    for file_path in SNAPSHOT_DIR.iterdir():
        if file_path.name in ["metadata.json", "environment_variables.json"]:
            continue
        
        try:
            dest = BASE_DIR / file_path.name
            shutil.copy2(file_path, dest)
            print(f"  ✓ 已還原: {{file_path.name}}")
            restored += 1
        except Exception as e:
            print(f"  ✗ 還原失敗 {{file_path.name}}: {{e}}")
            failed += 1
    
    print()
    print(f"已還原 {{restored}} 個檔案")
    if failed > 0:
        print(f"失敗 {{failed}} 個檔案")
    
    print()
    print("=" * 70)
    print("回滾完成")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    success = rollback()
    sys.exit(0 if success else 1)
'''
    
    rollback_script.write_text(script_content, encoding="utf-8")
    
    # 在 Windows 上設定執行權限
    import os
    os.chmod(rollback_script, 0o755)
    
    print(f"  ✓ 回滾腳本已建立: {rollback_script.name}")
    print()
    
    return rollback_script


def execute_installation():
    """執行安裝"""
    print("【步驟 3：執行 Google Tasks API 安裝】")
    print()
    
    import subprocess
    
    try:
        result = subprocess.run(
            [sys.executable, "auto_setup_google_tasks.py", "--auto"],
            cwd=BASE_DIR,
            check=False
        )
        
        if result.returncode == 0:
            print()
            print("✓ 安裝完成")
            return True
        else:
            print()
            print("⚠️  安裝過程中有警告或錯誤")
            return False
    except Exception as e:
        print(f"✗ 安裝失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("建立快照回滾點並執行安裝")
    print("=" * 70)
    print()
    
    # 步驟 1: 建立快照
    snapshot_id, snapshot_dir = create_snapshot()
    
    # 步驟 2: 建立回滾腳本
    rollback_script = create_rollback_script(snapshot_id, snapshot_dir)
    
    # 步驟 3: 執行安裝
    print("=" * 70)
    install_success = execute_installation()
    print("=" * 70)
    print()
    
    # 總結
    print("=" * 70)
    print("【完成】")
    print("=" * 70)
    print()
    print(f"快照 ID: {snapshot_id}")
    print(f"快照目錄: {snapshot_dir}")
    print(f"回滾腳本: {rollback_script.name}")
    print()
    
    if install_success:
        print("✓ 安裝成功完成")
    else:
        print("⚠️  安裝過程中有問題")
        print()
        print("如果需要回滾，請執行：")
        print(f"  python {rollback_script.name}")
    
    print()
    print("【回滾方式】")
    print(f"  執行: python {rollback_script.name}")
    print()
    print("=" * 70)
    
    return 0 if install_success else 1


if __name__ == "__main__":
    sys.exit(main())
