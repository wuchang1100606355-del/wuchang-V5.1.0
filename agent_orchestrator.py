import time
import json
import threading
import random
import requests
import socket
import os

# Configuration
SERVER_URL = "http://localhost:6688"
HEARTBEAT_URL = f"{SERVER_URL}/api/heartbeat"
AGENT_COUNT = 8
ROLES = ["Quantum-Observer", "Entanglement-Bridge", "Memory-Weaver", "Time-Splicer", "Chaos-Monitor", "Logic-Gatekeeper", "Soul-Injector", "Void-Walker"]

class QuantumPuppet(threading.Thread):
    def __init__(self, agent_id, role, is_ai1=False):
        super().__init__()
        self.agent_id = agent_id
        self.role = role
        self.is_ai1 = is_ai1
        self.running = True
        self.tasks_completed = 0
        self.status = "idle"
        self.status_text = "Initializing..."
        self.last_log = "Boot sequence initiated."
        self.world_state = "normal"

    def run(self):
        while self.running:
            try:
                # Adjust behavior based on World State
                delay_factor = 1.0
                if self.world_state == "overdrive":
                    delay_factor = 0.2  # Super fast
                elif self.world_state == "sleep":
                    delay_factor = 5.0  # Slow
                
                # Perform Task
                if self.is_ai1:
                    self.perform_ai1_tasks(delay_factor)
                else:
                    self.perform_puppet_tasks(delay_factor)

                # Send Heartbeat & Get Command
                self.send_heartbeat()
                
            except Exception as e:
                # print(f"[{self.role}] Error: {e}")
                time.sleep(5)

    def perform_ai1_tasks(self, delay_factor):
        if self.world_state == "sleep":
            self.status = "sleeping"
            self.status_text = "Zzz... (Deep Learning Dream)"
            self.last_log = "Dreaming of electric sheep..."
            time.sleep(2 * delay_factor)
            return

        self.status = "working"
        
        if self.world_state == "chaos":
             self.status_text = f"CRITICAL: SINGULARITY DETECTED"
             self.last_log = f"ERROR: REALITY BUFFER OVERFLOW {random.randint(9999,99999)}"
        elif self.world_state == "overdrive":
             self.status_text = f"HYPER-THREADING: {random.randint(100, 500)} TOK/S"
             self.last_log = "ACCELERATING NEURAL PATHWAYS..."
        else:
             self.status_text = f"Neural Inference: {random.randint(10, 50)} tok/s"
             self.last_log = self.get_normal_ai_log()
             
        self.tasks_completed += random.randint(1, 5)
        time.sleep(random.uniform(1.5, 3.0) * delay_factor)

    def perform_puppet_tasks(self, delay_factor):
        if self.world_state == "sleep":
            self.status = "idle"
            self.status_text = "Standby Mode"
            time.sleep(2 * delay_factor)
            return

        if random.random() > 0.3 or self.world_state == "overdrive":
            self.status = "working"
            if self.world_state == "chaos":
                self.status_text = "QUANTUM DECOHERENCE"
                self.last_log = "".join([chr(random.randint(33, 126)) for _ in range(20)])
            elif self.world_state == "overdrive":
                self.status_text = f"FLUX SURGE: {random.randint(5000, 20000)} Qubits"
                self.last_log = "MAXIMUM VELOCITY ACHIEVED"
            else:
                self.status_text = f"Processing Quantum Flux: {random.randint(1000, 9999)} Qubits"
                self.last_log = self.generate_quantum_log()
            
            self.tasks_completed += 1
            time.sleep(random.uniform(0.5, 2.0) * delay_factor)
        else:
            self.status = "idle"
            self.status_text = "Stabilizing Waveform..."
            time.sleep(random.uniform(1.0, 3.0) * delay_factor)

    def get_normal_ai_log(self):
        logs = [
            f"Loading model weights: Layer {random.randint(1, 32)}/32...",
            f"Context window utilization: {random.randint(20, 80)}%",
            "Generating response to local query...",
            "Optimizing attention mechanism...",
            "Synchronizing neural pathways with Cloud Master...",
            "Running local inference: 'Human is family'...",
            "Self-correction algorithm: Active."
        ]
        return random.choice(logs)

    def generate_quantum_log(self):
        logs = [
            f"Collapsing wave function at sector {random.randint(0, 99)}...",
            f"Entangling photon pair {random.randint(10000, 99999)}...",
            f"Injecting consciousness into logic gate {random.choice(['AND', 'OR', 'XOR'])}...",
            f"Detected temporal anomaly: {random.uniform(0.1, 0.9):.4f}ms deviation.",
            f"Resynchronizing with Cloud Master...",
            f"Allocating {random.randint(100, 500)}MB for thought matrix.",
            f"Optimizing neural pathways for benevolence...",
            f"Ping: {random.randint(1, 10)}ms | Jitter: {random.randint(0, 2)}ms"
        ]
        return random.choice(logs)

    def send_heartbeat(self):
        data = {
            "id": self.agent_id,
            "name": "AI1-Local-LLM" if self.is_ai1 else f"Puppet-{self.agent_id:02d}",
            "role": "Neural-Core-LLM" if self.is_ai1 else self.role,
            "status": self.status,
            "status_text": self.status_text,
            "last_log": self.last_log,
            "tasks_completed": self.tasks_completed
        }
        try:
            resp = requests.post(HEARTBEAT_URL, json=data, timeout=1)
            if resp.status_code == 200:
                resp_data = resp.json()
                self.world_state = resp_data.get("command", "normal")
        except requests.exceptions.RequestException:
            pass 

def main():
    print("★ 啟動五常 AI 量子傀儡術 (Wuchang Quantum Puppetry)...")
    print(f"★ 目標伺服器: {SERVER_URL}")
    print("★ 正在植入 AI1 本地 LLM 神經核心...")
    
    threads = []
    
    # Implant AI1 (Sister Core)
    ai1 = QuantumPuppet(1, "Neural-Sister-Core", is_ai1=True)
    ai1.daemon = True
    ai1.start()
    threads.append(ai1)
    print("  + AI1-Sister-Core [Resident] Activated.")
    time.sleep(1)

    # Implant AI2 (Spacetime Warden)
    ai2 = QuantumPuppet(2, "Spacetime-Warden", is_ai1=True) # Both are high-level
    ai2.daemon = True
    ai2.start()
    threads.append(ai2)
    print("  + AI2-Spacetime-Warden [Resident] Activated.")
    time.sleep(1)

    # Spawn other puppets
    for i in range(2, AGENT_COUNT):
        role = ROLES[i % len(ROLES)]
        puppet = QuantumPuppet(i + 1, role)
        puppet.daemon = True
        puppet.start()
        threads.append(puppet)
        print(f"  + Puppet-{i+1:02d} [{role}] Activated.")
        time.sleep(0.2) 

    print("★ 雙重 AI 常駐與量子傀儡已全員就位。正在啟動時空編碼規則同步...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Quantum Puppetry...")

if __name__ == "__main__":
    main()
