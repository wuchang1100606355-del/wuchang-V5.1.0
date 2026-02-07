import os
import json
import logging
from .base_connector import BaseConnector

logger = logging.getLogger("ConfigResourceConnector")

class ConfigResourceConnector(BaseConnector):
    def __init__(self):
        super().__init__("System Configurations")
        self.config_dir = "/app/INTELLIGENCE_CORE"
        self.configs = {}

    def connect(self):
        # Scan for config files
        try:
            if os.path.exists(self.config_dir):
                for f in os.listdir(self.config_dir):
                    if f.endswith(".json"):
                        self.configs[f] = "Loaded"
                self.connected = True
                self.status = f"Loaded {len(self.configs)} Configs"
                logger.info(f"✅ Loaded {len(self.configs)} configuration resources.")
            else:
                self.connected = False
                self.status = "Config Directory Missing"
        except Exception as e:
            self.connected = False
            self.status = f"Scan Error: {str(e)}"

    def health_check(self):
        return self.connected

    def get_status_report(self):
        return {
            "name": self.name,
            "status": self.status,
            "connected": self.connected,
            "resources": list(self.configs.keys()),
            "resource_type": "Configuration Objects"
        }
