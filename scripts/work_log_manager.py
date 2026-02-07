#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
work_log_manager.py

系統工作日誌管理器

功能：
- 自動記錄系統工作執行情況
- 維護工作日誌檔案
- 提供日誌查詢功能
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
WORK_LOG_FILE = BASE_DIR / "reports" / "SYSTEM_WORK_LOGS.md"

class WorkLogManager:
    """工作日誌管理器"""
    
    def __init__(self, log_file: Path = WORK_LOG_FILE):
        self.log_file = log_file
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """確保日誌檔案存在"""
        if not self.log_file.exists():
            self.create_log_file()
    
    def create_log_file(self):
        """建立日誌檔案"""
        header = """# 五常系統工作日誌

**建立時間：** {create_time}  
**維護者：** 雙J工作小組（雲端小J指揮）  
**更新頻率：** 實時更新

---

## 📋 日誌說明

本檔案記錄所有系統維護與優化工作的執行記錄，包含：
- 工作執行時間
- 執行內容
- 執行結果
- 負責AI代理
- 相關檔案/腳本

---

## 📊 工作統計

### 今日工作
- **日期：** {today}
- **總工作數：** 0
- **完成數：** 0
- **進行中：** 0
- **失敗數：** 0

---

## 📝 工作日誌

### {today}

---

## 📅 歷史記錄

---

**最後更新時間：** {last_update}  
**當前狀態：** 系統工作日誌運行中
""".format(
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            today=datetime.now().strftime("%Y-%m-%d"),
            last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.write_text(header, encoding='utf-8')
    
    def log_work(self, 
                 work_type: str,
                 work_content: str,
                 agent: str = "little_j",
                 status: str = "進行中",
                 result: Optional[str] = None,
                 related_files: Optional[List[str]] = None,
                 error: Optional[str] = None,
                 permission_level: str = "最高權限"):
        """
        記錄工作執行情況
        
        參數:
            work_type: 工作類型（如：系統維護、配置更新等）
            work_content: 工作內容描述
            agent: 負責的AI代理（little_j 或 jules）
            status: 執行狀態（進行中、完成、失敗）
            result: 執行結果描述
            related_files: 相關檔案列表
            error: 錯誤訊息（如果失敗）
            permission_level: 權限等級（預設：最高權限）
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 讀取現有日誌
        if self.log_file.exists():
            content = self.log_file.read_text(encoding='utf-8')
        else:
            content = ""
            self.create_log_file()
            content = self.log_file.read_text(encoding='utf-8')
        
        # 建立工作記錄
        status_icon = {
            "進行中": "🔄",
            "完成": "✅",
            "失敗": "❌",
            "待開始": "⏳"
        }.get(status, "•")
        
        work_entry = f"""
#### {timestamp} - {work_type}

- **負責代理：** {agent} ({'小J' if agent == 'little_j' else 'Jules'})
- **權限等級：** 🔐 {permission_level}
- **工作內容：** {work_content}
- **狀態：** {status_icon} {status}
"""
        
        if result:
            work_entry += f"- **執行結果：** {result}\n"
        
        if related_files:
            work_entry += f"- **相關檔案：** {', '.join(related_files)}\n"
        
        if error:
            work_entry += f"- **錯誤訊息：** {error}\n"
        
        work_entry += "\n---\n"
        
        # 插入到今日日誌區塊
        today_section = f"### {today}"
        if today_section in content:
            # 在今日區塊後插入新記錄
            insert_pos = content.find(today_section) + len(today_section)
            # 找到下一個日期區塊或歷史記錄區塊
            next_date_pos = content.find("### ", insert_pos)
            history_pos = content.find("## 📅 歷史記錄", insert_pos)
            
            if next_date_pos != -1 and (history_pos == -1 or next_date_pos < history_pos):
                insert_pos = next_date_pos
            elif history_pos != -1:
                insert_pos = history_pos
            else:
                insert_pos = len(content)
            
            new_content = content[:insert_pos] + work_entry + content[insert_pos:]
        else:
            # 建立今日區塊
            log_section = content.find("## 📝 工作日誌")
            if log_section != -1:
                history_section = content.find("## 📅 歷史記錄")
                if history_section != -1:
                    # 在歷史記錄前插入今日區塊
                    new_content = content[:history_section] + f"## 📝 工作日誌\n\n{today_section}\n{work_entry}\n" + content[history_section:]
                else:
                    new_content = content + f"\n## 📝 工作日誌\n\n{today_section}\n{work_entry}\n"
            else:
                new_content = content + f"\n## 📝 工作日誌\n\n{today_section}\n{work_entry}\n"
        
        # 更新最後更新時間
        if "**最後更新時間：**" in new_content:
            import re
            new_content = re.sub(
                r'\*\*最後更新時間：\*\* .*',
                f'**最後更新時間：** {timestamp}',
                new_content
            )
        
        # 寫回檔案
        self.log_file.write_text(new_content, encoding='utf-8')
        
        return True
    
    def update_statistics(self):
        """更新工作統計"""
        if not self.log_file.exists():
            return
        
        content = self.log_file.read_text(encoding='utf-8')
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 計算統計（簡化版，可根據需要擴展）
        # 這裡可以解析日誌內容計算統計數據
        
        return True

def main():
    """測試功能"""
    manager = WorkLogManager()
    
    # 測試記錄
    manager.log_work(
        work_type="系統初始化",
        work_content="建立系統工作日誌檔案",
        agent="little_j",
        status="完成",
        result="工作日誌系統已建立並運行",
        related_files=["scripts/work_log_manager.py", "reports/SYSTEM_WORK_LOGS.md"]
    )
    
    print("✅ 工作日誌記錄測試完成")

if __name__ == "__main__":
    main()
