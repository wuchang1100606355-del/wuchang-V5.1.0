import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("SpacetimeConnector")

class BaseConnector(ABC):
    def __init__(self, name):
        self.name = name
        self.connected = False
        self.status = "Initialized"

    @abstractmethod
    def connect(self):
        """Establish connection to the service."""
        pass

    @abstractmethod
    def health_check(self):
        """Check if the service is healthy."""
        pass

    @abstractmethod
    def get_status_report(self):
        """Return a dictionary with status details."""
        pass
