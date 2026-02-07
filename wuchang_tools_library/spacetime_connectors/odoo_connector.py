import logging
import xmlrpc.client
import socket
from .base_connector import BaseConnector

logger = logging.getLogger('spacetime_odoo')

class OdooConnector(BaseConnector):
    def __init__(self):
        super().__init__('Odoo POS & ERP')
        # Dual-environment configuration
        self.service_url = 'http://wuchang-pos:8069'
        self.local_url = 'http://localhost:8069'
        self.active_url = None
        
        self.db = 'wuchang'
        self.username = 'admin'
        self.password = 'admin'
        self.uid = None

    def _test_connection(self, url):
        try:
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(self.db, self.username, self.password, {})
            if uid:
                return uid
        except Exception:
            return None
        return None

    def connect(self):
        # Try Docker Service URL first
        logger.info(f'Attempting connection to {self.service_url}...')
        self.uid = self._test_connection(self.service_url)
        
        if self.uid:
            self.active_url = self.service_url
            self.connected = True
            self.status = f'Active (Service: {self.service_url})'
            logger.info(f'✅ Odoo Connected via Service (UID: {self.uid})')
        else:
            # Try Localhost URL
            logger.info(f'Service connection failed. Attempting {self.local_url}...')
            self.uid = self._test_connection(self.local_url)
            
            if self.uid:
                self.active_url = self.local_url
                self.connected = True
                self.status = f'Active (Localhost: {self.local_url})'
                logger.info(f'✅ Odoo Connected via Localhost (UID: {self.uid})')
            else:
                self.connected = False
                self.status = 'Authentication Failed (Both Methods)'
                logger.error('❌ Odoo Connection Failed')

    def get_status(self):
        return {
            'name': self.name,
            'status': self.status,
            'connected': self.connected,
            'details': {
                'url': self.active_url,
                'database': self.db,
                'uid': self.uid
            }
        }

