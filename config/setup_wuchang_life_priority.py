#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_wuchang_life_priority.py

優先設定 www.wuchang.life 首頁

確保 www.wuchang.life 一定要能夠訪問
"""

import sys
import subprocess
import socket
import requests
from pathlib import Path
from typing import Tuple

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "cloudflared" / "config.yml"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄",
        "SUCCESS": "🎉"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_dns_resolution(domain: str) -> Tuple[bool, str]:
    """檢查 DNS 解析"""
    try:
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, None
    except Exception as e:
        return False, str(e)


def check_http_service(url: str, timeout: int = 5) -> Tuple[bool, int]:
    """檢查 HTTP 服務"""
    try:
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return True, response.status_code
    except requests.exceptions.Timeout:
        return False, 0
    except requests.exceptions.ConnectionError:
        return False, 0
    except Exception as e:
        return False, 0


def check_config_file():
    """檢查配置檔案"""
    if not CONFIG_FILE.exists():
        log(f"配置檔案不存在: {CONFIG_FILE}", "ERROR")
        return False, None
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 檢查是否包含 www.wuchang.life
            has_wuchang_life = 'www.wuchang.life' in content or 'wuchang.life' in content
            has_caddy_service = 'wuchangv510-caddy-1:80' in content
            
            return has_wuchang_life and has_caddy_service, content
    except Exception as e:
        log(f"讀取配置檔案時發生錯誤: {e}", "ERROR")
        return False, None


def ensure_config_priority():
    """確保配置優先級正確"""
    log("檢查配置檔案優先級...", "PROGRESS")
    
    if not CONFIG_FILE.exists():
        log("配置檔案不存在，建立配置...", "WARN")
        return False
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 檢查 www.wuchang.life 是否在第一個
        ingress_started = False
        wuchang_life_index = -1
        
        for i, line in enumerate(lines):
            if 'ingress:' in line:
                ingress_started = True
                continue
            
            if ingress_started and 'hostname:' in line:
                if 'www.wuchang.life' in line:
                    wuchang_life_index = i
                    log(f"找到 www.wuchang.life 在第 {i+1} 行", "OK")
                    break
        
        if wuchang_life_index == -1:
            log("未找到 www.wuchang.life 配置", "ERROR")
            return False
        
        # 檢查是否在第一位（除了註釋）
        if wuchang_life_index > 0:
            # 檢查前面的行
            for i in range(len(lines[:wuchang_life_index])):
                prev_line = lines[i].strip()
                if prev_line and not prev_line.startswith('#') and 'hostname:' in prev_line:
                    log(f"警告：www.wuchang.life 不是第一個域名配置（前面有 {prev_line}）", "WARN")
                    log("建議將 www.wuchang.life 移到第一位以確保優先匹配", "INFO")
                    return False
        
        log("配置優先級正確：www.wuchang.life 在第一位", "OK")
        return True
        
    except Exception as e:
        log(f"檢查配置時發生錯誤: {e}", "ERROR")
        return False


def main():
    """主函數"""
    print("=" * 70)
    print("www.wuchang.life 首頁設定檢查（優先）")
    print("=" * 70)
    print()
    
    log("www.wuchang.life 是必須能訪問的首頁域名", "INFO")
    print()
    
    # 1. 檢查配置檔案
    print("=" * 70)
    print("【1. 配置檔案檢查】")
    print("=" * 70)
    print()
    
    config_ok, config_content = check_config_file()
    
    if config_ok:
        log("配置檔案包含 www.wuchang.life 和 Caddy 服務", "OK")
    else:
        log("配置檔案缺少必要配置", "ERROR")
        log("需要確保配置包含 www.wuchang.life → wuchangv510-caddy-1:80", "INFO")
        return 1
    
    # 檢查優先級
    priority_ok = ensure_config_priority()
    print()
    
    # 2. 檢查 DNS 解析
    print("=" * 70)
    print("【2. DNS 解析檢查】")
    print("=" * 70)
    print()
    
    domains_to_check = [
        "www.wuchang.life",  # 優先檢查
        "wuchang.life"       # 可選
    ]
    
    dns_results = {}
    for domain in domains_to_check:
        log(f"檢查 {domain}...", "PROGRESS")
        resolved, result = check_dns_resolution(domain)
        
        if resolved:
            log(f"  DNS 解析成功: {result}", "OK")
            dns_results[domain] = {"resolved": True, "ip": result}
        else:
            log(f"  DNS 解析失敗", "ERROR")
            dns_results[domain] = {"resolved": False, "error": result}
        print()
    
    # 3. 檢查服務訪問
    print("=" * 70)
    print("【3. 服務訪問檢查】")
    print("=" * 70)
    print()
    
    log("檢查 http://www.wuchang.life...", "PROGRESS")
    accessible, status_code = check_http_service("http://www.wuchang.life", timeout=5)
    
    if accessible:
        log(f"  服務可訪問: HTTP {status_code}", "SUCCESS")
        log("  ✅ www.wuchang.life 可以正常訪問！", "SUCCESS")
    else:
        log(f"  服務無法訪問 (狀態碼: {status_code})", "ERROR")
        log("  ❌ www.wuchang.life 無法訪問，需要設定 DNS", "ERROR")
    print()
    
    # 4. 檢查 Caddy 容器
    print("=" * 70)
    print("【4. Caddy 容器檢查】")
    print("=" * 70)
    print()
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=caddy", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='replace'
        )
        
        if "caddy" in result.stdout:
            log("Caddy 容器運行中", "OK")
            print(result.stdout)
        else:
            log("Caddy 容器未運行", "ERROR")
            log("需要啟動 Caddy 容器以提供首頁服務", "WARN")
    except Exception as e:
        log(f"檢查容器時發生錯誤: {e}", "ERROR")
    print()
    
    # 5. 總結和建議
    print("=" * 70)
    print("【總結和建議】")
    print("=" * 70)
    print()
    
    homepage_ok = dns_results.get("www.wuchang.life", {}).get("resolved", False) and accessible
    
    if homepage_ok:
        log("✅ www.wuchang.life 配置正常，可以正常訪問！", "SUCCESS")
    else:
        log("⚠️ www.wuchang.life 需要設定才能訪問", "WARN")
        print()
        print("執行以下步驟確保 www.wuchang.life 可以訪問：")
        print()
        print("1. 設定 DNS 路由（使用 Docker）：")
        print("   docker run --rm \\")
        print("     -v \"${USERPROFILE}\\.cloudflared:/home/nonroot/.cloudflared\" \\")
        print("     cloudflare/cloudflared:latest tunnel route dns wuchang-tunnel www.wuchang.life")
        print()
        print("2. 確認配置檔案正確（cloudflared/config.yml）：")
        print("   - hostname: www.wuchang.life")
        print("     service: http://wuchangv510-caddy-1:80")
        print()
        print("3. 重啟 Cloudflare Tunnel 容器：")
        print("   docker restart wuchangv510-cloudflared-1")
        print()
        print("4. 驗證訪問：")
        print("   http://www.wuchang.life")
        print()
    
    return 0 if homepage_ok else 1


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
