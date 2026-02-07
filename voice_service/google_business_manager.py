import json
import os
import glob
from datetime import datetime

CONFIG_DIR = r"J:\共用雲端硬碟\五常雲端空間\config"

class GoogleBusinessManager:
    def __init__(self):
        self.accounts = []
        self.load_accounts()

    def load_accounts(self):
        """Load all google_*.json config files and filter for valid accounts."""
        pattern = os.path.join(CONFIG_DIR, "google_*.json")
        for config_file in glob.glob(pattern):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Only include files that look like account configs (have email)
                    if "account_email" in data:
                        data["_config_file"] = os.path.basename(config_file)
                        self.accounts.append(data)
            except Exception as e:
                print(f"Error loading {config_file}: {e}")

    def generate_report(self):
        """Generate a formatted report string."""
        lines = []
        lines.append(f"=== 📧 Consolidated Gmail Assets Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
        lines.append(f"Total Accounts Managed: {len(self.accounts)}\n")
        
        for idx, acc in enumerate(self.accounts, 1):
            lines.append(f"{idx}. [{acc.get('role', 'General Account')}] {acc.get('account_email', 'Unknown')}")
            lines.append(f"   Service: {acc.get('service', 'N/A')}")
            lines.append(f"   Status:  {acc.get('status', 'Unknown')}")
            lines.append(f"   Managed By: {acc.get('managed_by', 'System')}")
            lines.append(f"   Note: {acc.get('note', '-')}")
            lines.append("-" * 40)
        
        return "\n".join(lines)

    def list_managed_assets(self):
        print(self.generate_report())

    def save_report(self):
        report = self.generate_report()
        report_path = os.path.join(CONFIG_DIR, "GMAIL_CONSOLIDATION_REPORT.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("```text\n" + report + "\n```")
        print(f"Report saved to {report_path}")

if __name__ == "__main__":
    manager = GoogleBusinessManager()
    manager.list_managed_assets()
    manager.save_report()

