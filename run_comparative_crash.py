# -*- coding: utf-8 -*-
import sys
import os
import json
import time

# Add tools library to path
sys.path.append(os.path.join(os.getcwd(), 'wuchang_tools_library'))

try:
    from measure_spacetime_effect import run_crash_test
except ImportError:
    # Fallback if file structure is different
    sys.path.append('J:\\共用雲端硬碟\\五常雲端空間\\wuchang_tools_library')
    from measure_spacetime_effect import run_crash_test

print('================================================================')
print('       啟動雙模式極限崩潰測試 (Comparative Crash Test)       ')
print('       模式: 高等模組算力全開 (High-Level Module Enabled)    ')
print('================================================================')

# Load Config to verify
try:
    with open('INTELLIGENCE_CORE/double_j_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        hl_enabled = config.get('high_level_module', False)
        print(f'[*] 設定檔確認: high_level_module = {hl_enabled}')
        if not hl_enabled:
            print('[!] 警告: 高等模組未開啟，測試結果可能不準確！')
except Exception as e:
    print(f'[!] 設定檔讀取失敗: {e}')

print('\n')
print('>>> 階段一: 傳統模式崩潰測試 (Traditional Mode) <<<')
print('    起始架次: 50 | 步進: 50 | 清除機制: 無')
try:
    run_crash_test(max_agents=2000, start_agents=50, step=50, threshold_ms=2000, mode='traditional')
except Exception as e:
    print(f'傳統模式測試中斷: {e}')

print('\n')
print('>>> 階段二: 時空模式崩潰測試 (Spacetime Mode) <<<')
print('    起始架次: 100 | 步進: 100 | 清除機制: 動態加大 (Based on Step)')
# User asked for increase cleanup based on increase amount
# We set cleanup_per_add to 50
try:
    run_crash_test(max_agents=10000, start_agents=100, step=100, threshold_ms=2000, mode='spacetime', cleanup_ratio=0.5, cleanup_per_add=50)
except Exception as e:
    print(f'時空模式測試中斷: {e}')

print('\n')
print('================================================================')
print('                 測試完成 (Test Completed)                  ')
print('================================================================')
