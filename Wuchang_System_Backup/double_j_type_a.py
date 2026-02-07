import time
import logging

class DoubleJCloudCNS:
    def __init__(self, name="Cloud-1"):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def distribute_tasks(self, tasks, nodes):
        self.logger.info(f"Distributing {len(tasks)} tasks to {len(nodes)} nodes via STAPS.")
        chunk_size = len(tasks) // len(nodes)
        distributions = {}
        for i, node in enumerate(nodes):
            start = i * chunk_size
            end = start + chunk_size if i < len(nodes) - 1 else len(tasks)
            distributions[node.node_id] = tasks[start:end]
        return distributions
