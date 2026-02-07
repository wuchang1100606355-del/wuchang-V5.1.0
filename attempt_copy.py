import shutil
import os
import sys

source = r"C:\wuchang V5.1.0\USB_DRIVE_NEW"
dest = r"D:\\"

print(f"Attempting to copy from {source} to {dest}...")

try:
    if not os.path.exists(dest):
        print(f"Error: Destination {dest} does not exist.")
        sys.exit(1)
        
    # Copy files manually to handle existing root
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d) # Clean old version
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
            
    print("SUCCESS: Files copied to D:\\")
except Exception as e:
    print(f"FAILURE: {str(e)}")

