#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dual_j_full_deployment.py

雙J全面部署系統
- 地端小J：準備部署檔案、替換DNS
- 雲端小J：執行部署、驗證結果
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

# 設定 UTF-8 編碼輸出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# DNS 替換規則（與 dual_j_file_sync_with_dns_replace.py 相同）
# 注意：只替換IP地址和localhost，不替換已存在的網域網址
DNS_REPLACEMENTS = {
    # 本機 IP 和 localhost（僅當不是網域網址時）
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

# 需要替換DNS的檔案類型
DNS_REPLACE_FILE_TYPES = [
    '.py', '.md', '.html', '.json', '.txt',
    '.yml', '.yaml', '.conf', '.cfg', '.ini',
    '.js', '.jsx', '.ts', '.tsx', '.css',
]

# 排除的檔案和目錄
EXCLUDE_PATTERNS = [
    '.git', '__pycache__', '.pyc', '.pyo', '.pyd',
    'node_modules', '.venv', 'venv', 'env', '.env',
    '*.log', '*.tmp', '*.swp', '.DS_Store', 'Thumbs.db',
    'certs/', '*.pem', '*.key', '*.cert',
    'router_config.json', 'google_credentials.json', 'google_token.json',
    'backups/', 'snapshots/',
]

# 部署檔案清單（核心檔案）
DEPLOYMENT_FILES = [
    # 核心系統檔案
    "local_control_center.py",
    "wuchang_control_center.html",
    "jules_memory_bank.json",
    "router_integration.py",
    "router_full_control.py",
    "property_management_router_integration.py",
    "dual_j_file_sync_with_dns_replace.py",
    
    # 雙J協作
    "little_j_jules_container_collaboration.py",
    "auto_jules_task_executor.py",
    "dual_j_work_log.py",
    "dual_j_deploy.py",
    
    # 路由器相關
    "router_api_controller.py",
    "router_api_explorer.py",
    
    # 文檔
    "ROUTER_FULL_CONTROL_GUIDE.md",
    "ROUTER_API_COMPLETE_GUIDE.md",
    "DUAL_J_FILE_SYNC_GUIDE.md",
    "AGENT_CONSTITUTION.md",
    "RISK_ACTION_SOP.md",
    
    # 工具
    "safe_sync_push.py",
    "risk_gate.py",
    "file_compare_sync.py",
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
        # 檢查替換目標是否已存在
        if replacement in replaced_content:
            continue
        
        matches = re.findall(pattern, replaced_content)
        if matches:
            replaced_content = re.sub(pattern, replacement, replaced_content)
            total_replacements += len(matches)
    
    return replaced_content, total_replacements


def scan_all_files_for_dns(base_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """掃描所有檔案，找出需要更改的DNS"""
    log("掃描所有檔案，找出需要更改的DNS...", "INFO")
    
    dns_findings = {
        "127.0.0.1": [],
        "localhost": [],
        "192.168.50.84": [],
    }
    
    for root, dirs, filenames in os.walk(base_dir):
        # 過濾排除的目錄
        dirs[:] = [d for d in dirs if not should_exclude_file(Path(root) / d)]
        
        for filename in filenames:
            file_path = Path(root) / filename
            relative_path = file_path.relative_to(base_dir)
            
            if should_exclude_file(file_path):
                continue
            
            if file_path.suffix not in DNS_REPLACE_FILE_TYPES:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 檢查各種DNS模式
                if re.search(r'127\.0\.0\.1', content):
                    dns_findings["127.0.0.1"].append({
                        "file": str(relative_path),
                        "count": len(re.findall(r'127\.0\.0\.1', content))
                    })
                
                if re.search(r'\blocalhost\b', content):
                    dns_findings["localhost"].append({
                        "file": str(relative_path),
                        "count": len(re.findall(r'\blocalhost\b', content))
                    })
                
                if re.search(r'192\.168\.50\.84', content):
                    dns_findings["192.168.50.84"].append({
                        "file": str(relative_path),
                        "count": len(re.findall(r'192\.168\.50\.84', content))
                    })
            except UnicodeDecodeError:
                # 二進位檔案，跳過
                continue
            except Exception as e:
                log(f"掃描檔案失敗 {file_path}: {e}", "ERROR")
    
    return dns_findings


def prepare_deployment_files(files: List[str], output_dir: Path) -> Dict[str, Any]:
    """準備部署檔案（替換DNS）"""
    log(f"準備部署檔案到: {output_dir}", "INFO")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "prepared": [],
        "failed": [],
        "total_replacements": 0
    }
    
    for file_path_str in files:
        file_path = BASE_DIR / file_path_str
        if not file_path.exists():
            log(f"  檔案不存在: {file_path_str}", "WARN")
            results["failed"].append(file_path_str)
            continue
        
        try:
            # 讀取原始檔案
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替換DNS
            replaced_content, replacements = replace_dns_in_content(content, file_path)
            results["total_replacements"] += replacements
            
            # 寫入輸出檔案
            output_path = output_dir / file_path.name
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(replaced_content)
            
            if replacements > 0:
                log(f"  {file_path_str}: 替換了 {replacements} 處DNS", "INFO")
            
            results["prepared"].append({
                "file": file_path_str,
                "output": str(output_path),
                "replacements": replacements
            })
            
        except UnicodeDecodeError:
            # 二進位檔案，直接複製
            output_path = output_dir / file_path.name
            shutil.copy2(file_path, output_path)
            results["prepared"].append({
                "file": file_path_str,
                "output": str(output_path),
                "replacements": 0,
                "binary": True
            })
        except Exception as e:
            log(f"  準備檔案失敗 {file_path_str}: {e}", "ERROR")
            results["failed"].append(file_path_str)
    
    log(f"準備完成: {len(results['prepared'])} 個檔案，替換 {results['total_replacements']} 處DNS", "INFO")
    return results


def deploy_to_server(prepared_dir: Path, server_path: str, health_url: str = None) -> bool:
    """部署到伺服器"""
    log(f"部署到伺服器: {server_path}", "INFO")
    
    try:
        # 使用 safe_sync_push.py 進行部署
        from safe_sync_push import main as safe_sync_main
        import sys as sys_module
        
        # 獲取所有準備好的檔案
        files_to_deploy = [f.name for f in prepared_dir.rglob('*') if f.is_file()]
        
        if not files_to_deploy:
            log("沒有檔案需要部署", "WARN")
            return False
        
        # 準備 safe_sync_push 參數
        original_argv = sys_module.argv
        original_cwd = os.getcwd()
        
        try:
            sys_module.argv = [
                "safe_sync_push.py",
                "--files", *files_to_deploy,
                "--copy-to", server_path,
                "--actor", "dual_j_full_deployment"
            ]
            
            if health_url:
                sys_module.argv.extend(["--health-url", health_url])
            
            os.chdir(prepared_dir)
            exit_code = safe_sync_main()
            
            if exit_code == 0:
                log("部署成功", "INFO")
                return True
            else:
                log(f"部署失敗 (退出碼: {exit_code})", "ERROR")
                return False
        finally:
            sys_module.argv = original_argv
            os.chdir(original_cwd)
            
    except ImportError:
        log("無法匯入 safe_sync_push，使用備用方法", "WARN")
        # 備用方法：直接複製
        server_path_obj = Path(server_path)
        for file_path in prepared_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(prepared_dir)
                dest_path = server_path_obj / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
        log("使用備用方法部署完成", "INFO")
        return True
    except Exception as e:
        log(f"部署失敗: {e}", "ERROR")
        return False


def add_work_log(agent: str, work_type: str, description: str, status: str = "completed", details: Dict = None, result: str = None):
    """記錄工作日誌"""
    try:
        from dual_j_work_log import add_work_log as _add_work_log
        _add_work_log(agent, work_type, description, status, details, result)
    except ImportError:
        log(f"[工作日誌] {agent}: {work_type} - {description}", "INFO")


def generate_dns_change_list() -> Dict[str, Any]:
    """生成DNS更改清單"""
    log("生成DNS更改清單...", "INFO")
    
    dns_findings = scan_all_files_for_dns(BASE_DIR)
    
    total_files = 0
    total_occurrences = 0
    
    for dns_type, files in dns_findings.items():
        total_files += len(files)
        total_occurrences += sum(f["count"] for f in files)
    
    change_list = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_files_need_change": total_files,
            "total_dns_occurrences": total_occurrences,
            "dns_types": {
                "127.0.0.1": {
                    "files_count": len(dns_findings["127.0.0.1"]),
                    "total_occurrences": sum(f["count"] for f in dns_findings["127.0.0.1"])
                },
                "localhost": {
                    "files_count": len(dns_findings["localhost"]),
                    "total_occurrences": sum(f["count"] for f in dns_findings["localhost"])
                },
                "192.168.50.84": {
                    "files_count": len(dns_findings["192.168.50.84"]),
                    "total_occurrences": sum(f["count"] for f in dns_findings["192.168.50.84"])
                }
            }
        },
        "files": dns_findings,
        "replacement_rules": DNS_REPLACEMENTS
    }
    
    return change_list


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="雙J全面部署系統")
    parser.add_argument("--files", nargs="+", help="要部署的檔案列表（如果未提供，使用預設清單）")
    parser.add_argument("--server-dir", default=None, help="伺服器目錄（覆蓋 WUCHANG_COPY_TO）")
    parser.add_argument("--health-url", default=None, help="伺服器健康檢查 URL（覆蓋 WUCHANG_HEALTH_URL）")
    parser.add_argument("--dns-list-only", action="store_true", help="只生成DNS更改清單，不部署")
    parser.add_argument("--dry-run", action="store_true", help="模擬執行")
    
    args = parser.parse_args()
    
    log("=" * 60, "INFO")
    log("雙J全面部署系統", "INFO")
    log("=" * 60, "INFO")
    
    # 記錄工作日誌
    add_work_log("地端小 j", "全面部署準備", "開始準備全面部署", "in_progress")
    
    # 1. 生成DNS更改清單
    log("\n[地端小J] 生成DNS更改清單...", "INFO")
    dns_change_list = generate_dns_change_list()
    
    # 儲存DNS更改清單
    dns_list_file = BASE_DIR / f"dns_change_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    dns_list_file.write_text(
        json.dumps(dns_change_list, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    log(f"DNS更改清單已儲存: {dns_list_file}", "INFO")
    
    # 顯示摘要
    summary = dns_change_list["summary"]
    log(f"\nDNS更改摘要:", "INFO")
    log(f"  需要更改的檔案數: {summary['total_files_need_change']}", "INFO")
    log(f"  總DNS出現次數: {summary['total_dns_occurrences']}", "INFO")
    for dns_type, stats in summary["dns_types"].items():
        if stats["files_count"] > 0:
            log(f"  {dns_type}: {stats['files_count']} 個檔案，{stats['total_occurrences']} 處", "INFO")
    
    if args.dns_list_only:
        log("\n只生成DNS清單，不執行部署", "INFO")
        return
    
    # 2. 準備部署檔案
    files_to_deploy = args.files if args.files else DEPLOYMENT_FILES
    log(f"\n[地端小J] 準備部署檔案 ({len(files_to_deploy)} 個)...", "INFO")
    
    prepared_dir = BASE_DIR / "deployment_prepared"
    if args.dry_run:
        log("【模擬模式】不會實際準備檔案", "INFO")
    else:
        prepare_results = prepare_deployment_files(files_to_deploy, prepared_dir)
        log(f"準備完成: {len(prepare_results['prepared'])} 個檔案，替換 {prepare_results['total_replacements']} 處DNS", "INFO")
    
    # 3. 雲端小J：部署到伺服器
    if not args.dry_run:
        log("\n[雲端小J] 開始部署到伺服器...", "INFO")
        add_work_log("雲端小 j (JULES)", "全面部署執行", "開始執行全面部署", "in_progress")
        
        server_path = args.server_dir or os.getenv("WUCHANG_COPY_TO", "")
        if not server_path:
            log("錯誤: 請提供 --server-dir 或設定 WUCHANG_COPY_TO 環境變數", "ERROR")
            return
        
        health_url = args.health_url or os.getenv("WUCHANG_HEALTH_URL", "https://wuchang.life/health")
        
        success = deploy_to_server(prepared_dir, server_path, health_url)
        
        if success:
            log("部署成功！", "INFO")
            add_work_log("地端小 j", "全面部署準備", "部署準備完成", "completed",
                        {"files_count": len(files_to_deploy), "dns_replacements": prepare_results.get("total_replacements", 0)},
                        "部署準備完成")
            add_work_log("雲端小 j (JULES)", "全面部署執行", "部署執行完成", "completed",
                        {"server_path": server_path},
                        "部署執行完成")
        else:
            log("部署失敗", "ERROR")
            add_work_log("雲端小 j (JULES)", "全面部署執行", "部署執行失敗", "failed")
    else:
        log("\n【模擬模式】不會實際部署", "INFO")
    
    log("\n部署流程完成！", "INFO")
    log("=" * 60, "INFO")


if __name__ == "__main__":
    main()
