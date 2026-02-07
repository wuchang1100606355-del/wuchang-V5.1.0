import psutil
import os
print('Double J Health Check')
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
try: print(os.popen('nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader').read())
except: pass
try: print(os.popen('docker ps --format ''{{.Names}}''').read())
except: pass
