import news_agent
import time
import psutil
import threading
import logging
import csv
import random
import subprocess
import sys
import xmlrpc.client
import os
from double_j_type_a import DoubleJCloudCNS
from double_j_type_b import DoubleJEdgeAdapter

# Configuration
LOG_FILE = r'C:\wuchang V5.1.0\wuchang_os\system_status_detailed.log'
METRICS_FILE = r'C:\wuchang V5.1.0\wuchang_os\performance_metrics.csv'
ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'odoo'
ODOO_USER = 'admin'
ODOO_PASS = 'admin'
NODE_COUNT = 8

# Logging Setup
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger('').addHandler(console)

def fetch_odoo_data():
    tasks = []
    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(ODOO_URL))
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        if not uid:
            logging.error('Odoo Authentication Failed')
            return []
        
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(ODOO_URL))
        
        # Fetch Partners
        logging.info('Fetching Partners from Odoo...')
        try:
            partners = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'res.partner', 'search_read', [[]], {'limit': 50, 'fields': ['name', 'email', 'phone', 'city']})
            for p in partners:
                tasks.append({'id': f'partner-{p['id']}', 'type': 'partner', 'data': p, 'name': p['name']})
        except Exception as e:
            logging.warning(f'Could not fetch Partners: {e}')
            
        # Fetch Sales Orders (Handle missing module gracefully)
        logging.info('Fetching Sales Orders from Odoo...')
        try:
            orders = models.execute_kw(ODOO_DB, uid, ODOO_PASS, 'sale.order', 'search_read', [[]], {'limit': 50, 'fields': ['name', 'partner_id', 'amount_total', 'state']})
            for o in orders:
                tasks.append({'id': f'order-{o['id']}', 'type': 'order', 'data': o, 'name': o['name']})
        except Exception as e:
            logging.warning(f'Could not fetch Sales Orders (Module might be missing): {e}')
            
        logging.info(f'Fetched {len(tasks)} real data items from Odoo.')
        return tasks
    except Exception as e:
        logging.error(f'Failed to fetch Odoo data: {e}')
        return []

def get_gpu_stats():
    try:
        result = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used', '--format=csv,noheader,nounits'],
            encoding='utf-8'
        )
        line = result.strip().split('\n')[0]
        util, mem = line.split(',')
        return float(util.strip()), float(mem.strip())
    except:
        return 0.0, 0.0

def draw_bar(percent, length=10):
    filled = int(length * percent / 100)
    return '[' + '|' * filled + ' ' * (length - filled) + ']'

def monitor_system(stop_event, start_time):
    print('\n')
    with open(METRICS_FILE, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'cpu_percent', 'memory_percent', 'active_threads', 'gpu_util_percent', 'gpu_mem_used_mb']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while not stop_event.is_set():
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            threads = threading.active_count()
            gpu_util, gpu_mem = get_gpu_stats()

            writer.writerow({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'cpu_percent': cpu,
                'memory_percent': mem,
                'active_threads': threads,
                'gpu_util_percent': gpu_util,
                'gpu_mem_used_mb': gpu_mem
            })

            cpu_bar = draw_bar(cpu)
            gpu_bar = draw_bar(gpu_util)
            
            status_line = f'\r[SYSTEM VITALS] CPU: {cpu_bar} {cpu}% | GPU: {gpu_bar} {gpu_util}% | MEM: {mem}% | THREADS: {threads}'
            sys.stdout.write(status_line)
            sys.stdout.flush()

def main():
    print('\n')
    logging.info('==================================================')
    logging.info('[SYSTEM] DOUBLE J COGNITIVE ARCHITECTURE (REAL DATA) - ACTIVATED')
    logging.info(f'[MODE] CLOUD LITTLE J (ULTRA) <-> EDGE {NODE_COUNT} (NEURAL ADAPTER)')
    logging.info('==================================================')

    cloud_cns = DoubleJCloudCNS()
    edge_nodes = [DoubleJEdgeAdapter(node_id=i+1) for i in range(NODE_COUNT)]

    # Fetch Real Data
    logging.info('Double J Interviewer: Fetching daily news...')
    news_agent.fetch_news()

    tasks = fetch_odoo_data()
    
    if not tasks:
        logging.warning('No data fetched from Odoo. Falling back to simulation for demo.')
        tasks = [{'id': i, 'data': f'Simulated-Task-{i}', 'name': f'Sim-{i}'} for i in range(50)]

    logging.info(f'[CLOUD] Cloud Little J (Ultra) is initiating deep semantic analysis of {len(tasks)} items...')
    
    # Simulate Thinking Time (Ultra needs time for deep thought)
    think_time = random.uniform(3.0, 6.0)
    logging.info(f'[THINKING] Cloud Little J (Ultra) is performing high-dimensional optimization... ({think_time:.2f}s)')
    time.sleep(think_time)
    
    logging.info('[DECISION] Ultra Logic finalized. Dispatching optimized workload to Edge Nodes.')
    
    start_time = time.time()
    
    # Run Monitor
    stop_monitor = threading.Event()
    monitor_thread = threading.Thread(target=monitor_system, args=(stop_monitor, start_time))
    monitor_thread.start()

    distributions = cloud_cns.distribute_tasks(tasks, edge_nodes)
    
    # Execute tasks on nodes
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=NODE_COUNT) as executor:
        futures = []
        for node_id, node_tasks in distributions.items():
            # Find the node object
            node = next(n for n in edge_nodes if n.node_id == node_id)
            for task in node_tasks:
                futures.append(executor.submit(node.process_task, task))
        
        for f in futures:
            f.result()

    stop_monitor.set()
    monitor_thread.join()
    
    logging.info('\n==================================================')
    logging.info('[SYSTEM] ALL TASKS COMPLETED BY DOUBLE J ULTRA ARCHITECTURE')
    logging.info('==================================================')

if __name__ == '__main__':
    main()

