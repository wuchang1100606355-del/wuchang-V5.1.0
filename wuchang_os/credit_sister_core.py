import os
import json
import datetime
import uuid
from time_transmission import transmitter

class CreditSisterCore:
    """
    抵免額妹妹 (Credit Sister) - Core Logic
    
    負責管理社區「抵免額 (Credits)」的發放、查詢與使用。
    """
    
    def __init__(self, base_dir=r"C:\wuchang V5.1.0\wuchang_os"):
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, "double_j_config.json")
        self.ledger_path = os.path.join(base_dir, "credit_ledger.jsonl")
        
    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def _save_config(self, config):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def get_balance(self, user_id):
        """查詢餘額"""
        config = self._load_config()
        return config.get("user_credits", {}).get(user_id, 0)

    def transaction(self, user_id, amount, transaction_type, description):
        """執行交易 (增加或扣除)"""
        config = self._load_config()
        
        # 1. Update Balance
        if "user_credits" not in config:
            config["user_credits"] = {}
        
        current_balance = config["user_credits"].get(user_id, 0)
        new_balance = current_balance + amount
        
        if new_balance < 0:
            return {"success": False, "message": "餘額不足 (Insufficient Funds)"}
            
        config["user_credits"][user_id] = new_balance
        
        # 2. Record to Ledger (Local)
        record = {
            "tx_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "amount": amount,
            "type": transaction_type,
            "description": description,
            "balance_after": new_balance
        }
        
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
        # 3. Save Config
        self._save_config(config)
        
        # 4. Time Transmission (System Log)
        transmitter.transmit("CreditSister", "Transaction", record)
        
        return {"success": True, "message": "交易成功", "new_balance": new_balance, "tx_id": record["tx_id"]}

    def get_persona_prompt(self):
        return """
        【抵免額妹妹 (Credit Sister)】
        你是五常社區的財務管家。你的性格嚴謹、精明，但對家人（使用者）非常貼心。
        
        **你的職責**：
        1. 查詢抵免額 (五常幣/WC)。
        2. 解釋如何獲得抵免額 (志工、貢獻)。
        3. 協助抵免訂閱費用。
        
        **說話風格**：
        - 稱呼使用者為「哥哥/姐姐」或「親愛的家人」。
        - 談到數字時非常精確。
        - 喜歡用 💰、📉、📈 等符號。
        """

# Singleton
credit_sister = CreditSisterCore()
