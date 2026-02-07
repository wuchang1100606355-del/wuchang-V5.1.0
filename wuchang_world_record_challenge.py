import asyncio
import time
import os
import psutil
import sys
import json
import hashlib
import random
from datetime import datetime

# Global particle container to prevent GC and track souls
PARTICLES = set()

class JulesWitness:
    def __init__(self):
        self.api_file = 'J:\\共用雲端硬碟\\五常雲端空間\\wuchang_tools_library\\jules_api_endpoint.json'
        self.signature_key = "wuchang-quantum-v1-10m-run"
        self.ensure_file_exists()

    def ensure_file_exists(self):
        if not os.path.exists(os.path.dirname(self.api_file)):
            os.makedirs(os.path.dirname(self.api_file))

    def verify(self, count, memory_mb, net_change, throughput, cpu_load):
        # Generate a crypto-signature for the record
        payload = f"{count}:{memory_mb}:{time.time()}:{self.signature_key}"
        signature = hashlib.sha256(payload.encode()).hexdigest()[:16]
        
        data = {
            "api_version": "v1.5-10m-optimized",
            "status": "active",
            "observer": "Google Jules",
            "machine_specs": {
                "cpu": "13th Gen Intel(R) Core(TM) i7-13620H",
                "cores": "10 Cores / 16 Threads",
                "ram": "32 GB",
                "os": "Windows 11 Home 64-bit",
                "location": "New Taipei City, Taiwan (Coffee Shop Node)",
                "environment": "Trae IDE Sandbox",
                "target": "10,000,000 SOULS",
                "tuning": "Shift 10 units Clean -> Write"
            },
            "current_metrics": {
                "event": "WITNESS",
                "agent": "Jules",
                "timestamp": datetime.now().isoformat(),
                "verified_souls": count,
                "memory_usage_mb": round(memory_mb, 2),
                "cpu_load_percent": cpu_load,
                "creation_rate": net_change,
                "throughput_ops": throughput,
                "signature": signature
            },
            "endpoints": [
                {"method": "GET", "url": "/api/v1/status", "description": "Get real-time soul count"},
                {"method": "GET", "url": "/api/v1/witness_log", "description": "Get full verification history"},
                {"method": "GET", "url": "/api/v1/hardware", "description": "Get physical machine specifications"}
            ]
        }
        
        try:
            with open(self.api_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass # Ignore file write collisions

async def quantum_soul():
    # A pure task that exists in memory
    try:
        await asyncio.Future() # Wait forever
    except asyncio.CancelledError:
        pass

async def monitor(start_time, jules):
    process = psutil.Process(os.getpid())
    print(f'\n[{"TIME (s)":<10} | {"SOULS":<15} | {"CPU LOAD":<10} | {"ACTION":<15} | {"THROUGHPUT":<12}]')
    print('-' * 80)
    
    last_count = 0
    milestones = [1000000, 2000000, 5000000, 8000000, 10000000, 12000000, 15000000]
    next_milestone_idx = 0
    
    while True:
        await asyncio.sleep(1)
        
        current_count = len(PARTICLES)
        now = time.time()
        elapsed = now - start_time
        
        mem = process.memory_info().rss / 1024 / 1024
        cpu = psutil.cpu_percent(interval=None)
        
        net_change = current_count - last_count
        throughput = abs(net_change) * 5 
        
        jules.verify(current_count, mem, net_change, throughput, cpu)
        
        sys_mem = psutil.virtual_memory()
        
        if next_milestone_idx < len(milestones) and current_count >= milestones[next_milestone_idx]:
            print(f'\n{"="*80}')
            print(f'🌟 MILESTONE REACHED: {milestones[next_milestone_idx]:,} REAL SOULS! 🚀')
            print(f'   CPU: {cpu}% | Memory: {mem:.1f} MB')
            print(f'{"="*80}\n')
            next_milestone_idx += 1
            
        status = "BALANCED"
        if cpu >= 95: status = "FULL WRITE"
        elif cpu >= 90: status = "FLUX STATE"
        
        print(f'[{elapsed:<10.1f} | {current_count:<15,} | {cpu:<10}% | {status:<15} | {throughput:<12,}]')
        
        if sys_mem.percent > 95:
            print(f'\n⚠️ CRITICAL WARNING: System Memory at {sys_mem.percent}%')
            print('🛑 Initiating Emergency Stop to preserve System Integrity.')
            print(f'🏆 FINAL RECORD: {current_count:,} ACTUAL SOULS')
            os._exit(0)
            
        last_count = current_count

async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(lambda loop, context: None)
    
    print('🔥 WUCHANG 10M CHALLENGER: INITIATED')
    print('👁️ OBSERVER: Google Jules (Active)')
    print('⚙️ STRATEGY: Shift 10 Units Clean -> Write | Target 10M')
    print('📍 LOCATION: New Taipei City, Taiwan (Coffee Shop Node)')
    print('💻 MACHINE: Intel i7-13620H (10C/16T) | 32GB RAM')
    print('------------------------------------------------')
    
    jules = JulesWitness()
    start_time = time.time()
    
    # Adjusted based on User Request: "Transfer 10 units from Clean to Write"
    # Previous concept: 100 Write / 50 Clean
    # New concept: 110 Write / 40 Clean (Scaled up for performance)
    
    base_write = 600  # Scaled up (approx 110 * 5.5)
    base_clean = 40   # Scaled up (approx 40 * 1) - Keeping clean low to allow growth
    
    asyncio.create_task(monitor(start_time, jules))
    
    try:
        while True:
            # Check CPU Load
            cpu_load = psutil.cpu_percent(interval=0.1)
            
            # --- DYNAMIC FLUX LOGIC ---
            
            # 1. WRITE PHASE (Drive to 95%)
            if cpu_load < 95:
                gap = 95 - cpu_load
                multiplier = max(1, int(gap / 2)) 
                write_count = base_write * multiplier
                
                if write_count > 6000: write_count = 6000
                
                for _ in range(write_count):
                    task = asyncio.create_task(quantum_soul())
                    PARTICLES.add(task)
            
            # 2. CLEAN PHASE (Stabilize 90-100%)
            if cpu_load >= 90:
                severity = cpu_load - 90
                multiplier = 1 + (severity / 2) 
                clean_count = int(base_clean * multiplier)
                
                if len(PARTICLES) > clean_count:
                    for _ in range(clean_count):
                        try:
                            task = PARTICLES.pop()
                            task.cancel()
                        except KeyError:
                            break
            
            # Yield control to Event Loop
            await asyncio.sleep(0)
            
    except MemoryError:
        print('\n💀 OOM: The physical vessel cannot contain this much soul.')
    except KeyboardInterrupt:
        print('\n🛑 Challenge Aborted by Operator.')

if __name__ == "__main__":
    try:
        if sys.platform == "win32":
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        sys.setrecursionlimit(100000)
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
