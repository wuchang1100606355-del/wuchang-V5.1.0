#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證伺服器連線環境及數據，並進行地端檔案比對
"""

import os
import sys
import json
import socket
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import paramiko

# 配置
SERVER_IP = "192.168.50.249"
SERVER_PORTS = [22, 8069, 8080, 8766, 3001]
LOCAL_PATH = Path(r"C:\wuchang V5.1.0")
REMOTE_PATH = "/home/admin"
SYNC_DIRS = [
    "wuchang_os/addons",
    "wuchang_os/config",
    "config",
    "scripts",
    "memory_store",
    "downloads"
]

# 可能的用戶名
POSSIBLE_USERS = ["admin", "wuchang", "user", "ubuntu", "debian", "root"]

def print_section(title):
    """打印章節標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(label, status, details=""):
    """打印結果"""
    status_symbol = "[OK]" if status else "[FAIL]"
    status_color = "\033[92m" if status else "\033[91m"
    reset_color = "\033[0m"
    print(f"{status_color}{status_symbol}{reset_color} {label}")
    if details:
        print(f"    {details}")

def test_connection(ip, port, timeout=3):
    """測試連線"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def verify_server_connection():
    """驗證伺服器連線環境"""
    print_section("步驟 1: 驗證伺服器連線環境")
    
    results = {
        "ping": False,
        "ports": {},
        "ssh_available": False,
        "ssh_user": None,
        "ssh_authenticated": False
    }
    
    # 1. Ping 測試
    print("\n[1.1] Ping 測試...")
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                ["ping", "-n", "2", SERVER_IP],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:  # Linux/Mac
            result = subprocess.run(
                ["ping", "-c", "2", SERVER_IP],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        if result.returncode == 0:
            print_result("Ping 測試", True, "伺服器可達")
            results["ping"] = True
        else:
            print_result("Ping 測試", False, "無法 ping 通伺服器")
    except Exception as e:
        print_result("Ping 測試", False, f"錯誤: {e}")
    
    # 2. 端口掃描
    print("\n[1.2] 端口掃描...")
    for port in SERVER_PORTS:
        is_open = test_connection(SERVER_IP, port, timeout=3)
        results["ports"][port] = is_open
        port_name = {
            22: "SSH",
            8069: "Odoo",
            8080: "AI/Web",
            8766: "Cloud Sync",
            3001: "Status Dashboard"
        }.get(port, f"Port {port}")
        print_result(f"{port_name} ({port})", is_open)
    
    # 3. SSH 連線測試
    print("\n[1.3] SSH 連線測試...")
    if results["ports"].get(22, False):
        results["ssh_available"] = True
        print("    嘗試 SSH 認證...")
        
        # 嘗試使用 paramiko
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 嘗試常見用戶名（需要密碼或密鑰）
            for user in POSSIBLE_USERS:
                try:
                    # 先嘗試使用密鑰
                    ssh_key_path = Path.home() / ".ssh" / "id_rsa"
                    if ssh_key_path.exists():
                        try:
                            client.connect(
                                SERVER_IP,
                                username=user,
                                key_filename=str(ssh_key_path),
                                timeout=5
                            )
                            print_result(f"SSH 認證 ({user})", True, "使用 SSH 密鑰")
                            results["ssh_user"] = user
                            results["ssh_authenticated"] = True
                            
                            # 測試執行命令
                            stdin, stdout, stderr = client.exec_command("hostname; pwd; ls -la /home 2>/dev/null | head -5")
                            output = stdout.read().decode()
                            print(f"    伺服器信息:")
                            for line in output.strip().split("\n")[:5]:
                                if line.strip():
                                    print(f"      {line}")
                            
                            client.close()
                            return results
                        except paramiko.AuthenticationException:
                            pass
                        except Exception as e:
                            pass
                except Exception:
                    pass
        except ImportError:
            print("    [INFO] paramiko 未安裝，跳過 SSH 認證測試")
            print("    安裝: pip install paramiko")
    
    return results

def get_file_hash(file_path: Path) -> str:
    """計算檔案雜湊值"""
    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest().upper()
    except Exception as e:
        print(f"    [ERROR] 計算雜湊失敗 {file_path}: {e}")
        return ""

def scan_local_files(base_path: Path, patterns: List[str] = None) -> Dict[str, dict]:
    """掃描本地檔案"""
    if patterns is None:
        patterns = ["**/*"]
    
    files = {}
    exclude_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "USB_DRIVE", "backups"}
    
    print(f"\n[*] 掃描本地檔案: {base_path}")
    
    for pattern in patterns:
        for file_path in base_path.rglob(pattern):
            # 跳過目錄和排除的目錄
            if not file_path.is_file():
                continue
            
            # 檢查是否在排除目錄中
            if any(exclude in file_path.parts for exclude in exclude_dirs):
                continue
            
            try:
                rel_path = file_path.relative_to(base_path)
                rel_path_str = str(rel_path).replace("\\", "/")
                
                stat = file_path.stat()
                files[rel_path_str] = {
                    "path": rel_path_str,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "hash": get_file_hash(file_path)
                }
            except Exception as e:
                print(f"    [WARN] 跳過檔案 {file_path}: {e}")
    
    print(f"    [OK] 找到 {len(files)} 個檔案")
    return files

def scan_remote_files(ssh_client: paramiko.SSHClient, remote_path: str, sync_dirs: List[str]) -> Dict[str, dict]:
    """掃描遠端檔案"""
    files = {}
    
    print(f"\n[*] 掃描遠端檔案: {remote_path}")
    
    for sync_dir in sync_dirs:
        remote_dir = f"{remote_path}/{sync_dir}"
        print(f"    掃描: {remote_dir}...")
        
        try:
            # 列出檔案
            stdin, stdout, stderr = ssh_client.exec_command(
                f"find '{remote_dir}' -type f 2>/dev/null | head -1000"
            )
            output = stdout.read().decode()
            errors = stderr.read().decode()
            
            if errors and "No such file" not in errors:
                print(f"    [WARN] {errors[:100]}")
            
            for line in output.strip().split("\n"):
                if not line.strip():
                    continue
                
                remote_file = line.strip()
                rel_path = remote_file.replace(remote_path + "/", "")
                
                try:
                    # 獲取檔案信息
                    stdin, stdout, stderr = ssh_client.exec_command(
                        f"stat -c '%s %Y' '{remote_file}' 2>/dev/null && sha256sum '{remote_file}' 2>/dev/null | cut -d' ' -f1"
                    )
                    info = stdout.read().decode().strip().split("\n")
                    
                    if len(info) >= 2:
                        size, mtime = info[0].split()
                        file_hash = info[1].upper()
                        
                        files[rel_path] = {
                            "path": rel_path,
                            "size": int(size),
                            "mtime": float(mtime),
                            "hash": file_hash
                        }
                except Exception as e:
                    print(f"    [WARN] 無法獲取檔案信息 {remote_file}: {e}")
        
        except Exception as e:
            print(f"    [ERROR] 掃描目錄失敗 {remote_dir}: {e}")
    
    print(f"    [OK] 找到 {len(files)} 個遠端檔案")
    return files

def compare_files(local_files: Dict[str, dict], remote_files: Dict[str, dict]) -> Dict[str, List[dict]]:
    """比對檔案"""
    print_section("步驟 3: 檔案比對")
    
    comparison = {
        "identical": [],
        "different": [],
        "local_only": [],
        "remote_only": []
    }
    
    # 比對雙方都有的檔案
    common_files = set(local_files.keys()) & set(remote_files.keys())
    for file_path in common_files:
        local_info = local_files[file_path]
        remote_info = remote_files[file_path]
        
        if local_info["hash"] == remote_info["hash"]:
            comparison["identical"].append({
                "path": file_path,
                "size": local_info["size"],
                "mtime_local": local_info["mtime"],
                "mtime_remote": remote_info["mtime"]
            })
        else:
            comparison["different"].append({
                "path": file_path,
                "size_local": local_info["size"],
                "size_remote": remote_info["size"],
                "hash_local": local_info["hash"][:16],
                "hash_remote": remote_info["hash"][:16],
                "mtime_local": local_info["mtime"],
                "mtime_remote": remote_info["mtime"]
            })
    
    # 僅本地有的檔案
    local_only = set(local_files.keys()) - set(remote_files.keys())
    for file_path in local_only:
        comparison["local_only"].append({
            "path": file_path,
            "size": local_files[file_path]["size"],
            "mtime": local_files[file_path]["mtime"]
        })
    
    # 僅遠端有的檔案
    remote_only = set(remote_files.keys()) - set(local_files.keys())
    for file_path in remote_only:
        comparison["remote_only"].append({
            "path": file_path,
            "size": remote_files[file_path]["size"],
            "mtime": remote_files[file_path]["mtime"]
        })
    
    return comparison

def generate_report(connection_results: dict, comparison: dict):
    """生成報告"""
    print_section("比對報告")
    
    print("\n連線環境驗證:")
    print(f"  Ping: {'通過' if connection_results['ping'] else '失敗'}")
    print(f"  SSH 可用: {'是' if connection_results['ssh_available'] else '否'}")
    print(f"  SSH 認證: {'成功' if connection_results['ssh_authenticated'] else '失敗'}")
    if connection_results.get('ssh_user'):
        print(f"  SSH 用戶: {connection_results['ssh_user']}")
    
    print("\n檔案比對結果:")
    print(f"  相同檔案: {len(comparison['identical'])}")
    print(f"  不同檔案: {len(comparison['different'])}")
    print(f"  僅本地有: {len(comparison['local_only'])}")
    print(f"  僅遠端有: {len(comparison['remote_only'])}")
    
    total = len(comparison['identical']) + len(comparison['different']) + len(comparison['local_only']) + len(comparison['remote_only'])
    print(f"  總計: {total}")
    
    # 保存報告
    report_file = LOCAL_PATH / "file_comparison_report.json"
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "server_ip": SERVER_IP,
        "connection": connection_results,
        "comparison": comparison
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] 報告已保存: {report_file}")
    
    # 顯示不同檔案的詳細信息
    if comparison['different']:
        print("\n不同檔案列表 (前10個):")
        for item in comparison['different'][:10]:
            print(f"  {item['path']}")
            print(f"    本地: {item['size_local']} bytes, Hash: {item['hash_local']}")
            print(f"    遠端: {item['size_remote']} bytes, Hash: {item['hash_remote']}")

def main():
    """主函數"""
    print("=" * 80)
    print("  伺服器連線環境驗證與檔案比對工具")
    print(f"  伺服器: {SERVER_IP}")
    print(f"  本地路徑: {LOCAL_PATH}")
    print("=" * 80)
    
    # 步驟 1: 驗證連線環境
    connection_results = verify_server_connection()
    
    if not connection_results["ssh_authenticated"]:
        print("\n[WARN] SSH 認證失敗，無法進行檔案比對")
        print("建議:")
        print("  1. 確認 SSH 用戶名和密碼")
        print("  2. 部署 SSH 密鑰: python deploy_ssh_key.py")
        print("  3. 或使用: .\\setup_ssh_auto.ps1")
        return
    
    # 步驟 2: 掃描檔案
    print_section("步驟 2: 掃描檔案")
    
    # 建立 SSH 連線
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh_key_path = Path.home() / ".ssh" / "id_rsa"
        if ssh_key_path.exists():
            ssh_client.connect(
                SERVER_IP,
                username=connection_results["ssh_user"],
                key_filename=str(ssh_key_path),
                timeout=10
            )
        else:
            print("[ERROR] 找不到 SSH 密鑰")
            return
        
        # 掃描本地檔案
        local_files = scan_local_files(LOCAL_PATH)
        
        # 掃描遠端檔案
        remote_files = scan_remote_files(ssh_client, REMOTE_PATH, SYNC_DIRS)
        
        # 步驟 3: 比對檔案
        comparison = compare_files(local_files, remote_files)
        
        # 步驟 4: 生成報告
        generate_report(connection_results, comparison)
        
    except Exception as e:
        print(f"\n[ERROR] 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh_client.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
