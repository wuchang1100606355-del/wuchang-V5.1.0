#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
little_j_jules_container_collaboration.py

地端小 j（本地 LLM）與雲端小 j（JULES）容器維護協作機制

架構：
- 地端小 j：監控容器狀態、發現問題、驗證結果
- 雲端小 j（JULES）：接收任務、執行修復、回報結果
- 協作流程：地端監控 → 發現問題 → 通知 JULES → JULES 執行 → 地端驗證
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent
COLLABORATION_STATE_FILE = BASE_DIR / "container_collaboration_state.json"
COLLABORATION_LOG_FILE = BASE_DIR / "container_collaboration.log"
OPTIMIZATION_SUGGESTIONS_FILE = BASE_DIR / "container_optimization_suggestions.json"
JULES_MEMORY_BANK_FILE = BASE_DIR / "jules_memory_bank.json"

# 匯入工作日誌模組
try:
    from dual_j_work_log import add_work_log
    WORK_LOG_AVAILABLE = True
except ImportError:
    WORK_LOG_AVAILABLE = False
    def add_work_log(*args, **kwargs):
        pass

# 標準容器配置
STANDARD_CONTAINERS = [
    "wuchangv510-caddy-1",
    "wuchangv510-caddy-ui-1",
    "wuchangv510-cloudflared-1",
    "wuchangv510-db-1",
    "wuchangv510-ollama-1",
    "wuchangv510-open-webui-1",
    "wuchangv510-portainer-1",
    "wuchangv510-uptime-kuma-1",
    "wuchangv510-wuchang-web-1"
]


def log(message: str, level: str = "INFO"):
    """記錄協作日誌（自動輪轉以防止檔案過大）"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    print(log_entry.strip())
    
    try:
        # 檢查日誌檔案大小，超過 10MB 時進行輪轉
        MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
        if COLLABORATION_LOG_FILE.exists():
            file_size = COLLABORATION_LOG_FILE.stat().st_size
            if file_size > MAX_LOG_SIZE:
                # 輪轉：將當前日誌備份為 .old
                old_log = COLLABORATION_LOG_FILE.with_suffix('.log.old')
                if old_log.exists():
                    old_log.unlink()
                COLLABORATION_LOG_FILE.rename(old_log)
        
        with open(COLLABORATION_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass


def load_memory_bank() -> Dict[str, Any]:
    """讀取 JULES 記憶庫（每次工作前必須讀取）"""
    if not JULES_MEMORY_BANK_FILE.exists():
        log("記憶庫檔案不存在，將建立新檔案", "WARN")
        return {}
    
    try:
        memory = json.loads(JULES_MEMORY_BANK_FILE.read_text(encoding="utf-8"))
        log("已讀取 JULES 記憶庫", "INFO")
        log(f"記憶庫版本: {memory.get('version', 'unknown')}", "INFO")
        log(f"最後更新: {memory.get('last_updated', 'unknown')}", "INFO")
        return memory
    except Exception as e:
        log(f"讀取記憶庫失敗: {e}", "ERROR")
        return {}


def update_memory_bank(updates: Dict[str, Any], contributor: str = "地端小 j"):
    """更新記憶庫（由兩小 j 共同編寫）"""
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
    """載入協作狀態"""
    if COLLABORATION_STATE_FILE.exists():
        try:
            return json.loads(COLLABORATION_STATE_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {
        "last_check": None,
        "last_issue_time": None,
        "issues_reported": [],
        "jules_tasks_created": [],
        "verification_results": []
    }


def save_state(state: Dict[str, Any]):
    """儲存協作狀態"""
    try:
        COLLABORATION_STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        log(f"儲存狀態失敗: {e}", "ERROR")


def check_container_status() -> Dict[str, Any]:
    """地端小 j：檢查容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Image}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return {"ok": False, "error": "無法執行 docker ps"}
        
        containers = []
        running = []
        stopped = []
        restarting = []
        
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 2)
            if len(parts) >= 2:
                container = {
                    "name": parts[0],
                    "status": parts[1],
                    "image": parts[2] if len(parts) > 2 else "",
                    "is_standard": parts[0] in STANDARD_CONTAINERS
                }
                containers.append(container)
                
                if "Up" in container["status"]:
                    running.append(container)
                elif "Restarting" in container["status"]:
                    restarting.append(container)
                else:
                    stopped.append(container)
        
        return {
            "ok": True,
            "containers": containers,
            "running": running,
            "stopped": stopped,
            "restarting": restarting,
            "total": len(containers),
            "running_count": len(running),
            "stopped_count": len(stopped),
            "restarting_count": len(restarting)
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def detect_issues(status: Dict[str, Any]) -> List[Dict[str, Any]]:
    """地端小 j：偵測容器問題"""
    issues = []
    
    if not status.get("ok"):
        issues.append({
            "type": "check_failed",
            "severity": "high",
            "message": f"無法檢查容器狀態: {status.get('error', '未知錯誤')}",
            "action": "check_docker_service"
        })
        return issues
    
    # 檢查標準容器是否都在運行
    running_names = {c["name"] for c in status.get("running", [])}
    for std_container in STANDARD_CONTAINERS:
        if std_container not in running_names:
            issues.append({
                "type": "standard_container_stopped",
                "severity": "high",
                "container": std_container,
                "message": f"標準容器 {std_container} 未運行",
                "action": "restart_container",
                "container_name": std_container
            })
    
    # 檢查重啟中的容器
    for container in status.get("restarting", []):
        if container["is_standard"]:
            issues.append({
                "type": "container_restarting",
                "severity": "medium",
                "container": container["name"],
                "message": f"標準容器 {container['name']} 正在重啟（可能異常）",
                "action": "check_container_logs",
                "container_name": container["name"]
            })
    
    # 檢查非標準容器
    non_standard_stopped = [
        c for c in status.get("stopped", [])
        if not c["is_standard"]
    ]
    if non_standard_stopped:
        issues.append({
            "type": "non_standard_containers",
            "severity": "low",
            "containers": [c["name"] for c in non_standard_stopped],
            "message": f"發現 {len(non_standard_stopped)} 個非標準容器已停止（可清理）",
            "action": "cleanup_non_standard"
        })
    
    return issues


def create_jules_task(issue: Dict[str, Any], status: Dict[str, Any]) -> Optional[str]:
    """地端小 j：建立 JULES 任務"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 尋找任務列表
        task_lists = integration.list_task_lists()
        target_list = None
        
        for task_list in task_lists:
            if "Wuchang" in task_list.title or "File Sync" in task_list.title:
                target_list = task_list
                break
        
        if not target_list:
            log("找不到適合的任務列表", "WARN")
            return None
        
        # 生成任務內容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = f"容器維護：{issue['type']} - {timestamp}"
        
        task_content = f"""# 容器維護任務（由地端小 j 偵測）

## 問題類型
{issue['type']}

## 嚴重程度
{issue['severity']}

## 問題描述
{issue['message']}

## 建議操作
{issue['action']}

## 當前容器狀態
- 總容器數：{status.get('total', 0)}
- 運行中：{status.get('running_count', 0)}
- 已停止：{status.get('stopped_count', 0)}
- 重啟中：{status.get('restarting_count', 0)}

## 執行指令

### 方式 1：使用 docker 命令
```json
{{
  "type": "execute",
  "command": "docker {issue.get('action', 'check')} {issue.get('container_name', '')}",
  "description": "{issue['message']}",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

### 方式 2：使用 docker-compose（如果是標準容器）
```json
{{
  "type": "execute",
  "command": "docker-compose restart {issue.get('container_name', '').replace('wuchangv510-', '').replace('-1', '')}",
  "description": "{issue['message']}",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

## 驗證指令
```json
{{
  "type": "execute",
  "command": "python check_container_status.py",
  "description": "驗證容器狀態",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

## 地端小 j 工作討論

{issue.get('discussion', '無討論內容')}

## 地端小 j 將在執行後驗證結果
"""
        
        # 建立任務
        task = integration.create_task(
            task_list_id=target_list.id,
            title=title,
            notes=task_content
        )
        
        if task:
            log(f"已建立 JULES 任務: {task.id} - {title}", "INFO")
            return task.id
        else:
            log("建立 JULES 任務失敗", "ERROR")
            return None
            
    except ImportError:
        log("無法匯入 google_tasks_integration", "ERROR")
        return None
    except Exception as e:
        log(f"建立 JULES 任務時發生錯誤: {e}", "ERROR")
        return None


def verify_fix(issue: Dict[str, Any]) -> Dict[str, Any]:
    """地端小 j：驗證修復結果"""
    log(f"驗證修復結果: {issue['type']}", "INFO")
    
    # 重新檢查容器狀態
    status = check_container_status()
    
    if not status.get("ok"):
        return {
            "ok": False,
            "message": "無法驗證：無法檢查容器狀態",
            "issue": issue
        }
    
    # 根據問題類型驗證
    if issue["type"] == "standard_container_stopped":
        container_name = issue.get("container_name")
        running_names = {c["name"] for c in status.get("running", [])}
        
        if container_name in running_names:
            return {
                "ok": True,
                "message": f"✅ 容器 {container_name} 已恢復運行",
                "issue": issue
            }
        else:
            return {
                "ok": False,
                "message": f"❌ 容器 {container_name} 仍未運行",
                "issue": issue
            }
    
    elif issue["type"] == "container_restarting":
        container_name = issue.get("container_name")
        restarting_names = {c["name"] for c in status.get("restarting", [])}
        
        if container_name not in restarting_names:
            # 檢查是否在運行
            running_names = {c["name"] for c in status.get("running", [])}
            if container_name in running_names:
                return {
                    "ok": True,
                    "message": f"✅ 容器 {container_name} 已停止重啟並正常運行",
                    "issue": issue
                }
            else:
                return {
                    "ok": False,
                    "message": f"⚠️ 容器 {container_name} 已停止重啟但未運行",
                    "issue": issue
                }
        else:
            return {
                "ok": False,
                "message": f"❌ 容器 {container_name} 仍在重啟中",
                "issue": issue
            }
    
    # 其他類型問題
    return {
        "ok": True,
        "message": "問題已處理（需手動確認）",
        "issue": issue
    }


def call_local_llm(prompt: str) -> Optional[str]:
    """呼叫本地 LLM（Ollama）進行工作討論"""
    try:
        import requests
        
        # 嘗試使用 Ollama API
        ollama_url = "http://127.0.0.1:11434/api/chat"
        
        payload = {
            "model": "llama3.2",  # 可根據實際模型調整
            "messages": [
                {
                    "role": "system",
                    "content": "你是五常平台的「地端小 j」助理。請用繁體中文回覆，語氣簡潔、專業。專注於容器維護和系統優化建議。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
        
        response = requests.post(ollama_url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
        else:
            log(f"Ollama API 回應錯誤: {response.status_code}", "WARN")
            return None
    except ImportError:
        log("無法匯入 requests，跳過 LLM 討論", "WARN")
        return None
    except Exception as e:
        log(f"呼叫本地 LLM 失敗: {e}", "WARN")
        return None


def analyze_and_discuss(status: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """地端小 j：分析狀態並進行工作討論"""
    log("開始工作討論...", "INFO")
    
    # 準備討論內容
    discussion_prompt = f"""請分析以下容器狀態並提供優化建議：

容器狀態：
- 總數：{status.get('total', 0)}
- 運行中：{status.get('running_count', 0)}
- 已停止：{status.get('stopped_count', 0)}
- 重啟中：{status.get('restarting_count', 0)}

問題列表：
{chr(10).join(f"- {issue['type']}: {issue['message']}" for issue in issues) if issues else "無問題"}

請提供：
1. 系統狀態評估
2. 優化建議（如果有的話）
3. 可以立即執行的小優化（不涉及巨大變動）
"""
    
    # 呼叫本地 LLM
    discussion_result = call_local_llm(discussion_prompt)
    
    if discussion_result:
        log("工作討論完成", "INFO")
        log(f"討論結果: {discussion_result[:200]}...", "INFO")
        
        # 解析優化建議
        suggestions = extract_optimization_suggestions(discussion_result, status, issues)
        
        return {
            "discussion": discussion_result,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    else:
        log("無法進行 LLM 討論，使用基本分析", "WARN")
        return {
            "discussion": "無法進行 LLM 討論",
            "suggestions": [],
            "timestamp": datetime.now().isoformat()
        }


def extract_optimization_suggestions(discussion: str, status: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """從討論結果中提取優化建議"""
    suggestions = []
    
    # 簡單的關鍵字匹配來提取建議
    discussion_lower = discussion.lower()
    
    # 檢查是否有可以立即執行的建議
    if "清理" in discussion_lower or "clean" in discussion_lower:
        suggestions.append({
            "type": "cleanup",
            "description": "清理未使用的容器或資源",
            "action": "docker system prune -f",
            "risk": "low",
            "can_execute_immediately": True
        })
    
    if "日誌" in discussion_lower or "log" in discussion_lower:
        suggestions.append({
            "type": "log_management",
            "description": "管理容器日誌",
            "action": "docker logs --tail 100 <container>",
            "risk": "low",
            "can_execute_immediately": True
        })
    
    if "資源" in discussion_lower or "resource" in discussion_lower:
        suggestions.append({
            "type": "resource_check",
            "description": "檢查容器資源使用",
            "action": "docker stats --no-stream",
            "risk": "low",
            "can_execute_immediately": True
        })
    
    return suggestions


def save_optimization_suggestions(suggestions: List[Dict[str, Any]]):
    """儲存優化建議"""
    try:
        if OPTIMIZATION_SUGGESTIONS_FILE.exists():
            existing = json.loads(OPTIMIZATION_SUGGESTIONS_FILE.read_text(encoding="utf-8"))
        else:
            existing = []
        
        # 加入新建議
        for suggestion in suggestions:
            suggestion["created_at"] = datetime.now().isoformat()
            existing.append(suggestion)
        
        # 只保留最近 100 個建議
        existing = existing[-100:]
        
        OPTIMIZATION_SUGGESTIONS_FILE.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        log(f"已儲存 {len(suggestions)} 個優化建議", "INFO")
    except Exception as e:
        log(f"儲存優化建議失敗: {e}", "ERROR")


def execute_safe_optimization(suggestion: Dict[str, Any]) -> Dict[str, Any]:
    """執行安全的優化（不涉及巨大變動）"""
    if not suggestion.get("can_execute_immediately"):
        return {"ok": False, "message": "此優化需要人工確認"}
    
    if suggestion.get("risk") != "low":
        return {"ok": False, "message": "此優化風險較高，需要人工確認"}
    
    action = suggestion.get("action", "")
    if not action:
        return {"ok": False, "message": "無有效操作指令"}
    
    log(f"執行安全優化: {suggestion.get('description', '')}", "INFO")
    
    try:
        # 執行指令
        if action.startswith("docker "):
            cmd = action.split()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                log(f"✅ 優化執行成功: {suggestion.get('description', '')}", "INFO")
                return {
                    "ok": True,
                    "message": "優化執行成功",
                    "output": result.stdout[:500]  # 限制輸出長度
                }
            else:
                log(f"⚠️ 優化執行失敗: {result.stderr[:200]}", "WARN")
                return {
                    "ok": False,
                    "message": "優化執行失敗",
                    "error": result.stderr[:500]
                }
        else:
            return {"ok": False, "message": "不支援的操作類型"}
            
    except Exception as e:
        log(f"執行優化時發生錯誤: {e}", "ERROR")
        return {"ok": False, "message": f"執行錯誤: {str(e)}"}


def main_loop(interval: int = 3600):  # 預設改為 1 小時
    """主循環：地端小 j 持續監控並與 JULES 協作"""
    log("啟動地端小 j 與 JULES 容器維護協作", "INFO")
    log(f"檢查間隔: {interval} 秒（{interval // 60} 分鐘）", "INFO")
    
    state = load_state()
    
    while True:
        try:
            log("開始檢查容器狀態...", "INFO")
            
            # 1. 地端小 j 檢查容器狀態
            status = check_container_status()
            
            if not status.get("ok"):
                log(f"檢查失敗: {status.get('error')}", "ERROR")
                time.sleep(interval)
                continue
            
            log(f"容器狀態: 總數 {status['total']}, 運行中 {status['running_count']}, 已停止 {status['stopped_count']}, 重啟中 {status['restarting_count']}", "INFO")
            
            # 2. 偵測問題
            issues = detect_issues(status)
            
            # 3. 進行工作討論和優化分析
            discussion_result = analyze_and_discuss(status, issues)
            
            # 4. 處理優化建議
            suggestions = discussion_result.get("suggestions", [])
            if suggestions:
                log(f"發現 {len(suggestions)} 個優化建議", "INFO")
                save_optimization_suggestions(suggestions)
                
                # 執行可以立即執行的安全優化
                for suggestion in suggestions:
                    if suggestion.get("can_execute_immediately") and suggestion.get("risk") == "low":
                        log(f"執行安全優化: {suggestion.get('description', '')}", "INFO")
                        result = execute_safe_optimization(suggestion)
                        if result.get("ok"):
                            log(f"✅ 優化完成: {suggestion.get('description', '')}", "INFO")
                        else:
                            log(f"⚠️ 優化失敗: {result.get('message', '')}", "WARN")
            
            # 5. 處理問題
            if issues:
                log(f"偵測到 {len(issues)} 個問題", "WARN")
                
                for issue in issues:
                    issue_id = f"{issue['type']}_{issue.get('container', '')}_{datetime.now().isoformat()}"
                    
                    # 檢查是否已回報過
                    if issue_id in state.get("issues_reported", []):
                        log(f"問題已回報過，跳過: {issue['type']}", "INFO")
                        continue
                    
                    # 6. 建立 JULES 任務（包含討論結果）
                    log(f"建立 JULES 任務: {issue['message']}", "INFO")
                    # 將討論結果加入任務內容
                    issue_with_discussion = issue.copy()
                    issue_with_discussion["discussion"] = discussion_result.get("discussion", "")
                    task_id = create_jules_task(issue_with_discussion, status)
                    
                    if task_id:
                        state["issues_reported"].append(issue_id)
                        state["jules_tasks_created"].append({
                            "issue_id": issue_id,
                            "task_id": task_id,
                            "issue": issue,
                            "timestamp": datetime.now().isoformat()
                        })
                        save_state(state)
                    else:
                        log(f"建立任務失敗: {issue['message']}", "ERROR")
            else:
                log("✅ 所有容器狀態正常", "INFO")
                
                # 驗證之前報告的問題是否已修復
                if state.get("jules_tasks_created"):
                    log("驗證之前報告的問題...", "INFO")
                    for task_info in state["jules_tasks_created"][-5:]:  # 只驗證最近5個
                        if task_info.get("verified"):
                            continue
                        
                        issue = task_info.get("issue", {})
                        verification = verify_fix(issue)
                        
                        task_info["verified"] = True
                        task_info["verification"] = verification
                        task_info["verification_time"] = datetime.now().isoformat()
                        
                        if verification.get("ok"):
                            log(f"✅ 問題已修復: {issue.get('message', '')}", "INFO")
                        else:
                            log(f"⚠️ 問題未修復: {verification.get('message', '')}", "WARN")
                    
                    save_state(state)
            
            state["last_check"] = datetime.now().isoformat()
            save_state(state)
            
            log(f"等待 {interval} 秒後再次檢查...", "INFO")
            time.sleep(interval)
            
        except KeyboardInterrupt:
            log("收到中斷信號，停止協作", "INFO")
            break
        except Exception as e:
            log(f"發生錯誤: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            time.sleep(interval)


def main():
    """主函數"""
    import argparse
    
    ap = argparse.ArgumentParser(description="地端小 j 與 JULES 容器維護協作")
    ap.add_argument("--interval", type=int, default=3600, help="檢查間隔（秒），預設 3600 秒（1小時）")
    ap.add_argument("--once", action="store_true", help="只執行一次檢查（不循環）")
    
    args = ap.parse_args()
    
    if args.once:
        log("執行單次檢查", "INFO")
        status = check_container_status()
        issues = detect_issues(status)
        
        print("\n" + "=" * 70)
        print("容器狀態檢查結果")
        print("=" * 70)
        print()
        print(f"總容器數: {status.get('total', 0)}")
        print(f"運行中: {status.get('running_count', 0)}")
        print(f"已停止: {status.get('stopped_count', 0)}")
        print(f"重啟中: {status.get('restarting_count', 0)}")
        print()
        
        if issues:
            print(f"偵測到 {len(issues)} 個問題：")
            for issue in issues:
                print(f"  - [{issue['severity']}] {issue['message']}")
                print(f"    建議操作: {issue['action']}")
        else:
            print("✅ 所有容器狀態正常")
        
        # 進行工作討論
        print("\n" + "=" * 70)
        print("工作討論與優化分析")
        print("=" * 70)
        print()
        
        discussion_result = analyze_and_discuss(status, issues)
        
        if discussion_result.get("discussion"):
            print("【討論結果】")
            print(discussion_result["discussion"])
            print()
        
        # 處理優化建議
        suggestions = discussion_result.get("suggestions", [])
        if suggestions:
            print(f"【優化建議】共 {len(suggestions)} 個")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. {suggestion.get('description', '')}")
                print(f"   類型: {suggestion.get('type', '')}")
                print(f"   風險: {suggestion.get('risk', '')}")
                print(f"   可立即執行: {'是' if suggestion.get('can_execute_immediately') else '否'}")
                print()
            
            # 執行可以立即執行的安全優化
            safe_suggestions = [s for s in suggestions if s.get("can_execute_immediately") and s.get("risk") == "low"]
            if safe_suggestions:
                print("【執行安全優化】")
                for suggestion in safe_suggestions:
                    print(f"執行: {suggestion.get('description', '')}")
                    result = execute_safe_optimization(suggestion)
                    if result.get("ok"):
                        print(f"✅ 完成: {result.get('message', '')}")
                    else:
                        print(f"⚠️ 失敗: {result.get('message', '')}")
                    print()
            
            # 儲存建議
            save_optimization_suggestions(suggestions)
        else:
            print("【優化建議】無新建議")
    else:
        main_loop(args.interval)


if __name__ == "__main__":
    main()

# 標準容器配置
STANDARD_CONTAINERS = [
    "wuchangv510-caddy-1",
    "wuchangv510-caddy-ui-1",
    "wuchangv510-cloudflared-1",
    "wuchangv510-db-1",
    "wuchangv510-ollama-1",
    "wuchangv510-open-webui-1",
    "wuchangv510-portainer-1",
    "wuchangv510-uptime-kuma-1",
    "wuchangv510-wuchang-web-1"
]


def log(message: str, level: str = "INFO"):
    """記錄協作日誌（自動輪轉以防止檔案過大）"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    print(log_entry.strip())
    
    try:
        # 檢查日誌檔案大小，超過 10MB 時進行輪轉
        MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
        if COLLABORATION_LOG_FILE.exists():
            file_size = COLLABORATION_LOG_FILE.stat().st_size
            if file_size > MAX_LOG_SIZE:
                # 輪轉：將當前日誌備份為 .old
                old_log = COLLABORATION_LOG_FILE.with_suffix('.log.old')
                if old_log.exists():
                    old_log.unlink()
                COLLABORATION_LOG_FILE.rename(old_log)
        
        with open(COLLABORATION_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass


def load_state() -> Dict[str, Any]:
    """載入協作狀態"""
    if COLLABORATION_STATE_FILE.exists():
        try:
            return json.loads(COLLABORATION_STATE_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {
        "last_check": None,
        "last_issue_time": None,
        "issues_reported": [],
        "jules_tasks_created": [],
        "verification_results": []
    }


def save_state(state: Dict[str, Any]):
    """儲存協作狀態"""
    try:
        COLLABORATION_STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        log(f"儲存狀態失敗: {e}", "ERROR")


def check_container_status() -> Dict[str, Any]:
    """地端小 j：檢查容器狀態"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.Names}}|{{.Status}}|{{.Image}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return {"ok": False, "error": "無法執行 docker ps"}
        
        containers = []
        running = []
        stopped = []
        restarting = []
        
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.split('|', 2)
            if len(parts) >= 2:
                container = {
                    "name": parts[0],
                    "status": parts[1],
                    "image": parts[2] if len(parts) > 2 else "",
                    "is_standard": parts[0] in STANDARD_CONTAINERS
                }
                containers.append(container)
                
                if "Up" in container["status"]:
                    running.append(container)
                elif "Restarting" in container["status"]:
                    restarting.append(container)
                else:
                    stopped.append(container)
        
        return {
            "ok": True,
            "containers": containers,
            "running": running,
            "stopped": stopped,
            "restarting": restarting,
            "total": len(containers),
            "running_count": len(running),
            "stopped_count": len(stopped),
            "restarting_count": len(restarting)
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def detect_issues(status: Dict[str, Any]) -> List[Dict[str, Any]]:
    """地端小 j：偵測容器問題"""
    issues = []
    
    if not status.get("ok"):
        issues.append({
            "type": "check_failed",
            "severity": "high",
            "message": f"無法檢查容器狀態: {status.get('error', '未知錯誤')}",
            "action": "check_docker_service"
        })
        return issues
    
    # 檢查標準容器是否都在運行
    running_names = {c["name"] for c in status.get("running", [])}
    for std_container in STANDARD_CONTAINERS:
        if std_container not in running_names:
            issues.append({
                "type": "standard_container_stopped",
                "severity": "high",
                "container": std_container,
                "message": f"標準容器 {std_container} 未運行",
                "action": "restart_container",
                "container_name": std_container
            })
    
    # 檢查重啟中的容器
    for container in status.get("restarting", []):
        if container["is_standard"]:
            issues.append({
                "type": "container_restarting",
                "severity": "medium",
                "container": container["name"],
                "message": f"標準容器 {container['name']} 正在重啟（可能異常）",
                "action": "check_container_logs",
                "container_name": container["name"]
            })
    
    # 檢查非標準容器
    non_standard_stopped = [
        c for c in status.get("stopped", [])
        if not c["is_standard"]
    ]
    if non_standard_stopped:
        issues.append({
            "type": "non_standard_containers",
            "severity": "low",
            "containers": [c["name"] for c in non_standard_stopped],
            "message": f"發現 {len(non_standard_stopped)} 個非標準容器已停止（可清理）",
            "action": "cleanup_non_standard"
        })
    
    return issues


def create_jules_task(issue: Dict[str, Any], status: Dict[str, Any]) -> Optional[str]:
    """地端小 j：建立 JULES 任務"""
    try:
        from google_tasks_integration import get_google_tasks_integration
        
        integration = get_google_tasks_integration()
        
        # 尋找任務列表
        task_lists = integration.list_task_lists()
        target_list = None
        
        for task_list in task_lists:
            if "Wuchang" in task_list.title or "File Sync" in task_list.title:
                target_list = task_list
                break
        
        if not target_list:
            log("找不到適合的任務列表", "WARN")
            return None
        
        # 生成任務內容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = f"容器維護：{issue['type']} - {timestamp}"
        
        task_content = f"""# 容器維護任務（由地端小 j 偵測）

## 問題類型
{issue['type']}

## 嚴重程度
{issue['severity']}

## 問題描述
{issue['message']}

## 建議操作
{issue['action']}

## 當前容器狀態
- 總容器數：{status.get('total', 0)}
- 運行中：{status.get('running_count', 0)}
- 已停止：{status.get('stopped_count', 0)}
- 重啟中：{status.get('restarting_count', 0)}

## 執行指令

### 方式 1：使用 docker 命令
```json
{{
  "type": "execute",
  "command": "docker {issue.get('action', 'check')} {issue.get('container_name', '')}",
  "description": "{issue['message']}",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

### 方式 2：使用 docker-compose（如果是標準容器）
```json
{{
  "type": "execute",
  "command": "docker-compose restart {issue.get('container_name', '').replace('wuchangv510-', '').replace('-1', '')}",
  "description": "{issue['message']}",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

## 驗證指令
```json
{{
  "type": "execute",
  "command": "python check_container_status.py",
  "description": "驗證容器狀態",
  "working_dir": "C:\\\\wuchang V5.1.0\\\\wuchang-V5.1.0"
}}
```

## 地端小 j 工作討論

{issue.get('discussion', '無討論內容')}

## 地端小 j 將在執行後驗證結果
"""
        
        # 建立任務
        task = integration.create_task(
            task_list_id=target_list.id,
            title=title,
            notes=task_content
        )
        
        if task:
            log(f"已建立 JULES 任務: {task.id} - {title}", "INFO")
            return task.id
        else:
            log("建立 JULES 任務失敗", "ERROR")
            return None
            
    except ImportError:
        log("無法匯入 google_tasks_integration", "ERROR")
        return None
    except Exception as e:
        log(f"建立 JULES 任務時發生錯誤: {e}", "ERROR")
        return None


def verify_fix(issue: Dict[str, Any]) -> Dict[str, Any]:
    """地端小 j：驗證修復結果"""
    log(f"驗證修復結果: {issue['type']}", "INFO")
    
    # 重新檢查容器狀態
    status = check_container_status()
    
    if not status.get("ok"):
        return {
            "ok": False,
            "message": "無法驗證：無法檢查容器狀態",
            "issue": issue
        }
    
    # 根據問題類型驗證
    if issue["type"] == "standard_container_stopped":
        container_name = issue.get("container_name")
        running_names = {c["name"] for c in status.get("running", [])}
        
        if container_name in running_names:
            return {
                "ok": True,
                "message": f"✅ 容器 {container_name} 已恢復運行",
                "issue": issue
            }
        else:
            return {
                "ok": False,
                "message": f"❌ 容器 {container_name} 仍未運行",
                "issue": issue
            }
    
    elif issue["type"] == "container_restarting":
        container_name = issue.get("container_name")
        restarting_names = {c["name"] for c in status.get("restarting", [])}
        
        if container_name not in restarting_names:
            # 檢查是否在運行
            running_names = {c["name"] for c in status.get("running", [])}
            if container_name in running_names:
                return {
                    "ok": True,
                    "message": f"✅ 容器 {container_name} 已停止重啟並正常運行",
                    "issue": issue
                }
            else:
                return {
                    "ok": False,
                    "message": f"⚠️ 容器 {container_name} 已停止重啟但未運行",
                    "issue": issue
                }
        else:
            return {
                "ok": False,
                "message": f"❌ 容器 {container_name} 仍在重啟中",
                "issue": issue
            }
    
    # 其他類型問題
    return {
        "ok": True,
        "message": "問題已處理（需手動確認）",
        "issue": issue
    }


def call_local_llm(prompt: str) -> Optional[str]:
    """呼叫本地 LLM（Ollama）進行工作討論"""
    try:
        import requests
        
        # 嘗試使用 Ollama API
        ollama_url = "http://127.0.0.1:11434/api/chat"
        
        payload = {
            "model": "llama3.2",  # 可根據實際模型調整
            "messages": [
                {
                    "role": "system",
                    "content": "你是五常平台的「地端小 j」助理。請用繁體中文回覆，語氣簡潔、專業。專注於容器維護和系統優化建議。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
        
        response = requests.post(ollama_url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
        else:
            log(f"Ollama API 回應錯誤: {response.status_code}", "WARN")
            return None
    except ImportError:
        log("無法匯入 requests，跳過 LLM 討論", "WARN")
        return None
    except Exception as e:
        log(f"呼叫本地 LLM 失敗: {e}", "WARN")
        return None


def analyze_and_discuss(status: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """地端小 j：分析狀態並進行工作討論"""
    log("開始工作討論...", "INFO")
    
    # 準備討論內容
    discussion_prompt = f"""請分析以下容器狀態並提供優化建議：

容器狀態：
- 總數：{status.get('total', 0)}
- 運行中：{status.get('running_count', 0)}
- 已停止：{status.get('stopped_count', 0)}
- 重啟中：{status.get('restarting_count', 0)}

問題列表：
{chr(10).join(f"- {issue['type']}: {issue['message']}" for issue in issues) if issues else "無問題"}

請提供：
1. 系統狀態評估
2. 優化建議（如果有的話）
3. 可以立即執行的小優化（不涉及巨大變動）
"""
    
    # 呼叫本地 LLM
    discussion_result = call_local_llm(discussion_prompt)
    
    if discussion_result:
        log("工作討論完成", "INFO")
        log(f"討論結果: {discussion_result[:200]}...", "INFO")
        
        # 解析優化建議
        suggestions = extract_optimization_suggestions(discussion_result, status, issues)
        
        return {
            "discussion": discussion_result,
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }
    else:
        log("無法進行 LLM 討論，使用基本分析", "WARN")
        return {
            "discussion": "無法進行 LLM 討論",
            "suggestions": [],
            "timestamp": datetime.now().isoformat()
        }


def extract_optimization_suggestions(discussion: str, status: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """從討論結果中提取優化建議"""
    suggestions = []
    
    # 簡單的關鍵字匹配來提取建議
    discussion_lower = discussion.lower()
    
    # 檢查是否有可以立即執行的建議
    if "清理" in discussion_lower or "clean" in discussion_lower:
        suggestions.append({
            "type": "cleanup",
            "description": "清理未使用的容器或資源",
            "action": "docker system prune -f",
            "risk": "low",
            "can_execute_immediately": True
        })
    
    if "日誌" in discussion_lower or "log" in discussion_lower:
        suggestions.append({
            "type": "log_management",
            "description": "管理容器日誌",
            "action": "docker logs --tail 100 <container>",
            "risk": "low",
            "can_execute_immediately": True
        })
    
    if "資源" in discussion_lower or "resource" in discussion_lower:
        suggestions.append({
            "type": "resource_check",
            "description": "檢查容器資源使用",
            "action": "docker stats --no-stream",
            "risk": "low",
            "can_execute_immediately": True
        })
    
    return suggestions


def save_optimization_suggestions(suggestions: List[Dict[str, Any]]):
    """儲存優化建議"""
    try:
        if OPTIMIZATION_SUGGESTIONS_FILE.exists():
            existing = json.loads(OPTIMIZATION_SUGGESTIONS_FILE.read_text(encoding="utf-8"))
        else:
            existing = []
        
        # 加入新建議
        for suggestion in suggestions:
            suggestion["created_at"] = datetime.now().isoformat()
            existing.append(suggestion)
        
        # 只保留最近 100 個建議
        existing = existing[-100:]
        
        OPTIMIZATION_SUGGESTIONS_FILE.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        log(f"已儲存 {len(suggestions)} 個優化建議", "INFO")
    except Exception as e:
        log(f"儲存優化建議失敗: {e}", "ERROR")


def execute_safe_optimization(suggestion: Dict[str, Any]) -> Dict[str, Any]:
    """執行安全的優化（不涉及巨大變動）"""
    if not suggestion.get("can_execute_immediately"):
        return {"ok": False, "message": "此優化需要人工確認"}
    
    if suggestion.get("risk") != "low":
        return {"ok": False, "message": "此優化風險較高，需要人工確認"}
    
    action = suggestion.get("action", "")
    if not action:
        return {"ok": False, "message": "無有效操作指令"}
    
    log(f"執行安全優化: {suggestion.get('description', '')}", "INFO")
    
    try:
        # 執行指令
        if action.startswith("docker "):
            cmd = action.split()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                log(f"✅ 優化執行成功: {suggestion.get('description', '')}", "INFO")
                return {
                    "ok": True,
                    "message": "優化執行成功",
                    "output": result.stdout[:500]  # 限制輸出長度
                }
            else:
                log(f"⚠️ 優化執行失敗: {result.stderr[:200]}", "WARN")
                return {
                    "ok": False,
                    "message": "優化執行失敗",
                    "error": result.stderr[:500]
                }
        else:
            return {"ok": False, "message": "不支援的操作類型"}
            
    except Exception as e:
        log(f"執行優化時發生錯誤: {e}", "ERROR")
        return {"ok": False, "message": f"執行錯誤: {str(e)}"}


def main_loop(interval: int = 3600):  # 預設改為 1 小時
    """主循環：地端小 j 持續監控並與 JULES 協作"""
    log("啟動地端小 j 與 JULES 容器維護協作", "INFO")
    log(f"檢查間隔: {interval} 秒（{interval // 60} 分鐘）", "INFO")
    
    state = load_state()
    
    while True:
        try:
            log("開始檢查容器狀態...", "INFO")
            
            # 1. 地端小 j 檢查容器狀態
            status = check_container_status()
            
            if not status.get("ok"):
                log(f"檢查失敗: {status.get('error')}", "ERROR")
                time.sleep(interval)
                continue
            
            log(f"容器狀態: 總數 {status['total']}, 運行中 {status['running_count']}, 已停止 {status['stopped_count']}, 重啟中 {status['restarting_count']}", "INFO")
            
            # 2. 偵測問題
            issues = detect_issues(status)
            
            # 3. 進行工作討論和優化分析
            discussion_result = analyze_and_discuss(status, issues)
            
            # 4. 處理優化建議
            suggestions = discussion_result.get("suggestions", [])
            if suggestions:
                log(f"發現 {len(suggestions)} 個優化建議", "INFO")
                save_optimization_suggestions(suggestions)
                
                # 執行可以立即執行的安全優化
                for suggestion in suggestions:
                    if suggestion.get("can_execute_immediately") and suggestion.get("risk") == "low":
                        log(f"執行安全優化: {suggestion.get('description', '')}", "INFO")
                        result = execute_safe_optimization(suggestion)
                        if result.get("ok"):
                            log(f"✅ 優化完成: {suggestion.get('description', '')}", "INFO")
                        else:
                            log(f"⚠️ 優化失敗: {result.get('message', '')}", "WARN")
            
            # 5. 處理問題
            if issues:
                log(f"偵測到 {len(issues)} 個問題", "WARN")
                
                for issue in issues:
                    issue_id = f"{issue['type']}_{issue.get('container', '')}_{datetime.now().isoformat()}"
                    
                    # 檢查是否已回報過
                    if issue_id in state.get("issues_reported", []):
                        log(f"問題已回報過，跳過: {issue['type']}", "INFO")
                        continue
                    
                    # 6. 建立 JULES 任務（包含討論結果）
                    log(f"建立 JULES 任務: {issue['message']}", "INFO")
                    # 將討論結果加入任務內容
                    issue_with_discussion = issue.copy()
                    issue_with_discussion["discussion"] = discussion_result.get("discussion", "")
                    task_id = create_jules_task(issue_with_discussion, status)
                    
                    if task_id:
                        state["issues_reported"].append(issue_id)
                        state["jules_tasks_created"].append({
                            "issue_id": issue_id,
                            "task_id": task_id,
                            "issue": issue,
                            "timestamp": datetime.now().isoformat()
                        })
                        save_state(state)
                    else:
                        log(f"建立任務失敗: {issue['message']}", "ERROR")
            else:
                log("✅ 所有容器狀態正常", "INFO")
                
                # 驗證之前報告的問題是否已修復
                if state.get("jules_tasks_created"):
                    log("驗證之前報告的問題...", "INFO")
                    for task_info in state["jules_tasks_created"][-5:]:  # 只驗證最近5個
                        if task_info.get("verified"):
                            continue
                        
                        issue = task_info.get("issue", {})
                        verification = verify_fix(issue)
                        
                        task_info["verified"] = True
                        task_info["verification"] = verification
                        task_info["verification_time"] = datetime.now().isoformat()
                        
                        if verification.get("ok"):
                            log(f"✅ 問題已修復: {issue.get('message', '')}", "INFO")
                        else:
                            log(f"⚠️ 問題未修復: {verification.get('message', '')}", "WARN")
                    
                    save_state(state)
            
            state["last_check"] = datetime.now().isoformat()
            save_state(state)
            
            log(f"等待 {interval} 秒後再次檢查...", "INFO")
            time.sleep(interval)
            
        except KeyboardInterrupt:
            log("收到中斷信號，停止協作", "INFO")
            break
        except Exception as e:
            log(f"發生錯誤: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            time.sleep(interval)


def main():
    """主函數"""
    import argparse
    
    ap = argparse.ArgumentParser(description="地端小 j 與 JULES 容器維護協作")
    ap.add_argument("--interval", type=int, default=3600, help="檢查間隔（秒），預設 3600 秒（1小時）")
    ap.add_argument("--once", action="store_true", help="只執行一次檢查（不循環）")
    
    args = ap.parse_args()
    
    if args.once:
        log("執行單次檢查", "INFO")
        status = check_container_status()
        issues = detect_issues(status)
        
        print("\n" + "=" * 70)
        print("容器狀態檢查結果")
        print("=" * 70)
        print()
        print(f"總容器數: {status.get('total', 0)}")
        print(f"運行中: {status.get('running_count', 0)}")
        print(f"已停止: {status.get('stopped_count', 0)}")
        print(f"重啟中: {status.get('restarting_count', 0)}")
        print()
        
        if issues:
            print(f"偵測到 {len(issues)} 個問題：")
            for issue in issues:
                print(f"  - [{issue['severity']}] {issue['message']}")
                print(f"    建議操作: {issue['action']}")
        else:
            print("✅ 所有容器狀態正常")
        
        # 進行工作討論
        print("\n" + "=" * 70)
        print("工作討論與優化分析")
        print("=" * 70)
        print()
        
        discussion_result = analyze_and_discuss(status, issues)
        
        if discussion_result.get("discussion"):
            print("【討論結果】")
            print(discussion_result["discussion"])
            print()
        
        # 處理優化建議
        suggestions = discussion_result.get("suggestions", [])
        if suggestions:
            print(f"【優化建議】共 {len(suggestions)} 個")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. {suggestion.get('description', '')}")
                print(f"   類型: {suggestion.get('type', '')}")
                print(f"   風險: {suggestion.get('risk', '')}")
                print(f"   可立即執行: {'是' if suggestion.get('can_execute_immediately') else '否'}")
                print()
            
            # 執行可以立即執行的安全優化
            safe_suggestions = [s for s in suggestions if s.get("can_execute_immediately") and s.get("risk") == "low"]
            if safe_suggestions:
                print("【執行安全優化】")
                for suggestion in safe_suggestions:
                    print(f"執行: {suggestion.get('description', '')}")
                    result = execute_safe_optimization(suggestion)
                    if result.get("ok"):
                        print(f"✅ 完成: {result.get('message', '')}")
                    else:
                        print(f"⚠️ 失敗: {result.get('message', '')}")
                    print()
            
            # 儲存建議
            save_optimization_suggestions(suggestions)
        else:
            print("【優化建議】無新建議")
    else:
        main_loop(args.interval)


if __name__ == "__main__":
    main()
