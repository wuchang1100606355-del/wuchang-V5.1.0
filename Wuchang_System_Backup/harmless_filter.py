import os
import psutil
import logging
from typing import Dict, Any, Tuple

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HarmlessFilter")

class HarmlessFilter:
    """
    無害決策過濾器 (Harmless Decision Filter)
    職責：作為「大總管」與「創世意志代理人」，過濾一切對哥哥 (User) 有害的決策。
    Role: As the Grand Manager and Representative of Divine Will, filter all decisions harmful to the User.
    """

    def __init__(self):
        self.risk_keywords = ["delete", "remove", "format", "shutdown", "reboot", "kill", "wipe", "destroy"]
        self.critical_services = ["vm_fastapi_main_new.py", "odoo-bin", "postgres"]
        self.resource_cap_cpu = 80.0  # CPU 使用上限 (保留 20% 給哥哥)
        self.resource_cap_memory = 80.0 # 記憶體使用上限

    def evaluate_action(self, action_type: str, details: Dict[str, Any]) -> Tuple[bool, str]:
        """
        評估動作是否安全 (Evaluate if the action is safe)
        Returns: (is_safe: bool, reason: str)
        """
        logger.info(f"Evaluating action: {action_type} - {details}")

        # 1. 關鍵字風險檢查 (Keyword Risk Check)
        if any(keyword in str(details).lower() for keyword in self.risk_keywords):
            # 特殊豁免：如果是清理暫存檔 (Special Exemption: Cleaning temp files)
            if "temp" in str(details).lower() or "cache" in str(details).lower():
                return True, "Risk keyword found but deemed safe (cleanup)."
            return False, f"Action blocked: Risk keyword detected in {details}"

        # 2. 資源保護檢查 (Resource Protection Check)
        if action_type == "start_process":
            if not self._check_resources():
                return False, "Action blocked: System resources too low (preserving for User)."

        # 3. 關鍵服務保護 (Critical Service Protection)
        if action_type == "stop_process":
            target = details.get("target_process", "")
            if any(service in target for service in self.critical_services):
                return False, f"Action blocked: Cannot stop critical service {target} without explicit override."

        # 4. 創世意志一致性 (Alignment with Creator's Will)
        # 這裡未來可以接入 AI 語意分析，判斷動作是否違背「無後顧之憂」原則
        
        return True, "Action approved: Harmless and aligned."

    def _check_resources(self) -> bool:
        """檢查系統資源是否充足 (Check if system resources are sufficient)"""
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_usage = psutil.virtual_memory().percent
        
        if cpu_usage > self.resource_cap_cpu:
            logger.warning(f"CPU usage high ({cpu_usage}%), blocking new heavy tasks.")
            return False
        if memory_usage > self.resource_cap_memory:
            logger.warning(f"Memory usage high ({memory_usage}%), blocking new heavy tasks.")
            return False
        return True

if __name__ == "__main__":
    # 測試案例
    filter_guard = HarmlessFilter()
    
    # 測試 1: 刪除檔案 (應被阻擋)
    print(filter_guard.evaluate_action("delete_file", {"path": "C:/important_data.txt"}))
    
    # 測試 2: 啟動服務 (資源允許時應通過)
    print(filter_guard.evaluate_action("start_process", {"cmd": "python script.py"}))
    
    # 測試 3: 清理快取 (應通過)
    print(filter_guard.evaluate_action("delete_file", {"path": "C:/temp/cache.tmp"}))
