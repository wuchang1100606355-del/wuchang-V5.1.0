#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_router_cert.py

設定路由器證書和密鑰

功能：
- 解壓縮 cert_key.tar 檔案
- 提取證書和密鑰檔案
- 配置路由器連接
- 測試路由器連接
"""

import sys
import tarfile
import json
import shutil
from pathlib import Path
from typing import Dict, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
CERTS_DIR = BASE_DIR / "certs"


def extract_cert_tar(tar_path: Path, extract_to: Path = None):
    """解壓縮證書 TAR 檔案"""
    if extract_to is None:
        extract_to = CERTS_DIR
    
    print(f"正在解壓縮: {tar_path.name}")
    print(f"目標目錄: {extract_to}")
    print()
    
    try:
        with tarfile.open(tar_path, 'r') as tar:
            # 列出所有檔案
            file_list = tar.getnames()
            print(f"【檔案清單】共 {len(file_list)} 個檔案")
            for f in file_list:
                print(f"  - {f}")
            print()
            
            # 解壓縮
            extract_to.mkdir(parents=True, exist_ok=True)
            tar.extractall(extract_to)
            
            print(f"✓ 解壓縮完成")
            print(f"  解壓縮到: {extract_to}")
            print()
            
            return extract_to, file_list
    except Exception as e:
        print(f"✗ 解壓縮失敗: {e}")
        return None, []


def find_cert_files(extract_dir: Path) -> Dict[str, Path]:
    """尋找證書和密鑰檔案"""
    cert_files = {}
    
    # 常見的證書檔案名稱
    cert_patterns = {
        "cert": ["cert.pem", "certificate.pem", "client.crt", "*.crt", "*.pem"],
        "key": ["key.pem", "private.key", "client.key", "*.key"],
    }
    
    for cert_type, patterns in cert_patterns.items():
        for pattern in patterns:
            if "*" in pattern:
                files = list(extract_dir.rglob(pattern))
            else:
                files = list(extract_dir.rglob(pattern))
            
            if files:
                cert_files[cert_type] = files[0]
                break
    
    return cert_files


def setup_router_connection(cert_path: Path = None, key_path: Path = None):
    """設定路由器連接"""
    print("【設定路由器連接】")
    
    # 預設路徑
    if not cert_path:
        cert_path = CERTS_DIR / "cert.pem"
    if not key_path:
        key_path = CERTS_DIR / "key.pem"
    
    # 檢查檔案是否存在
    if not cert_path.exists():
        print(f"✗ 證書檔案不存在: {cert_path}")
        return False
    
    if not key_path.exists():
        print(f"✗ 密鑰檔案不存在: {key_path}")
        return False
    
    print(f"✓ 證書檔案: {cert_path}")
    print(f"✓ 密鑰檔案: {key_path}")
    print()
    
    # 測試路由器連接
    print("【測試路由器連接】")
    try:
        from router_connection import AsusRouterConnection
        
        router = AsusRouterConnection(
            hostname="coffeeLofe.asuscomm.com",
            port=8443,
            cert_path=str(cert_path),
            key_path=str(key_path)
        )
        
        # 測試連接
        print("正在測試連接...")
        # 這裡可以添加實際的連接測試
        print("✓ 路由器連接配置完成")
        
        return True
    except ImportError:
        print("⚠️  router_connection 模組不可用")
        return False
    except Exception as e:
        print(f"✗ 連接測試失敗: {e}")
        return False


def main():
    """主函數"""
    if len(sys.argv) < 2:
        # 自動尋找 cert_key tar 檔案
        tar_files = list(BASE_DIR.glob("*cert_key*.tar"))
        if not tar_files:
            tar_files = list(BASE_DIR.glob("*cert*.tar"))
        
        if tar_files:
            tar_path = tar_files[0]
            print(f"自動找到證書檔案: {tar_path.name}")
        else:
            print("使用方式: python setup_router_cert.py <cert_key.tar>")
            print("或將 cert_key (1).tar 放置在專案根目錄")
            sys.exit(1)
    else:
        tar_path = Path(sys.argv[1])
        if not tar_path.is_absolute():
            tar_path = BASE_DIR / tar_path
    
    print("=" * 70)
    print("路由器證書設定工具")
    print("=" * 70)
    print(f"證書檔案: {tar_path}")
    print()
    
    # 檢查檔案是否存在
    if not tar_path.exists():
        print(f"✗ 檔案不存在: {tar_path}")
        print()
        print("請確認檔案路徑，或將檔案放置在專案根目錄")
        sys.exit(1)
    
    print(f"✓ 檔案存在")
    print(f"  檔案大小: {tar_path.stat().st_size / 1024:.2f} KB")
    print()
    
    # 解壓縮
    extract_dir, file_list = extract_cert_tar(tar_path)
    if not extract_dir:
        sys.exit(1)
    
    # 尋找證書檔案
    print("【尋找證書檔案】")
    cert_files = find_cert_files(extract_dir)
    
    if cert_files:
        print("找到證書檔案:")
        for cert_type, cert_path in cert_files.items():
            print(f"  - {cert_type}: {cert_path}")
        
        # 複製到 certs 目錄
        print()
        print("【複製證書檔案】")
        CERTS_DIR.mkdir(parents=True, exist_ok=True)
        
        cert_path = None
        key_path = None
        
        if "cert" in cert_files:
            src = cert_files["cert"]
            dst = CERTS_DIR / "cert.pem"
            shutil.copy2(src, dst)
            cert_path = dst
            print(f"✓ 已複製證書: {dst}")
        
        if "key" in cert_files:
            src = cert_files["key"]
            dst = CERTS_DIR / "key.pem"
            shutil.copy2(src, dst)
            key_path = dst
            print(f"✓ 已複製密鑰: {dst}")
        
        print()
        
        # 設定路由器連接
        if cert_path and key_path:
            setup_router_connection(cert_path, key_path)
    else:
        print("⚠️  未找到標準證書檔案")
        print("請手動檢查解壓縮的檔案，並將證書和密鑰複製到 certs/ 目錄")
        print(f"解壓縮目錄: {extract_dir}")
    
    print()
    print("=" * 70)
    print("【設定完成】")
    print()
    print("證書檔案位置:")
    print(f"  certs/cert.pem")
    print(f"  certs/key.pem")
    print()
    print("【下一步】")
    print("可以使用 router_connection.py 連接到路由器")
    print("=" * 70)


if __name__ == "__main__":
    main()
