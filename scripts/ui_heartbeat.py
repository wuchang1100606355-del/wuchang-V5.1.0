#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI 心跳服務
用途：UI 設備定時發送心跳到 VM 伺服器，讓伺服器知道 UI 設備在線狀態
"""

import requests
import time
import socket
import sys
import argparse
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [UI-Heartbeat] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 預設設定
DEFAULT_VM_IP = "192.168.50.84"
DEFAULT_INTERVAL = 30  # 秒

def get_local_ip():
    """獲取本機 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.warning(f"無法獲取本機 IP，使用 127.0.0.1: {e}")
        return '127.0.0.1'

def get_hostname():
    """獲取主機名稱"""
    try:
        return socket.gethostname()
    except Exception:
        return 'Unknown'

def send_heartbeat(vm_ip, device_ip, device_name, interval):
    """發送心跳到 VM 伺服器"""
    heartbeat_url = f"http://{vm_ip}:8069/wuchang/ui/heartbeat"
    
    logger.info(f"UI 心跳服務啟動")
    logger.info(f"  VM 伺服器: {vm_ip}")
    logger.info(f"  UI 設備 IP: {device_ip}")
    logger.info(f"  UI 設備名稱: {device_name}")
    logger.info(f"  心跳間隔: {interval} 秒")
    logger.info("")
    
    consecutive_failures = 0
    max_failures = 5
    
    while True:
        try:
            payload = {
                'device_ip': device_ip,
                'device_name': device_name
            }
            
            response = requests.post(
                heartbeat_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                is_proxying = data.get('is_proxying', False)
                status_msg = "代理中" if is_proxying else "正常"
                
                logger.info(f"✓ 心跳已發送 - 狀態: {status_msg}")
                
                if is_proxying:
                    logger.warning("⚠ 伺服器正在代理 UI 工作，請檢查 UI 設備連線狀態")
                
                consecutive_failures = 0
            else:
                logger.warning(f"⚠ 心跳發送失敗: HTTP {response.status_code}")
                consecutive_failures += 1
                
        except requests.exceptions.ConnectionError:
            consecutive_failures += 1
            logger.error(f"✗ 無法連接到 VM 伺服器 {vm_ip}:8069")
            logger.error("  請確認：")
            logger.error("    1. VM 伺服器的 Odoo 服務正在運行")
            logger.error("    2. 網路連線正常")
            logger.error("    3. IP 地址正確")
            
        except requests.exceptions.Timeout:
            consecutive_failures += 1
            logger.error("✗ 連線超時")
            
        except Exception as e:
            consecutive_failures += 1
            logger.error(f"✗ 心跳發送失敗: {e}")
        
        # 如果連續失敗次數過多，建議檢查
        if consecutive_failures >= max_failures:
            logger.error(f"")
            logger.error(f"⚠ 連續 {consecutive_failures} 次心跳失敗")
            logger.error(f"  請檢查 VM 伺服器狀態和網路連線")
            logger.error(f"")
            consecutive_failures = 0  # 重置計數器，繼續嘗試
        
        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description='UI 心跳服務')
    parser.add_argument('--vm-ip', type=str, default=DEFAULT_VM_IP,
                        help=f'VM 伺服器 IP 地址（預設: {DEFAULT_VM_IP}）')
    parser.add_argument('--device-ip', type=str, default=None,
                        help='UI 設備 IP 地址（預設: 自動偵測）')
    parser.add_argument('--device-name', type=str, default=None,
                        help='UI 設備名稱（預設: 主機名稱）')
    parser.add_argument('--interval', type=int, default=DEFAULT_INTERVAL,
                        help=f'心跳間隔（秒，預設: {DEFAULT_INTERVAL}）')
    
    args = parser.parse_args()
    
    # 獲取設備資訊
    device_ip = args.device_ip or get_local_ip()
    device_name = args.device_name or get_hostname()
    
    try:
        send_heartbeat(
            vm_ip=args.vm_ip,
            device_ip=device_ip,
            device_name=device_name,
            interval=args.interval
        )
    except KeyboardInterrupt:
        logger.info("")
        logger.info("UI 心跳服務已停止")
        sys.exit(0)

if __name__ == '__main__':
    main()
