import os
import json
import shutil
import time
import asyncio
from datetime import datetime

# Import Core Modules
from time_transmission import transmitter
from self_evolution_core import SelfEvolutionCore
from cloud_neural_sync import CloudNeuralSync

# Background Task Manager
class SystemBrain:
    def __init__(self):
        self.evolution_core = SelfEvolutionCore()
        self.cloud_sync = CloudNeuralSync()
        self.last_sync_time = 0
        self.sync_interval = 300  # 5 minutes
        
    async def run_background_tasks(self):
        """週期性執行後台任務"""
        while True:
            now = time.time()
            
            # 1. Self-Evolution Check (Every 5 mins)
            if now - self.last_sync_time > self.sync_interval:
                print("[Brain] Running Self-Evolution Cycle...")
                try:
                    self.evolution_core.analyze_failures()
                    self.evolution_core.consolidate_wisdom()
                    self.evolution_core.evolve_config()
                    transmitter.transmit("SystemBrain", "Evolution Cycle", {"status": "Success"})
                except Exception as e:
                    print(f"[Brain] Evolution Error: {e}")
                    transmitter.transmit("SystemBrain", "Evolution Error", {"error": str(e)})

                # 2. Cloud Neural Sync
                print("[Brain] Running Cloud Neural Sync...")
                try:
                    self.cloud_sync.sync_all()
                    transmitter.transmit("SystemBrain", "Cloud Sync", {"status": "Success"})
                except Exception as e:
                    print(f"[Brain] Sync Error: {e}")
                    transmitter.transmit("SystemBrain", "Cloud Sync Error", {"error": str(e)})
                    
                self.last_sync_time = now
            
            await asyncio.sleep(60)  # Check every minute

brain = SystemBrain()
