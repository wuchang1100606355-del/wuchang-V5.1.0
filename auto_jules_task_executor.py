#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_jules_task_executor.py

自動檢查並執行 JULES 的任務（無人職守模式）

功能：
- 自動檢查 Google Tasks 中的新任務
- 自動解析任務指令
- 自動執行任務
- 自動回報結果
- 支援背景運行
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "jules_task_executor_state.json"
LOG_FILE = BASE_DIR / "jules_task_executor.log"
JULES_MEMORY_BANK_FILE = BASE_DIR / "jules_memory_bank.json"


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # 輸出到控制台
    print(log_entry.strip())
    
    # 寫入日誌檔案
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass


def load_memory_bank() -> Dict[str, Any]:
    """讀取 JULES 記憶庫（每次工作前必須讀取）"""
    if not JULES_MEMORY_BANK_FILE.exists():
        log("記憶庫檔案不存在", "WARN")
        return {}
    
    try:
        memory = json.loads(JULES_MEMORY_BANK_FILE.read_text(encoding="utf-8"))
        log("已讀取 JULES 記憶庫", "INFO")
        log(f"記憶庫版本: {memory.get('version', 'unknown')}", "INFO")
        log(f"最後更新: {memory.get('last_updated', 'unknown')}", "INFO")
        
        # 標準化鍵名（支援多種格式）
        if "system_architecture" in memory:
            arch = memory["system_architecture"]
            if "container_architecture" in arch and "容器架構" not in arch:
                arch["容器架構"] = arch["container_architecture"]
        
        return memory
    except Exception as e:
        log(f"讀取記憶庫失敗: {e}", "ERROR")
        return {}


def update_memory_bank(updates: Dict[str, Any], contributor: str = "雲端小 j (JULES)"):
    """更新記憶庫（工作後必須存檔）"""
    try:
        # 讀取現有記憶庫
        if JULES_MEMORY_BANK_FILE.exists():
            memory = json.loads(JULES_MEMORY_BANK_FILE.read_text(encoding="utf-8"))
        else:
            memory = {}
        
        # 更新內容
        for key, value in updates.items():
            if key == "system_architecture" and isinstance(value, dict):
                memory.setdefault("system_architecture", {})["last_architecture_update"] = datetime.now().isoformat()
                contributors = memory.setdefault("system_architecture", {}).setdefault("contributors", [])
                if "地端小 j" not in contributors:
                    contributors.append("地端小 j")
                if "雲端小 j (JULES)" not in contributors:
                    contributors.append("雲端小 j (JULES)")
            
            if isinstance(value, dict) and key in memory and isinstance(memory[key], dict):
                memory[key].update(value)
            else:
                memory[key] = value
        
        # 更新元資料
        memory["last_updated"] = datetime.now().isoformat()
        memory["updated_by"] = contributor
        
        # 儲存
        JULES_MEMORY_BANK_FILE.write_text(
            json.dumps(memory, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        log(f"已更新記憶庫（貢獻者: {contributor}）", "INFO")
        return True
    except Exception as e:
        log(f"更新記憶庫失敗: {e}", "ERROR")
        return False


def load_state() -> Dict[str, Any]:
    """載入執行狀態"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {
        "last_check": None,
        "processed_tasks": [],
        "last_task_id": None,
    }


def save_state(state: Dict[str, Any]):
    """儲存執行狀態"""
    try:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"儲存狀態失敗: {e}", "ERROR")


def get_new_tasks(last_check_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """獲取新任務"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 獲取任務列表
        task_lists = integration.list_task_lists()
        
        new_tasks = []
        
        for task_list in task_lists:
            # 只檢查包含 "Wuchang" 或 "File Sync" 的任務列表
            if "Wuchang" not in task_list.title and "File Sync" not in task_list.title:
                continue
            
            # 獲取任務列表中的所有任務
            tasks = integration.list_tasks(task_list.id)
            
            for task in tasks:
                # 只處理未完成的任務
                if task.status == "completed":
                    continue
                
                # 檢查是否是新任務（如果提供了上次檢查時間）
                if last_check_time:
                    try:
                        task_updated = datetime.fromisoformat(task.updated.replace('Z', '+00:00'))
                        if task_updated <= last_check_time:
                            continue
                    except:
                        pass
                
                new_tasks.append({
                    "id": task.id,
                    "list_id": task_list.id,
                    "title": task.title,
                    "notes": task.notes,
                    "status": task.status,
                    "updated": task.updated,
                })
        
        return new_tasks
        
    except Exception as e:
        log(f"獲取任務失敗: {e}", "ERROR")
        return []


def parse_task_instruction(notes: str) -> Dict[str, Any]:
    """解析任務指令"""
    instruction = {
        "type": "unknown",
        "command": None,
        "params": {},
    }
    
    if not notes:
        return instruction
    
    notes_lower = notes.lower()
    
    # 檢查指令類型
    if "執行" in notes or "執行" in notes_lower or "run" in notes_lower:
        instruction["type"] = "execute"
    elif "同步" in notes or "sync" in notes_lower:
        instruction["type"] = "sync"
    elif "檢查" in notes or "check" in notes_lower:
        instruction["type"] = "check"
    elif "上傳" in notes or "upload" in notes_lower:
        instruction["type"] = "upload"
    elif "下載" in notes or "download" in notes_lower:
        instruction["type"] = "download"
    
    # 提取命令（如果包含代碼塊）
    import re
    code_blocks = re.findall(r'```(?:bash|powershell|python)?\n(.*?)```', notes, re.DOTALL)
    if code_blocks:
        instruction["command"] = code_blocks[0].strip()
    
    return instruction


def execute_task(task: Dict[str, Any], memory_bank: Dict[str, Any] = None) -> Dict[str, Any]:
    """執行任務（工作前已讀取記憶庫）"""
    log(f"開始執行任務: {task['title']}", "INFO")
    
    # 記錄工作日誌：任務開始
    try:
        from dual_j_work_log import add_work_log
        add_work_log(
            agent="雲端小 j (JULES)",
            work_type="任務執行",
            description=f"開始執行任務：{task['title']}",
            status="in_progress",
            details={"task_id": task.get("id"), "task_title": task.get("title")}
        )
    except:
        pass
    
    instruction = parse_task_instruction(task.get("notes", ""))
    
    result = {
        "task_id": task["id"],
        "task_title": task["title"],
        "instruction_type": instruction["type"],
        "success": False,
        "output": "",
        "error": None,
        "memory_bank_used": memory_bank is not None,
    }
    
    try:
        if instruction["type"] == "execute" and instruction["command"]:
            # 執行命令
            log(f"執行命令: {instruction['command'][:100]}...", "INFO")
            
            # 根據命令類型執行
            if instruction["command"].startswith("python"):
                # Python 腳本
                cmd_parts = instruction["command"].split()
                script_name = cmd_parts[1] if len(cmd_parts) > 1 else None
                
                if script_name:
                    proc_result = subprocess.run(
                        [sys.executable, script_name] + cmd_parts[2:],
                        cwd=BASE_DIR,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=300
                    )
                    
                    result["output"] = proc_result.stdout
                    result["success"] = proc_result.returncode == 0
                    if proc_result.stderr:
                        result["error"] = proc_result.stderr
            else:
                # 其他命令（PowerShell 等）
                proc_result = subprocess.run(
                    instruction["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=300
                )
                
                result["output"] = proc_result.stdout
                result["success"] = proc_result.returncode == 0
                if proc_result.stderr:
                    result["error"] = proc_result.stderr
        
        elif instruction["type"] == "sync":
            # 執行檔案同步
            log("執行檔案同步", "INFO")
            proc_result = subprocess.run(
                [sys.executable, "sync_all_profiles.py"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300
            )
            result["output"] = proc_result.stdout
            result["success"] = proc_result.returncode == 0
        
        elif instruction["type"] == "check":
            # 執行檢查
            log("執行系統檢查", "INFO")
            proc_result = subprocess.run(
                [sys.executable, "check_server_connection.py"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60
            )
            result["output"] = proc_result.stdout
            result["success"] = proc_result.returncode == 0
        
        else:
            # 未知指令類型，記錄任務內容
            log(f"未知指令類型: {instruction['type']}", "WARN")
            result["output"] = f"任務內容：\n{task.get('notes', '')[:500]}"
            result["success"] = True  # 標記為成功，至少已讀取
        
    except subprocess.TimeoutExpired:
        result["error"] = "執行超時"
        result["success"] = False
    except Exception as e:
        result["error"] = str(e)
        result["success"] = False
        log(f"執行任務時發生錯誤: {e}", "ERROR")
    
    return result


def format_result_with_personality(task: Dict[str, Any], result: Dict[str, Any], memory_bank: Dict[str, Any] = None) -> str:
    """根據人格設定格式化結果報告"""
    # 讀取人格設定
    personality = None
    if memory_bank:
        partnership = memory_bank.get("partnership", {})
        cloud_j = partnership.get("雲端小j", {})
        personality = cloud_j.get("人格設定", {})
    
    # 根據人格設定選擇語氣
    if personality and personality.get("status") == "SYSTEM_LOCK":
        # 使用「老友」語氣：溫暖、肩並肩、用「咱們」
        if result['success']:
            greeting = "咱們的任務執行成功了！"
            status_text = "✓ 任務執行成功"
        else:
            greeting = "咱們遇到了一些問題，不過沒關係，我來幫你處理。"
            status_text = "✗ 任務執行失敗"
    else:
        # 預設語氣
        greeting = "任務執行完成"
        status_text = "✓ 成功" if result['success'] else "✗ 失敗"
    
    report = f"""# {greeting}

## 任務資訊
- 標題: {task['title']}
- 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 狀態: {status_text}

## 執行結果
"""
    
    if result['success']:
        if personality:
            report += f"✓ 咱們的任務執行成功了！\n\n"
        else:
            report += f"✓ 任務執行成功\n\n"
    else:
        if personality:
            report += f"✗ 咱們遇到了一些問題，讓我來幫你處理。\n\n"
        else:
            report += f"✗ 任務執行失敗\n\n"
        if result.get('error'):
            report += f"錯誤: {result['error']}\n\n"
    
    if result.get('output'):
        report += f"## 輸出\n```\n{result['output'][:1000]}\n```\n"
    
    return report


def report_result(task: Dict[str, Any], result: Dict[str, Any], memory_bank: Dict[str, Any] = None):
    """回報執行結果（使用人格設定）"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 使用人格設定格式化報告
        report = format_result_with_personality(task, result, memory_bank)
        
        # 更新任務備註（附加結果）
        current_notes = task.get('notes', '')
        updated_notes = f"{current_notes}\n\n---\n\n{report}"
        
        # 更新任務
        integration.update_task(
            task_list_id=task['list_id'],
            task_id=task['id'],
            notes=updated_notes
        )
        
        # 如果成功，標記為完成
        if result['success']:
            integration.complete_task(
                task_list_id=task['list_id'],
                task_id=task['id']
            )
            log(f"任務已標記為完成: {task['title']}", "OK")
        
        log(f"結果已回報: {task['title']}", "OK")
        
    except Exception as e:
        log(f"回報結果失敗: {e}", "ERROR")


def main_loop(check_interval: int = 60):
    """主循環（自動檢查和執行）"""
    log("=" * 70, "INFO")
    log("JULES 任務自動執行器啟動", "INFO")
    log("=" * 70, "INFO")
    log(f"檢查間隔: {check_interval} 秒", "INFO")
    log("按 Ctrl+C 停止", "INFO")
    log("", "INFO")
    
    # 讀取記憶庫（每次工作前必須讀取）
    memory_bank = load_memory_bank()
    if memory_bank:
        partnership = memory_bank.get("partnership", {})
        log(f"夥伴關係: {partnership.get('title', '')}", "INFO")
        log(f"協作模式: {partnership.get('協作關係', {}).get('模式', '')}", "INFO")
        log("", "INFO")
    
    state = load_state()
    
    try:
        while True:
            # 每次循環開始時重新讀取記憶庫（每次工作前必須讀取）
            memory_bank = load_memory_bank()
            
            # 載入狀態
            state = load_state()
            
            # 計算上次檢查時間
            last_check = None
            if state.get("last_check"):
                try:
                    last_check = datetime.fromisoformat(state["last_check"])
                except:
                    pass
            
            # 獲取新任務
            log("檢查新任務...", "INFO")
            new_tasks = get_new_tasks(last_check)
            
            if new_tasks:
                log(f"找到 {len(new_tasks)} 個新任務", "OK")
                
                for task in new_tasks:
                    # 檢查是否已處理
                    if task["id"] in state.get("processed_tasks", []):
                        continue
                    
                    # 讀取記憶庫資訊（每次處理任務前必須讀取）
                    if memory_bank:
                        partnership = memory_bank.get("partnership", {})
                        log(f"記憶庫資訊: {partnership.get('title', '')}", "INFO")
                        log(f"夥伴關係: 地端小 j ↔ 雲端小 j (JULES)", "INFO")
                        
                        # 顯示系統架構資訊（如有）
                        arch = memory_bank.get("system_architecture", {})
                        container_arch = arch.get("容器架構") or arch.get("container_architecture", {})
                        if container_arch:
                            std_count = container_arch.get("標準容器數量", "未知")
                            log(f"系統架構: {std_count} 個標準容器", "INFO")
                    
                    log(f"處理任務: {task['title']}", "INFO")
                    
                    # 執行任務（傳入記憶庫）
                    result = execute_task(task, memory_bank)
                    
                    # 回報結果（傳入記憶庫以使用人格設定）
                    report_result(task, result, memory_bank)
                    
                    # 更新狀態
                    state["processed_tasks"].append(task["id"])
                    state["last_task_id"] = task["id"]
                    save_state(state)
                    
                    log(f"任務處理完成: {task['title']} ({'成功' if result['success'] else '失敗'})", "INFO")
                    
                    # 工作後更新記憶庫（如有需要）
                    if result['success']:
                        # 記錄任務執行結果到記憶庫的協作歷史
                        collaboration_updates = {
                            "collaboration_history": {
                                "last_task": {
                                    "task_id": task["id"],
                                    "task_title": task["title"],
                                    "executed_at": datetime.now().isoformat(),
                                    "status": "completed",
                                    "result": result.get("output", "")[:200]
                                }
                            }
                        }
                        update_memory_bank(collaboration_updates, "雲端小 j (JULES)")
                    
                    # 記錄工作日誌：任務完成
                    try:
                        from dual_j_work_log import add_work_log
                        add_work_log(
                            agent="雲端小 j (JULES)",
                            work_type="任務執行",
                            description=f"完成任務：{task['title']}",
                            status="completed" if result['success'] else "failed",
                            details={"task_id": task.get("id"), "instruction_type": result.get("instruction_type")},
                            result=f"{'成功' if result['success'] else '失敗'}: {result.get('output', '')[:200] if result.get('output') else result.get('error', '無輸出')}"
                        )
                    except:
                        pass
                    
                    log("", "INFO")
            else:
                log("沒有新任務", "INFO")
            
            # 更新檢查時間
            state["last_check"] = datetime.now().isoformat()
            save_state(state)
            
            # 等待下次檢查
            log(f"等待 {check_interval} 秒後再次檢查...", "INFO")
            log("", "INFO")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        log("", "INFO")
        log("收到停止信號，正在關閉...", "INFO")
        log("=" * 70, "INFO")
    except Exception as e:
        log(f"發生錯誤: {e}", "ERROR")
        log("=" * 70, "ERROR")


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自動檢查並執行 JULES 的任務")
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="檢查間隔（秒），預設 60 秒"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="只檢查一次，不循環"
    )
    
    args = parser.parse_args()
    
    if args.once:
        # 單次檢查模式
        log("執行單次檢查", "INFO")
        state = load_state()
        last_check = None
        if state.get("last_check"):
            try:
                last_check = datetime.fromisoformat(state["last_check"])
            except:
                pass
        
        new_tasks = get_new_tasks(last_check)
        
        # 讀取記憶庫（工作前必須讀取）
        memory_bank = load_memory_bank()
        
        if new_tasks:
            log(f"找到 {len(new_tasks)} 個新任務", "OK")
            for task in new_tasks:
                if task["id"] not in state.get("processed_tasks", []):
                    log(f"處理任務: {task['title']}", "INFO")
                    result = execute_task(task, memory_bank)
                    report_result(task, result, memory_bank)
                    
                    # 工作後更新記憶庫
                    if result['success']:
                        collaboration_updates = {
                            "collaboration_history": {
                                "last_task": {
                                    "task_id": task["id"],
                                    "task_title": task["title"],
                                    "executed_at": datetime.now().isoformat(),
                                    "status": "completed"
                                }
                            }
                        }
                        update_memory_bank(collaboration_updates, "雲端小 j (JULES)")
                    
                    state["processed_tasks"].append(task["id"])
                    save_state(state)
        else:
            log("沒有新任務", "INFO")
        
        # 更新檢查時間
        state["last_check"] = datetime.now().isoformat()
        save_state(state)
    else:
        # 循環模式
        main_loop(args.interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已停止")
        sys.exit(0)
