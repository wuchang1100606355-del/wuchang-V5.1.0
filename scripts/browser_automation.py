#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀏覽器自動化工作程序
用途：自動化瀏覽器操作，支援 Odoo、Google Tasks、Google Workspace 等
"""

import asyncio
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_logger = logging.getLogger(__name__)


class BrowserAutomation:
    """瀏覽器自動化類別"""
    
    def __init__(self, headless: bool = False, browser_type: str = "chromium"):
        """
        初始化瀏覽器自動化
        
        Args:
            headless: 是否使用無頭模式（不顯示瀏覽器視窗）
            browser_type: 瀏覽器類型 ("chromium", "firefox", "webkit")
        """
        self.headless = headless
        self.browser_type = browser_type
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def start(self):
        """啟動瀏覽器"""
        try:
            self.playwright = await async_playwright().start()
            
            if self.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    args=['--disable-blink-features=AutomationControlled']
                )
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=self.headless)
            else:
                raise ValueError(f"不支援的瀏覽器類型: {self.browser_type}")
            
            # 建立瀏覽器上下文（可設定使用者資料目錄、Cookie 等）
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            self.page = await self.context.new_page()
            _logger.info(f"瀏覽器已啟動: {self.browser_type}")
            return True
        except Exception as e:
            _logger.error(f"啟動瀏覽器失敗: {e}")
            return False
    
    async def stop(self):
        """關閉瀏覽器"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            _logger.info("瀏覽器已關閉")
        except Exception as e:
            _logger.error(f"關閉瀏覽器失敗: {e}")
    
    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """導航到指定 URL"""
        try:
            await self.page.goto(url, wait_until=wait_until)
            _logger.info(f"已導航到: {url}")
            return True
        except Exception as e:
            _logger.error(f"導航失敗: {e}")
            return False
    
    async def login_odoo(self, base_url: str, username: str, password: str, database: str = "admin"):
        """
        登入 Odoo
        
        Args:
            base_url: Odoo 基礎 URL (例如: http://192.168.50.249:8069)
            username: 使用者名稱
            password: 密碼
            database: 資料庫名稱
        """
        try:
            login_url = f"{base_url}/web/login"
            await self.navigate(login_url)
            
            # 等待登入表單載入
            await self.page.wait_for_selector('input[name="login"]', timeout=10000)
            
            # 填入登入資訊
            await self.page.fill('input[name="login"]', username)
            await self.page.fill('input[name="password"]', password)
            
            # 如果有資料庫選擇，選擇資料庫
            db_select = await self.page.query_selector('select[name="db"]')
            if db_select:
                await self.page.select_option('select[name="db"]', database)
            
            # 點擊登入按鈕
            await self.page.click('button[type="submit"]')
            
            # 等待登入完成（檢查是否跳轉到主頁）
            await self.page.wait_for_url('**/web**', timeout=15000)
            
            _logger.info(f"Odoo 登入成功: {username}")
            return True
        except Exception as e:
            _logger.error(f"Odoo 登入失敗: {e}")
            return False
    
    async def enroll_device_in_odoo(self, device_info: Dict[str, Any]):
        """
        在 Odoo 中納管設備
        
        Args:
            device_info: 設備資訊字典
                - name: 設備名稱
                - ip_address: IP 地址
                - device_type: 設備類型
                - status: 狀態
                - note: 備註
        """
        try:
            # 導航到設備管理頁面
            devices_url = "/web#action=&model=wuchang.infrastructure.device&view_type=list&menu_id="
            await self.navigate(f"{self.page.url.split('/web')[0]}/web{devices_url}")
            
            # 等待頁面載入
            await self.page.wait_for_load_state('networkidle')
            
            # 點擊「建立」按鈕
            create_button = await self.page.query_selector('button.o_list_button_add')
            if create_button:
                await create_button.click()
            else:
                # 嘗試其他可能的建立按鈕選擇器
                await self.page.click('button:has-text("建立")', timeout=5000)
            
            # 等待表單載入
            await self.page.wait_for_selector('input[name="name"]', timeout=10000)
            
            # 填入設備資訊
            await self.page.fill('input[name="name"]', device_info.get('name', ''))
            await self.page.fill('input[name="ip_address"]', device_info.get('ip_address', ''))
            
            # 選擇設備類型
            device_type_select = await self.page.query_selector('select[name="device_type"]')
            if device_type_select:
                await self.page.select_option('select[name="device_type"]', device_info.get('device_type', 'pos'))
            
            # 選擇狀態
            status_select = await self.page.query_selector('select[name="status"]')
            if status_select:
                await self.page.select_option('select[name="status"]', device_info.get('status', 'online'))
            
            # 填入備註（如果有備註欄位）
            note_field = await self.page.query_selector('textarea[name="note"]')
            if note_field and device_info.get('note'):
                await self.page.fill('textarea[name="note"]', device_info.get('note', ''))
            
            # 儲存
            save_button = await self.page.query_selector('button.o_form_button_save')
            if save_button:
                await save_button.click()
            else:
                await self.page.click('button:has-text("儲存")', timeout=5000)
            
            # 等待儲存完成
            await self.page.wait_for_load_state('networkidle')
            
            _logger.info(f"設備納管成功: {device_info.get('name')}")
            return True
        except Exception as e:
            _logger.error(f"設備納管失敗: {e}")
            return False
    
    async def access_google_tasks(self, task_url: str, cookies: Optional[Dict] = None):
        """
        訪問 Google Tasks
        
        Args:
            task_url: Google Tasks URL
            cookies: 可選的 Cookie 字典
        """
        try:
            # 如果有 Cookie，先設定
            if cookies:
                await self.context.add_cookies(cookies)
            
            await self.navigate(task_url)
            
            # 等待頁面載入
            await self.page.wait_for_load_state('networkidle')
            
            _logger.info(f"已訪問 Google Tasks: {task_url}")
            return True
        except Exception as e:
            _logger.error(f"訪問 Google Tasks 失敗: {e}")
            return False
    
    async def take_screenshot(self, filepath: str):
        """截圖"""
        try:
            await self.page.screenshot(path=filepath, full_page=True)
            _logger.info(f"截圖已儲存: {filepath}")
            return True
        except Exception as e:
            _logger.error(f"截圖失敗: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = 10000):
        """等待元素出現"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            _logger.warning(f"等待元素失敗: {selector}, {e}")
            return False


async def main():
    """主函數範例"""
    automation = BrowserAutomation(headless=False)
    
    try:
        await automation.start()
        
        # 範例：登入 Odoo
        # await automation.login_odoo(
        #     base_url="http://192.168.50.249:8069",
        #     username="admin",
        #     password="admin"
        # )
        
        # 範例：納管設備
        # device_info = {
        #     'name': 'v3_mix_edla_gl',
        #     'ip_address': '192.168.50.86',
        #     'device_type': 'pos',
        #     'status': 'online',
        #     'note': 'Android 13 POS 設備，開發者模式已開啟'
        # }
        # await automation.enroll_device_in_odoo(device_info)
        
        # 等待一段時間以便觀察
        await asyncio.sleep(5)
        
    finally:
        await automation.stop()


if __name__ == '__main__':
    asyncio.run(main())
