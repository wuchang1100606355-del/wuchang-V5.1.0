#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動化 Google Tasks 操作
用途：自動化訪問和操作 Google Tasks
"""

import asyncio
import sys
import os
import argparse
import json
from browser_automation import BrowserAutomation
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
_logger = logging.getLogger(__name__)


async def auto_google_tasks(
    task_url: str,
    cookies_file: str = None,
    headless: bool = False,
    take_screenshot: bool = True
):
    """
    自動化訪問 Google Tasks
    
    Args:
        task_url: Google Tasks URL
        cookies_file: Cookie 檔案路徑（JSON 格式）
        headless: 是否使用無頭模式
        take_screenshot: 是否截圖
    """
    automation = BrowserAutomation(headless=headless)
    
    try:
        _logger.info("啟動瀏覽器自動化...")
        if not await automation.start():
            _logger.error("無法啟動瀏覽器")
            return False
        
        # 載入 Cookie（如果有）
        cookies = None
        if cookies_file and os.path.exists(cookies_file):
            try:
                with open(cookies_file, 'r', encoding='utf-8') as f:
                    cookies_data = json.load(f)
                    # Playwright 需要的 Cookie 格式
                    if isinstance(cookies_data, list):
                        cookies = cookies_data
                    else:
                        # 如果是單一 Cookie 字串，需要轉換
                        _logger.warning("Cookie 格式可能需要轉換，請確認格式")
            except Exception as e:
                _logger.warning(f"載入 Cookie 失敗: {e}")
        
        # 訪問 Google Tasks
        _logger.info(f"訪問 Google Tasks: {task_url}")
        if not await automation.access_google_tasks(task_url, cookies):
            _logger.error("訪問 Google Tasks 失敗")
            return False
        
        # 等待頁面載入
        await asyncio.sleep(3)
        
        # 截圖（如果需要）
        if take_screenshot:
            screenshot_path = f"downloads/google_tasks_{int(asyncio.get_event_loop().time())}.png"
            os.makedirs("downloads", exist_ok=True)
            await automation.take_screenshot(screenshot_path)
            _logger.info(f"截圖已儲存: {screenshot_path}")
        
        # 等待一段時間以便觀察
        await asyncio.sleep(5)
        
        return True
        
    except Exception as e:
        _logger.error(f"自動化 Google Tasks 失敗: {e}")
        return False
    finally:
        await automation.stop()


def main():
    parser = argparse.ArgumentParser(description='自動化 Google Tasks 操作')
    parser.add_argument('--task-url', type=str,
                        default='https://jules.google.com/task/14099380313947031783',
                        help='Google Tasks URL')
    parser.add_argument('--cookies-file', type=str,
                        help='Cookie 檔案路徑（JSON 格式）')
    parser.add_argument('--headless', action='store_true',
                        help='使用無頭模式（不顯示瀏覽器視窗）')
    parser.add_argument('--no-screenshot', action='store_true',
                        help='不截圖')
    
    args = parser.parse_args()
    
    success = asyncio.run(auto_google_tasks(
        task_url=args.task_url,
        cookies_file=args.cookies_file,
        headless=args.headless,
        take_screenshot=not args.no_screenshot
    ))
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
