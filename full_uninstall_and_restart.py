#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
full_uninstall_and_restart.py

完整卸載並重啟

功能：
- 停止所有服務
- 清理臨時檔案和快取
- 卸載網路連接
- 重啟所有服務
"""

import sys
import os
import subprocess
import time
import requests
import socket
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONTROL_CENTER_URL = "http://127.0.0.1:8788"
HUB_URL = "http://127.0.0.1:8799"


def find_process_by_port(port: int):
    """根據端口找到進程"""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        for line in result.stdout.split('\n'):
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    return pid
    except:
        pass
    return None


def stop_service_by_port(port: int, service_name: str):
    """根據端口停止服務"""
    print(f"  停止 {service_name} (端口 {port})...")
    
    pid = find_process_by_port(port)
    if pid:
        try:
            subprocess.run(
                ["taskkill", "/F", "/PID", pid],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"    ✓ 已停止進程 {pid}")
            time.sleep(1)
            return True
        except Exception as e:
            print(f"    ✗ 停止失敗: {e}")
            return False
    else:
        print(f"    ○ 未找到運行中的服務")
        return True


def stop_all_services():
    """停止所有服務"""
    print("【步驟 1：停止所有服務】")
    
    services = [
        (8788, "控制中心"),
        (8799, "Little J Hub"),
    ]
    
    stopped = []
    for port, name in services:
        if stop_service_by_port(port, name):
            stopped.append(name)
    
    # 等待服務完全停止
    time.sleep(2)
    
    print()
    return stopped


def cleanup_temp_files():
    """清理臨時檔案"""
    print("【步驟 2：清理臨時檔案】")
    
    cleanup_dirs = [
        BASE_DIR / "dev" / "temp",
        BASE_DIR / "dev" / "cache",
        BASE_DIR / "__pycache__",
    ]
    
    cleanup_patterns = [
        "*.pyc",
        "*.pyo",
        "*.tmp",
        "*.log",
    ]
    
    cleaned = 0
    
    # 清理目錄
    for dir_path in cleanup_dirs:
        if dir_path.exists():
            try:
                for item in dir_path.iterdir():
                    if item.is_file():
                        item.unlink()
                        cleaned += 1
                    elif item.is_dir():
                        import shutil
                        shutil.rmtree(item)
                        cleaned += 1
                print(f"  ✓ 已清理: {dir_path}")
            except Exception as e:
                print(f"  ⚠️  清理失敗 {dir_path}: {e}")
    
    # 清理根目錄的臨時檔案
    for pattern in cleanup_patterns:
        for file_path in BASE_DIR.glob(pattern):
            try:
                file_path.unlink()
                cleaned += 1
            except:
                pass
    
    print(f"  已清理 {cleaned} 個項目")
    print()


def disconnect_network_drives():
    """斷開網路磁碟機"""
    print("【步驟 3：斷開網路磁碟機】")
    
    try:
        result = subprocess.run(
            ["net", "use"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # 查找 Z: 磁碟機
        if "Z:" in result.stdout:
            print("  斷開 Z: 磁碟機...")
            subprocess.run(
                ["net", "use", "Z:", "/delete", "/yes"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print("    ✓ Z: 磁碟機已斷開")
        else:
            print("    ○ 未找到 Z: 磁碟機")
    except Exception as e:
        print(f"    ⚠️  斷開失敗: {e}")
    
    print()


def clear_environment_cache():
    """清理環境快取"""
    print("【步驟 4：清理環境快取】")
    
    # 清理 Python 快取
    import py_compile
    try:
        for pycache in BASE_DIR.rglob("__pycache__"):
            import shutil
            shutil.rmtree(pycache)
            print(f"  ✓ 已清理: {pycache}")
    except Exception as e:
        print(f"  ⚠️  清理快取失敗: {e}")
    
    print()


def restart_services():
    """重啟服務"""
    print("【步驟 5：重啟服務】")
    
    services = [
        {
            "name": "控制中心",
            "script": "local_control_center.py",
            "port": 8788,
            "url": CONTROL_CENTER_URL
        },
        {
            "name": "Little J Hub",
            "script": "little_j_hub_server.py",
            "port": 8799,
            "url": HUB_URL
        }
    ]
    
    restarted = []
    
    for service in services:
        print(f"  啟動 {service['name']}...")
        
        try:
            # 檢查是否已在運行
            try:
                response = requests.get(f"{service['url']}/api/local/health", timeout=1)
                if response.status_code == 200:
                    print(f"    ✓ {service['name']} 已在運行")
                    restarted.append(service['name'])
                    continue
            except:
                pass
            
            # 啟動服務
            process = subprocess.Popen(
                [sys.executable, service['script']],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服務啟動
            for i in range(10):
                time.sleep(1)
                try:
                    response = requests.get(f"{service['url']}/api/local/health", timeout=1)
                    if response.status_code == 200:
                        print(f"    ✓ {service['name']} 已啟動")
                        restarted.append(service['name'])
                        break
                except:
                    continue
            else:
                print(f"    ⚠️  {service['name']} 啟動中，請稍候...")
                restarted.append(service['name'])
                
        except Exception as e:
            print(f"    ✗ 啟動失敗: {e}")
            print(f"    請手動啟動: python {service['script']}")
    
    print()
    return restarted


def verify_services():
    """驗證服務狀態"""
    print("【步驟 6：驗證服務狀態】")
    
    services = [
        ("控制中心", CONTROL_CENTER_URL),
        ("Little J Hub", HUB_URL),
    ]
    
    all_ok = True
    for name, url in services:
        try:
            response = requests.get(f"{url}/api/local/health", timeout=2)
            if response.status_code == 200:
                print(f"  ✓ {name}: 運行中")
            else:
                print(f"  ⚠️  {name}: 回應異常 ({response.status_code})")
                all_ok = False
        except:
            print(f"  ✗ {name}: 無回應")
            all_ok = False
    
    print()
    return all_ok


def main():
    """主函數"""
    print("=" * 70)
    print("完整卸載並重啟")
    print("=" * 70)
    print()
    
    # 步驟 1：停止所有服務
    stopped = stop_all_services()
    
    # 步驟 2：清理臨時檔案
    cleanup_temp_files()
    
    # 步驟 3：斷開網路磁碟機
    disconnect_network_drives()
    
    # 步驟 4：清理環境快取
    clear_environment_cache()
    
    # 步驟 5：重啟服務
    restarted = restart_services()
    
    # 等待服務完全啟動
    time.sleep(3)
    
    # 步驟 6：驗證服務狀態
    all_ok = verify_services()
    
    print("=" * 70)
    print("【執行摘要】")
    print("=" * 70)
    
    print(f"已停止服務: {len(stopped)} 個")
    print(f"已重啟服務: {len(restarted)} 個")
    print(f"服務狀態: {'✓ 全部正常' if all_ok else '⚠️  部分異常'}")
    
    print()
    print("=" * 70)
    
    # 生成報告
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "stopped_services": stopped,
        "restarted_services": restarted,
        "all_services_ok": all_ok
    }
    
    report_file = BASE_DIR / "uninstall_restart_report.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"執行報告已儲存到: {report_file}")


if __name__ == "__main__":
    import json
    main()
