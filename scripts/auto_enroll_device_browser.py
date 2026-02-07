#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動化設備納管腳本（使用瀏覽器自動化）
用途：自動化在 Odoo 中納管 v3_mix_edla_gl 設備
"""

import asyncio
import sys
import os
import argparse
from browser_automation import BrowserAutomation
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
_logger = logging.getLogger(__name__)


async def auto_enroll_device(
    odoo_url: str = "http://192.168.50.249:8069",
    username: str = "admin",
    password: str = "admin",
    database: str = "admin",
    device_name: str = "v3_mix_edla_gl",
    device_ip: str = "192.168.50.86",
    device_port: int = 41895,
    headless: bool = False
):
    """
    自動化納管設備
    
    Args:
        odoo_url: Odoo 基礎 URL
        username: Odoo 使用者名稱
        password: Odoo 密碼
        database: 資料庫名稱
        device_name: 設備名稱
        device_ip: 設備 IP 地址
        device_port: 設備通訊埠
        headless: 是否使用無頭模式
    """
    automation = BrowserAutomation(headless=headless)
    
    try:
        _logger.info("啟動瀏覽器自動化...")
        if not await automation.start():
            _logger.error("無法啟動瀏覽器")
            return False
        
        # 登入 Odoo
        _logger.info(f"登入 Odoo: {odoo_url}")
        if not await automation.login_odoo(odoo_url, username, password, database):
            _logger.error("Odoo 登入失敗")
            return False
        
        # 準備設備資訊
        device_info = {
            'name': device_name,
            'ip_address': device_ip,
            'device_type': 'pos',
            'status': 'online',
            'note': f"""Android 13 POS 設備
IP: {device_ip}:{device_port}
開發者模式: 已開啟
USB/GPU/WiFi 偵錯: 已開啟
納管時間: {asyncio.get_event_loop().time()}"""
        }
        
        # 納管設備
        _logger.info(f"開始納管設備: {device_name}")
        if not await automation.enroll_device_in_odoo(device_info):
            _logger.error("設備納管失敗")
            return False
        
        # 截圖確認
        screenshot_path = f"downloads/enrollment_{device_name}_{int(asyncio.get_event_loop().time())}.png"
        os.makedirs("downloads", exist_ok=True)
        await automation.take_screenshot(screenshot_path)
        
        _logger.info(f"✅ 設備納管成功: {device_name}")
        _logger.info(f"截圖已儲存: {screenshot_path}")
        
        # 等待一段時間以便觀察結果
        await asyncio.sleep(3)
        
        return True
        
    except Exception as e:
        _logger.error(f"自動化納管失敗: {e}")
        return False
    finally:
        await automation.stop()


def main():
    parser = argparse.ArgumentParser(description='自動化設備納管（瀏覽器自動化）')
    parser.add_argument('--odoo-url', type=str, default='http://192.168.50.249:8069',
                        help='Odoo 基礎 URL')
    parser.add_argument('--username', type=str, default='admin',
                        help='Odoo 使用者名稱')
    parser.add_argument('--password', type=str, default='admin',
                        help='Odoo 密碼')
    parser.add_argument('--database', type=str, default='admin',
                        help='資料庫名稱')
    parser.add_argument('--device-name', type=str, default='v3_mix_edla_gl',
                        help='設備名稱')
    parser.add_argument('--device-ip', type=str, default='192.168.50.86',
                        help='設備 IP 地址')
    parser.add_argument('--device-port', type=int, default=41895,
                        help='設備通訊埠')
    parser.add_argument('--headless', action='store_true',
                        help='使用無頭模式（不顯示瀏覽器視窗）')
    
    args = parser.parse_args()
    
    success = asyncio.run(auto_enroll_device(
        odoo_url=args.odoo_url,
        username=args.username,
        password=args.password,
        database=args.database,
        device_name=args.device_name,
        device_ip=args.device_ip,
        device_port=args.device_port,
        headless=args.headless
    ))
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
