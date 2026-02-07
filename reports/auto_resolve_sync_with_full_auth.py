#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_resolve_sync_with_full_auth.py

全自動執行兩機同步事件解決方案

功能：
- 自動處理路由器證書
- 自動設定網路互通
- 自動獲取完整權限（full_agent）
- 自動執行兩機同步
- 自動解決所有相關問題
"""

import sys
import json
import os
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONTROL_CENTER_URL = "http://127.0.0.1:8788"


def print_step(step_num: int, title: str):
    """列印步驟標題"""
    print()
    print("=" * 70)
    print(f"【步驟 {step_num}】{title}")
    print("=" * 70)
    print()


def check_control_center() -> bool:
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


def start_control_center() -> bool:
    """啟動控制中心"""
    try:
        print("正在啟動控制中心...")
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
                print("✓ 控制中心已啟動")
                return True
        print("⚠️  控制中心啟動中，請稍候...")
        return True
    except Exception as e:
        print(f"✗ 啟動失敗: {e}")
        return False


def find_cert_tar() -> Optional[Path]:
    """尋找證書 TAR 檔案"""
    patterns = [
        "cert_key (2).tar",
        "cert_key (1).tar",
        "cert_key*.tar",
        "*cert*.tar"
    ]
    
    for pattern in patterns:
        files = list(BASE_DIR.glob(pattern))
        if files:
            return files[0]
    
    # 檢查下載資料夾
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        for pattern in patterns:
            files = list(downloads.glob(pattern))
            if files:
                return files[0]
    
    return None


def setup_router_cert_auto(cert_file: Path) -> bool:
    """自動設定路由器證書"""
    try:
        print(f"處理證書檔案: {cert_file.name}")
        result = subprocess.run(
            [sys.executable, "setup_router_cert.py", str(cert_file)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )
        
        if result.returncode == 0:
            print("✓ 路由器證書設定完成")
            return True
        else:
            print(f"⚠️  證書設定警告: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"✗ 證書設定失敗: {e}")
        return False


def setup_network_interconnection_auto() -> bool:
    """自動設定網路互通"""
    try:
        print("設定網路互通...")
        result = subprocess.run(
            [sys.executable, "setup_network_interconnection.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )
        
        if result.returncode == 0:
            print("✓ 網路互通設定完成")
            return True
        else:
            print(f"⚠️  網路設定警告: {result.stderr[:200]}")
            return True  # 即使有警告也繼續
    except Exception as e:
        print(f"⚠️  網路設定錯誤: {e}")
        return True  # 繼續執行


def auto_authorize_full_agent() -> Optional[Dict[str, Any]]:
    """自動獲取 full_agent 權限"""
    try:
        # 檢查配置檔案
        auth_config_file = BASE_DIR / "auto_auth_config.json"
        if not auth_config_file.exists():
            print("⚠️  未找到授權配置檔案，跳過自動授權")
            print("   提示：建立 auto_auth_config.json 以啟用自動授權")
            return None
        
        config = json.loads(auth_config_file.read_text(encoding="utf-8"))
        account_id = config.get("account_id", "").strip()
        pin = config.get("pin", "").strip()
        
        if not account_id or not pin:
            print("⚠️  授權配置不完整，跳過自動授權")
            return None
        
        print("正在自動授權...")
        result = subprocess.run(
            [sys.executable, "auto_authorize_and_execute.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120
        )
        
        if result.returncode == 0:
            print("✓ 自動授權完成")
            return {"success": True}
        else:
            print(f"⚠️  授權警告: {result.stderr[:200]}")
            return {"success": False, "warning": result.stderr[:200]}
    except Exception as e:
        print(f"⚠️  授權錯誤: {e}")
        return None


def execute_sync_all_profiles() -> bool:
    """執行所有配置檔案的同步"""
    try:
        print("執行檔案同步...")
        result = subprocess.run(
            [sys.executable, "sync_all_profiles.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        
        if result.returncode == 0:
            print("✓ 檔案同步完成")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print(f"⚠️  同步警告: {result.stderr[:200]}")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            return False
    except Exception as e:
        print(f"✗ 同步失敗: {e}")
        return False


def verify_connection() -> Dict[str, Any]:
    """驗證連接狀態"""
    try:
        result = subprocess.run(
            [sys.executable, "check_connection_status.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """主函數 - 全自動執行"""
    print("=" * 70)
    print("全自動兩機同步事件解決方案")
    print("授予完整權限並執行同步")
    print("=" * 70)
    print(f"開始時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "steps": {}
    }
    
    # 步驟 1: 檢查/啟動控制中心
    print_step(1, "檢查控制中心狀態")
    if not check_control_center():
        print("控制中心未運行，正在啟動...")
        if not start_control_center():
            print("⚠️  無法啟動控制中心，將繼續執行其他步驟")
        else:
            time.sleep(3)  # 等待服務完全啟動
    else:
        print("✓ 控制中心運行中")
    results["steps"]["control_center"] = {"status": "ready"}
    
    # 步驟 2: 修復網路磁碟機連接
    print_step(2, "修復網路磁碟機連接")
    try:
        fix_result = subprocess.run(
            [sys.executable, "fix_network_drive.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )
        if fix_result.returncode == 0:
            print("✓ 網路磁碟機連接已修復")
            results["steps"]["network_drive"] = {"status": "completed"}
        else:
            print("⚠️  網路磁碟機修復有警告")
            results["steps"]["network_drive"] = {"status": "warning"}
    except Exception as e:
        print(f"⚠️  網路磁碟機修復錯誤: {e}")
        results["steps"]["network_drive"] = {"status": "skipped"}
    
    # 步驟 3: 處理路由器證書
    print_step(3, "處理路由器證書")
    cert_file = find_cert_tar()
    if cert_file:
        print(f"找到證書檔案: {cert_file}")
        cert_success = setup_router_cert_auto(cert_file)
        results["steps"]["router_cert"] = {
            "status": "completed" if cert_success else "warning",
            "file": str(cert_file)
        }
    else:
        print("⚠️  未找到證書檔案，跳過證書設定")
        print("   提示：將 cert_key (2).tar 放置在專案目錄")
        results["steps"]["router_cert"] = {"status": "skipped"}
    
    # 步驟 4: 設定網路互通
    print_step(4, "設定網路互通")
    network_success = setup_network_interconnection_auto()
    results["steps"]["network_setup"] = {
        "status": "completed" if network_success else "warning"
    }
    
    # 讀取網路配置並設定環境變數
    network_config_file = BASE_DIR / "network_interconnection_config.json"
    if network_config_file.exists():
        try:
            network_config = json.loads(network_config_file.read_text(encoding="utf-8"))
            if network_config.get("health_url"):
                os.environ["WUCHANG_HEALTH_URL"] = network_config["health_url"]
                print(f"✓ 已設定 WUCHANG_HEALTH_URL: {network_config['health_url']}")
            if network_config.get("server_share"):
                os.environ["WUCHANG_COPY_TO"] = network_config["server_share"]
                print(f"✓ 已設定 WUCHANG_COPY_TO: {network_config['server_share']}")
        except:
            pass
    
    # 步驟 5: 自動授權
    print_step(5, "獲取完整權限（full_agent）")
    auth_result = auto_authorize_full_agent()
    if auth_result:
        results["steps"]["authorization"] = {
            "status": "completed" if auth_result.get("success") else "warning",
            "result": auth_result
        }
    else:
        results["steps"]["authorization"] = {"status": "skipped"}
    
    # 步驟 6: 執行檔案同步
    print_step(6, "執行兩機檔案同步")
    sync_success = execute_sync_all_profiles()
    results["steps"]["file_sync"] = {
        "status": "completed" if sync_success else "partial",
        "success": sync_success
    }
    
    # 步驟 7: 驗證連接
    print_step(7, "驗證連接狀態")
    verify_result = verify_connection()
    results["steps"]["verification"] = verify_result
    if verify_result.get("success"):
        print("✓ 連接驗證完成")
        output = verify_result.get("output")
        if output:
            print(output[-500:] if len(output) > 500 else output)
    else:
        print("⚠️  連接驗證有問題")
        error = verify_result.get("error", "")
        if error:
            print(error)
    
    # 生成報告
    print()
    print("=" * 70)
    print("【執行摘要】")
    print("=" * 70)
    
    completed = sum(1 for s in results["steps"].values() if s.get("status") == "completed")
    total = len(results["steps"])
    
    print(f"完成步驟: {completed}/{total}")
    print()
    
    for step_name, step_result in results["steps"].items():
        status = step_result.get("status", "unknown")
        status_icon = "✓" if status == "completed" else "⚠️" if status == "warning" else "○"
        print(f"  {status_icon} {step_name}: {status}")
    
    print()
    
    # 儲存執行報告
    report_file = BASE_DIR / "auto_sync_execution_report.json"
    report_file.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"執行報告已儲存到: {report_file}")
    print()
    print("=" * 70)
    print(f"完成時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
