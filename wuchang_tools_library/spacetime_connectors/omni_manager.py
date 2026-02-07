import logging
from .google_workspace import GoogleWorkspaceConnector
from .google_cloud import GoogleCloudConnector
from .google_nonprofit import GoogleNonProfitConnector
from .odoo_connector import OdooConnector
from .router_connector import RouterConnector
from .config_resource import ConfigResourceConnector

logger = logging.getLogger('SpacetimeOmniManager')

class SpacetimeOmniManager:
    def __init__(self):
        self.connectors = []
        self.initialize_connectors()

    def initialize_connectors(self):
        self.connectors = [
            GoogleWorkspaceConnector(),
            GoogleCloudConnector(),
            GoogleNonProfitConnector(),
            OdooConnector(),
            RouterConnector(),
            ConfigResourceConnector()
        ]
        logger.info('🌌 Spacetime Omni-Manager initialized with 6 connectors.')

    def connect_all(self):
        results = {}
        for connector in self.connectors:
            connector.connect()
            results[connector.name] = connector.status
        return results

    def get_full_report(self):
        report = {}
        for connector in self.connectors:
            report[connector.name] = connector.get_status_report()
        return report

    def health_check_all(self):
        return {c.name: c.health_check() for c in self.connectors}
