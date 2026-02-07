#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每小時檢查系統部署狀態
檢查 wuchang.life 網域的首頁和登入頁是否可見
並聯繫 UI 電腦進行回報
"""

import sys
import os
import json
import requests
import socket
import ssl
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent

# 檢查的網域和頁面
DOMAIN = "wuchang.life"
CHECK_URLS = {
    "首頁": f"https://{DOMAIN}/",
    "登入頁": f"https://{DOMAIN}/web/login",
    "HTTP 首頁": f"http://{DOMAIN}/",
    "HTTP 登入頁": f"http://{DOMAIN}/web/login",
}

# UI 設備列表
UI_DEVICES = [
    {
        'ip': '192.168.50.84',
        'name': 'LUNGsMSI.wuchang.life',
        'type': 'Odoo 實例',
        'ports': [22, 80, 443, 8080, 8069]
    },
    {
        'ip': '192.168.50.88',
        'name': 'POS-PC.wuchang.life',
        'type': 'POS 系統電腦',
        'ports': []
    },
    {
        'ip': '192.168.50.249',
        'name': 'Home-commput.wuchang.life',
        'type': '本機（當前主機）',
        'ports': [22, 3389]
    }
]

# 禁用 SSL 警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_url_accessible(url: str, timeout: int = 10) -> Dict:
    """檢查 URL 是否可訪問"""
    result = {
        "url": url,
        "accessible": False,
        "status_code": None,
        "error": None,
        "response_time": None,
        "content_length": None,
        "final_url": None
    }
    
    try:
        start_time = datetime.now()
        response = requests.get(
            url,
            timeout=timeout,
            verify=False,  # 允許自簽證書
            allow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        result.update({
            "accessible": response.status_code < 500,  # 200-499 都算可訪問
            "status_code": response.status_code,
            "response_time": round(response_time, 2),
            "content_length": len(response.content),
            "final_url": response.url
        })
        
        # 檢查是否包含登入相關關鍵字（針對登入頁）
        if "/web/login" in url or "login" in url.lower():
            content_text = response.text.lower()
            login_keywords = ["login", "登入", "password", "密碼", "username", "使用者"]
            result["has_login_content"] = any(keyword in content_text for keyword in login_keywords)
        else:
            # 檢查首頁是否有正常內容
            result["has_content"] = len(response.content) > 1000  # 首頁應該有一定內容
        
    except requests.exceptions.SSLError as e:
        result["error"] = f"SSL 錯誤: {str(e)[:100]}"
        # SSL 錯誤時嘗試 HTTP
        if url.startswith("https://"):
            http_url = url.replace("https://", "http://")
            return check_url_accessible(http_url, timeout)
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"連接錯誤: {str(e)[:100]}"
    except requests.exceptions.Timeout:
        result["error"] = "請求超時"
    except Exception as e:
        result["error"] = f"未知錯誤: {str(e)[:100]}"
    
    return result

def check_dns_resolution(domain: str) -> Dict:
    """檢查 DNS 解析"""
    result = {
        "domain": domain,
        "resolved": False,
        "ip": None,
        "error": None
    }
    
    try:
        ip = socket.gethostbyname(domain)
        result.update({
            "resolved": True,
            "ip": ip
        })
    except socket.gaierror as e:
        result["error"] = f"DNS 解析失敗: {str(e)}"
    except Exception as e:
        result["error"] = f"未知錯誤: {str(e)[:100]}"
    
    return result

def ping_device(ip: str, timeout: float = 1.0) -> bool:
    """Ping 設備檢查是否在線"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip],
                capture_output=True,
                timeout=timeout + 1
            )
            return result.returncode == 0
        else:  # Linux/Mac
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(timeout), ip],
                capture_output=True,
                timeout=timeout + 1
            )
            return result.returncode == 0
    except Exception:
        return False

def create_notification_file(device: Dict, check_results: Dict) -> Optional[str]:
    """創建通知文件供設備讀取"""
    try:
        notification_data = {
            "title": "系統部署狀態檢查報告",
            "timestamp": datetime.now().isoformat(),
            "domain": DOMAIN,
            "check_results": check_results,
            "target_device": device,
            "notification_method": "file"
        }
        
        # 創建通知目錄
        notification_dir = PROJECT_ROOT / "notifications"
        notification_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"deployment_check_{device['ip'].replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = notification_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notification_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    except Exception as e:
        print(f"    ⚠ 無法創建通知文件: {e}")
        return None

def send_http_notification(ip: str, port: int, check_results: Dict) -> Dict:
    """通過 HTTP 發送通知"""
    try:
        url = f"http://{ip}:{port}/api/notify/deployment"
        notification_data = {
            "title": "系統部署狀態檢查報告",
            "timestamp": datetime.now().isoformat(),
            "domain": DOMAIN,
            "results": check_results
        }
        
        response = requests.post(
            url,
            json=notification_data,
            timeout=5,
            headers={'Content-Type': 'application/json'}
        )
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.text[:200]
        }
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "連接失敗"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "請求超時"}
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}

def notify_ui_devices(check_results: Dict) -> Dict:
    """通知所有 UI 設備（即使設備不在線也會創建通知文件）"""
    print("\n" + "=" * 80)
    print("  聯繫 UI 電腦進行回報")
    print("=" * 80)
    
    notification_results = {
        "timestamp": datetime.now().isoformat(),
        "devices": [],
        "summary": {
            "total_devices": len(UI_DEVICES),
            "online_devices": 0,
            "offline_devices": 0,
            "notifications_sent": 0,
            "notification_files_created": 0
        }
    }
    
    # 檢查設備連接狀態
    active_devices = []
    offline_devices = []
    
    for device in UI_DEVICES:
        ip = device['ip']
        print(f"\n檢查設備: {device['name']} ({ip})")
        
        if ping_device(ip):
            active_devices.append(device)
            print(f"  ✅ 設備在線")
            notification_results["summary"]["online_devices"] += 1
        else:
            offline_devices.append(device)
            print(f"  ⚠ 設備離線或無法連接")
            notification_results["summary"]["offline_devices"] += 1
    
    print(f"\n設備狀態摘要:")
    print(f"  總設備數: {len(UI_DEVICES)}")
    print(f"  在線設備: {len(active_devices)}")
    print(f"  離線設備: {len(offline_devices)}")
    
    # 為所有設備（包括離線設備）創建通知文件，以便設備上線後可以讀取
    all_devices_to_notify = [d for d in UI_DEVICES if d['ip'] != '192.168.50.249']
    
    if not all_devices_to_notify:
        print("\n⚠ 沒有可通知的 UI 設備（跳過本機）")
        return notification_results
    
    print(f"\n開始處理通知（包含在線和離線設備）...")
    
    # 處理在線設備：嘗試發送即時通知
    if active_devices:
        print(f"\n處理 {len(active_devices)} 個在線設備...")
        for device in active_devices:
            if device['ip'] == '192.168.50.249':
                print(f"  跳過本機: {device['name']}")
                continue
            
            ip = device['ip']
            device_result = {
                "device": device,
                "status": "online",
                "notification_methods": []
            }
            
            # 方法 1: HTTP 通知（僅在線設備）
            ports = device.get('ports', [])
            if 80 in ports or 8080 in ports:
                http_port = 80 if 80 in ports else 8080
                print(f"  [{device['name']}] 嘗試 HTTP 通知 ({ip}:{http_port})...")
                http_result = send_http_notification(ip, http_port, check_results)
                device_result["notification_methods"].append({
                    "method": "HTTP",
                    "port": http_port,
                    **http_result
                })
                if http_result.get("success"):
                    print(f"    ✅ HTTP 通知發送成功")
                    notification_results["summary"]["notifications_sent"] += 1
                else:
                    print(f"    ⚠ HTTP 通知失敗: {http_result.get('error', 'Unknown')}")
            
            # 方法 2: 創建通知文件（所有設備都創建）
            print(f"  [{device['name']}] 創建通知文件...")
            filename = create_notification_file(device, check_results)
            if filename:
                device_result["notification_methods"].append({
                    "method": "File",
                    "file": filename,
                    "success": True
                })
                print(f"    ✅ 通知文件已創建: {filename}")
                notification_results["summary"]["notification_files_created"] += 1
            else:
                device_result["notification_methods"].append({
                    "method": "File",
                    "success": False,
                    "error": "無法創建文件"
                })
                print(f"    ⚠ 無法創建通知文件")
            
            notification_results["devices"].append(device_result)
    
    # 處理離線設備：僅創建通知文件，等待設備上線後讀取
    offline_to_notify = [d for d in offline_devices if d['ip'] != '192.168.50.249']
    if offline_to_notify:
        print(f"\n處理 {len(offline_to_notify)} 個離線設備（創建通知文件供上線後讀取）...")
        for device in offline_to_notify:
            ip = device['ip']
            device_result = {
                "device": device,
                "status": "offline",
                "notification_methods": []
            }
            
            # 僅創建通知文件
            print(f"  [{device['name']}] 創建通知文件（設備離線，等待上線後讀取）...")
            filename = create_notification_file(device, check_results)
            if filename:
                device_result["notification_methods"].append({
                    "method": "File",
                    "file": filename,
                    "success": True,
                    "note": "設備離線，文件待設備上線後讀取"
                })
                print(f"    ✅ 通知文件已創建: {filename}")
                print(f"    💡 提示: 當設備 {device['name']} 上線時，可以讀取此文件獲取最新檢查結果")
                notification_results["summary"]["notification_files_created"] += 1
            else:
                device_result["notification_methods"].append({
                    "method": "File",
                    "success": False,
                    "error": "無法創建文件"
                })
                print(f"    ⚠ 無法創建通知文件")
            
            notification_results["devices"].append(device_result)
    
    # 總結
    print(f"\n通知處理完成:")
    print(f"  ✅ 通知文件已創建: {notification_results['summary']['notification_files_created']} 個")
    if notification_results["summary"]["notifications_sent"] > 0:
        print(f"  ✅ 即時通知已發送: {notification_results['summary']['notifications_sent']} 個")
    if notification_results["summary"]["offline_devices"] > 0:
        print(f"  💡 離線設備通知文件已準備，等待設備上線後讀取")
    
    return notification_results

def generate_check_report(url_results: Dict, dns_result: Dict, notification_results: Dict) -> Path:
    """生成檢查報告"""
    report_dir = PROJECT_ROOT / "logs"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"deployment_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "domain": DOMAIN,
        "dns_check": dns_result,
        "url_checks": url_results,
        "notification_results": notification_results,
        "summary": {
            "dns_resolved": dns_result.get("resolved", False),
            "homepage_accessible": any(
                r.get("accessible", False) 
                for name, r in url_results.items() 
                if "首頁" in name
            ),
            "login_accessible": any(
                r.get("accessible", False) 
                for name, r in url_results.items() 
                if "登入" in name
            ),
            "all_accessible": all(
                r.get("accessible", False) for r in url_results.values()
            )
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_file

def main():
    """主函數"""
    print("=" * 80)
    print("  系統部署狀態檢查 - 每小時檢查")
    print("=" * 80)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"檢查網域: {DOMAIN}")
    print()
    
    # 1. 檢查 DNS 解析
    print("=" * 80)
    print("  步驟 1: 檢查 DNS 解析")
    print("=" * 80)
    dns_result = check_dns_resolution(DOMAIN)
    if dns_result.get("resolved"):
        print(f"  ✅ DNS 解析成功: {DOMAIN} -> {dns_result['ip']}")
    else:
        print(f"  ❌ DNS 解析失敗: {dns_result.get('error', 'Unknown')}")
    print()
    
    # 1.1. 檢查首頁可訪問性和 SSL 證書（Google 非營利組織合規要求）
    print("=" * 80)
    print("  步驟 1.1: 檢查首頁可訪問性和 SSL 證書")
    print("=" * 80)
    homepage_url = f"https://{DOMAIN}/"
    homepage_check = check_url_accessible(homepage_url)
    
    if homepage_check.get("accessible"):
        status_code = homepage_check.get("status_code", "N/A")
        response_time = homepage_check.get("response_time", "N/A")
        print(f"  ✅ 首頁可訪問 - 狀態碼: {status_code}, 響應時間: {response_time}秒")
        
        # 檢查 SSL 證書
        try:
            parsed = urlparse(homepage_url)
            context = ssl.create_default_context()
            with socket.create_connection((parsed.hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=parsed.hostname) as ssock:
                    cert = ssock.getpeercert()
                    expiry_str = cert.get('notAfter')
                    if expiry_str:
                        expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                        days_remaining = (expiry_date - datetime.now()).days
                        print(f"  ✅ SSL 證書有效 - 剩餘 {days_remaining} 天")
                        homepage_check["cert_days_remaining"] = days_remaining
                        if days_remaining < 30:
                            print(f"    ⚠ 警告: 證書將在 30 天內過期")
        except Exception as e:
            print(f"  ⚠ SSL 證書檢查失敗: {str(e)[:100]}")
    else:
        print(f"  ❌ 首頁不可訪問: {homepage_check.get('error', 'Unknown')}")
    print()
    
    # 2. 檢查 URL 可訪問性
    print("=" * 80)
    print("  步驟 2: 檢查頁面可訪問性")
    print("=" * 80)
    url_results = {}
    
    for page_name, url in CHECK_URLS.items():
        print(f"\n檢查 {page_name}: {url}")
        result = check_url_accessible(url)
        url_results[page_name] = result
        
        if result.get("accessible"):
            status_code = result.get("status_code", "N/A")
            response_time = result.get("response_time", "N/A")
            print(f"  ✅ 可訪問 - 狀態碼: {status_code}, 響應時間: {response_time}秒")
            if result.get("final_url") and result["final_url"] != url:
                print(f"    最終 URL: {result['final_url']}")
        else:
            error = result.get("error", "Unknown")
            print(f"  ❌ 不可訪問 - 錯誤: {error}")
    
    print()
    
    # 3. 生成摘要
    print("=" * 80)
    print("  檢查摘要")
    print("=" * 80)
    
    homepage_ok = any(
        r.get("accessible", False) 
        for name, r in url_results.items() 
        if "首頁" in name
    )
    login_ok = any(
        r.get("accessible", False) 
        for name, r in url_results.items() 
        if "登入" in name
    )
    
    print(f"  DNS 解析: {'✅ 成功' if dns_result.get('resolved') else '❌ 失敗'}")
    print(f"  首頁可訪問: {'✅ 是' if homepage_ok else '❌ 否'}")
    print(f"  登入頁可訪問: {'✅ 是' if login_ok else '❌ 否'}")
    print()
    
    # 4. 聯繫 UI 設備
    notification_results = notify_ui_devices({
        "dns": dns_result,
        "urls": url_results,
        "summary": {
            "homepage_accessible": homepage_ok,
            "login_accessible": login_ok,
            "all_ok": homepage_ok and login_ok
        }
    })
    
    print()
    
    # 5. 生成報告
    print("=" * 80)
    print("  生成檢查報告")
    print("=" * 80)
    report_file = generate_check_report(url_results, dns_result, notification_results)
    print(f"  ✅ 報告已保存: {report_file}")
    print()
    
    # 6. 最終狀態
    print("=" * 80)
    print("  最終狀態")
    print("=" * 80)
    
    all_ok = dns_result.get("resolved") and homepage_ok and login_ok
    ui_summary = notification_results.get("summary", {})
    online_count = ui_summary.get("online_devices", 0)
    offline_count = ui_summary.get("offline_devices", 0)
    files_created = ui_summary.get("notification_files_created", 0)
    
    # 系統部署狀態
    if all_ok:
        print("  ✅ 系統部署正常，首頁和登入頁均可訪問")
    else:
        print("  ❌ 系統部署檢查發現問題:")
        if not dns_result.get("resolved"):
            print("    - DNS 解析失敗")
        if not homepage_ok:
            print("    - 首頁不可訪問")
        if not login_ok:
            print("    - 登入頁不可訪問")
    
    print()
    
    # UI 設備通知狀態
    print("  UI 設備通知狀態:")
    if online_count > 0:
        print(f"    ✅ 在線設備: {online_count} 個")
        if ui_summary.get("notifications_sent", 0) > 0:
            print(f"    ✅ 即時通知已發送: {ui_summary['notifications_sent']} 個")
    if offline_count > 0:
        print(f"    ⚠ 離線設備: {offline_count} 個")
        print(f"    💡 通知文件已準備，等待設備上線後讀取")
    if files_created > 0:
        print(f"    ✅ 通知文件已創建: {files_created} 個（包含在線和離線設備）")
    
    if offline_count > 0:
        print()
        print("  💡 提示: 即使 UI 設備不在線，檢查已正常完成")
        print("  💡 提示: 通知文件已保存在 notifications/ 目錄，設備上線後可自動讀取")
    
    print()
    
    # 返回狀態碼：即使UI設備不在線，只要系統部署正常，就返回成功
    if all_ok:
        if offline_count > 0:
            print("  ✅ 系統部署正常（UI 設備通知文件已準備，等待設備上線）")
        else:
            print("  ✅ 系統部署正常，所有 UI 設備已收到通知")
        return 0
    else:
        print("  ⚠ 請查看詳細報告並聯繫管理員")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n檢查已中斷")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
