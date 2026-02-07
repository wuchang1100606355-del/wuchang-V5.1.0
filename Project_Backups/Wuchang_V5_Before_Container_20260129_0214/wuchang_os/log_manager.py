import os
import datetime
import time
import psutil
import sys
import gc

# Log file path - using wuchang_os directory
LOG_FILE = os.path.join(os.path.dirname(__file__), "TIME_SPACE_TRANSMISSION_LOG.md")

def get_system_metrics():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        return {
            "cpu": f"{cpu}%",
            "ram_used": f"{mem.used / (1024**3):.2f}GB",
            "ram_total": f"{mem.total / (1024**3):.2f}GB",
            "ram_percent": f"{mem.percent}%"
        }
    except Exception as e:
        return {"error": str(e)}

def init_log():
    if not os.path.exists(LOG_FILE):
        headers = "| Timestamp | User Intent | Action Taken | Response Time | CPU | RAM | Status |\n"
        headers += "|---|---|---|---|---|---|---|\n"
        try:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("# Time-Space System Transmission Log\n\n")
                f.write(headers)
            print(f"Log initialized at {LOG_FILE}")
        except PermissionError:
            print(f"Permission denied writing to {LOG_FILE}.")

def log_entry(intent, action, start_time):
    end_time = time.time()
    duration = f"{end_time - start_time:.4f}s"
    metrics = get_system_metrics()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Fix: Use raw string for backslash or double escape
    intent = intent.replace("|", r"\|")
    action = action.replace("|", r"\|")
    row = f"| {timestamp} | {intent} | {action} | {duration} | {metrics.get('cpu')} | {metrics.get('ram_percent')} | Active |\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(row)
        print(f"Logged: {intent} -> {duration}")
    except Exception as e:
        print(f"Failed to log: {e}")

def clean_resources():
    print("--- Resource Cleanup & Inspection ---")
    initial_mem = psutil.virtual_memory().percent
    print(f"Initial Memory Usage: {initial_mem}%")
    gc.collect()
    print("Python GC executed.")
    print("Top Memory Consumers:")
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            procs.append(p.info)
        except:
            pass
    procs.sort(key=lambda x: x['memory_percent'], reverse=True)
    for p in procs[:5]:
        print(f"  - {p['name']} (PID: {p['pid']}): {p['memory_percent']:.2f}%")
    print("--- End Inspection ---")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "init": init_log()
        elif sys.argv[1] == "log": log_entry(sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv)>4 else time.time())
        elif sys.argv[1] == "clean": clean_resources()
