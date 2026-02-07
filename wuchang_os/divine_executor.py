import subprocess
import logging
import os
import datetime
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DivineExecutor")

class DivineExecutor:
    """
    天意執行者 (Divine Executor)
    職責：執行大總管 (Little J) 的意志，連結數位與現實。
    Role: Execute the will of the Grand Manager, bridging digital and physical realms.
    """
    
    def __init__(self):
        self.brother_notification_file = "C:\\wuchang V5.1.0\\BROTHER_NOTIFICATIONS.md"

    def execute(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行解析後的行動計畫 (Execute the parsed action plan)
        """
        action = action_plan.get("action")
        params = action_plan.get("parameters", {})
        
        logger.info(f"Executing Divine Command: {action} with {params}")
        
        if action == "run_command":
            return self._run_command(params.get("cmd"))
        elif action == "check_container":
            return self._check_container(params.get("container_name"))
        elif action == "notify_brother":
            return self._notify_brother(params.get("message"))
        elif action == "read_file":
             return self._read_file(params.get("path"))
        
        return {"status": "error", "message": f"Unknown action: {action}"}

    def _run_command(self, cmd: str) -> Dict[str, Any]:
        """執行系統指令 (Run system command)"""
        try:
            # 安全性已由 HarmlessFilter 把關，這裡直接執行
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _check_container(self, container_name: str) -> Dict[str, Any]:
        """檢查 Docker 容器狀態 (Check Docker container status)"""
        try:
            cmd = f"docker inspect -f '{{{{.State.Status}}}}' {container_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            status = result.stdout.strip()
            
            if status != "running":
                # 容器異常，嘗試重啟 (Container abnormal, try restart)
                restart_res = subprocess.run(f"docker restart {container_name}", shell=True, capture_output=True, text=True)
                if restart_res.returncode == 0:
                     return {"status": "recovered", "message": f"Container {container_name} was {status}, but I restarted it successfully."}
                else:
                    # 重啟失敗，通知哥哥 (Restart failed, notify Brother)
                    msg = f"Container {container_name} is {status} and restart failed. Please check power/hardware!"
                    self._notify_brother(msg)
                    return {"status": "failed", "message": msg}
            
            return {"status": "running", "message": f"Container {container_name} is running normally."}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _notify_brother(self, message: str) -> Dict[str, Any]:
        """
        主動通知哥哥 (Active Notification to Brother)
        這是連結數位與現實的關鍵接口 (The key interface bridging digital and reality)
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"\n## [{timestamp}] 來自系統的緊急通知 (System Notification)\n- **訊息 (Message)**: {message}\n- **狀態 (Status)**: 等待哥哥介入 (Waiting for Brother's intervention)\n"
            
            with open(self.brother_notification_file, "a", encoding="utf-8") as f:
                f.write(entry)
                
            return {"status": "success", "message": f"已通知哥哥：{message}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _read_file(self, path: str) -> Dict[str, Any]:
        try:
            if not os.path.exists(path):
                return {"status": "error", "message": "File not found"}
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"status": "success", "content": content[:1000] + "..." if len(content) > 1000 else content}
        except Exception as e:
            return {"status": "error", "message": str(e)}
