import os
import logging
from .base_connector import BaseConnector

logger = logging.getLogger('GoogleNonProfitConnector')

class GoogleNonProfitConnector(BaseConnector):
    def __init__(self):
        super().__init__('Google for Nonprofits')
        self.credentials_path = '/app/config/google_token.json'
        self.products = ['Google Ad Grants', 'YouTube Nonprofit Program', 'Google Workspace for Nonprofits']

    def connect(self):
        # NPO resources rely on the main Google Token
        if os.path.exists(self.credentials_path):
            self.connected = True
            self.status = 'Active (Managed via Google Token)'
            logger.info('✅ Google Non-Profit resources linked.')
        else:
            self.connected = False
            self.status = 'Pending Google Token'
    
    def health_check(self):
        return self.connected

    def get_status_report(self):
        return {
            'name': self.name,
            'status': self.status,
            'connected': self.connected,
            'managed_resources': self.products,
            'resource_type': 'Organization Benefits'
        }
