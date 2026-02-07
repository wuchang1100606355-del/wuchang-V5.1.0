import time
import logging
import random
import json

class DoubleJEdgeAdapter:
    def __init__(self, node_id):
        self.node_id = node_id
        self.logger = logging.getLogger(f'Edge-{node_id}')
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def process_task(self, task):
        process_time = random.uniform(0.01, 0.05)
        time.sleep(process_time)
        
        try:
            task_str = json.dumps(task, ensure_ascii=False)
        except:
            task_str = str(task)

        self.logger.info(f'Processing -> {task_str}')
        
        return {'id': task.get('id'), 'status': 'completed', 'node': self.node_id, 'time': process_time}
