#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每小時全面檢查系統
包含：
1. 網域部署檢查（wuchang.life）
2. 全球可見性檢查
3. Google 非營利組織規定的首頁合規檢查

合規要求：符合 Google 非營利組織合規要求
"""

import sys
import os
import json
import requests
import socket
import ssl
import subprocess
import dns.resolver
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_ROOT = Path(__file__).parent.parent

# Google 非營利組織合規配置
DOMAIN = "wuchang.life"
ORGANIZATION_NAME = "新北市三重區五常社區發展協會"
ORGANIZATION_TYPE = "Non-profit"
COMPLIANCE_REQUIRED = True

# Caddy 配置
CADDY_CONTAINER_NAME = "caddy"
CADDY_CONFIG_PATH = PROJECT_ROOT / "wuchang_os" / "Caddyfile"
CADDY_DATA_PATH = PROJECT_ROOT / "volumes" / "caddy-data"

# 靜態 DNS 設定（預期值）
REQUIRED_DNS_RECORDS = {
    "A": {
        "@": ["104.199.144.93"],  # 主站 IP（請根據實際情況調整）
        "www": ["104.199.144.93"],
    },
    "MX": {
        "@": [{"priority": 1, "server": "smtp.google.com"}]
    },
    "TXT": {
        "@": [],  # SPF, DKIM, DMARC 等
        "_acme-challenge": [],  # Let's Encrypt 驗證
    }
}

# 檢查的 URL
CHECK_URLS = {
    "首頁": f"https://{DOMAIN}/",
    "HTTP 首頁": f"http://{DOMAIN}/",
    "登入頁": f"https://{DOMAIN}/web/login",
}

# Google 非營利組織首頁合規要求（關鍵字檢查）
COMPLIANCE_KEYWORDS = {
    "organization_name": ["五常社區", "五常", "社區發展協會", "非營利", "non-profit"],
    "mission": ["社區", "公益", "服務", "community", "public service"],
    "contact": ["聯絡", "聯繫", "contact"],
    # 可選但建議的內容
    "optional": ["志工", "volunteer", "活動", "activity"]
}

def print_header(title: str):
    """打印標題"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_dns_resolution(domain: str) -> Dict:
    """檢查 DNS 解析（網域部署檢查）"""
    result = {
        "domain": domain,
        "resolved": False,
        "ip": None,
        "error": None,
        "dns_servers": [],
        "matches_expected": False
    }
    
    try:
        ip = socket.gethostbyname(domain)
        result.update({
            "resolved": True,
            "ip": ip
        })
        
        # 檢查是否符合預期的靜態DNS設定
        expected_ips = REQUIRED_DNS_RECORDS.get("A", {}).get("@", [])
        if expected_ips:
            result["matches_expected"] = ip in expected_ips
    except socket.gaierror as e:
        result["error"] = f"DNS 解析失敗: {str(e)}"
    except Exception as e:
        result["error"] = f"未知錯誤: {str(e)[:100]}"
    
    # 嘗試使用 dns.resolver 獲取更多 DNS 資訊
    try:
        answers = dns.resolver.resolve(domain, 'A')
        result["dns_servers"] = [str(rdata) for rdata in answers]
    except Exception:
        pass
    
    return result

def check_dns_record(domain: str, record_type: str, subdomain: str = "@") -> Dict:
    """檢查 DNS 記錄（靜態DNS設定檢查）"""
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

def check_static_dns_config(domain: str) -> Dict:
    """檢查靜態DNS設定"""
    result = {
        "domain": domain,
        "compliant": True,
        "checks": {},
        "issues": [],
        "warnings": []
    }
    
    # 檢查 A 記錄（主站和 www）
    for subdomain in ["@", "www"]:
        dns_result = check_dns_record(domain, "A", subdomain)
        result["checks"][f"A_{subdomain}"] = dns_result
        
        if dns_result.get("resolved"):
            records = dns_result.get("records", [])
            expected_ips = REQUIRED_DNS_RECORDS.get("A", {}).get(subdomain, [])
            
            if expected_ips:
                if not any(ip in records for ip in expected_ips):
                    result["warnings"].append(
                        f"A 記錄 {subdomain if subdomain != '@' else 'root'} 不符合預期 (預期: {expected_ips}, 實際: {records})"
                    )
        else:
            result["compliant"] = False
            result["issues"].append(f"A 記錄 {subdomain if subdomain != '@' else 'root'} 無法解析: {dns_result.get('error')}")
    
    # 檢查 MX 記錄
    mx_result = check_dns_record(domain, "MX", "@")
    result["checks"]["MX"] = mx_result
    
    if mx_result.get("resolved"):
        mx_records = mx_result.get("records", [])
        has_google_mx = any(
            "google.com" in str(mx.get("server", "")) if isinstance(mx, dict) else "google.com" in str(mx)
            for mx in mx_records
        )
        if not has_google_mx:
            result["warnings"].append("MX 記錄未包含 Google 郵件服務")
    else:
        result["warnings"].append(f"MX 記錄無法解析: {mx_result.get('error')}")
    
    return result

def check_caddy_certificate_status() -> Dict:
    """檢查 Caddy 憑證簽發狀態"""
    result = {
        "caddy_running": False,
        "caddy_config_exists": False,
        "caddy_data_exists": False,
        "certificates": [],
        "auto_renewal_enabled": True,
        "domain_configured": False,
        "errors": [],
        "warnings": []
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
            
            if not caddy_running:
                result["errors"].append("Caddy 容器未運行")
    except FileNotFoundError:
        result["errors"].append("Docker 命令未找到")
    except Exception as e:
        result["errors"].append(f"Docker 檢查失敗: {str(e)[:100]}")
    
    # 檢查 Caddy 配置文件
    if CADDY_CONFIG_PATH.exists():
        result["caddy_config_exists"] = True
        try:
            with open(CADDY_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config_content = f.read()
                if DOMAIN in config_content:
                    result["domain_configured"] = True
                else:
                    result["errors"].append(f"配置中未找到 {DOMAIN} 網域")
        except Exception as e:
            result["errors"].append(f"無法讀取配置文件: {str(e)[:100]}")
    else:
        result["errors"].append("Caddy 配置文件不存在")
    
    # 檢查 Caddy 數據目錄（證書存儲位置）
    if CADDY_DATA_PATH.exists():
        result["caddy_data_exists"] = True
        cert_path = CADDY_DATA_PATH / "caddy" / "certificates" / "acme-v02.api.letsencrypt.org-directory"
        if cert_path.exists():
            domain_certs = list(cert_path.glob(f"*{DOMAIN.replace('.', '_')}*"))
            if domain_certs:
                result["certificates"] = [str(cert) for cert in domain_certs]
            else:
                result["warnings"].append(f"未找到 {DOMAIN} 的證書文件（可能需要首次申請）")
    else:
        result["warnings"].append("Caddy 數據目錄不存在（首次運行可能正常）")
    
    return result

def check_url_accessible(url: str, timeout: int = 15) -> Dict:
    """檢查 URL 是否可訪問（全球可見性檢查）"""
    result = {
        "url": url,
        "accessible": False,
        "status_code": None,
        "error": None,
        "response_time": None,
        "content_length": None,
        "final_url": None,
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        )
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        result.update({
            "accessible": response.status_code < 500,
            "status_code": response.status_code,
            "response_time": round(response_time, 2),
            "content_length": len(response.content),
            "final_url": response.url,
            "ssl_valid": url.startswith("https://")
        })
        
        # 檢查 SSL 證書（如果是 HTTPS）
        if url.startswith("https://"):
            try:
                parsed = urlparse(url)
                context = ssl.create_default_context()
                with socket.create_connection((parsed.hostname, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=parsed.hostname) as ssock:
                        cert = ssock.getpeercert()
                        expiry_str = cert.get('notAfter')
                        if expiry_str:
                            expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                            days_remaining = (expiry_date - datetime.now()).days
                            result["cert_expiry"] = expiry_date.isoformat()
                            result["cert_days_remaining"] = days_remaining
                            result["ssl_valid"] = days_remaining > 0
            except Exception as e:
                result["ssl_error"] = str(e)[:100]
        
        # 儲存內容以便後續檢查
        result["content"] = response.text[:50000]  # 限制長度
        
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

def check_global_accessibility(domain: str) -> Dict:
    """檢查全球可見性（模擬多個地區訪問）"""
    result = {
        "domain": domain,
        "checks": [],
        "summary": {
            "total_checks": 0,
            "successful": 0,
            "failed": 0
        }
    }
    
    # 使用不同的 User-Agent 模擬不同地區（實際環境可以使用代理）
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',  # 全球標準
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',  # 北美
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',  # 歐洲
    ]
    
    urls_to_check = [
        f"https://{domain}/",
        f"http://{domain}/",
    ]
    
    for url in urls_to_check:
        for ua in user_agents:
            check_result = {
                "url": url,
                "user_agent": ua,
                "accessible": False,
                "status_code": None,
                "response_time": None,
                "error": None
            }
            
            try:
                start_time = datetime.now()
                response = requests.get(
                    url,
                    timeout=15,
                    verify=False,
                    allow_redirects=True,
                    headers={'User-Agent': ua}
                )
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds()
                check_result.update({
                    "accessible": response.status_code < 500,
                    "status_code": response.status_code,
                    "response_time": round(response_time, 2)
                })
                result["summary"]["successful"] += 1
            except Exception as e:
                check_result["error"] = str(e)[:100]
                result["summary"]["failed"] += 1
            
            result["checks"].append(check_result)
            result["summary"]["total_checks"] += 1
    
    return result

def check_homepage_compliance(homepage_content: str) -> Dict:
    """檢查首頁是否符合 Google 非營利組織規定"""
    result = {
        "compliant": False,
        "checks": {},
        "missing_keywords": [],
        "score": 0,
        "total_checks": 0,
        "passed_checks": 0
    }
    
    content_lower = homepage_content.lower()
    
    # 檢查必要關鍵字
    for category, keywords in COMPLIANCE_KEYWORDS.items():
        if category == "optional":
            continue  # 跳過可選項
            
        result["checks"][category] = {
            "required": True,
            "found": False,
            "keywords_found": []
        }
        
        result["total_checks"] += 1
        
        for keyword in keywords:
            if keyword.lower() in content_lower:
                result["checks"][category]["found"] = True
                result["checks"][category]["keywords_found"].append(keyword)
        
        if result["checks"][category]["found"]:
            result["passed_checks"] += 1
        else:
            result["missing_keywords"].extend(keywords)
    
    # 檢查可選關鍵字（加分項）
    for keyword in COMPLIANCE_KEYWORDS.get("optional", []):
        if keyword.lower() in content_lower:
            result["checks"]["optional"] = result["checks"].get("optional", {
                "required": False,
                "found": False,
                "keywords_found": []
            })
            result["checks"]["optional"]["found"] = True
            result["checks"]["optional"]["keywords_found"].append(keyword)
    
    # 計算合規分數（必須通過所有必要檢查）
    if result["total_checks"] > 0:
        result["score"] = (result["passed_checks"] / result["total_checks"]) * 100
    
    # 合規標準：必須通過所有必要檢查
    result["compliant"] = result["passed_checks"] == result["total_checks"] and result["total_checks"] > 0
    
    return result

def generate_report(dns_result: Dict, static_dns_result: Dict, cert_result: Dict, url_results: Dict, global_check: Dict, compliance_result: Dict) -> Path:
    """生成檢查報告"""
    report_dir = PROJECT_ROOT / "logs"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"comprehensive_hourly_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "domain": DOMAIN,
        "organization": ORGANIZATION_NAME,
        "compliance_required": COMPLIANCE_REQUIRED,
        "checks": {
            "domain_deployment": dns_result,
            "static_dns_config": static_dns_result,
            "certificate_status": cert_result,
            "url_accessibility": url_results,
            "global_accessibility": global_check,
            "homepage_compliance": compliance_result
        },
        "summary": {
            "domain_resolved": dns_result.get("resolved", False),
            "static_dns_compliant": static_dns_result.get("compliant", False),
            "certificate_ok": cert_result.get("caddy_running", False) and cert_result.get("domain_configured", False),
            "homepage_accessible": any(
                r.get("accessible", False) 
                for name, r in url_results.items() 
                if "首頁" in name
            ),
            "global_accessible": global_check["summary"]["successful"] > 0,
            "homepage_compliant": compliance_result.get("compliant", False),
            "overall_status": "OK" if (
                dns_result.get("resolved", False) and
                static_dns_result.get("compliant", False) and
                cert_result.get("caddy_running", False) and
                cert_result.get("domain_configured", False) and
                any(r.get("accessible", False) for name, r in url_results.items() if "首頁" in name) and
                compliance_result.get("compliant", False)
            ) else "FAIL"
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_file

def main():
    """主函數"""
    print_header("每小時全面檢查系統")
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"檢查網域: {DOMAIN}")
    print(f"組織: {ORGANIZATION_NAME}")
    print(f"合規要求: {'是' if COMPLIANCE_REQUIRED else '否'}")
    print()
    
    # 1. 網域部署檢查
    print_header("步驟 1: 網域部署檢查")
    dns_result = check_dns_resolution(DOMAIN)
    if dns_result.get("resolved"):
        print(f"  ✅ DNS 解析成功: {DOMAIN} -> {dns_result['ip']}")
        if dns_result.get("dns_servers"):
            print(f"  DNS 伺服器: {', '.join(dns_result['dns_servers'])}")
        if dns_result.get("matches_expected"):
            print(f"  ✅ DNS IP 符合預期的靜態DNS設定")
        else:
            print(f"  ⚠ DNS IP 不符合預期的靜態DNS設定（實際: {dns_result['ip']}）")
    else:
        print(f"  ❌ DNS 解析失敗: {dns_result.get('error', 'Unknown')}")
    print()
    
    # 1.1. 靜態DNS設定檢查
    print_header("步驟 1.1: 靜態DNS設定檢查")
    static_dns_result = check_static_dns_config(DOMAIN)
    
    for check_name, check_result in static_dns_result.get("checks", {}).items():
        if check_result.get("resolved"):
            records = check_result.get("records", [])
            print(f"  ✅ {check_name}: {records}")
        else:
            print(f"  ❌ {check_name}: {check_result.get('error', 'Unknown')}")
    
    if static_dns_result.get("compliant"):
        print(f"  ✅ 靜態DNS設定符合要求")
    else:
        print(f"  ❌ 靜態DNS設定不符合要求")
        if static_dns_result.get("issues"):
            for issue in static_dns_result["issues"]:
                print(f"    問題: {issue}")
    
    if static_dns_result.get("warnings"):
        for warning in static_dns_result["warnings"]:
            print(f"    ⚠ 警告: {warning}")
    print()
    
    # 1.2. 憑證簽發檢查
    print_header("步驟 1.2: 憑證簽發檢查（Caddy + Let's Encrypt）")
    cert_result = check_caddy_certificate_status()
    
    if cert_result.get("caddy_running"):
        print(f"  ✅ Caddy 容器運行中")
    else:
        print(f"  ❌ Caddy 容器未運行")
    
    if cert_result.get("caddy_config_exists"):
        print(f"  ✅ Caddy 配置文件存在")
    else:
        print(f"  ❌ Caddy 配置文件不存在")
    
    if cert_result.get("domain_configured"):
        print(f"  ✅ 網域 {DOMAIN} 已配置")
    else:
        print(f"  ❌ 網域 {DOMAIN} 未配置")
    
    if cert_result.get("caddy_data_exists"):
        print(f"  ✅ Caddy 數據目錄存在")
        if cert_result.get("certificates"):
            print(f"  ✅ 找到 {len(cert_result['certificates'])} 個證書文件")
        else:
            print(f"  ⚠ 未找到證書文件（可能需要首次申請）")
    else:
        print(f"  ⚠ Caddy 數據目錄不存在（首次運行可能正常）")
    
    if cert_result.get("errors"):
        for error in cert_result["errors"]:
            print(f"    ❌ 錯誤: {error}")
    
    if cert_result.get("warnings"):
        for warning in cert_result["warnings"]:
            print(f"    ⚠ 警告: {warning}")
    print()
    
    # 2. 首頁可訪問性檢查
    print_header("步驟 2: 首頁可訪問性檢查")
    url_results = {}
    homepage_content = ""
    
    homepage_url = f"https://{DOMAIN}/"
    homepage_result = check_url_accessible(homepage_url)
    url_results["首頁"] = homepage_result
    
    if homepage_result.get("accessible"):
        status_code = homepage_result.get("status_code", "N/A")
        response_time = homepage_result.get("response_time", "N/A")
        print(f"  ✅ 首頁可訪問 - 狀態碼: {status_code}, 響應時間: {response_time}秒")
        
        if homepage_result.get("ssl_valid"):
            cert_days = homepage_result.get("cert_days_remaining", "N/A")
            print(f"  ✅ SSL 證書有效 - 剩餘 {cert_days} 天")
        else:
            print(f"  ⚠ SSL 證書問題: {homepage_result.get('ssl_error', 'Unknown')}")
        
        homepage_content = homepage_result.get("content", "")
    else:
        print(f"  ❌ 首頁不可訪問: {homepage_result.get('error', 'Unknown')}")
    
    # 檢查其他 URL
    for page_name, url in CHECK_URLS.items():
        if page_name == "首頁":
            continue  # 已經檢查過
        
        print(f"\n檢查 {page_name}: {url}")
        result = check_url_accessible(url)
        url_results[page_name] = result
        
        if result.get("accessible"):
            print(f"  ✅ 可訪問 - 狀態碼: {result.get('status_code')}, 響應時間: {result.get('response_time')}秒")
        else:
            print(f"  ❌ 不可訪問 - 錯誤: {result.get('error', 'Unknown')}")
    print()
    
    # 3. 全球可見性檢查
    print_header("步驟 3: 全球可見性檢查")
    global_check = check_global_accessibility(DOMAIN)
    summary = global_check["summary"]
    print(f"  總檢查數: {summary['total_checks']}")
    print(f"  成功: {summary['successful']}")
    print(f"  失敗: {summary['failed']}")
    
    if summary['successful'] > 0:
        print(f"  ✅ 全球可見性: 正常（{summary['successful']}/{summary['total_checks']} 成功）")
    else:
        print(f"  ❌ 全球可見性: 失敗（所有檢查都失敗）")
    print()
    
    # 4. Google 非營利組織首頁合規檢查
    print_header("步驟 4: Google 非營利組織首頁合規檢查")
    compliance_result = {}
    
    if homepage_content:
        compliance_result = check_homepage_compliance(homepage_content)
        
        print(f"  合規分數: {compliance_result['score']:.1f}%")
        print(f"  通過檢查: {compliance_result['passed_checks']}/{compliance_result['total_checks']}")
        
        print(f"\n  詳細檢查結果:")
        for category, check_info in compliance_result['checks'].items():
            if category == "optional":
                continue
            status = "✅" if check_info['found'] else "❌"
            required = "（必要）" if check_info.get('required', False) else "（可選）"
            keywords = ", ".join(check_info.get('keywords_found', []))
            print(f"    {status} {category}{required}: {keywords if keywords else '未找到關鍵字'}")
        
        if compliance_result.get('compliant'):
            print(f"\n  ✅ 首頁符合 Google 非營利組織規定")
        else:
            print(f"\n  ❌ 首頁不符合 Google 非營利組織規定")
            if compliance_result.get('missing_keywords'):
                print(f"  缺少關鍵字: {', '.join(set(compliance_result['missing_keywords']))}")
    else:
        print(f"  ⚠ 無法獲取首頁內容，跳過合規檢查")
        compliance_result = {
            "compliant": False,
            "error": "無法獲取首頁內容",
            "checks": {},
            "score": 0
        }
    print()
    
    # 5. 生成報告
    print_header("生成檢查報告")
    report_file = generate_report(dns_result, static_dns_result, cert_result, url_results, global_check, compliance_result)
    print(f"  ✅ 報告已保存: {report_file}")
    print()
    
    # 6. 最終狀態
    print_header("最終狀態")
    
    summary_report = {
        "domain_deployment": "✅" if dns_result.get("resolved") else "❌",
        "static_dns_config": "✅" if static_dns_result.get("compliant", False) else "❌",
        "certificate_status": "✅" if cert_result.get("caddy_running", False) and cert_result.get("domain_configured", False) else "❌",
        "homepage_accessible": "✅" if any(r.get("accessible", False) for name, r in url_results.items() if "首頁" in name) else "❌",
        "global_accessible": "✅" if global_check["summary"]["successful"] > 0 else "❌",
        "homepage_compliant": "✅" if compliance_result.get("compliant", False) else "❌"
    }
    
    print(f"  網域部署: {summary_report['domain_deployment']}")
    print(f"  靜態DNS設定: {summary_report['static_dns_config']}")
    print(f"  憑證簽發: {summary_report['certificate_status']}")
    print(f"  首頁可訪問: {summary_report['homepage_accessible']}")
    print(f"  全球可見性: {summary_report['global_accessible']}")
    print(f"  Google 非營利組織首頁合規: {summary_report['homepage_compliant']}")
    print()
    
    all_ok = all(status == "✅" for status in summary_report.values())
    
    if all_ok:
        print("  ✅ 所有檢查通過，系統運行正常")
        return 0
    else:
        print("  ⚠ 部分檢查未通過，請查看詳細報告")
        failed_items = [item for item, status in summary_report.items() if status == "❌"]
        print(f"  未通過項目: {', '.join(failed_items)}")
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
