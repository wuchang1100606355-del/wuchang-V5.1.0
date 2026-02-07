import time
import json
import os
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

def load_config():
    with open('INTELLIGENCE_CORE/double_j_config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def run_simulation():
    config = load_config()
    settings = config.get('concurrency_settings', {})
    target = settings.get('default_agents', 50)
    interval = settings.get('ramp_up_interval_seconds', 5)
    
    print(f'🛡️ 啟動安全運作模式 (Safe Mode Simulation)')
    print(f'   -> 目標併發數: {target}')
    print(f'   -> 啟動間隔: {interval} 秒')
    print('----------------------------------------')
    
    active_agents = 0
    try:
        while active_agents < target:
            time.sleep(interval) # Simulate wait first or after? Usually wait then start.
            active_agents += 1
            print(f'✅ [System] Agent #{active_agents} Started. (Total Active: {active_agents}/{target})')
            
            # For demo purposes, stop after 3 to save time
            if active_agents >= 3:
                print('   -> (模擬模式: 僅展示前 3 個啟動程序以節省時間)')
                break
                
    except KeyboardInterrupt:
        print('\n�� Simulation stopped.')

if __name__ == '__main__':
    run_simulation()
