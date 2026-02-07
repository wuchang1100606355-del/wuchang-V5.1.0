import logging
import queue
import threading
import time
import json
import os
import xmlrpc.client
from datetime import datetime

# Local fallback log
LOCAL_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOCAL_LOG_DIR):
    os.makedirs(LOCAL_LOG_DIR)

class OdooLogger:
    def __init__(self, host=None, port=None, db=None, user=None, password=None):
        self.queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
        # Odoo Connection Details
        self.url = f"http://{host}:{port}" if host and port else None
        self.db = db
        self.username = user
        self.password = password
        self.uid = None
        self.connected = False
        
        # Initial Connection
        if self.url:
            self._connect()

    def _connect(self):
        try:
            common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                self.connected = True
                self._log_local("INFO", "Connected to Odoo successfully.")
            else:
                self._log_local("WARNING", "Odoo authentication failed.")
        except Exception as e:
            self._log_local("ERROR", f"Odoo connection error: {e}")

    def _worker(self):
        while self.running:
            try:
                task = self.queue.get(timeout=1)
                self._process_task(task)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self._log_local("ERROR", f"Worker error: {e}")

    def _process_task(self, task):
        log_type = task.get("type")
        data = task.get("data")
        
        if log_type == "audit":
            self._send_audit_log(data)
        elif log_type == "identity":
            self._send_identity_log(data)

    def _send_audit_log(self, data):
        # Fallback to local first
        self._log_local("AUDIT", json.dumps(data, ensure_ascii=False))
        
        if self.connected and self.uid:
            try:
                models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
                models.execute_kw(self.db, self.uid, self.password,
                    "audit.log", "create", [{
                        "name": data.get("action", "Unknown"),
                        "user_id": data.get("user", "System"),
                        "description": data.get("content", ""),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])
            except Exception as e:
                self._log_local("ERROR", f"Failed to send audit log to Odoo: {e}")

    def _send_identity_log(self, data):
         # Fallback to local
        self._log_local("IDENTITY", json.dumps(data, ensure_ascii=False))
        # Implementation for identity contract logging to Odoo would go here
        # For now, we rely on local logs or a specific Odoo model if it exists

    def _log_local(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(LOCAL_LOG_DIR, f"system_{datetime.now().strftime("%Y%m%d")}.log")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{level}] {message}\n")
        except Exception as e:
            print(f"CRITICAL: Cannot write to local log: {e}")

    def log_audit(self, user, action, content):
        task = {
            "type": "audit",
            "data": {
                "user": user,
                "action": action,
                "content": content
            }
        }
        self.queue.put(task)

    def log_identity_contract(self, contract_data):
        task = {
            "type": "identity",
            "data": contract_data
        }
        self.queue.put(task)

    def close(self):
        self.running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2)

