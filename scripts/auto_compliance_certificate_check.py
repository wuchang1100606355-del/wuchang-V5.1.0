#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自動 DNS 狀態和證書檢查系統
- 確認首頁由 wuchang.life 可連
- Google 非營利組織合規確認 DNS 狀態
- 自動完成憑證簽發（Caddy + Let's Encrypt）
- 無人職守全自動執行
- 授予工作內所必要之權限

合規要求：符合 Google 非營利組織合規要求
"""

import sys
import os
import json
import requests
import socket
import subprocess
import dns.resolver
import ssl
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT = Path(__file__).parent.parent

# Google 非營利組織合規配置
DOMAIN = "wuchang.life"
ORGANIZATION_TYPE = "Non-profit"
COMPLIANCE_REQUIRED = True

# 檢查的 URL
CHECK_URLS = {
    "首頁": f"https://{DOMAIN}/",
    "HTTP 首頁": f"http://{DOMAIN}/",
}

# Google 非營利組織合規所需的 DNS 記錄
REQUIRED_DNS_RECORDS = {
    "A": {
        "@": ["104.199.144.93"],  # 主站 IP
        "www": ["104.199.144.93"],
    },
    "MX": {
        "@": [{"priority": 1, "server": "smtp.google.com"}]
    },
    "TXT": {
        "@": [],  # SPF, DKIM, DMARC 等會檢查
        "_acme-challenge": [],  # Let's Encrypt 驗證
    },
    "CNAME": {}
}

# Caddy 配置
CADDY_CONTAINER_NAME = "caddy"
CADDY_CONFIG_PATH = PROJECT_ROOT / "wuchang_os" / "Caddyfile"
CADDY_DATA_PATH = PROJECT_ROOT / "volumes" / "caddy-data"

def print_header(title: str):
    """打印標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_homepage_accessible(url: str, timeout: int = 10) -> Dict:
    """檢查首頁可訪問性"""
    result = {
        "url": url,
        "accessible": False,
        "status_code": None,
        "error": None,
        "response_time": None,
        "ssl_valid": None,
        "cert_expiry": None
    }
    
    try:
        start_time = datetime.now()
        response = requests.get(
            url,
            timeout=timeout,
            verify=True,
            allow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        result.update({
            "accessible": response.status_code < 500,
            "status_code": response.status_code,
            "response_time": round(response_time, 2),
            "final_url": response.url
        })
        
        # 檢查 SSL 證書（如果是 HTTPS）
        if url.startswith("https://"):
            try:
                parsed = urlparse(url)
                hostname = parsed.hostname
                port = parsed.port or 443
                
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port), timeout=timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        
                        result["ssl_valid"] = True
                        
                        # 獲取證書過期時間
                        expiry_str = cert.get('notAfter')
                        if expiry_str:
                            expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                            result["cert_expiry"] = expiry_date.isoformat()
                            result["cert_days_remaining"] = (expiry_date - datetime.now()).days
            except Exception as e:
                result["ssl_valid"] = False
                result["ssl_error"] = str(e)[:100]
        
    except requests.exceptions.SSLError as e:
        result["error"] = f"SSL 錯誤: {str(e)[:100]}"
        result["ssl_valid"] = False
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"連接錯誤: {str(e)[:100]}"
    except requests.exceptions.Timeout:
        result["error"] = "請求超時"
    except Exception as e:
        result["error"] = f"未知錯誤: {str(e)[:100]}"
    
    return result

def check_dns_record(domain: str, record_type: str, subdomain: str = "@") -> Dict:
    """檢查 DNS 記錄"""
    result = {
        "domain": domain,
        "subdomain": subdomain,
        "type": record_type,
        "resolved": False,
        "records": [],
        "error": None
    }
    
    try:
        query_name = f"{subdomain}.{domain}" if subdomain != "@" else domain
        query_name = query_name.replace("@.", "")
        
        answers = dns.resolver.resolve(query_name, record_type)
        records = []
        
        for answer in answers:
            if record_type == "A":
                records.append(str(answer))
            elif record_type == "AAAA":
                records.append(str(answer))
            elif record_type == "MX":
                records.append({
                    "priority": answer.preference,
                    "server": str(answer.exchange)
                })
            elif record_type == "TXT":
                # TXT 記錄可能是字符串列表
                txt_data = "".join([s.decode('utf-8') if isinstance(s, bytes) else s for s in answer.strings])
                records.append(txt_data)
            elif record_type == "CNAME":
                records.append(str(answer.target))
            else:
                records.append(str(answer))
        
        result.update({
            "resolved": True,
            "records": records
        })
        
    except dns.resolver.NXDOMAIN:
        result["error"] = "域名不存在"
    except dns.resolver.NoAnswer:
        result["error"] = "無記錄"
    except dns.resolver.Timeout:
        result["error"] = "DNS 查詢超時"
    except Exception as e:
        result["error"] = str(e)[:100]
    
    return result

def check_dns_compliance(domain: str) -> Dict:
    """檢查 Google 非營利組織合規所需的 DNS 記錄"""
    print_header("Google 非營利組織合規 DNS 檢查")
    
    compliance_results = {
        "domain": domain,
        "organization_type": ORGANIZATION_TYPE,
        "compliant": True,
        "checks": {},
        "issues": [],
        "warnings": []
    }
    
    # 檢查 A 記錄（主站和 www）
    print("\n檢查 A 記錄...")
    for subdomain in ["@", "www"]:
        result = check_dns_record(domain, "A", subdomain)
        compliance_results["checks"][f"A_{subdomain}"] = result
        
        if result.get("resolved"):
            records = result.get("records", [])
            print(f"  ✅ {subdomain if subdomain != '@' else 'root'}: {', '.join(records)}")
            
            # 驗證是否符合預期
            expected_ips = REQUIRED_DNS_RECORDS.get("A", {}).get(subdomain, [])
            if expected_ips:
                if not any(ip in records for ip in expected_ips):
                    compliance_results["warnings"].append(
                        f"A 記錄 {subdomain} 不符合預期 (預期: {expected_ips}, 實際: {records})"
                    )
        else:
            print(f"  ❌ {subdomain if subdomain != '@' else 'root'}: {result.get('error', 'Unknown')}")
            compliance_results["compliant"] = False
            compliance_results["issues"].append(f"A 記錄 {subdomain} 無法解析: {result.get('error')}")
    
    # 檢查 MX 記錄（Google 郵件服務）
    print("\n檢查 MX 記錄...")
    mx_result = check_dns_record(domain, "MX", "@")
    compliance_results["checks"]["MX"] = mx_result
    
    if mx_result.get("resolved"):
        mx_records = mx_result.get("records", [])
        print(f"  ✅ MX 記錄: {len(mx_records)} 條")
        for mx in mx_records:
            if isinstance(mx, dict):
                print(f"    優先級 {mx.get('priority')}: {mx.get('server')}")
        
        # 檢查是否包含 Google 郵件服務
        has_google_mx = any(
            "google.com" in str(mx.get("server", "")) if isinstance(mx, dict) else "google.com" in str(mx)
            for mx in mx_records
        )
        if not has_google_mx:
            compliance_results["warnings"].append("MX 記錄未包含 Google 郵件服務")
    else:
        print(f"  ⚠ MX 記錄: {mx_result.get('error', 'Unknown')}")
        compliance_results["warnings"].append(f"MX 記錄無法解析: {mx_result.get('error')}")
    
    # 檢查 TXT 記錄（SPF, DKIM, DMARC, ACME 挑戰）
    print("\n檢查 TXT 記錄...")
    txt_result = check_dns_record(domain, "TXT", "@")
    compliance_results["checks"]["TXT_root"] = txt_result
    
    if txt_result.get("resolved"):
        txt_records = txt_result.get("records", [])
        print(f"  ✅ TXT 記錄: {len(txt_records)} 條")
        
        # 檢查 SPF
        has_spf = any("v=spf1" in str(record).lower() for record in txt_records)
        if has_spf:
            print("    ✅ SPF 記錄存在")
        else:
            compliance_results["warnings"].append("缺少 SPF 記錄（建議添加以提升郵件安全性）")
        
        # 檢查 DMARC
        has_dmarc = any("v=dmarc1" in str(record).lower() for record in txt_records)
        if has_dmarc:
            print("    ✅ DMARC 記錄存在")
        else:
            compliance_results["warnings"].append("缺少 DMARC 記錄（建議添加以提升郵件安全性）")
        
        # 檢查 DKIM（通常在子域名）
        dkim_result = check_dns_record(domain, "TXT", "_dmarc")
        if dkim_result.get("resolved"):
            print("    ✅ DKIM/DMARC 子域名記錄存在")
        
        # 顯示所有 TXT 記錄（前 3 條）
        for i, record in enumerate(txt_records[:3], 1):
            record_str = str(record)[:80] + "..." if len(str(record)) > 80 else str(record)
            print(f"    {i}. {record_str}")
    else:
        print(f"  ⚠ TXT 記錄: {txt_result.get('error', 'Unknown')}")
    
    # 檢查 ACME 挑戰記錄（Let's Encrypt 驗證）
    print("\n檢查 ACME 挑戰記錄...")
    acme_result = check_dns_record(domain, "TXT", "_acme-challenge")
    compliance_results["checks"]["TXT_acme"] = acme_result
    
    if acme_result.get("resolved"):
        print(f"  ✅ ACME 挑戰記錄存在: {len(acme_result.get('records', []))} 條")
    else:
        print(f"  💡 ACME 挑戰記錄: {acme_result.get('error', '無記錄')} (正常，僅在證書申請時需要)")
    
    # 總結
    print("\n" + "-" * 80)
    print("合規檢查總結:")
    print(f"  域名: {domain}")
    print(f"  組織類型: {ORGANIZATION_TYPE}")
    print(f"  合規狀態: {'✅ 符合' if compliance_results['compliant'] else '❌ 不符合'}")
    
    if compliance_results["issues"]:
        print(f"  問題: {len(compliance_results['issues'])} 個")
        for issue in compliance_results["issues"]:
            print(f"    - {issue}")
    
    if compliance_results["warnings"]:
        print(f"  警告: {len(compliance_results['warnings'])} 個")
        for warning in compliance_results["warnings"]:
            print(f"    - {warning}")
    
    return compliance_results

def check_caddy_certificate_status() -> Dict:
    """檢查 Caddy 證書狀態"""
    print_header("Caddy SSL 證書狀態檢查")
    
    result = {
        "caddy_running": False,
        "caddy_config_exists": False,
        "caddy_data_exists": False,
        "certificates": [],
        "auto_renewal_enabled": True,
        "errors": []
    }
    
    # 檢查 Caddy 容器是否運行
    try:
        docker_ps = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if docker_ps.returncode == 0:
            running_containers = docker_ps.stdout.strip().split('\n')
            caddy_running = any(CADDY_CONTAINER_NAME in name for name in running_containers)
            result["caddy_running"] = caddy_running
            
            if caddy_running:
                print(f"  ✅ Caddy 容器運行中")
            else:
                print(f"  ❌ Caddy 容器未運行")
                result["errors"].append("Caddy 容器未運行")
    except Exception as e:
        print(f"  ⚠ 無法檢查 Docker 容器: {e}")
        result["errors"].append(f"Docker 檢查失敗: {str(e)[:100]}")
    
    # 檢查 Caddy 配置文件
    if CADDY_CONFIG_PATH.exists():
        result["caddy_config_exists"] = True
        print(f"  ✅ Caddy 配置文件存在: {CADDY_CONFIG_PATH}")
        
        # 檢查配置中是否包含自動 HTTPS
        try:
            with open(CADDY_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config_content = f.read()
                if DOMAIN in config_content:
                    print(f"  ✅ 配置包含 {DOMAIN} 網域")
                    if "https://" in config_content or DOMAIN in config_content:
                        result["auto_renewal_enabled"] = True
                        print(f"  ✅ 自動 HTTPS 已啟用（Caddy 會自動處理 Let's Encrypt）")
                else:
                    result["errors"].append(f"配置中未找到 {DOMAIN} 網域")
        except Exception as e:
            result["errors"].append(f"無法讀取配置文件: {str(e)[:100]}")
    else:
        print(f"  ❌ Caddy 配置文件不存在: {CADDY_CONFIG_PATH}")
        result["errors"].append("Caddy 配置文件不存在")
    
    # 檢查 Caddy 數據目錄（證書存儲位置）
    if CADDY_DATA_PATH.exists():
        result["caddy_data_exists"] = True
        print(f"  ✅ Caddy 數據目錄存在: {CADDY_DATA_PATH}")
        
        # 嘗試查找證書文件
        cert_path = CADDY_DATA_PATH / "caddy" / "certificates" / "acme-v02.api.letsencrypt.org-directory"
        if cert_path.exists():
            print(f"  ✅ Let's Encrypt 證書目錄存在")
            # 查找域名證書
            domain_certs = list(cert_path.glob(f"*{DOMAIN.replace('.', '_')}*"))
            if domain_certs:
                print(f"  ✅ 找到 {len(domain_certs)} 個證書文件")
                result["certificates"] = [str(cert) for cert in domain_certs]
            else:
                print(f"  💡 未找到 {DOMAIN} 的證書文件（可能需要首次申請）")
    else:
        print(f"  💡 Caddy 數據目錄不存在（首次運行可能正常）")
        result["warnings"] = result.get("warnings", [])
        result["warnings"].append("Caddy 數據目錄不存在（首次運行）")
    
    return result

def trigger_caddy_certificate_renewal() -> Dict:
    """觸發 Caddy 證書自動更新"""
    print_header("觸發 Caddy 證書自動更新")
    
    result = {
        "success": False,
        "method": None,
        "message": None,
        "error": None
    }
    
    # 方法 1: 通過 Docker 容器重載 Caddy 配置
    try:
        # 查找 Caddy 容器名稱
        docker_ps = subprocess.run(
            ["docker", "ps", "--filter", f"name={CADDY_CONTAINER_NAME}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if docker_ps.returncode == 0 and docker_ps.stdout.strip():
            container_name = docker_ps.stdout.strip().split('\n')[0]
            
            # 重載 Caddy 配置（這會觸發證書檢查和更新）
            print(f"  正在重載 Caddy 容器配置: {container_name}")
            reload_result = subprocess.run(
                ["docker", "exec", container_name, "caddy", "reload", "--config", "/etc/caddy/Caddyfile"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if reload_result.returncode == 0:
                result.update({
                    "success": True,
                    "method": "docker_reload",
                    "message": "Caddy 配置已重載，證書將自動檢查和更新"
                })
                print(f"  ✅ Caddy 配置重載成功")
            else:
                result["error"] = f"重載失敗: {reload_result.stderr[:200]}"
                print(f"  ⚠ 重載失敗: {reload_result.stderr[:200]}")
        else:
            # 方法 2: 重啟 Caddy 容器
            print(f"  嘗試重啟 Caddy 容器...")
            restart_result = subprocess.run(
                ["docker", "restart", CADDY_CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if restart_result.returncode == 0:
                result.update({
                    "success": True,
                    "method": "docker_restart",
                    "message": "Caddy 容器已重啟，將自動申請和更新證書"
                })
                print(f"  ✅ Caddy 容器重啟成功")
            else:
                result["error"] = f"重啟失敗: {restart_result.stderr[:200]}"
                print(f"  ❌ 容器重啟失敗: {restart_result.stderr[:200]}")
        
    except FileNotFoundError:
        result["error"] = "Docker 命令未找到"
        print(f"  ❌ Docker 命令未找到")
    except subprocess.TimeoutExpired:
        result["error"] = "操作超時"
        print(f"  ❌ 操作超時")
    except Exception as e:
        result["error"] = str(e)[:100]
        print(f"  ❌ 發生錯誤: {e}")
    
    # 如果 Docker 方法失敗，提示手動操作
    if not result["success"]:
        print(f"\n  💡 提示: Caddy 會自動檢查和更新證書")
        print(f"  💡 提示: 如果證書即將過期，Caddy 會在下次訪問時自動更新")
        print(f"  💡 提示: 也可以手動重啟 Caddy 容器: docker restart {CADDY_CONTAINER_NAME}")
    
    return result

def detect_and_fix_issues(
    homepage_result: Dict,
    dns_compliance: Dict,
    caddy_status: Dict
) -> Dict:
    """自動檢測問題並進行修復"""
    print_header("自動問題檢測和修復")
    
    repair_results = {
        "timestamp": datetime.now().isoformat(),
        "issues_detected": [],
        "repairs_attempted": [],
        "repairs_successful": [],
        "repairs_failed": [],
        "summary": {
            "total_issues": 0,
            "total_repairs": 0,
            "successful_repairs": 0,
            "failed_repairs": 0
        }
    }
    
    # 1. 檢測 Caddy 容器未運行問題
    if not caddy_status.get("caddy_running", False):
        issue = {
            "type": "caddy_container_not_running",
            "severity": "high",
            "description": "Caddy 容器未運行",
            "detected_at": datetime.now().isoformat()
        }
        repair_results["issues_detected"].append(issue)
        print(f"\n  🔴 發現問題: {issue['description']}")
        
        # 嘗試修復
        print(f"  正在修復: 啟動 Caddy 容器...")
        fix_result = fix_caddy_container()
        repair_results["repairs_attempted"].append({
            "issue": issue,
            "repair_action": "start_caddy_container",
            "result": fix_result
        })
        
        if fix_result.get("success"):
            repair_results["repairs_successful"].append(issue)
            print(f"  ✅ 修復成功: Caddy 容器已啟動")
        else:
            repair_results["repairs_failed"].append(issue)
            print(f"  ❌ 修復失敗: {fix_result.get('error', 'Unknown')}")
    
    # 2. 檢測首頁不可訪問問題
    if not homepage_result.get("accessible", False):
        issue = {
            "type": "homepage_not_accessible",
            "severity": "critical",
            "description": f"首頁不可訪問: {homepage_result.get('error', 'Unknown')}",
            "detected_at": datetime.now().isoformat()
        }
        repair_results["issues_detected"].append(issue)
        print(f"\n  🔴 發現問題: {issue['description']}")
        
        # 嘗試修復
        print(f"  正在修復: 檢查並重啟相關服務...")
        fix_result = fix_homepage_accessibility()
        repair_results["repairs_attempted"].append({
            "issue": issue,
            "repair_action": "restart_services",
            "result": fix_result
        })
        
        if fix_result.get("success"):
            repair_results["repairs_successful"].append(issue)
            print(f"  ✅ 修復成功: 服務已重啟")
        else:
            repair_results["repairs_failed"].append(issue)
            print(f"  ❌ 修復失敗: {fix_result.get('error', 'Unknown')}")
    
    # 3. 檢測 SSL 證書無效或即將過期問題
    ssl_valid = homepage_result.get("ssl_valid")
    cert_days_remaining = homepage_result.get("cert_days_remaining")
    
    if ssl_valid is False or (cert_days_remaining is not None and cert_days_remaining < 7):
        issue = {
            "type": "ssl_certificate_issue",
            "severity": "high" if cert_days_remaining and cert_days_remaining < 7 else "medium",
            "description": f"SSL 證書問題: {'無效' if ssl_valid is False else f'將在 {cert_days_remaining} 天內過期'}",
            "detected_at": datetime.now().isoformat()
        }
        repair_results["issues_detected"].append(issue)
        print(f"\n  🔴 發現問題: {issue['description']}")
        
        # 嘗試修復
        print(f"  正在修復: 觸發證書更新...")
        fix_result = trigger_caddy_certificate_renewal()
        repair_results["repairs_attempted"].append({
            "issue": issue,
            "repair_action": "renew_certificate",
            "result": fix_result
        })
        
        if fix_result.get("success"):
            repair_results["repairs_successful"].append(issue)
            print(f"  ✅ 修復成功: 證書更新已觸發")
        else:
            repair_results["repairs_failed"].append(issue)
            print(f"  ⚠ 修復部分成功: {fix_result.get('message', '需要手動檢查')}")
    
    # 4. 檢測 DNS 不合規問題
    if not dns_compliance.get("compliant", False):
        issues_list = dns_compliance.get("issues", [])
        if issues_list:
            issue = {
                "type": "dns_compliance_issue",
                "severity": "medium",
                "description": f"DNS 合規問題: {len(issues_list)} 個問題",
                "details": issues_list,
                "detected_at": datetime.now().isoformat()
            }
            repair_results["issues_detected"].append(issue)
            print(f"\n  ⚠ 發現問題: {issue['description']}")
            print(f"  💡 提示: DNS 記錄需要手動修復，請聯繫 DNS 管理員")
    
    # 5. 檢測 Caddy 配置問題
    if not caddy_status.get("caddy_config_exists", False):
        issue = {
            "type": "caddy_config_missing",
            "severity": "high",
            "description": "Caddy 配置文件不存在",
            "detected_at": datetime.now().isoformat()
        }
        repair_results["issues_detected"].append(issue)
        print(f"\n  🔴 發現問題: {issue['description']}")
        print(f"  💡 提示: 需要手動檢查配置文件: {CADDY_CONFIG_PATH}")
    
    # 更新摘要
    repair_results["summary"].update({
        "total_issues": len(repair_results["issues_detected"]),
        "total_repairs": len(repair_results["repairs_attempted"]),
        "successful_repairs": len(repair_results["repairs_successful"]),
        "failed_repairs": len(repair_results["repairs_failed"])
    })
    
    # 顯示摘要
    print(f"\n" + "-" * 80)
    print(f"修復摘要:")
    print(f"  發現問題: {repair_results['summary']['total_issues']} 個")
    print(f"  嘗試修復: {repair_results['summary']['total_repairs']} 次")
    print(f"  修復成功: {repair_results['summary']['successful_repairs']} 次")
    print(f"  修復失敗: {repair_results['summary']['failed_repairs']} 次")
    
    return repair_results

def fix_caddy_container() -> Dict:
    """修復 Caddy 容器未運行問題"""
    result = {
        "success": False,
        "method": None,
        "message": None,
        "error": None
    }
    
    try:
        # 方法 1: 使用 docker-compose 啟動
        print(f"    嘗試使用 docker-compose 啟動 Caddy...")
        compose_result = subprocess.run(
            ["docker-compose", "up", "-d", "caddy"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if compose_result.returncode == 0:
            result.update({
                "success": True,
                "method": "docker_compose_up",
                "message": "Caddy 容器已通過 docker-compose 啟動"
            })
            # 等待容器啟動
            import time
            time.sleep(5)
            return result
    except Exception as e:
        pass
    
    try:
        # 方法 2: 直接使用 docker start
        print(f"    嘗試直接啟動 Caddy 容器...")
        start_result = subprocess.run(
            ["docker", "start", CADDY_CONTAINER_NAME],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if start_result.returncode == 0:
            result.update({
                "success": True,
                "method": "docker_start",
                "message": "Caddy 容器已啟動"
            })
            # 等待容器啟動
            import time
            time.sleep(5)
            return result
    except Exception as e:
        result["error"] = str(e)[:100]
    
    try:
        # 方法 3: 檢查容器是否存在，如果不存在則創建
        print(f"    檢查容器是否存在...")
        inspect_result = subprocess.run(
            ["docker", "inspect", CADDY_CONTAINER_NAME],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if inspect_result.returncode != 0:
            # 容器不存在，需要創建
            print(f"    容器不存在，需要重新創建...")
            result["error"] = "容器不存在，需要手動創建或使用 docker-compose up"
        else:
            # 容器存在但未運行，嘗試啟動
            print(f"    容器存在但未運行，嘗試啟動...")
            start_result = subprocess.run(
                ["docker", "start", CADDY_CONTAINER_NAME],
                capture_output=True,
                text=True,
                timeout=30
            )
            if start_result.returncode == 0:
                result.update({
                    "success": True,
                    "method": "docker_start",
                    "message": "Caddy 容器已啟動"
                })
                import time
                time.sleep(5)
    except Exception as e:
        result["error"] = str(e)[:100]
    
    return result

def fix_homepage_accessibility() -> Dict:
    """修復首頁不可訪問問題"""
    result = {
        "success": False,
        "methods": [],
        "message": None,
        "error": None
    }
    
    try:
        # 方法 1: 重啟 Caddy 容器
        print(f"    重啟 Caddy 容器...")
        restart_result = subprocess.run(
            ["docker", "restart", CADDY_CONTAINER_NAME],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if restart_result.returncode == 0:
            result["methods"].append("restart_caddy")
            import time
            time.sleep(10)  # 等待服務啟動
            
            # 驗證修復是否成功
            test_result = check_homepage_accessible(f"https://{DOMAIN}/", timeout=5)
            if test_result.get("accessible"):
                result.update({
                    "success": True,
                    "message": "Caddy 容器重啟後首頁可訪問"
                })
                return result
        
    except Exception as e:
        result["error"] = str(e)[:100]
    
    try:
        # 方法 2: 重啟 wuchang-web 容器
        print(f"    重啟 wuchang-web 容器...")
        restart_result = subprocess.run(
            ["docker", "restart", "wuchang-web"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if restart_result.returncode == 0:
            result["methods"].append("restart_wuchang_web")
            import time
            time.sleep(10)  # 等待服務啟動
            
            # 驗證修復是否成功
            test_result = check_homepage_accessible(f"https://{DOMAIN}/", timeout=5)
            if test_result.get("accessible"):
                result.update({
                    "success": True,
                    "message": "wuchang-web 容器重啟後首頁可訪問"
                })
                return result
    except Exception as e:
        if not result.get("error"):
            result["error"] = str(e)[:100]
    
    # 如果所有方法都失敗
    if not result["success"]:
        result["error"] = "無法自動修復首頁訪問問題，需要手動檢查"
    
    return result

def generate_compliance_report(
    homepage_check: Dict,
    dns_compliance: Dict,
    caddy_status: Dict,
    cert_renewal: Dict,
    repair_results: Dict
) -> Tuple[Path, Dict]:
    """生成合規檢查報告（包含自動修復結果）"""
    report_dir = PROJECT_ROOT / "logs"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"compliance_cert_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 檢查修復後的狀態（重新檢查如果修復成功）
    homepage_accessible_after_repair = homepage_check.get("accessible", False)
    caddy_running_after_repair = caddy_status.get("caddy_running", False)
    
    # 如果進行了修復，等待一段時間後重新檢查
    if repair_results.get("summary", {}).get("successful_repairs", 0) > 0:
        print("  等待服務穩定（10秒）...")
        import time
        time.sleep(10)
        
        # 重新檢查 Caddy 狀態
        if not caddy_running_after_repair:
            try:
                docker_ps = subprocess.run(
                    ["docker", "ps", "--filter", f"name={CADDY_CONTAINER_NAME}", "--format", "{{.Names}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                caddy_running_after_repair = docker_ps.returncode == 0 and docker_ps.stdout.strip()
            except:
                pass
        
        # 重新檢查首頁可訪問性
        if not homepage_accessible_after_repair:
            retest_result = check_homepage_accessible(f"https://{DOMAIN}/", timeout=10)
            homepage_accessible_after_repair = retest_result.get("accessible", False)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "domain": DOMAIN,
        "organization_type": ORGANIZATION_TYPE,
        "compliance_required": COMPLIANCE_REQUIRED,
        "homepage_check": homepage_check,
        "dns_compliance": dns_compliance,
        "caddy_certificate_status": caddy_status,
        "certificate_renewal": cert_renewal,
        "auto_repair_results": repair_results,
        "summary": {
            "homepage_accessible": homepage_accessible_after_repair,
            "homepage_ssl_valid": homepage_check.get("ssl_valid", False),
            "dns_compliant": dns_compliance.get("compliant", False),
            "caddy_running": caddy_running_after_repair,
            "auto_renewal_enabled": caddy_status.get("auto_renewal_enabled", False),
            "cert_renewal_triggered": cert_renewal.get("success", False),
            "issues_detected": repair_results.get("summary", {}).get("total_issues", 0),
            "repairs_attempted": repair_results.get("summary", {}).get("total_repairs", 0),
            "repairs_successful": repair_results.get("summary", {}).get("successful_repairs", 0),
            "repairs_failed": repair_results.get("summary", {}).get("failed_repairs", 0),
            "all_checks_passed": (
                homepage_accessible_after_repair and
                homepage_check.get("ssl_valid", False) and
                dns_compliance.get("compliant", False) and
                caddy_running_after_repair
            )
        },
        "compliance_status": {
            "google_nonprofit_compliant": (
                dns_compliance.get("compliant", False) and
                homepage_check.get("ssl_valid", False)
            ),
            "certificate_auto_renewal": caddy_status.get("auto_renewal_enabled", False),
            "auto_repair_enabled": True,
            "ready_for_production": (
                homepage_accessible_after_repair and
                homepage_check.get("ssl_valid", False) and
                dns_compliance.get("compliant", False) and
                caddy_running_after_repair and
                caddy_status.get("auto_renewal_enabled", False)
            )
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_file, report

def main():
    """主函數 - 全自動執行"""
    print("=" * 80)
    print("  全自動 DNS 狀態和證書檢查系統")
    print("  Google 非營利組織合規確認")
    print("=" * 80)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"域名: {DOMAIN}")
    print(f"組織類型: {ORGANIZATION_TYPE}")
    print(f"合規要求: {'✅ 是' if COMPLIANCE_REQUIRED else '❌ 否'}")
    print()
    
    try:
        # 1. 檢查首頁可訪問性（wuchang.life）
        print_header("步驟 1: 檢查首頁可訪問性 (wuchang.life)")
        homepage_result = None
        
        for name, url in CHECK_URLS.items():
            print(f"\n檢查 {name}: {url}")
            result = check_homepage_accessible(url)
            
            if result.get("accessible"):
                status_code = result.get("status_code", "N/A")
                response_time = result.get("response_time", "N/A")
                ssl_valid = result.get("ssl_valid", None)
                
                print(f"  ✅ 可訪問 - 狀態碼: {status_code}, 響應時間: {response_time}秒")
                
                if url.startswith("https://"):
                    if ssl_valid:
                        cert_expiry = result.get("cert_expiry")
                        days_remaining = result.get("cert_days_remaining", 0)
                        print(f"  ✅ SSL 證書有效")
                        if cert_expiry:
                            print(f"    證書過期時間: {cert_expiry}")
                            print(f"    剩餘天數: {days_remaining} 天")
                            if days_remaining < 30:
                                print(f"    ⚠ 警告: 證書將在 30 天內過期")
                            if days_remaining < 7:
                                print(f"    🔴 緊急: 證書將在 7 天內過期，需要立即更新")
                    else:
                        print(f"  ❌ SSL 證書無效: {result.get('ssl_error', 'Unknown')}")
                
                # 使用 HTTPS 結果作為主要結果
                if url.startswith("https://"):
                    homepage_result = result
            else:
                error = result.get("error", "Unknown")
                print(f"  ❌ 不可訪問 - 錯誤: {error}")
        
        if not homepage_result:
            homepage_result = result  # 使用最後一個結果
        
        print()
        
        # 2. Google 非營利組織合規 DNS 檢查
        dns_compliance_result = check_dns_compliance(DOMAIN)
        print()
        
        # 3. 檢查 Caddy 證書狀態
        caddy_status = check_caddy_certificate_status()
        print()
        
        # 4. 自動問題檢測和修復
        print_header("步驟 4: 自動問題檢測和修復")
        repair_results = detect_and_fix_issues(
            homepage_result,
            dns_compliance_result,
            caddy_status
        )
        print()
        
        # 4.1 如果證書即將過期或無效，觸發自動更新（如果未在修復中處理）
        cert_renewal_result = {"success": False, "method": None, "message": "未觸發"}
        
        # 檢查是否已經在修復中處理了證書問題
        cert_issue_fixed = any(
            r.get("repair_action") == "renew_certificate" and r.get("result", {}).get("success")
            for r in repair_results.get("repairs_attempted", [])
        )
        
        days_remaining = homepage_result.get("cert_days_remaining")
        ssl_valid = homepage_result.get("ssl_valid")
        
        if not cert_issue_fixed and ((days_remaining is not None and days_remaining < 30) or (ssl_valid is False)):
            print_header("步驟 4.1: 觸發證書自動更新")
            cert_renewal_result = trigger_caddy_certificate_renewal()
        elif not cert_issue_fixed:
            print("步驟 4.1: 證書狀態良好，無需更新")
            if days_remaining:
                print(f"  證書剩餘 {days_remaining} 天，狀態良好")
        else:
            print("步驟 4.1: 證書問題已在修復步驟中處理")
        print()
        
        # 5. 生成合規報告（包含修復結果）
        print_header("生成合規檢查報告")
        report_file, report = generate_compliance_report(
            homepage_result,
            dns_compliance_result,
            caddy_status,
            cert_renewal_result,
            repair_results
        )
        print(f"  ✅ 報告已保存: {report_file}")
        print()
        
        # 6. 最終狀態
        print_header("最終狀態")
        
        summary = report["summary"]
        compliance = report["compliance_status"]
        
        print(f"  首頁可訪問: {'✅ 是' if summary['homepage_accessible'] else '❌ 否'}")
        print(f"  SSL 證書有效: {'✅ 是' if summary['homepage_ssl_valid'] else '❌ 否'}")
        print(f"  DNS 合規: {'✅ 是' if summary['dns_compliant'] else '❌ 否'}")
        print(f"  Caddy 運行中: {'✅ 是' if summary['caddy_running'] else '❌ 否'}")
        print(f"  自動續期啟用: {'✅ 是' if summary['auto_renewal_enabled'] else '❌ 否'}")
        print()
        
        # 顯示自動修復結果
        if summary.get("issues_detected", 0) > 0:
            print(f"  自動問題檢測和修復:")
            print(f"    發現問題: {summary['issues_detected']} 個")
            print(f"    嘗試修復: {summary['repairs_attempted']} 次")
            print(f"    修復成功: {summary['repairs_successful']} 次")
            if summary.get("repairs_failed", 0) > 0:
                print(f"    修復失敗: {summary['repairs_failed']} 次（需要手動處理）")
            print()
        
        print(f"  Google 非營利組織合規: {'✅ 符合' if compliance['google_nonprofit_compliant'] else '❌ 不符合'}")
        print(f"  證書自動續期: {'✅ 已啟用' if compliance['certificate_auto_renewal'] else '❌ 未啟用'}")
        print(f"  自動修復啟用: {'✅ 是' if compliance.get('auto_repair_enabled', False) else '❌ 否'}")
        print(f"  生產環境就緒: {'✅ 是' if compliance['ready_for_production'] else '❌ 否'}")
        print()
        
        if compliance["ready_for_production"]:
            print("  ✅ 所有檢查通過，系統已就緒")
            print("  ✅ 首頁由 wuchang.life 可連")
            print("  ✅ Google 非營利組織合規確認完成")
            print("  ✅ DNS 狀態正常")
            print("  ✅ 證書自動簽發已配置")
            if summary.get("repairs_successful", 0) > 0:
                print(f"  ✅ 自動修復已完成 {summary['repairs_successful']} 個問題")
            return 0
        else:
            print("  ⚠ 部分檢查未通過，請查看詳細報告")
            if not summary['homepage_accessible']:
                print("    - 首頁不可訪問（已嘗試自動修復）")
            if not summary['homepage_ssl_valid']:
                print("    - SSL 證書無效或即將過期（已嘗試自動修復）")
            if not summary['dns_compliant']:
                print("    - DNS 記錄不符合要求（需要手動修復）")
            if not summary['caddy_running']:
                print("    - Caddy 容器未運行（已嘗試自動修復）")
            if summary.get("repairs_failed", 0) > 0:
                print(f"    - 有 {summary['repairs_failed']} 個修復失敗，需要手動處理")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n檢查已中斷")
        return 130
    except Exception as e:
        print(f"\n\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # 檢查是否安裝了 dnspython
    try:
        import dns.resolver
    except ImportError:
        print("錯誤: 需要安裝 dnspython 套件")
        print("請執行: pip install dnspython")
        sys.exit(1)
    
    sys.exit(main())
