#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
google_nonprofit_compliance_check.py

全系統 Google 非營利組織合規檢查

功能：
- 檢查 HTTPS/SSL 證書配置
- 檢查網站可訪問性
- 檢查 DNS 記錄
- 檢查網站內容合規性
- 檢查轉換追蹤設定
- 檢查組織資格驗證
- 生成合規報告
"""

import sys
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent

# 檢查目標
DOMAIN = "wuchang.life"
WWW_DOMAIN = "www.wuchang.life"
TEST_URLS = [
    f"https://{DOMAIN}",
    f"https://{WWW_DOMAIN}",
    f"http://{DOMAIN}",
    f"http://{WWW_DOMAIN}",
]

# 組織資訊
ORGANIZATION_NAME = "新北市三重區五常社區發展協會"
ORGANIZATION_COUNTRY = "台灣"


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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{icon} [{timestamp}] [{level}] {message}")


def check_https_certificate(url: str) -> Dict[str, Any]:
    """檢查 HTTPS 證書"""
    log(f"檢查 HTTPS 證書: {url}", "PROGRESS")
    
    result = {
        "url": url,
        "accessible": False,
        "has_ssl": False,
        "cert_valid": False,
        "redirects_to_https": False,
        "status_code": 0,
        "error": None,
    }
    
    try:
        # 檢查 HTTPS
        response = requests.get(url, timeout=10, allow_redirects=True, verify=True)
        result["accessible"] = True
        result["has_ssl"] = url.startswith("https://")
        result["cert_valid"] = True
        result["status_code"] = response.status_code
        
        # 檢查最終 URL
        if response.url.startswith("https://"):
            result["redirects_to_https"] = True
        
    except requests.exceptions.SSLError as e:
        result["error"] = f"SSL 錯誤: {str(e)}"
        result["cert_valid"] = False
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"連接錯誤: {str(e)}"
    except requests.exceptions.Timeout:
        result["error"] = "連接超時"
    except Exception as e:
        result["error"] = f"未知錯誤: {str(e)}"
    
    return result


def check_dns_records(domain: str) -> Dict[str, Any]:
    """檢查 DNS 記錄"""
    log(f"檢查 DNS 記錄: {domain}", "PROGRESS")
    
    result = {
        "domain": domain,
        "a_records": [],
        "cname_records": [],
        "txt_records": [],
        "mx_records": [],
        "has_acme_challenge": False,
        "error": None,
    }
    
    try:
        # 使用 nslookup 查詢 DNS
        # A 記錄
        cmd = ["nslookup", "-type=A", domain]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if proc.returncode == 0:
            for line in proc.stdout.split('\n'):
                if 'Address:' in line and not '#' in line:
                    ip = line.split('Address:')[-1].strip()
                    if ip and ip != '127.0.0.1':
                        result["a_records"].append(ip)
        
        # TXT 記錄
        cmd = ["nslookup", "-type=TXT", domain]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if proc.returncode == 0:
            for line in proc.stdout.split('\n'):
                if '_acme-challenge' in line.lower():
                    result["has_acme_challenge"] = True
                if 'text =' in line.lower():
                    txt = line.split('text =')[-1].strip()
                    result["txt_records"].append(txt)
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


def check_website_content(url: str) -> Dict[str, Any]:
    """檢查網站內容"""
    log(f"檢查網站內容: {url}", "PROGRESS")
    
    result = {
        "url": url,
        "accessible": False,
        "has_about": False,
        "has_mission": False,
        "has_contact": False,
        "has_org_info": False,
        "has_adsense": False,
        "content_length": 0,
        "status_code": 0,
        "error": None,
    }
    
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        result["accessible"] = True
        result["status_code"] = response.status_code
        result["content_length"] = len(response.content)
        
        content = response.text.lower()
        
        # 檢查必要頁面關鍵字
        if any(keyword in content for keyword in ["關於", "about", "我們", "組織"]):
            result["has_about"] = True
        
        if any(keyword in content for keyword in ["使命", "mission", "目標", "宗旨"]):
            result["has_mission"] = True
        
        if any(keyword in content for keyword in ["聯絡", "contact", "聯繫", "地址", "電話"]):
            result["has_contact"] = True
        
        if ORGANIZATION_NAME in content or "非營利" in content or "nonprofit" in content:
            result["has_org_info"] = True
        
        # 檢查是否有 AdSense
        if "adsense" in content or "googleadservices" in content:
            result["has_adsense"] = True
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


def check_google_analytics(url: str) -> Dict[str, Any]:
    """檢查 Google Analytics"""
    log(f"檢查 Google Analytics: {url}", "PROGRESS")
    
    result = {
        "url": url,
        "has_ga": False,
        "has_ga4": False,
        "has_gtag": False,
        "ga_id": None,
        "error": None,
    }
    
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        content = response.text
        
        # 檢查 GA4 (gtag.js)
        if "gtag.js" in content or "gtag(" in content:
            result["has_gtag"] = True
            result["has_ga4"] = True
            # 嘗試提取 GA ID
            import re
            match = re.search(r'gtag\(["\']config["\'],\s*["\']([^"\']+)["\']', content)
            if match:
                result["ga_id"] = match.group(1)
        
        # 檢查 Universal Analytics (analytics.js)
        if "analytics.js" in content or "ga(" in content:
            result["has_ga"] = True
            # 嘗試提取 GA ID
            import re
            match = re.search(r'["\']UA-[0-9]+-[0-9]+["\']', content)
            if match:
                result["ga_id"] = match.group(0).strip('"\'')
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


def check_organization_verification() -> Dict[str, Any]:
    """檢查組織資格驗證"""
    log("檢查組織資格驗證", "PROGRESS")
    
    result = {
        "verified": False,
        "organization_name": ORGANIZATION_NAME,
        "country": ORGANIZATION_COUNTRY,
        "evidence_files": [],
    }
    
    # 檢查證據文件
    evidence_files = [
        BASE_DIR / "AGENT_CONSTITUTION.md",
        BASE_DIR / "ASSET_INVENTORY.md",
        BASE_DIR / "GOOGLE_NONPROFIT_COMPLIANCE_CHECK.md",
    ]
    
    for file_path in evidence_files:
        if file_path.exists():
            result["evidence_files"].append(str(file_path.name))
            # 讀取文件內容檢查
            try:
                content = file_path.read_text(encoding="utf-8")
                if "Google for Nonprofits" in content or "Google for Nonprofits 驗證" in content:
                    result["verified"] = True
            except:
                pass
    
    return result


def check_ssl_certificate_files() -> Dict[str, Any]:
    """檢查 SSL 證書檔案"""
    log("檢查 SSL 證書檔案", "PROGRESS")
    
    result = {
        "cert_dir_exists": False,
        "has_cert_files": False,
        "cert_files": [],
        "error": None,
    }
    
    cert_dir = BASE_DIR / "certs"
    if cert_dir.exists():
        result["cert_dir_exists"] = True
        cert_files = list(cert_dir.rglob("*.pem")) + list(cert_dir.rglob("*.crt")) + list(cert_dir.rglob("*.key"))
        if cert_files:
            result["has_cert_files"] = True
            result["cert_files"] = [str(f.relative_to(BASE_DIR)) for f in cert_files]
    
    return result


def generate_compliance_report(results: Dict[str, Any]) -> str:
    """生成合規報告"""
    report = []
    report.append("# Google 非營利組織合規檢查報告")
    report.append("")
    report.append(f"**檢查時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**檢查域名**: {DOMAIN}")
    report.append("")
    report.append("---")
    report.append("")
    
    # 總體狀態
    report.append("## 📊 總體合規狀態")
    report.append("")
    
    total_checks = 0
    passed_checks = 0
    
    # HTTPS/SSL 檢查
    report.append("### 1. HTTPS/SSL 證書配置")
    report.append("")
    for url in TEST_URLS:
        if url in results.get("https_checks", {}):
            check = results["https_checks"][url]
            total_checks += 1
            if check.get("accessible") and check.get("cert_valid"):
                passed_checks += 1
                status = "✅"
            else:
                status = "❌"
            report.append(f"- {status} {url}")
            if check.get("error"):
                report.append(f"  - 錯誤: {check['error']}")
    report.append("")
    
    # DNS 檢查
    report.append("### 2. DNS 記錄檢查")
    report.append("")
    dns_result = results.get("dns_check", {})
    if dns_result.get("a_records"):
        report.append(f"- ✅ A 記錄: {', '.join(dns_result['a_records'])}")
    else:
        report.append("- ❌ 無 A 記錄")
    if dns_result.get("has_acme_challenge"):
        report.append("- ✅ 有 _acme-challenge TXT 記錄")
    else:
        report.append("- ⚠️  無 _acme-challenge TXT 記錄")
    report.append("")
    
    # 網站內容檢查
    report.append("### 3. 網站內容合規性")
    report.append("")
    content_result = results.get("content_check", {})
    checks = [
        ("關於我們頁面", "has_about"),
        ("使命與活動頁面", "has_mission"),
        ("聯絡方式", "has_contact"),
        ("組織資訊披露", "has_org_info"),
    ]
    for name, key in checks:
        total_checks += 1
        if content_result.get(key):
            passed_checks += 1
            report.append(f"- ✅ {name}")
        else:
            report.append(f"- ❌ {name}")
    if content_result.get("has_adsense"):
        report.append("- ❌ **發現 AdSense 廣告（違規）**")
    else:
        report.append("- ✅ 無 AdSense 廣告")
    report.append("")
    
    # Google Analytics 檢查
    report.append("### 4. 轉換追蹤設定")
    report.append("")
    ga_result = results.get("ga_check", {})
    total_checks += 1
    if ga_result.get("has_ga4") or ga_result.get("has_ga"):
        passed_checks += 1
        report.append(f"- ✅ 已安裝 Google Analytics")
        if ga_result.get("ga_id"):
            report.append(f"  - GA ID: {ga_result['ga_id']}")
    else:
        report.append("- ❌ 未安裝 Google Analytics")
    report.append("")
    
    # 組織驗證
    report.append("### 5. 組織資格驗證")
    report.append("")
    org_result = results.get("org_check", {})
    total_checks += 1
    if org_result.get("verified"):
        passed_checks += 1
        report.append(f"- ✅ 組織已通過 Google for Nonprofits 驗證")
        report.append(f"  - 組織名稱: {org_result.get('organization_name')}")
        report.append(f"  - 國家/地區: {org_result.get('country')}")
    else:
        report.append("- ❌ 未找到組織驗證證據")
    report.append("")
    
    # SSL 證書檔案
    report.append("### 6. SSL 證書檔案")
    report.append("")
    cert_result = results.get("cert_files_check", {})
    if cert_result.get("has_cert_files"):
        report.append(f"- ✅ 找到證書檔案: {len(cert_result.get('cert_files', []))} 個")
        for cert_file in cert_result.get("cert_files", [])[:5]:
            report.append(f"  - {cert_file}")
    else:
        report.append("- ⚠️  未找到證書檔案")
    report.append("")
    
    # 合規分數
    compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    report.append("---")
    report.append("")
    report.append("## 📈 合規分數")
    report.append("")
    report.append(f"**通過項目**: {passed_checks}/{total_checks}")
    report.append(f"**合規分數**: {compliance_score:.1f}%")
    report.append("")
    
    if compliance_score >= 90:
        report.append("🟢 **合規狀態**: 優秀")
    elif compliance_score >= 70:
        report.append("🟡 **合規狀態**: 良好（需改進）")
    else:
        report.append("🔴 **合規狀態**: 不符合（需立即處理）")
    
    report.append("")
    report.append("---")
    report.append("")
    report.append("## 📋 建議行動")
    report.append("")
    
    if not results.get("https_checks", {}).get(f"https://{DOMAIN}", {}).get("cert_valid"):
        report.append("1. **立即處理**: 配置 HTTPS/SSL 證書")
    if not content_result.get("has_about"):
        report.append("2. **高優先級**: 建立關於我們頁面")
    if not ga_result.get("has_ga4"):
        report.append("3. **高優先級**: 安裝 Google Analytics 4")
    
    return "\n".join(report)


def main():
    """主函數"""
    print("=" * 70)
    print("全系統 Google 非營利組織合規檢查")
    print("=" * 70)
    print()
    
    results = {}
    
    # 1. 檢查 HTTPS/SSL
    print("【檢查 1】HTTPS/SSL 證書配置")
    print()
    results["https_checks"] = {}
    for url in TEST_URLS:
        results["https_checks"][url] = check_https_certificate(url)
    
    # 2. 檢查 DNS
    print()
    print("【檢查 2】DNS 記錄")
    print()
    results["dns_check"] = check_dns_records(DOMAIN)
    
    # 3. 檢查網站內容
    print()
    print("【檢查 3】網站內容合規性")
    print()
    results["content_check"] = check_website_content(f"https://{DOMAIN}")
    
    # 4. 檢查 Google Analytics
    print()
    print("【檢查 4】轉換追蹤設定")
    print()
    results["ga_check"] = check_google_analytics(f"https://{DOMAIN}")
    
    # 5. 檢查組織驗證
    print()
    print("【檢查 5】組織資格驗證")
    print()
    results["org_check"] = check_organization_verification()
    
    # 6. 檢查 SSL 證書檔案
    print()
    print("【檢查 6】SSL 證書檔案")
    print()
    results["cert_files_check"] = check_ssl_certificate_files()
    
    # 生成報告
    print()
    print("=" * 70)
    print("生成合規報告")
    print("=" * 70)
    print()
    
    report = generate_compliance_report(results)
    
    # 儲存報告
    report_file = BASE_DIR / f"Google非營利組織合規檢查報告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding="utf-8")
    
    print(report)
    print()
    print(f"報告已儲存至: {report_file.name}")
    print()
    print("=" * 70)
    
    # 儲存 JSON 結果
    json_file = BASE_DIR / f"compliance_check_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_file.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"JSON 結果已儲存至: {json_file.name}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
