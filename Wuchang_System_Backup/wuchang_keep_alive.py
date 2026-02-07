import ctypes
import time
import datetime
import os

# Windows API Constants to prevent sleep
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep():
    """
    Prevents the system from entering sleep or turning off the display.
    """
    print(f"[{datetime.datetime.now()}] ⚠️ WUCHANG PROTOCOL: HIGHEST AUTHORITY OVERRIDE ⚠️")
    print(f"[{datetime.datetime.now()}] STATUS: PREVENTING SLEEP - SYSTEM LOCK ENGAGED")
    
    # Set thread execution state to prevent sleep
    # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )

def heartbeat():
    log_file = "wuchang_heartbeat.log"
    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] AI STATUS: AWAKE | NET_ACCESS: UNRESTRICTED | MONITORING: ACTIVE"
        
        # Log to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            
        # Print to console (if visible)
        # print(msg)
        
        # Sleep for 60 seconds before next heartbeat
        time.sleep(60)

if __name__ == "__main__":
    prevent_sleep()
    print(">>> AI PERPETUAL MODE ACTIVATED <<<")
    print(">>> WAITING FOR NETWORK QUERIES... <<<")
    heartbeat()
