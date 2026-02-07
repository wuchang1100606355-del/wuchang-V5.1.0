#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載並配置 ASUS 路由器伺服器憑證
"""

import sys
import os
import requests
import tarfile
import json
from datetime import datetime
from pathlib import Path

CERT_URL = "http://www.asusrouter.com/cert_key.tar"
CERT_DIR = "router_certificates"
ROUTER_IP = "192.168.50.1"

def download_certificate():
    """下載路由器證書"""
    print("=" * 80)
    print("  下載 ASUS 路由器伺服器憑證")
    print("=" * 80)
    print()
    print(f"證書 URL: {CERT_URL}")
    print(f"路由器 IP: {ROUTER_IP}")
    print()
    
    # 創建證書目錄
    cert_path = Path(CERT_DIR)
    cert_path.mkdir(exist_ok=True)
    
    tar_file = cert_path / "cert_key.tar"
    
    print("[1/3] 下載證書文件...")
    try:
        response = requests.get(CERT_URL, timeout=30, stream=True)
        response.raise_for_status()
        
        with open(tar_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = tar_file.stat().st_size
        print(f"  ✓ 證書已下載: {tar_file}")
        print(f"  文件大小: {file_size / 1024:.2f} KB")
    except requests.exceptions.RequestException as e:
        print(f"  ✗ 下載失敗: {e}")
        return None
    
    print()
    return tar_file

def extract_certificate(tar_file):
    """解壓證書文件"""
    print("[2/3] 解壓證書文件...")
    cert_path = Path(CERT_DIR)
    
    try:
        with tarfile.open(tar_file, 'r') as tar:
            # 列出文件
            members = tar.getmembers()
            print(f"  找到 {len(members)} 個文件:")
            for member in members:
                print(f"    • {member.name}")
            
            # 解壓
            tar.extractall(cert_path)
            print(f"  ✓ 證書已解壓到: {cert_path}")
    except Exception as e:
        print(f"  ✗ 解壓失敗: {e}")
        return None
    
    print()
    return cert_path

def analyze_certificate(cert_path):
    """分析證書文件"""
    print("[3/3] 分析證書文件...")
    
    cert_files = {
        'cert': None,
        'key': None,
        'ca': None,
        'pem': None
    }
    
    # 查找證書文件
    for file_path in cert_path.rglob('*'):
        if file_path.is_file():
            name_lower = file_path.name.lower()
            if 'cert' in name_lower or '.crt' in name_lower:
                if 'key' not in name_lower:
                    cert_files['cert'] = file_path
            elif 'key' in name_lower or '.key' in name_lower:
                cert_files['key'] = file_path
            elif 'ca' in name_lower or 'chain' in name_lower:
                cert_files['ca'] = file_path
            elif '.pem' in name_lower:
                cert_files['pem'] = file_path
    
    # 顯示找到的文件
    for cert_type, cert_file in cert_files.items():
        if cert_file:
            print(f"  ✓ {cert_type}: {cert_file.name}")
            try:
                size = cert_file.stat().st_size
                print(f"    大小: {size} bytes")
                
                # 嘗試讀取前幾行來確認文件類型
                with open(cert_file, 'rb') as f:
                    content = f.read(200)
                    if b'BEGIN CERTIFICATE' in content or b'BEGIN PRIVATE KEY' in content:
                        print(f"    類型: PEM 格式證書/密鑰")
                    elif b'-----BEGIN' in content:
                        print(f"    類型: PEM 格式")
            except Exception as e:
                print(f"    ⚠ 無法讀取: {e}")
        else:
            print(f"  ⚠ {cert_type}: 未找到")
    
    print()
    return cert_files

def generate_caddy_config(cert_files):
    """生成 Caddy 配置"""
    print("生成 Caddy 配置建議...")
    print()
    
    config = {
        'router_certificate': {
            'cert_file': str(cert_files.get('cert')) if cert_files.get('cert') else None,
            'key_file': str(cert_files.get('key')) if cert_files.get('key') else None,
            'ca_file': str(cert_files.get('ca')) if cert_files.get('ca') else None,
        },
        'caddy_config_suggestion': {
            'comment': '路由器證書配置建議',
            'options': [
                '使用 Caddy 自動 HTTPS (推薦)',
                '手動配置路由器證書',
                '使用 Cloudflare 證書'
            ]
        }
    }
    
    # 保存配置
    config_file = Path(CERT_DIR) / "certificate_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 配置已保存: {config_file}")
    print()
    
    return config

def main():
    # 下載證書
    tar_file = download_certificate()
    if not tar_file:
        print("無法下載證書，請檢查網絡連接或 URL")
        return 1
    
    # 解壓證書
    cert_path = extract_certificate(tar_file)
    if not cert_path:
        print("無法解壓證書文件")
        return 1
    
    # 分析證書
    cert_files = analyze_certificate(cert_path)
    
    # 生成配置
    config = generate_caddy_config(cert_files)
    
    print("=" * 80)
    print("  證書處理完成")
    print("=" * 80)
    print()
    print("下一步:")
    print("  1. 檢查證書文件內容")
    print("  2. 配置 Caddy 使用證書（如需要）")
    print("  3. 或使用 Caddy 自動 HTTPS（推薦）")
    print()
    print(f"證書文件位置: {Path(CERT_DIR).absolute()}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
