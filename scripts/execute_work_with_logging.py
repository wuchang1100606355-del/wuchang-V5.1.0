#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
execute_work_with_logging.py

執行工作並自動記錄到工作日誌

功能：
- 提供統一的介面執行任何系統工作
- 自動記錄到系統工作日誌
- 支援錯誤處理和狀態更新
"""

import sys
import subprocess
from pathlib import Path
from typing import Callable, Optional, Dict, Any

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
from work_log_manager import WorkLogManager

def execute_work(work_type: str,
                 work_content: str,
                 work_function: Callable,
                 agent: str = "little_j",
                 related_files: Optional[list] = None,
                 **kwargs) -> Dict[str, Any]:
    """
    執行工作並自動記錄到工作日誌
    
    參數:
        work_type: 工作類型
        work_content: 工作內容描述
        work_function: 執行工作的函數
        agent: 負責的AI代理
        related_files: 相關檔案列表
        **kwargs: 傳給工作函數的額外參數
    
    返回:
        執行結果字典
    """
    log_manager = WorkLogManager()
    
    # 記錄工作開始
    log_manager.log_work(
        work_type=work_type,
        work_content=work_content,
        agent=agent,
        status="進行中",
        related_files=related_files or []
    )
    
    try:
        # 執行工作
        result = work_function(**kwargs)
        
        # 記錄成功
        log_manager.log_work(
            work_type=work_type,
            work_content=work_content,
            agent=agent,
            status="完成",
            result=str(result) if result else "工作執行成功",
            related_files=related_files or []
        )
        
        return {
            "success": True,
            "result": result,
            "error": None
        }
        
    except Exception as e:
        # 記錄失敗
        error_msg = str(e)
        log_manager.log_work(
            work_type=work_type,
            work_content=work_content,
            agent=agent,
            status="失敗",
            error=error_msg,
            related_files=related_files or []
        )
        
        return {
            "success": False,
            "result": None,
            "error": error_msg
        }

def execute_script(script_path: Path,
                   work_type: str,
                   work_content: str,
                   agent: str = "little_j",
                   args: Optional[list] = None) -> Dict[str, Any]:
    """
    執行腳本並記錄到工作日誌
    
    參數:
        script_path: 腳本路徑
        work_type: 工作類型
        work_content: 工作內容描述
        agent: 負責的AI代理
        args: 腳本參數
    """
    def run_script():
        cmd = ["python", str(script_path)]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            raise Exception(f"腳本執行失敗: {result.stderr}")
        
        return result.stdout
    
    return execute_work(
        work_type=work_type,
        work_content=work_content,
        work_function=run_script,
        agent=agent,
        related_files=[str(script_path)]
    )

if __name__ == "__main__":
    # 測試功能
    print("測試工作日誌記錄功能...")
    
    def test_work():
        return "測試工作執行成功"
    
    result = execute_work(
        work_type="測試工作",
        work_content="測試工作日誌記錄功能",
        work_function=test_work,
        agent="little_j"
    )
    
    print(f"執行結果: {result}")
