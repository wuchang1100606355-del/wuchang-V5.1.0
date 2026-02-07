#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
request_server_push_and_restart.py

要求伺服器推送所有變更並重啟容器

功能：
- 向伺服器發送推送請求
- 要求伺服器推送所有變更到本地
- 重啟容器/服務
"""

import sys
import json
import requests
import time
from pathlib import Path

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONTROL_CENTER_URL = "http://127.0.0.1:8788"

import os
HUB_URL = os.getenv("WUCHANG_HUB_URL", "http://127.0.0.1:8799")


def check_control_center():
    """檢查控制中心是否運行"""
    try:
        endpoints = ["/api/local/health", "/health", "/"]
        for endpoint in endpoints:
            try:
                response = requests.get(f"{CONTROL_CENTER_URL}{endpoint}", timeout=2)
                if response.status_code in [200, 404]:
                    return True
            except:
                continue
        return False
    except:
        return False


def start_control_center():
    """啟動控制中心"""
    import subprocess
    try:
        print("  正在啟動控制中心...")
        process = subprocess.Popen(
            [sys.executable, "local_control_center.py"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # 等待服務啟動
        for i in range(10):
            time.sleep(1)
            if check_control_center():
                print("  ✓ 控制中心已啟動")
                return True
        print("  ⚠️  控制中心啟動中，請稍候...")
        return True
    except Exception as e:
        print(f"  ✗ 啟動失敗: {e}")
        return False


def request_server_push(profile: str = "all"):
    """要求伺服器推送變更（Server -> Local）"""
    print("【步驟 1：要求伺服器推送變更】")
    
    if not check_control_center():
        print("  ✗ 控制中心未運行")
        return False
    
    # 透過控制中心 API 建立反向推送任務
    try:
        print(f"  透過控制中心 API 建立反向推送任務...")
        
        # 建立推送命令單（要求伺服器推送到本地）
        job_data = {
            "type": "sync_push",
            "profile": profile if profile != "all" else "rules",
            "actor": "system",
            "direction": "server_to_local",  # 反向推送
            "params": {
                "profile": profile if profile != "all" else "rules",
                "direction": "server_to_local",
                "note": "要求伺服器推送所有變更到本地"
            }
        }
        
        response = requests.post(
            f"{CONTROL_CENTER_URL}/api/jobs/create",
            json=job_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("  ✓ 反向推送任務已建立")
                job = result.get("job", {})
                job_id = job.get("id") or result.get("job_id")
                if job_id:
                    print(f"  任務 ID: {job_id}")
                job_path = result.get("job_path")
                if job_path:
                    print(f"  任務位置: {job_path}")
                return True
            else:
                print(f"  ✗ 任務建立失敗: {result.get('error', '未知錯誤')}")
        else:
            print(f"  ✗ API 回應錯誤: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"  錯誤詳情: {error_detail}")
            except:
                print(f"  回應內容: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("  ✗ 無法連接到控制中心")
    except Exception as e:
        print(f"  ✗ 請求失敗: {e}")
    
    return False


def request_server_push_all_profiles():
    """要求伺服器推送所有配置檔案的變更"""
    print("【要求伺服器推送所有變更】")
    print()
    
    profiles = ["kb", "rules"]
    results = {}
    
    for profile in profiles:
        print(f"推送 {profile} profile...")
        success = request_server_push(profile)
        results[profile] = success
        if success:
            print(f"  ✓ {profile} 推送請求已發送")
        else:
            print(f"  ✗ {profile} 推送請求失敗")
        print()
        time.sleep(1)  # 避免請求過快
    
    return results


def restart_containers():
    """重啟容器/服務"""
    print("【步驟 2：重啟容器/服務】")
    
    services_to_restart = [
        {
            "name": "控制中心",
            "script": "local_control_center.py",
            "port": 8788
        },
        {
            "name": "Little J Hub",
            "script": "little_j_hub_server.py",
            "port": 8799
        }
    ]
    
    restarted = []
    
    for service in services_to_restart:
        print(f"  重啟 {service['name']}...")
        
        # 檢查服務是否運行
        try:
            response = requests.get(f"http://127.0.0.1:{service['port']}/api/local/health", timeout=1)
            if response.status_code == 200:
                print(f"    {service['name']} 正在運行")
                
                # 發送重啟請求（如果 API 支援）
                try:
                    restart_response = requests.post(
                        f"http://127.0.0.1:{service['port']}/api/system/restart",
                        timeout=5
                    )
                    if restart_response.status_code == 200:
                        print(f"    ✓ {service['name']} 重啟請求已發送")
                        restarted.append(service['name'])
                        continue
                except:
                    pass
                
                # 如果沒有重啟 API，提示手動重啟
                print(f"    ⚠️  請手動重啟 {service['name']}")
                print(f"    停止: 在運行該服務的終端機按 Ctrl+C")
                print(f"    啟動: python {service['script']}")
            else:
                print(f"    {service['name']} 未運行，需要啟動")
                print(f"    啟動: python {service['script']}")
        except:
            print(f"    {service['name']} 未運行，需要啟動")
            print(f"    啟動: python {service['script']}")
    
    print()
    return restarted


def main():
    """主函數"""
    print("=" * 70)
    print("要求伺服器推送所有變更並重啟容器")
    print("=" * 70)
    print()
    
    # 步驟 0：確保控制中心運行
    if not check_control_center():
        print("【步驟 0：啟動控制中心】")
        if not start_control_center():
            print("  ✗ 無法啟動控制中心")
            print("  請手動啟動: python local_control_center.py")
            return
        print()
        time.sleep(3)  # 等待服務完全啟動
    
    # 步驟 1：要求伺服器推送
    push_results = request_server_push_all_profiles()
    
    print()
    
    # 步驟 2：重啟容器
    restarted = restart_containers()
    
    print()
    print("=" * 70)
    print("【執行摘要】")
    print("=" * 70)
    
    print("推送請求結果：")
    for profile, success in push_results.items():
        status = "✓ 已發送" if success else "✗ 失敗"
        print(f"  {profile}: {status}")
    
    print()
    print("容器重啟狀態：")
    if restarted:
        print(f"  ✓ 已重啟: {', '.join(restarted)}")
    else:
        print("  ⚠️  需要手動重啟服務")
    
    print()
    print("=" * 70)
    
    # 生成報告
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "push_requests": push_results,
        "restarted_services": restarted
    }
    
    report_file = BASE_DIR / "server_push_restart_report.json"
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"執行報告已儲存到: {report_file}")


if __name__ == "__main__":
    import os
    main()
