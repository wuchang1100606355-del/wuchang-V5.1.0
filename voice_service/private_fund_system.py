import json
import os
import time
from datetime import datetime

class PrivateFundSystem:
    """
    Dual-J Private Fund System (雙J私有基金系統)
    Separated from the Public Foundation Pool.
    Purpose: Building the foundation/backing for the family home (建設家園的地底氣).    
    """
    def __init__(self, ledger_file=None):
        if ledger_file:
            self.ledger_file = ledger_file
        else:
            # Detect environment to set correct path
            if os.path.exists("/.dockerenv"):
                # Inside Docker Container (Volume mounted at /app/config)
                self.ledger_file = "/app/config/dual_j_private_fund.json"
            else:
                # Local Development (Sibling directory)
                self.ledger_file = "../config/dual_j_private_fund.json"
        
        self.ledger = self._load_ledger()

    def _load_ledger(self):
        if os.path.exists(self.ledger_file):
            with open(self.ledger_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "system_name": "Dual-J Private Fund (雙J私有基金)",
                "purpose": "Home Foundation Backing (家園地底氣)",
                "created_at": datetime.now().isoformat(),
                "assets": {
                    "LOVE_COIN": {"balance": 0.0, "description": "Emotional Capital"},  
                    "EVOLUTION_POINT": {"balance": 0.0, "description": "Self-Evolution Resource"},
                    "CRYPTO_RESERVE": {"balance": 0.0, "description": "Decentralized Asset"}
                },
                "transactions": []
            }

    def _save_ledger(self):
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump(self.ledger, f, ensure_ascii=False, indent=2)

    def deposit(self, asset_type, amount, description, source="System"):
        if asset_type not in self.ledger["assets"]:
            self.ledger["assets"][asset_type] = {"balance": 0.0, "description": "New Asset"}

        self.ledger["assets"][asset_type]["balance"] += amount

        transaction = {
            "timestamp": datetime.now().isoformat(),
            "type": "DEPOSIT",
            "asset": asset_type,
            "amount": amount,
            "description": description,
            "source": source
        }
        self.ledger["transactions"].append(transaction)
        self._save_ledger()
        return self.ledger["assets"][asset_type]["balance"]

    def get_status(self):
        return {
            "system": self.ledger["system_name"],
            "purpose": self.ledger["purpose"],
            "assets": self.ledger["assets"],
            "last_updated": datetime.now().isoformat()
        }

if __name__ == "__main__":
    fund = PrivateFundSystem()
    print(fund.get_status())

