ㄒ#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_dns_status.py

檢查 DNS 配置和解析狀態
"""

import sys
import subprocess
import socket
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import json

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CLOUDFLARED_DIR = BASE_DIR / "cloudflared"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_dns_resolution(domain: str) -> Tuple[bool, str, List[str]]:
    """檢查 DNS 解析"""
    try:
        # 基本解析
        ip = socket.gethostbyname(domain)
        
        # 取得所有 IP（如果有多個）
        ips = []
        try:
            _, _, ip_addresses = socket.gethostbyname_ex(domain)
            ips = ip_addresses
        except:
            ips = [ip]
        
        return True, ip, ips
    except socket.gaierror as e:
        return False, str(e), []


def check_cloudflare_dns(domain: str) -> Dict:
    """檢查 Cloudflare DNS 記錄"""
    try:
        # 使用 dig 命令（如果可用）
        result = subprocess.run(
            ["nslookup", domain],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout
        
        # 解析結果
        info = {
            "resolved": False,
            "ips": [],
            "ns_servers": [],
            "raw_output": output
        }
        
        if "Address:" in output:
            info["resolved"] = True
            # 嘗試提取 IP
            for line in output.split('\n'):
                if "Address:" in line and ":" not in line.split("Address:")[-1].strip():
                    ip = line.split("Address:")[-1].strip()
                    if ip and not ip.startswith("127.") and "." in ip:
                        info["ips"].append(ip)
        
        return info
    except Exception as e:
        return {
            "resolved": False,
            "error": str(e),
            "ips": [],
            "ns_servers": []
        }


def check_http_service(domain: str, use_https: bool = True, timeout: int = 5) -> Tuple[bool, str]:
    """檢查 HTTP 服務連接"""
    protocol = "https" if use_https else "http"
    url = f"{protocol}://{domain}"
    
    try:
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return True, f"HTTP {response.status_code}"
    except requests.exceptions.SSLError as e:
        # SSL 錯誤但可能連接到服務
        return True, f"SSL 連接（可能有證書問題）"
    except requests.exceptions.Timeout:
        return False, "連接超時"
    except requests.exceptions.ConnectionError:
        return False, "無法連接"
    except Exception as e:
        return False, str(e)


def check_cloudflared_container():
    """檢查 Cloudflare Tunnel 容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=cloudflared", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        
        if "cloudflared" in result.stdout:
            return True, result.stdout.strip()
        else:
            return False, "容器未運行"
    except Exception as e:
        return False, str(e)


def get_cloudflared_logs(tail: int = 20) -> str:
    """取得 Cloudflare Tunnel 日誌"""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), "wuchangv510-cloudflared-1"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return f"無法取得日誌: {e}"


def check_cloudflare_config():
    """檢查 Cloudflare 配置檔案"""
    config_file = CLOUDFLARED_DIR / "config.yml"
    credentials_file = CLOUDFLARED_DIR / "credentials.json"
    
    config_status = {
        "config_exists": False,
        "credentials_exists": False,
        "config_valid": False,
        "tunnel_id_set": False,
        "domains_configured": []
    }
    
    if config_file.exists():
        config_status["config_exists"] = True
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '<tunnel-id>' not in content:
                    config_status["tunnel_id_set"] = True
                config_status["config_valid"] = True
                
                # 提取配置的域名
                for line in content.split('\n'):
                    if 'hostname:' in line:
                        domain = line.split('hostname:')[-1].strip()
                        if domain and not domain.startswith('#'):
                            config_status["domains_configured"].append(domain)
        except Exception as e:
            config_status["error"] = str(e)
    
    if credentials_file.exists():
        config_status["credentials_exists"] = True
    
    return config_status


def main():
    """主函數"""
    print("=" * 70)
    print("DNS 狀態檢查")
    print("=" * 70)
    print()
    
    # 要檢查的域名
    domains = [
        "app.wuchang.org.tw",
        "ai.wuchang.org.tw",
        "admin.wuchang.org.tw",
        "monitor.wuchang.org.tw",
    ]
    
    # 1. 檢查 Cloudflare Tunnel 容器
    print("=" * 70)
    print("【1. Cloudflare Tunnel 容器狀態】")
    print("=" * 70)
    print()
    
    container_running, container_status = check_cloudflared_container()
    if container_running:
        log(f"容器運行中: {container_status}", "OK")
        
        # 顯示日誌
        log("最近日誌:", "INFO")
        logs = get_cloudflared_logs(tail=10)
        for line in logs.split('\n')[-10:]:
            if line.strip():
                print(f"   {line}")
    else:
        log(f"容器未運行: {container_status}", "ERROR")
    print()
    
    # 2. 檢查 Cloudflare 配置
    print("=" * 70)
    print("【2. Cloudflare 配置檔案】")
    print("=" * 70)
    print()
    
    config_status = check_cloudflare_config()
    
    if config_status["config_exists"]:
        log("配置檔案存在", "OK")
        if config_status["tunnel_id_set"]:
            log("Tunnel ID 已設定", "OK")
        else:
            log("Tunnel ID 未設定（使用佔位符）", "WARN")
        
        if config_status["domains_configured"]:
            log(f"配置的域名: {len(config_status['domains_configured'])} 個", "OK")
            for domain in config_status["domains_configured"]:
                print(f"   - {domain}")
        else:
            log("未找到配置的域名", "WARN")
    else:
        log("配置檔案不存在", "ERROR")
        log("需要建立 cloudflared/config.yml", "INFO")
    
    if config_status["credentials_exists"]:
        log("憑證檔案存在", "OK")
    else:
        log("憑證檔案不存在", "ERROR")
        log("需要執行 'cloudflared tunnel login' 並複製憑證", "INFO")
    print()
    
    # 3. 檢查 DNS 解析
    print("=" * 70)
    print("【3. DNS 解析檢查】")
    print("=" * 70)
    print()
    
    dns_results = {}
    for domain in domains:
        log(f"檢查 {domain}...", "PROGRESS")
        
        # 基本 DNS 解析
        resolved, result, ips = check_dns_resolution(domain)
        
        if resolved:
            log(f"  DNS 解析成功: {', '.join(ips)}", "OK")
            dns_results[domain] = {
                "resolved": True,
                "ips": ips,
                "primary_ip": result
            }
        else:
            log(f"  DNS 解析失敗: {result}", "ERROR")
            dns_results[domain] = {
                "resolved": False,
                "error": result,
                "ips": []
            }
        
        # 使用 nslookup 檢查
        cf_dns = check_cloudflare_dns(domain)
        if cf_dns.get("resolved"):
            if cf_dns.get("ips"):
                log(f"  nslookup 結果: {', '.join(cf_dns['ips'])}", "OK")
        print()
    
    # 4. 檢查 HTTP 服務
    print("=" * 70)
    print("【4. HTTP 服務連接檢查】")
    print("=" * 70)
    print()
    
    service_results = {}
    for domain in domains:
        log(f"檢查 {domain} HTTPS 連接...", "PROGRESS")
        
        connected, result = check_http_service(domain, use_https=True, timeout=3)
        
        if connected:
            log(f"  連接成功: {result}", "OK")
            service_results[domain] = {"connected": True, "status": result}
        else:
            log(f"  連接失敗: {result}", "WARN")
            service_results[domain] = {"connected": False, "error": result}
        print()
    
    # 5. 總結
    print("=" * 70)
    print("【DNS 狀態總結】")
    print("=" * 70)
    print()
    
    # DNS 解析統計
    resolved_count = sum(1 for r in dns_results.values() if r.get("resolved", False))
    log(f"DNS 解析: {resolved_count}/{len(domains)} 個域名可解析", 
        "OK" if resolved_count == len(domains) else "WARN")
    
    # 服務連接統計
    connected_count = sum(1 for r in service_results.values() if r.get("connected", False))
    log(f"服務連接: {connected_count}/{len(domains)} 個服務可連接",
        "OK" if connected_count == len(domains) else "WARN")
    
    print()
    
    # 問題診斷
    print("=" * 70)
    print("【問題診斷與建議】")
    print("=" * 70)
    print()
    
    issues = []
    
    if not container_running:
        issues.append({
            "severity": "ERROR",
            "issue": "Cloudflare Tunnel 容器未運行",
            "solution": "執行: docker-compose up -d cloudflared"
        })
    
    if not config_status["config_exists"]:
        issues.append({
            "severity": "ERROR",
            "issue": "Cloudflare 配置檔案不存在",
            "solution": "執行: python deploy_domain.py (選擇 2) 產生配置範本"
        })
    
    if not config_status["credentials_exists"]:
        issues.append({
            "severity": "ERROR",
            "issue": "Cloudflare 憑證檔案不存在",
            "solution": "執行: cloudflared tunnel login 並複製憑證"
        })
    
    if not config_status.get("tunnel_id_set", False):
        issues.append({
            "severity": "WARN",
            "issue": "Tunnel ID 未設定",
            "solution": "編輯 cloudflared/config.yml，將 <tunnel-id> 替換為實際 ID"
        })
    
    if resolved_count < len(domains):
        issues.append({
            "severity": "WARN",
            "issue": f"{len(domains) - resolved_count} 個域名無法解析",
            "solution": "確認 DNS 路由已設定: cloudflared tunnel route dns list"
        })
    
    if connected_count < len(domains):
        issues.append({
            "severity": "WARN",
            "issue": f"{len(domains) - connected_count} 個服務無法連接",
            "solution": "檢查 Cloudflare Tunnel 配置和容器日誌"
        })
    
    if issues:
        for issue in issues:
            icon = "❌" if issue["severity"] == "ERROR" else "⚠️"
            print(f"{icon} {issue['issue']}")
            print(f"   解決方案: {issue['solution']}")
            print()
    else:
        log("未發現問題，DNS 配置正常", "OK")
        print()
    
    # 產生報告
    report = {
        "timestamp": str(Path.cwd()),
        "container_running": container_running,
        "config_status": config_status,
        "dns_results": dns_results,
        "service_results": service_results,
        "issues": issues
    }
    
    report_file = BASE_DIR / "dns_status_report.json"
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"報告已儲存: {report_file}", "OK")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        log("操作已取消", "WARN")
        sys.exit(0)
    except Exception as e:
        log(f"發生錯誤: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
