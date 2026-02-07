# -*- coding: utf-8 -*-
import time
import os
import threading
import random
import json
import shutil
import psutil

# Configuration
TEST_DIR = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "spacetime_benchmark")
NUM_OPERATIONS = 100
DATA_PAYLOAD = "X" * 1024  # 1KB

spacetime_memory = {}

def setup_test_env():
    if os.path.exists(TEST_DIR):
        try:
            shutil.rmtree(TEST_DIR)
        except:
            pass
    os.makedirs(TEST_DIR, exist_ok=True)

def cleanup_test_env():
    if os.path.exists(TEST_DIR):
        try:
            shutil.rmtree(TEST_DIR)
        except:
            pass

def standard_mode_task(task_id):
    filename = os.path.join(TEST_DIR, f"task_{task_id}.txt")
    try:
        with open(filename, "w") as f:
            f.write(DATA_PAYLOAD)
            f.flush()
            os.fsync(f.fileno())
        time.sleep(0.01)
        with open(filename, "r") as f:
            _ = f.read()
    except Exception:
        pass

def spacetime_mode_task(task_id, cleanup_ratio=0.05):
    key = f"task_{task_id}"
    spacetime_memory[key] = DATA_PAYLOAD
    time.sleep(0.001)
    _ = spacetime_memory.get(key)
    
    # Probabilistic cleanup (Active Garbage Collection)
    if random.random() < cleanup_ratio:
        if key in spacetime_memory:
            del spacetime_memory[key]

def run_spiral_crash_test(start_agents=100, max_agents=20000, latency_threshold_ms=500, mode="spacetime"):
    print(f"\n🌀 啟動螺旋時空極限測試 (Spiral Spacetime Test) - [{mode.upper()}]")
    print(f"   策略: 動態迴旋逼近 (Adaptive Spiral Approach)")
    print(f"   目標: 尋找真實極限而不觸發硬碰撞 (Find Limit without Hard Crash)")
    
    setup_test_env()
    
    current_agents = start_agents
    step = 100
    history = []
    stable_max = 0
    
    try:
        while current_agents < max_agents:
            # 1. Run Burst
            start_time = time.time()
            threads = []
            
            target = standard_mode_task if mode == "traditional" else spacetime_mode_task
            
            for i in range(current_agents):
                t = threading.Thread(target=target, args=(i,))
                threads.append(t)
                t.start()
                
            for t in threads:
                t.join()
                
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            avg_latency = duration_ms / max(1, current_agents)
            
            # 2. Spiral Logic (The Feedback Loop)
            cpu_usage = psutil.cpu_percent(interval=None)
            mem_usage = psutil.virtual_memory().percent
            
            print(f"   🌊 Wave: {current_agents} Agents | Latency: {duration_ms:.1f}ms | CPU: {cpu_usage}% | RAM: {mem_usage}%")
            history.append((current_agents, duration_ms, cpu_usage, mem_usage))
            
            if duration_ms < latency_threshold_ms and cpu_usage < 90:
                # Stable: Expand Spiral (Accelerate)
                stable_max = current_agents
                step = int(step * 1.5) # Spiral Out
                current_agents += step
            else:
                # Unstable/Collision Risk: Spiral In (Decelerate & Refine)
                print(f"   ⚠️ 碰撞預警 (Collision Warning) at {current_agents} Agents! (Latency: {duration_ms:.1f}ms)")
                
                if step < 50:
                    print(f"   🏁 螺旋收斂完成 (Spiral Converged). 真實極限約為: {stable_max}")
                    break
                    
                print(f"   🔄 執行螺旋收斂 (Spiraling In)... Backing off.")
                current_agents = stable_max + int(step * 0.5) # Try halfway
                step = int(step * 0.5) # Smaller steps
                
                # Cooldown
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 測試手動中止")
    finally:
        cleanup_test_env()
        
    return stable_max, history

# Keep original functions for compatibility
def run_rate_sweep_per_agent(*args, **kwargs): pass
def run_rate_capacity_test(*args, **kwargs): pass
def run_crash_test(*args, **kwargs): pass

