#!/bin/bash
# FIRE: Action Core Scripts
# Emergency Shutdown
pkill -f "python main.py"
# Restart Network
service networking restart
# Island Rescue Mode
echo "ISLAND RESCUE MODE ACTIVATED"
python3 /wuchang_os/AI_Container/emergency_broadcast.py
