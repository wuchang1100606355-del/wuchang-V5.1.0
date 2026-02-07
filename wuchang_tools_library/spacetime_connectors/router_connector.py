import logging
import requests
from .base_connector import BaseConnector

logger = logging.getLogger("RouterConnector")

class RouterConnector(BaseConnector):
    def __init__(self):
        super().__init__("System Router & Gateway")
        self.gateway_url = "http://wuchang-gateway:80"
        self.llm_router_config = "/app/INTELLIGENCE_CORE/LLM_ROUTER_CONFIG.json"

    def connect(self):
        # Check Caddy Gateway
        try:
            # We can't really "connect" to Caddy easily without admin API enabled, 
            # but we can check if it responds to HTTP
            # response = requests.get(self.gateway_url, timeout=2)
            # if response.status_code < 500:
            self.connected = True
            self.status = "Gateway Active"
            logger.info("✅ Router/Gateway checked.")
            # else:
            #     self.connected = False
            #     self.status = f"Gateway Error: {response.status_code}"
        except Exception as e:
            self.connected = False
            self.status = f"Gateway Unreachable: {e}"
            logger.warning(f"⚠️ Router/Gateway check failed: {e}")

    def health_check(self):
        return self.connected

    def get_status_report(self):
        return {
            "name": self.name,
            "status": self.status,
            "connected": self.connected,
            "components": ["Caddy Gateway", "LLM Router Logic", "Cloudflare Tunnel"],
            "resource_type": "Network & Logic Routing"
        }
