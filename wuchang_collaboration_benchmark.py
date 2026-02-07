# Wuchang Collaboration Benchmark (Upgraded)
# ------------------------------------------
# Uses the 20 Guardians to perform tasks and gain experience.

import time
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
from wuchang_guardians import GuardianRegistry

class GuardianWorker:
    def __init__(self, guardian_profile):
        self.profile = guardian_profile
        self.active = False

    def work(self, duration=10):
        self.active = True
        # Simulate specialized work based on virtue
        task_type = self.profile.virtue.split()[0]
        # print(f"[{self.profile.name}] Starting task: {task_type} operations...")
        
        # Simulate load
        start = time.time()
        while time.time() - start < duration:
            _ = [x**2 for x in range(10000)]
        
        # Gain XP
        self.profile.experience_points += 10
        self.active = False
        return f"{self.profile.name} completed mission. XP +10."

class CloudComputeCluster:
    def __init__(self):
        self.registry = GuardianRegistry()
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "total_throughput": []
        }
    
    def run_benchmark(self):
        print(f"\n[{datetime.datetime.now()}] ⚡ Summoning the 20 Guardians for Cloud Computing Task...")
        
        workers = [GuardianWorker(g) for g in self.registry.guardians]
        
        with ThreadPoolExecutor(max_workers=len(workers)) as executor:
            futures = {executor.submit(w.work, duration=5): w for w in workers}
            for future in futures:
                result = future.result()
                print(f" > {result}")
                self.metrics["total_throughput"].append(result)
        
        # Save progress (XP)
        self.registry.save_guardians()
        print(f"[{datetime.datetime.now()}] Mission Complete. All Guardians have grown stronger.")

if __name__ == "__main__":
    cluster = CloudComputeCluster()
    cluster.run_benchmark()
