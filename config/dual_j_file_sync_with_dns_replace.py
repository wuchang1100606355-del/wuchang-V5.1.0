#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dual_j_file_sync_with_dns_replace.py

雙J協作：本機與伺服器檔案比對與同步
- 地端小J：比對檔案、識別新增項目
- 雲端小J：執行同步、驗證結果
- 自動將本機DNS替換為伺服器DNS
"""

import sys
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# DNS 替換規則
# 注意：只替換IP地址和localhost，不替換已存在的網域網址
DNS_REPLACEMENTS = {
    # 本機 IP 和 localhost（僅當不是網域網址時）
    # 使用負向先行斷言確保不替換已存在的網域
    r'(?<![\w\.-])127\.0\.0\.1(?![\w\.-])': 'wuchang.life',
    r'(?<![\w\.-])localhost(?![\w\.-])': 'wuchang.life',
    r'(?<![\w\.-])192\.168\.50\.84(?![\w\.-])': 'wuchang.life',
    # HTTP/HTTPS URL替換（僅當不是網域網址時）
    r'http://127\.0\.0\.1(?![\w\.-])': 'https://wuchang.life',
    r'http://localhost(?![\w\.-])': 'https://wuchang.life',
    r'https://127\.0\.0\.1(?![\w\.-])': 'https://wuchang.life',
    r'https://localhost(?![\w\.-])': 'https://wuchang.life',
    r'http://192\.168\.50\.84(?![\w\.-])': 'https://wuchang.life',
    r'https://192\.168\.50\.84(?![\w\.-])': 'https://wuchang.life',
    # 端口替換（保留端口號，僅當不是網域網址時）
    r'(?<![\w\.-])127\.0\.0\.1:(\d+)(?![\w\.-])': r'wuchang.life:\1',
    r'(?<![\w\.-])localhost:(\d+)(?![\w\.-])': r'wuchang.life:\1',
    r'(?<![\w\.-])192\.168\.50\.84:(\d+)(?![\w\.-])': r'wuchang.life:\1',
    # 特定服務的DNS替換（僅當不是網域網址時）
    r'http://127\.0\.0\.1:8788(?![\w\.-])': 'https://admin.wuchang.life',
    r'http://localhost:8788(?![\w\.-])': 'https://admin.wuchang.life',
    r'http://192\.168\.50\.84:8788(?![\w\.-])': 'https://admin.wuchang.life',
    r'http://127\.0\.0\.1:5000(?![\w\.-])': 'https://ui.wuchang.life',
    r'http://localhost:5000(?![\w\.-])': 'https://ui.wuchang.life',
    r'http://192\.168\.50\.84:5000(?![\w\.-])': 'https://ui.wuchang.life',
    r'http://127\.0\.0\.1:8069(?![\w\.-])': 'https://odoo.wuchang.life',
    r'http://localhost:8069(?![\w\.-])': 'https://odoo.wuchang.life',
    r'http://192\.168\.50\.84:8069(?![\w\.-])': 'https://odoo.wuchang.life',
}

# 需要排除的檔案和目錄
EXCLUDE_PATTERNS = [
    '.git',
    '__pycache__',
    '.pyc',
    '.pyo',
    '.pyd',
    'node_modules',
    '.venv',
    'venv',
    'env',
    '.env',
    '*.log',
    '*.tmp',
    '*.swp',
    '.DS_Store',
    'Thumbs.db',
    'certs/',
    '*.pem',
    '*.key',
    '*.cert',
    'router_config.json',  # 包含敏感資訊
    'google_credentials.json',
    'google_token.json',
]

# 需要替換DNS的檔案類型
DNS_REPLACE_FILE_TYPES = [
    '.py',
    '.md',
    '.html',
    '.json',
    '.txt',
    '.yml',
    '.yaml',
    '.conf',
    '.conf',
    '.cfg',
    '.ini',
]


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)


def should_exclude_file(file_path: Path) -> bool:
    """檢查檔案是否應該被排除"""
    file_str = str(file_path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_str:
            return True
    return False


def replace_dns_in_content(content: str, file_path: Path) -> Tuple[str, int]:
    """
    替換檔案內容中的本機DNS為伺服器DNS
    注意：不替換已存在的網域網址（如 wuchang.life）
    
    Returns:
        (替換後的內容, 替換次數)
    """
    if file_path.suffix not in DNS_REPLACE_FILE_TYPES:
        return content, 0
    
    replaced_content = content
    total_replacements = 0
    
    # 檢查是否已包含網域網址，如果包含則跳過替換
    if re.search(r'wuchang\.life|\.life', replaced_content, re.IGNORECASE):
        log(f"  檔案已包含網域網址，跳過DNS替換", "INFO")
        return replaced_content, 0
    
    for pattern, replacement in DNS_REPLACEMENTS.items():
        # 使用負向先行斷言確保不替換已存在的網域
        # 檢查替換目標是否已存在
        if replacement in replaced_content:
            continue
        
        matches = re.findall(pattern, replaced_content)
        if matches:
            replaced_content = re.sub(pattern, replacement, replaced_content)
            total_replacements += len(matches)
            log(f"  替換 {len(matches)} 處: {pattern} -> {replacement}", "INFO")
    
    return replaced_content, total_replacements


def calculate_file_hash(file_path: Path) -> str:
    """計算檔案 SHA256 雜湊值"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        log(f"計算雜湊失敗 {file_path}: {e}", "ERROR")
        return ""


def scan_local_files(base_dir: Path) -> Dict[str, Dict[str, Any]]:
    """掃描本機檔案"""
    log("開始掃描本機檔案...", "INFO")
    files = {}
    
    for root, dirs, filenames in os.walk(base_dir):
        # 過濾排除的目錄
        dirs[:] = [d for d in dirs if not should_exclude_file(Path(root) / d)]
        
        for filename in filenames:
            file_path = Path(root) / filename
            relative_path = file_path.relative_to(base_dir)
            
            if should_exclude_file(file_path):
                continue
            
            try:
                file_hash = calculate_file_hash(file_path)
                file_stat = file_path.stat()
                
                files[str(relative_path)] = {
                    "path": str(relative_path),
                    "full_path": str(file_path),
                    "hash": file_hash,
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                }
            except Exception as e:
                log(f"掃描檔案失敗 {file_path}: {e}", "ERROR")
    
    log(f"掃描完成，共 {len(files)} 個檔案", "INFO")
    return files


def get_server_file_list(server_url: str, api_key: str = None) -> Dict[str, Dict[str, Any]]:
    """從伺服器獲取檔案列表"""
    log("開始獲取伺服器檔案列表...", "INFO")
    
    # 這裡可以透過 API 或 SSH 獲取伺服器檔案列表
    # 暫時返回空字典，需要根據實際伺服器API實現
    try:
        # 範例：透過 API 獲取
        # response = requests.get(f"{server_url}/api/files/list", headers={"Authorization": f"Bearer {api_key}"})
        # return response.json()
        log("伺服器檔案列表獲取功能待實現", "WARN")
        return {}
    except Exception as e:
        log(f"獲取伺服器檔案列表失敗: {e}", "ERROR")
        return {}


def compare_files(local_files: Dict[str, Dict], server_files: Dict[str, Dict]) -> Dict[str, List[str]]:
    """比對本機和伺服器檔案"""
    log("開始比對檔案...", "INFO")
    
    result = {
        "new_files": [],  # 本機新增的檔案
        "modified_files": [],  # 本機修改的檔案
        "unchanged_files": [],  # 未變更的檔案
    }
    
    for file_path, file_info in local_files.items():
        if file_path in server_files:
            if file_info["hash"] != server_files[file_path]["hash"]:
                result["modified_files"].append(file_path)
                log(f"  修改: {file_path}", "INFO")
            else:
                result["unchanged_files"].append(file_path)
        else:
            result["new_files"].append(file_path)
            log(f"  新增: {file_path}", "INFO")
    
    log(f"比對完成: 新增 {len(result['new_files'])} 個，修改 {len(result['modified_files'])} 個", "INFO")
    return result


def prepare_file_for_sync(file_path: Path, output_dir: Path) -> Tuple[Path, int]:
    """
    準備檔案用於同步（替換DNS）
    
    Returns:
        (輸出檔案路徑, 替換次數)
    """
    output_path = output_dir / file_path.name
    
    try:
        # 讀取原始檔案
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替換DNS
        replaced_content, replacements = replace_dns_in_content(content, file_path)
        
        # 寫入輸出檔案
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(replaced_content)
        
        return output_path, replacements
    
    except UnicodeDecodeError:
        # 二進位檔案，直接複製
        shutil.copy2(file_path, output_path)
        return output_path, 0
    
    except Exception as e:
        log(f"準備檔案失敗 {file_path}: {e}", "ERROR")
        return output_path, 0


def sync_files_to_server(
    files_to_sync: List[str],
    local_files: Dict[str, Dict],
    server_url: str,
    server_path: str,
    health_url: str = None,
    api_key: str = None
) -> Dict[str, Any]:
    """同步檔案到伺服器（使用 safe_sync_push.py）"""
    log(f"開始同步 {len(files_to_sync)} 個檔案到伺服器...", "INFO")
    
    # 建立臨時目錄用於DNS替換後的檔案
    temp_dir = BASE_DIR / "sync_temp"
    temp_dir.mkdir(exist_ok=True)
    
    results = {
        "success": [],
        "failed": [],
        "total_replacements": 0,
        "files_processed": []
    }
    
    # 準備檔案（替換DNS）
    prepared_files = []
    for file_path_str in files_to_sync:
        try:
            file_info = local_files[file_path_str]
            local_file_path = Path(file_info["full_path"])
            
            # 準備檔案（替換DNS）
            output_path, replacements = prepare_file_for_sync(local_file_path, temp_dir / local_file_path.name)
            results["total_replacements"] += replacements
            
            if replacements > 0:
                log(f"  {file_path_str}: 替換了 {replacements} 處DNS", "INFO")
            
            prepared_files.append({
                "original": file_path_str,
                "prepared": str(output_path),
                "replacements": replacements
            })
            results["files_processed"].append(file_path_str)
            
        except Exception as e:
            log(f"準備檔案失敗 {file_path_str}: {e}", "ERROR")
            results["failed"].append(file_path_str)
    
    # 使用 safe_sync_push.py 進行同步
    if prepared_files:
        try:
            from safe_sync_push import main as safe_sync_main
            import sys as sys_module
            
            # 準備 safe_sync_push 的參數
            sync_files = [Path(p["prepared"]).name for p in prepared_files]
            
            # 建立臨時的 safe_sync_push 參數
            original_argv = sys_module.argv
            try:
                sys_module.argv = [
                    "safe_sync_push.py",
                    "--files", *sync_files,
                    "--copy-to", str(server_path),
                    "--actor", "dual_j_collaboration"
                ]
                
                if health_url:
                    sys_module.argv.extend(["--health-url", health_url])
                
                # 修改 safe_sync_push 的工作目錄為 temp_dir
                original_cwd = os.getcwd()
                try:
                    os.chdir(temp_dir)
                    exit_code = safe_sync_main()
                    
                    if exit_code == 0:
                        log("safe_sync_push 執行成功", "INFO")
                        results["success"].extend([p["original"] for p in prepared_files])
                    else:
                        log(f"safe_sync_push 執行失敗 (退出碼: {exit_code})", "ERROR")
                        results["failed"].extend([p["original"] for p in prepared_files])
                finally:
                    os.chdir(original_cwd)
                    
            finally:
                sys_module.argv = original_argv
                
        except ImportError:
            log("無法匯入 safe_sync_push，使用備用方法", "WARN")
            # 備用方法：直接複製到伺服器目錄
            for prep in prepared_files:
                try:
                    src = Path(prep["prepared"])
                    dst = Path(server_path) / Path(prep["original"]).name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    results["success"].append(prep["original"])
                except Exception as e:
                    log(f"複製檔案失敗 {prep['original']}: {e}", "ERROR")
                    results["failed"].append(prep["original"])
        except Exception as e:
            log(f"同步過程發生錯誤: {e}", "ERROR")
            results["failed"].extend([p["original"] for p in prepared_files])
    
    # 清理臨時目錄
    try:
        shutil.rmtree(temp_dir)
    except:
        pass
    
    log(f"同步完成: 成功 {len(results['success'])} 個，失敗 {len(results['failed'])} 個", "INFO")
    return results


def call_local_j(message: str) -> Dict[str, Any]:
    """呼叫地端小J"""
    if not REQUESTS_AVAILABLE:
        return {"response": "requests 模組不可用"}
    try:
        # 透過 local_control_center API 呼叫
        response = requests.post(
            "http://127.0.0.1:8788/api/local_j/chat",
            json={"message": message},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        log(f"呼叫地端小J失敗: {e}", "ERROR")
    return {"response": "無法連線到地端小J"}


def call_cloud_j(message: str) -> Dict[str, Any]:
    """呼叫雲端小J (JULES)"""
    try:
        # 透過 Google Tasks 建立任務給 JULES
        from google_tasks_integration import get_google_tasks_integration
        integration = get_google_tasks_integration()
        # 獲取任務列表
        task_lists = integration.list_task_lists()
        primary_list = None
        for task_list in task_lists:
            if task_list.title == "JULES" or task_list.id == "primary":
                primary_list = task_list
                break
        if not primary_list and task_lists:
            primary_list = task_lists[0]
        
        if primary_list:
            task = integration.create_task(
                task_list_id=primary_list.id,
                title="檔案同步任務",
                notes=message
            )
            return {"response": "任務已建立", "task_id": task.id if task else None}
        else:
            return {"response": "找不到任務列表"}
    except ImportError:
        log("Google Tasks 整合不可用", "WARN")
    except Exception as e:
        log(f"呼叫雲端小J失敗: {e}", "ERROR")
    return {"response": "無法連線到雲端小J"}


def add_work_log(agent: str, work_type: str, description: str, status: str = "completed", details: Dict = None, result: str = None):
    """記錄工作日誌"""
    try:
        from dual_j_work_log import add_work_log as _add_work_log
        _add_work_log(agent, work_type, description, status, details, result)
    except ImportError:
        log(f"[工作日誌] {agent}: {work_type} - {description}", "INFO")


def get_new_files_from_git() -> List[str]:
    """從 Git 獲取新增的檔案（相對於上次提交）"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        new_files = []
        for line in result.stdout.strip().split('\n'):
            if line.startswith('??'):  # 未追蹤的檔案
                file_path = line[3:].strip()
                if not should_exclude_file(BASE_DIR / file_path):
                    new_files.append(file_path)
            elif line.startswith('A ') or line.startswith('AM'):  # 新增的檔案
                file_path = line[3:].strip()
                if not should_exclude_file(BASE_DIR / file_path):
                    new_files.append(file_path)
        
        return new_files
    except Exception as e:
        log(f"獲取 Git 新增檔案失敗: {e}", "ERROR")
        return []


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="雙J協作：本機與伺服器檔案比對與同步（自動替換DNS）")
    parser.add_argument("--files", nargs="+", help="要同步的檔案列表（如果未提供，則從 Git 獲取新增檔案）")
    parser.add_argument("--server-dir", default=None, help="伺服器目錄（覆蓋 WUCHANG_COPY_TO）")
    parser.add_argument("--health-url", default=None, help="伺服器健康檢查 URL（覆蓋 WUCHANG_HEALTH_URL）")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行，不實際同步")
    
    args = parser.parse_args()
    
    log("=" * 60, "INFO")
    log("雙J協作：本機與伺服器檔案比對與同步", "INFO")
    log("=" * 60, "INFO")
    
    # 記錄工作日誌
    add_work_log("地端小 j", "檔案比對", "開始比對本機與伺服器檔案", "in_progress")
    
    # 1. 地端小J：識別需要同步的檔案
    log("\n[地端小J] 開始識別需要同步的檔案...", "INFO")
    local_j_response = call_local_j("請協助識別本機新增的檔案，準備同步到伺服器")
    log(f"地端小J回應: {local_j_response.get('response', 'N/A')}", "INFO")
    
    if args.files:
        files_to_sync = args.files
        log(f"使用命令行指定的檔案: {len(files_to_sync)} 個", "INFO")
    else:
        # 從 Git 獲取新增檔案
        files_to_sync = get_new_files_from_git()
        if not files_to_sync:
            log("未找到新增的檔案", "INFO")
            return
        log(f"從 Git 識別到 {len(files_to_sync)} 個新增檔案", "INFO")
    
    # 過濾排除的檔案
    files_to_sync = [f for f in files_to_sync if not should_exclude_file(BASE_DIR / f)]
    
    if not files_to_sync:
        log("沒有需要同步的檔案", "INFO")
        return
    
    log(f"\n需要同步的檔案 ({len(files_to_sync)} 個):", "INFO")
    for file_path in files_to_sync[:20]:  # 顯示前20個
        log(f"  - {file_path}", "INFO")
    if len(files_to_sync) > 20:
        log(f"  ... 還有 {len(files_to_sync) - 20} 個檔案", "INFO")
    
    # 2. 掃描本機檔案資訊
    log("\n[地端小J] 掃描本機檔案資訊...", "INFO")
    local_files = {}
    for file_path_str in files_to_sync:
        file_path = BASE_DIR / file_path_str
        if file_path.exists():
            try:
                file_hash = calculate_file_hash(file_path)
                file_stat = file_path.stat()
                local_files[file_path_str] = {
                    "path": file_path_str,
                    "full_path": str(file_path),
                    "hash": file_hash,
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                }
            except Exception as e:
                log(f"掃描檔案失敗 {file_path_str}: {e}", "ERROR")
    
    if not local_files:
        log("沒有有效的檔案可以同步", "ERROR")
        return
    
    # 3. 雲端小J：同步檔案（替換DNS）
    log("\n[雲端小J] 開始同步檔案到伺服器（自動替換DNS）...", "INFO")
    cloud_j_message = f"準備同步 {len(files_to_sync)} 個檔案到伺服器，將自動替換本機DNS為伺服器DNS"
    cloud_j_response = call_cloud_j(cloud_j_message)
    log(f"雲端小J回應: {cloud_j_response.get('response', 'N/A')}", "INFO")
    add_work_log("雲端小 j (JULES)", "檔案同步", cloud_j_message, "in_progress")
    
    server_path = args.server_dir or os.getenv("WUCHANG_COPY_TO", "")
    if not server_path:
        log("錯誤: 請提供 --server-dir 或設定 WUCHANG_COPY_TO 環境變數", "ERROR")
        return
    
    health_url = args.health_url or os.getenv("WUCHANG_HEALTH_URL", "https://wuchang.life/health")
    server_url = os.getenv("WUCHANG_SERVER_URL", "https://wuchang.life")
    
    if args.dry_run:
        log("【模擬模式】不會實際同步檔案", "INFO")
        # 模擬替換DNS
        total_replacements = 0
        for file_path_str in files_to_sync:
            file_path = BASE_DIR / file_path_str
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    _, replacements = replace_dns_in_content(content, file_path)
                    total_replacements += replacements
                    if replacements > 0:
                        log(f"  {file_path_str}: 將替換 {replacements} 處DNS", "INFO")
                except:
                    pass
        log(f"\n模擬完成: 將替換 {total_replacements} 處DNS", "INFO")
        return
    
    sync_results = sync_files_to_server(
        files_to_sync,
        local_files,
        server_url,
        server_path,
        health_url=health_url
    )
    
    # 4. 生成報告
    report = {
        "timestamp": datetime.now().isoformat(),
        "files_to_sync": files_to_sync,
        "local_files_count": len(local_files),
        "sync_results": sync_results,
        "dns_replacements": sync_results.get("total_replacements", 0),
        "server_path": server_path,
        "health_url": health_url
    }
    
    report_file = BASE_DIR / f"dual_j_sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    log(f"\n同步報告已儲存: {report_file}", "INFO")
    log(f"總共替換了 {sync_results.get('total_replacements', 0)} 處DNS", "INFO")
    log(f"成功同步: {len(sync_results.get('success', []))} 個檔案", "INFO")
    if sync_results.get('failed'):
        log(f"失敗: {len(sync_results['failed'])} 個檔案", "ERROR")
    
    # 記錄工作日誌
    result_summary = f"成功同步 {len(sync_results.get('success', []))} 個檔案，替換 {sync_results.get('total_replacements', 0)} 處DNS"
    add_work_log("地端小 j", "檔案比對", "檔案比對完成", "completed", 
                 {"files_count": len(files_to_sync), "dns_replacements": sync_results.get('total_replacements', 0)},
                 result_summary)
    add_work_log("雲端小 j (JULES)", "檔案同步", "檔案同步完成", "completed",
                 {"success_count": len(sync_results.get('success', [])), "failed_count": len(sync_results.get('failed', []))},
                 result_summary)
    
    log("\n同步完成！", "INFO")


if __name__ == "__main__":
    main()
