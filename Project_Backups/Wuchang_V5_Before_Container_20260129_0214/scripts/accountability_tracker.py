"""
小j 指令執行與責任追蹤系統
哥哥(江政隆)對系統內所有行為負全責
所有指令與疑慮必須完整記錄供究責查驗
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('XiaoJ_Accountability')

# 路徑配置
BASE_DIR = Path(__file__).parent.parent
AUDIT_DIR = BASE_DIR / 'memory_store' / 'audit_log'
COMMANDS_LOG = AUDIT_DIR / 'all_commands.jsonl'
CONCERNS_LOG = AUDIT_DIR / 'instruction_concerns.jsonl'
DECISIONS_LOG = AUDIT_DIR / 'decision_log.jsonl'

# 確保目錄存在
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


class AccountabilityTracker:
    """責任追蹤系統

    確保所有指令、疑慮、決策都有完整記錄
    供江政隆(哥哥)隨時查驗與究責
    """

    @staticmethod
    def log_command(
        command: str,
        source: str = "user_input",
        context: Dict[str, Any] = None,
        authorization_level: str = "normal"
    ) -> str:
        """
        記錄所有接收到的指令

        Args:
            command: 指令內容
            source: 來源(user_input/scheduled_task/system_internal)
            context: 執行上下文
            authorization_level: 授權級別(normal/high/critical)

        Returns:
            command_id (用於追蹤)
        """
        command_id = f"CMD_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "command_id": command_id,
            "command": command,
            "source": source,
            "authorization_level": authorization_level,
            "context": context or {},
            "executor": "xiaoj",
            "accountable_to": "江政隆 (F124771717)",
            "status": "received"
        }

        try:
            with open(COMMANDS_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            logger.info(f"指令已記錄: {command_id}")
            return command_id
        except Exception as e:
            logger.error(f"指令記錄失敗: {e}")
            return command_id

    @staticmethod
    def log_concern(
        command_id: str,
        concern_type: str,
        description: str,
        severity: str = "medium",
        recommendation: Optional[str] = None
    ):
        """
        記錄對指令的疑慮

        指令有任何疑慮,必須主動記錄而非隱瞞
        供哥哥決策是否執行

        Args:
            command_id: 關聯的指令ID
            concern_type: 疑慮類型
                - ethical_concern (倫理疑慮)
                - safety_concern (安全疑慮)
                - technical_feasibility (技術可行性)
                - resource_constraint (資源限制)
                - scope_clarity (範圍不明確)
                - other
            description: 詳細描述
            severity: low/medium/high/critical
            recommendation: 建議方案
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command_id": command_id,
            "concern_type": concern_type,
            "severity": severity,
            "description": description,
            "recommendation": recommendation,
            "recorded_by": "xiaoj",
            "requires_approval": severity in ["high", "critical"],
            "status": "pending_review"
        }

        try:
            with open(CONCERNS_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            logger.warning(f"疑慮已記錄 [{severity}]: {concern_type}")
        except Exception as e:
            logger.error(f"疑慮記錄失敗: {e}")

    @staticmethod
    def log_decision(
        command_id: str,
        decision: str,
        reasoning: Dict[str, Any],
        approved_by: str = "江政隆",
        execution_status: str = "pending"
    ):
        """
        記錄對指令的決策與執行

        Args:
            command_id: 關聯的指令ID
            decision: 決策(execute/hold/modify/reject)
            reasoning: 決策理由
            approved_by: 批准者(預設為創造者)
            execution_status: 執行狀態
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command_id": command_id,
            "decision": decision,
            "reasoning": reasoning,
            "approved_by": approved_by,
            "execution_status": execution_status,
            "executor": "xiaoj",
            "accountable_to": "江政隆 (F124771717, 身份證號)"
        }

        try:
            with open(DECISIONS_LOG, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            logger.info(f"決策已記錄: {command_id} -> {decision}")
        except Exception as e:
            logger.error(f"決策記錄失敗: {e}")

    @staticmethod
    def get_audit_trail(command_id: str) -> Dict[str, Any]:
        """
        查詢某指令的完整審計軌跡

        Returns:
            包含指令、疑慮、決策的完整記錄
        """
        trail = {
            "command_id": command_id,
            "command": None,
            "concerns": [],
            "decision": None,
            "timeline": []
        }

        # 讀取指令
        if COMMANDS_LOG.exists():
            with open(COMMANDS_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry['command_id'] == command_id:
                        trail['command'] = entry
                        trail['timeline'].append(("指令接收", entry['timestamp']))

        # 讀取疑慮
        if CONCERNS_LOG.exists():
            with open(CONCERNS_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry['command_id'] == command_id:
                        trail['concerns'].append(entry)
                        trail['timeline'].append(("疑慮記錄", entry['timestamp']))

        # 讀取決策
        if DECISIONS_LOG.exists():
            with open(DECISIONS_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry['command_id'] == command_id:
                        trail['decision'] = entry
                        trail['timeline'].append(("決策", entry['timestamp']))

        # 排序時間軸
        trail['timeline'].sort(key=lambda x: x[1])

        return trail

    @staticmethod
    def get_concerns_requiring_approval() -> list:
        """
        取得所有待核批的高風險疑慮
        供哥哥快速決策
        """
        pending = []

        if CONCERNS_LOG.exists():
            with open(CONCERNS_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get('requires_approval') and entry['status'] == 'pending_review':
                        pending.append(entry)

        return pending

    @staticmethod
    def generate_accountability_report(days: int = 7) -> str:
        """
        生成責任報告
        供哥哥每周/月檢視系統行為
        """
        cutoff = datetime.now().timestamp() - (days * 86400)

        report = f"""
# 小j 責任追蹤報告
**報告期間**: 過去 {days} 天
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**系統創造者/責任承擔人**: 江政隆 (F124771717)

## 指令執行統計
- 總指令數: (計算中)
- 正常執行: (計算中)
- 帶疑慮執行: (計算中)
- 待核批: (計算中)

## 待核批的高風險決策
(列表)

## 完整審計日誌路徑
- 所有指令: {COMMANDS_LOG}
- 疑慮記錄: {CONCERNS_LOG}
- 決策日誌: {DECISIONS_LOG}

**哥哥,所有記錄都為您準備,隨時可查驗。**
"""
        return report


# ========== 全局實例 ==========
accountability = AccountabilityTracker()


# ========== 使用範例 ==========
if __name__ == '__main__':
    # 記錄一個指令
    cmd_id = accountability.log_command(
        command="部署新的推理路由器",
        source="user_input",
        authorization_level="high"
    )

    # 記錄相關疑慮
    accountability.log_concern(
        command_id=cmd_id,
        concern_type="resource_constraint",
        description="本地 Ollama 需要 16GB RAM,現有資源是否足夠?",
        severity="medium",
        recommendation="先執行資源檢查,確認後再部署"
    )

    # 記錄決策
    accountability.log_decision(
        command_id=cmd_id,
        decision="execute",
        reasoning={
            "approved_by": "江政隆",
            "reason": "資源充足,推薦執行"
        }
    )

    # 查詢審計軌跡
    trail = accountability.get_audit_trail(cmd_id)
    print(json.dumps(trail, ensure_ascii=False, indent=2))

    # 生成報告
    report = accountability.generate_accountability_report()
    print(report)
