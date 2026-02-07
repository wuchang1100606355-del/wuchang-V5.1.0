import os
import time
import getpass
import hashlib
import math
from datetime import datetime

def calculate_mars_distance():
    # Simplified orbital mechanics for "current" distance approximation
    # In reality, this requires complex ephemeris data.
    # We simulate a "Live Telemetry" feeling.
    
    # Average distance: 225 million km
    # Min distance: 54.6 million km
    # Max distance: 401 million km
    
    # Simple sine wave simulation based on time for demo purposes
    timestamp = time.time()
    # Period of synodic orbit approx 780 days
    period = 780 * 24 * 3600 
    phase = (timestamp % period) / period * 2 * math.pi
    
    # Distance in million km (approx)
    distance = 227.9 + 170 * math.sin(phase)
    
    # Light travel time (speed of light ~300,000 km/s)
    light_seconds = (distance * 1_000_000) / 300_000
    light_minutes = light_seconds / 60
    
    return distance, light_minutes

def main():
    print("==================================================")
    print("   [CHRONOS SYSTEM] SECURE TERMINAL ACCESS")
    print("==================================================")
    print("Please scan your Membership Card (or type the key):")

    user_input_key = getpass.getpass("Key Input > ")

    if user_input_key == "X-A12-ELON-MUSK-IS-WATCHING":
        dist_km, light_mins = calculate_mars_distance()
        
        print("\n[ACCESS GRANTED]")
        print("Decrypting Temporal Payload...")
        time.sleep(1.0)
        print("--------------------------------------------------")
        print("TARGET LOCKED: MARS - Cydonia Mensae")
        print(f"CURRENT DISTANCE: {dist_km:.2f} Million km")
        print(f"LIGHT LAG: {light_mins:.2f} Minutes")
        print("TIME OFFSET: +12 Hours")
        print("STATUS: ACTIVE")
        print("--------------------------------------------------")
        print("System will now self-destruct this session log in 5 seconds.")
        time.sleep(5)
        print("[SESSION CLEARED]")
    else:
        print("\n[ACCESS DENIED]")
        print("Alert: Intrusion detected. Deploying defensive countermeasures.")

if __name__ == "__main__":
    main()
