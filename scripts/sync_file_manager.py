#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_file_manager.py

雲端空間與外接硬碟檔案同步管理工具

規則：
1. 雲端空間為主要資料夾區
2. 找不到依賴檔案時，可從外接硬碟調用
3. 寫入檔案時，需同時寫入雲端空間和外接硬碟
"""

import sys
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
import json

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

# 路徑設定
CLOUD_SPACE_PATH = Path(r"G:\共用雲端硬碟\五常雲端空間")
EXTERNAL_DRIVE_PATH = Path(r"E:\wuchang V5.1.0")
CONFIG_FILE = CLOUD_SPACE_PATH / "config" / "sync_config.json"


class SyncFileManager:
    """檔案同步管理器"""
    
    def __init__(self):
        self.cloud_space = CLOUD_SPACE_PATH
        self.external_drive = EXTERNAL_DRIVE_PATH
        self.load_config()
    
    def load_config(self):
        """載入配置"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            self.config = {
                "cloud_space_path": str(self.cloud_space),
                "external_drive_path": str(self.external_drive),
                "sync_rules": {
                    "read_priority": "cloud_space",
                    "write_mode": "both"
                }
            }
            self.save_config()
    
    def save_config(self):
        """儲存配置"""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def find_file(self, file_path: str) -> Optional[Path]:
        """
        尋找檔案（優先從雲端空間，找不到則從外接硬碟）
        
        Args:
            file_path: 相對路徑（相對於根目錄）
            
        Returns:
            找到的檔案路徑，如果找不到返回 None
        """
        # 優先從雲端空間尋找
        cloud_file = self.cloud_space / file_path
        if cloud_file.exists():
            return cloud_file
        
        # 從外接硬碟尋找
        external_file = self.external_drive / file_path
        if external_file.exists():
            return external_file
        
        return None
    
    def read_file(self, file_path: str) -> Optional[str]:
        """
        讀取檔案（優先從雲端空間，找不到則從外接硬碟）
        
        Args:
            file_path: 相對路徑
            
        Returns:
            檔案內容，如果找不到返回 None
        """
        file_location = self.find_file(file_path)
        
        if file_location:
            try:
                with open(file_location, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"讀取檔案失敗: {file_location} - {e}")
                return None
        
        return None
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        寫入檔案（同時寫入雲端空間和外接硬碟）
        
        Args:
            file_path: 相對路徑
            content: 檔案內容
            encoding: 編碼格式
            
        Returns:
            是否成功寫入兩邊
        """
        cloud_file = self.cloud_space / file_path
        external_file = self.external_drive / file_path
        
        success_cloud = False
        success_external = False
        
        # 寫入雲端空間
        try:
            cloud_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cloud_file, 'w', encoding=encoding) as f:
                f.write(content)
            success_cloud = True
            print(f"✓ 已寫入雲端空間: {cloud_file}")
        except Exception as e:
            print(f"✗ 寫入雲端空間失敗: {cloud_file} - {e}")
        
        # 寫入外接硬碟
        try:
            external_file.parent.mkdir(parents=True, exist_ok=True)
            with open(external_file, 'w', encoding=encoding) as f:
                f.write(content)
            success_external = True
            print(f"✓ 已寫入外接硬碟: {external_file}")
        except Exception as e:
            print(f"⚠ 寫入外接硬碟失敗: {external_file} - {e}")
            print("   注意：外接硬碟可能未連接或路徑不存在")
        
        return success_cloud and success_external
    
    def copy_file_to_both(self, source_path: str, relative_path: str) -> bool:
        """
        複製檔案到兩邊（雲端空間和外接硬碟）
        
        Args:
            source_path: 來源檔案完整路徑
            relative_path: 目標相對路徑
            
        Returns:
            是否成功複製到兩邊
        """
        source = Path(source_path)
        if not source.exists():
            print(f"✗ 來源檔案不存在: {source_path}")
            return False
        
        cloud_file = self.cloud_space / relative_path
        external_file = self.external_drive / relative_path
        
        success_cloud = False
        success_external = False
        
        # 複製到雲端空間
        try:
            cloud_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, cloud_file)
            success_cloud = True
            print(f"✓ 已複製到雲端空間: {cloud_file}")
        except Exception as e:
            print(f"✗ 複製到雲端空間失敗: {cloud_file} - {e}")
        
        # 複製到外接硬碟
        try:
            external_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, external_file)
            success_external = True
            print(f"✓ 已複製到外接硬碟: {external_file}")
        except Exception as e:
            print(f"⚠ 複製到外接硬碟失敗: {external_file} - {e}")
            print("   注意：外接硬碟可能未連接或路徑不存在")
        
        return success_cloud and success_external
    
    def sync_from_external(self, relative_path: str) -> bool:
        """
        從外接硬碟同步檔案到雲端空間（如果雲端空間沒有該檔案）
        
        Args:
            relative_path: 相對路徑
            
        Returns:
            是否成功同步
        """
        cloud_file = self.cloud_space / relative_path
        external_file = self.external_drive / relative_path
        
        # 如果雲端空間已有檔案，不覆蓋
        if cloud_file.exists():
            print(f"✓ 雲端空間已有檔案，跳過: {relative_path}")
            return True
        
        # 如果外接硬碟有檔案，複製到雲端空間
        if external_file.exists():
            try:
                cloud_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(external_file, cloud_file)
                print(f"✓ 已從外接硬碟同步到雲端空間: {relative_path}")
                return True
            except Exception as e:
                print(f"✗ 同步失敗: {relative_path} - {e}")
                return False
        
        print(f"⚠ 兩邊都沒有檔案: {relative_path}")
        return False
    
    def ensure_file_exists(self, relative_path: str) -> Optional[Path]:
        """
        確保檔案存在（如果不存在，從外接硬碟複製到雲端空間）
        
        Args:
            relative_path: 相對路徑
            
        Returns:
            檔案路徑，如果不存在且無法同步則返回 None
        """
        # 檢查雲端空間
        cloud_file = self.cloud_space / relative_path
        if cloud_file.exists():
            return cloud_file
        
        # 從外接硬碟同步
        if self.sync_from_external(relative_path):
            return cloud_file
        
        return None


def main():
    """主程式 - 示範用法"""
    print("=" * 70)
    print("雲端空間與外接硬碟檔案同步管理工具")
    print("=" * 70)
    print()
    
    manager = SyncFileManager()
    
    print("配置:")
    print(f"  雲端空間: {manager.cloud_space}")
    print(f"  外接硬碟: {manager.external_drive}")
    print()
    
    # 示範：尋找檔案
    print("示範：尋找檔案")
    test_file = manager.find_file("README.md")
    if test_file:
        print(f"  找到檔案: {test_file}")
    else:
        print("  檔案不存在")
    print()
    
    # 示範：讀取檔案
    print("示範：讀取檔案")
    content = manager.read_file("README.md")
    if content:
        print(f"  檔案內容長度: {len(content)} 字元")
    else:
        print("  無法讀取檔案")
    print()
    
    # 示範：確保檔案存在
    print("示範：確保檔案存在")
    file_path = manager.ensure_file_exists("requirements.txt")
    if file_path:
        print(f"  檔案已確保存在: {file_path}")
    else:
        print("  無法確保檔案存在")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已中斷")
        sys.exit(0)
    except Exception as e:
        print(f"發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
