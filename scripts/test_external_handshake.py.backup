#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試外網握手（通過路由器中繼）
"""

import sys
import os
import requests
import json
from datetime import datetime

# 測試端點
HANDSHAKE_ENDPOINTS = {
    'local': 'http://localhost/api/handshake',
    'via_router': 'http://192.168.50.1/relay/api/handshake',
    'external_wuchang': 'https://wuchang.life/api/handshake',
    'external_cloudflare': None  # 將從 Cloudflare 日誌獲取
}

def test_handshake(endpoint: str, timeout: int = 10) -> dict:
    """測試握手端點"""
    try:
        print(f"  測試: {endpoint}")
        response = requests.get(
            endpoint,
            timeout=timeout,
            headers={
                'User-Agent': 'Wuchang-OS-Handshake-Test/1.0',
                'Accept': 'application/json'
            },
            allow_redirects=True
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response': data,
                    'latency_ms': round(response.elapsed.total_seconds() * 1000, 2)
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response_text': response.text[:200],
                    'latency_ms': round(response.elapsed.total_seconds() * 1000, 2)
                }
        else:
            return {
                'success': False,
                'status_code': response.status_code,
                'error': f'HTTP {response.status_code}'
            }
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': '連接失敗'}
    except requests.exceptions.Timeout:
        return {'success': False, 'error': '請求超時'}
    except Exception as e:
        return {'success': False, 'error': str(e)[:100]}

def get_cloudflare_tunnel_url():
    """從 Cloudflare 日誌獲取隧道 URL"""
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'logs', '--tail', '100', 'wuchangv510-cloudflared-1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            if 'trycloudflare.com' in line:
                # 提取 URL
                import re
                match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
                if match:
                    return match.group(0)
    except Exception:
        pass
    return None

def main():
    print("=" * 80)
    print("  測試外網握手（通過路由器中繼）")
    print("=" * 80)
    print()
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 獲取 Cloudflare 隧道 URL
    print("檢查 Cloudflare 隧道...")
    cf_url = get_cloudflare_tunnel_url()
    if cf_url:
        HANDSHAKE_ENDPOINTS['external_cloudflare'] = f"{cf_url}/api/handshake"
        print(f"  ✓ 找到 Cloudflare 隧道: {cf_url}")
    else:
        print("  ⚠ 未找到 Cloudflare 隧道 URL")
    print()
    
    # 測試各個端點
    results = {}
    
    print("測試握手端點...")
    print()
    
    for name, endpoint in HANDSHAKE_ENDPOINTS.items():
        if not endpoint:
            print(f"  跳過 {name}: URL 不可用")
            continue
        
        result = test_handshake(endpoint, timeout=5)
        results[name] = result
        
        if result['success']:
            print(f"  ✓ {name}: 成功")
            print(f"    狀態碼: {result['status_code']}")
            if 'latency_ms' in result:
                print(f"    延遲: {result['latency_ms']}ms")
            if 'response' in result:
                print(f"    響應: {json.dumps(result['response'], ensure_ascii=False)[:100]}...")
        else:
            print(f"  ✗ {name}: 失敗")
            print(f"    錯誤: {result.get('error', 'Unknown')}")
        print()
    
    # 總結
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)
    
    print("=" * 80)
    print("  測試總結")
    print("=" * 80)
    print(f"成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print()
    
    if success_count > 0:
        print("✅ 可用的握手端點:")
        for name, result in results.items():
            if result.get('success'):
                endpoint = HANDSHAKE_ENDPOINTS[name]
                print(f"  • {name}: {endpoint}")
    
    print()
    print("=" * 80)
    print("  ✅ 握手測試完成")
    print("=" * 80)
    
    return 0 if success_count > 0 else 1

if __name__ == '__main__':
    sys.exit(main())
