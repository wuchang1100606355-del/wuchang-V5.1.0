#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_control_center_conflict.py

修復控制中心衝突

功能：
- 終止所有控制中心進程
- 等待端口釋放
- 重新啟動單一實例
"""

import sys
import subprocess
import time
import socket
import psutil
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
PORT = 8788


def find_control_center_processes():
    """找到所有控制中心進程"""
    processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    if 'local_control_center.py' in cmdline_str:
                        processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"  ⚠️  無法檢查進程: {e}")
    
    return processes


def terminate_processes(processes):
    """終止進程"""
    print("【終止重複進程】")
    print()
    
    if not processes:
        print("  ✓ 未找到需要終止的進程")
        return True
    
    print(f"  找到 {len(processes)} 個控制中心進程")
    
    terminated = []
    failed = []
    
    for proc in processes:
        try:
            pid = proc.pid
            print(f"  正在終止 PID {pid}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
                terminated.append(pid)
                print(f"    ✓ PID {pid} 已終止")
            except psutil.TimeoutExpired:
                print(f"    ⚠️  PID {pid} 未響應，強制終止...")
                proc.kill()
                terminated.append(pid)
                print(f"    ✓ PID {pid} 已強制終止")
        except psutil.NoSuchProcess:
            print(f"    ✓ PID {proc.pid} 已不存在")
            terminated.append(proc.pid)
        except psutil.AccessDenied:
            print(f"    ✗ PID {proc.pid} 無權限終止")
            failed.append(proc.pid)
        except Exception as e:
            print(f"    ✗ PID {proc.pid} 終止失敗: {e}")
            failed.append(proc.pid)
    
    print()
    if terminated:
        print(f"  ✓ 已終止 {len(terminated)} 個進程")
    if failed:
        print(f"  ✗ {len(failed)} 個進程終止失敗（可能需要管理員權限）")
    
    return len(failed) == 0


def wait_for_port_release(port: int, max_wait: int = 10):
    """等待端口釋放"""
    print()
    print("【等待端口釋放】")
    print()
    
    for i in range(max_wait):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result != 0:
                print(f"  ✓ 端口 {port} 已釋放（等待 {i+1} 秒）")
                return True
        except:
            pass
        
        time.sleep(1)
        if i % 2 == 0 and i > 0:
            print(f"    等待中... ({i}/{max_wait} 秒)")
    
    print(f"  ⚠️  端口 {port} 可能仍在使用中")
    return False


def start_control_center():
    """啟動控制中心"""
    print()
    print("【啟動控制中心】")
    print()
    
    control_center_script = BASE_DIR / "local_control_center.py"
    
    if not control_center_script.exists():
        print(f"  ✗ 找不到控制中心腳本: {control_center_script}")
        return False
    
    try:
        # 在背景啟動
        subprocess.Popen(
            [sys.executable, str(control_center_script), "--port", str(PORT)],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        
        print(f"  ✓ 已啟動控制中心（背景執行）")
        print("  等待服務啟動...")
        
        # 等待服務啟動（最多 15 秒）
        for i in range(15):
            time.sleep(1)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', PORT))
                sock.close()
                
                if result == 0:
                    # 測試 HTTP 連接
                    import requests
                    try:
                        response = requests.get(f"http://127.0.0.1:{PORT}/", timeout=2)
                        if response.status_code == 200:
                            print(f"  ✓ 控制中心已啟動並響應（等待 {i+1} 秒）")
                            return True
                    except:
                        pass
            except:
                pass
            
            if i % 3 == 0 and i > 0:
                print(f"    等待中... ({i}/15 秒)")
        
        print("  ⚠️  等待超時，請手動檢查控制中心狀態")
        return False
        
    except Exception as e:
        print(f"  ✗ 啟動失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("修復控制中心衝突")
    print("=" * 70)
    print()
    
    # 步驟 1: 找到所有進程
    print("【步驟 1：檢查進程】")
    print()
    processes = find_control_center_processes()
    
    if len(processes) <= 1:
        print("  ✓ 未發現進程衝突")
        print()
        print("控制中心可能正常運行，或未啟動")
        print("如果需要重新啟動，請手動執行：")
        print("  python local_control_center.py")
        return 0
    
    # 步驟 2: 終止重複進程
    if not terminate_processes(processes):
        print()
        print("⚠️  部分進程終止失敗，可能需要管理員權限")
        print("請手動在任務管理器中終止 Python 進程")
        return 1
    
    # 步驟 3: 等待端口釋放
    wait_for_port_release(PORT)
    
    # 步驟 4: 重新啟動
    if start_control_center():
        print()
        print("=" * 70)
        print("【完成】")
        print("=" * 70)
        print()
        print("✓ 控制中心已重新啟動")
        print()
        print("現在可以使用：")
        print("  - python diagnose_control_center.py（檢查狀態）")
        print("  - python grant_little_j_full_agent_for_credentials.py（授予權限）")
        print()
        return 0
    else:
        print()
        print("=" * 70)
        print("【需要手動操作】")
        print("=" * 70)
        print()
        print("請手動啟動控制中心：")
        print("  python local_control_center.py")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
