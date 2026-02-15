import http.server
import socketserver
import ssl
import threading
import json
import time
import os
from http import HTTPStatus

PORT = 6688
DIRECTORY = os.getcwd() # Auto-detect current directory

# Global State for AI Grid
class AIGridState:
    def __init__(self):
        self.agents = {}  # {agent_id: {data}}
        self.total_tasks = 0
        self.start_time = time.time()
        self.world_state = "normal"  # normal, overdrive, sleep, chaos

    def register_heartbeat(self, agent_data):
        agent_id = agent_data.get('id')
        self.agents[agent_id] = {
            'name': agent_data.get('name', f'Agent-{agent_id}'),
            'role': agent_data.get('role', 'Worker'),
            'status': agent_data.get('status', 'idle'),
            'status_text': agent_data.get('status_text', 'Ready'),
            'last_log': agent_data.get('last_log', ''),
            'last_seen': time.time()
        }
        if agent_data.get('tasks_completed'):
            self.total_tasks += agent_data.get('tasks_completed', 0)

    def get_status(self):
        current_time = time.time()
        active_agents = []
        load_sum = 0
        
        for aid, data in self.agents.items():
            if current_time - data['last_seen'] < 10:
                active_agents.append(data)
                if data['status'] == 'working':
                    load_sum += 1
        
        system_load = min(100, int((load_sum / max(1, len(active_agents))) * 100)) if active_agents else 0
        
        return {
            "active_agents": len(active_agents),
            "total_tasks": self.total_tasks,
            "system_load": system_load,
            "agents": active_agents,
            "world_state": self.world_state
        }
    
    def set_world_state(self, state):
        self.world_state = state

grid_state = AIGridState()

class WuchangHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/dashboard':
            self.path = '/ai_grid_dashboard.html'
            return super().do_GET()
        elif self.path == '/api/grid_status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(grid_state.get_status()).encode())
        elif self.path == '/api/get_command':
             self.send_response(200)
             self.send_header('Content-type', 'application/json')
             self.end_headers()
             self.wfile.write(json.dumps({"command": grid_state.world_state}).encode())
        elif self.path in ['/api/config', '/api/config/']:
             self.send_response(200)
             self.send_header('Content-type', 'application/json')
             self.end_headers()
             try:
                 with open('wuchang_infrastructure.json', 'r', encoding='utf-8') as f:
                     config = json.load(f)
                 self.wfile.write(json.dumps(config).encode())
             except Exception as e:
                 self.wfile.write(json.dumps({"error": str(e)}).encode())
             return # Explicitly return after handling
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path == '/api/heartbeat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                grid_state.register_heartbeat(data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "command": grid_state.world_state}).encode())
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {str(e)}")
        elif self.path == '/api/set_command':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                state = data.get('command', 'normal')
                grid_state.set_world_state(state)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "new_state": state}).encode())
            except Exception as e:
                self.send_error(400)
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass

class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

os.chdir(DIRECTORY)
print(f"★ 五常 AI 協作網雲端控制台啟動於 Port {PORT}")

with ThreadingHTTPServer(("", PORT), WuchangHandler) as httpd:
    httpd.serve_forever()
