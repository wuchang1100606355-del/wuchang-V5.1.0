#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnose_control_center.py

診斷控制中心狀態

功能：
- 檢查端口狀態
- 檢查進程狀態
- 測試 API 連接
- 提供修復建議
"""

import sys
import subprocess
import socket
import requests
import psutil
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

CONTROL_CENTER_URL = "http://127.0.0.1:8788"
PORT = 8788


def check_port_listening(port: int):
    """檢查端口是否在監聽"""
    print("【檢查端口狀態】")
    print()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"  ✓ 端口 {port} 正在監聽")
            return True
        else:
            print(f"  ✗ 端口 {port} 未監聽")
            return False
    except Exception as e:
        print(f"  ✗ 檢查端口時發生錯誤: {e}")
        return False


def check_processes():
    """檢查相關進程"""
    print()
    print("【檢查進程狀態】")
    print()
    
    control_center_processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    if 'local_control_center.py' in cmdline_str:
                        control_center_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline_str[:100]
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"  ⚠️  無法檢查進程: {e}")
        print("  請手動檢查任務管理器")
        return []
    
    if control_center_processes:
        print(f"  找到 {len(control_center_processes)} 個控制中心進程：")
        for proc in control_center_processes:
            print(f"    PID: {proc['pid']}, 命令: {proc['cmdline']}")
    else:
        print("  ✗ 未找到控制中心進程")
    
    return control_center_processes


def test_api_connection():
    """測試 API 連接"""
    print()
    print("【測試 API 連接】")
    print()
    
    endpoints = [
        "/api/local/health",
        "/health",
        "/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{CONTROL_CENTER_URL}{endpoint}",
                timeout=3
            )
            print(f"  ✓ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    回應: {json.dumps(data, ensure_ascii=False)[:100]}")
                except:
                    print(f"    回應長度: {len(response.text)} 字元")
                return True
        except requests.exceptions.ConnectionError:
            print(f"  ✗ {endpoint}: 連接被拒絕")
        except requests.exceptions.Timeout:
            print(f"  ✗ {endpoint}: 連接超時")
        except Exception as e:
            print(f"  ✗ {endpoint}: {type(e).__name__}: {e}")
    
    return False


def check_port_conflict():
    """檢查端口衝突"""
    print()
    print("【檢查端口衝突】")
    print()
    
    try:
        # 使用 netstat 檢查
        result = subprocess.run(
            ["netstat", "-an"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        lines = result.stdout.splitlines()
        port_lines = [line for line in lines if f":{PORT}" in line]
        
        if port_lines:
            print(f"  找到 {len(port_lines)} 個相關連接：")
            for line in port_lines[:10]:  # 只顯示前 10 個
                print(f"    {line}")
            
            # 檢查是否有重複的 LISTENING
            listening_count = sum(1 for line in port_lines if "LISTENING" in line)
            if listening_count > 1:
                print()
                print(f"  ⚠️  警告：發現 {listening_count} 個 LISTENING 狀態")
                print("  這可能表示有端口衝突或多個進程在監聽")
        else:
            print("  ✓ 未發現端口衝突")
    except Exception as e:
        print(f"  ⚠️  無法檢查端口衝突: {e}")


def provide_solutions(port_listening: bool, processes: list, api_working: bool):
    """提供解決方案"""
    print()
    print("=" * 70)
    print("【診斷結果與建議】")
    print("=" * 70)
    print()
    
    if api_working:
        print("✓ 控制中心運行正常")
        print()
        return
    
    if port_listening and not api_working:
        print("⚠️  端口正在監聽，但 API 無法連接")
        print()
        print("可能原因：")
        print("  1. 服務器啟動不完整")
        print("  2. 服務器崩潰但端口未釋放")
        print("  3. 多個進程衝突")
        print()
        print("解決方案：")
        print("  1. 終止所有控制中心進程：")
        if processes:
            for proc in processes:
                print(f"     taskkill /F /PID {proc['pid']}")
        else:
            print("     請在任務管理器中手動終止 Python 進程")
        print()
        print("  2. 等待幾秒讓端口釋放")
        print()
        print("  3. 重新啟動控制中心：")
        print("     python local_control_center.py")
        print()
        return
    
    if not port_listening:
        print("✗ 控制中心未運行")
        print()
        print("解決方案：")
        print("  1. 啟動控制中心：")
        print("     python local_control_center.py")
        print()
        print("  2. 或使用啟動腳本：")
        print("     start_servers.bat")
        print()


def main():
    """主函數"""
    import json
    
    print("=" * 70)
    print("控制中心診斷工具")
    print("=" * 70)
    print()
    print(f"目標 URL: {CONTROL_CENTER_URL}")
    print(f"端口: {PORT}")
    print()
    
    # 檢查端口
    port_listening = check_port_listening(PORT)
    
    # 檢查進程
    processes = check_processes()
    
    # 檢查端口衝突
    check_port_conflict()
    
    # 測試 API
    api_working = test_api_connection()
    
    # 提供解決方案
    provide_solutions(port_listening, processes, api_working)
    
    print("=" * 70)


if __name__ == "__main__":
    try:
        import json
    except:
        pass
    main()
