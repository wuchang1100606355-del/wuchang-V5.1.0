import subprocess
import hashlib
import platform
import os

class QuantumLock:
    def __init__(self):
        self.os_type = platform.system()

    def get_device_fingerprint(self):
        """Generates a unique hardware fingerprint for the device."""
        fingerprint_data = []
        
        try:
            if self.os_type == "Windows":
                # Get CPU Serial
                cpu = subprocess.check_output("wmic cpu get processorid", shell=True).decode().split('\n')[1].strip()
                fingerprint_data.append(f"CPU:{cpu}")
                
                # Get Disk Serial (C: drive)
                disk = subprocess.check_output("vol c:", shell=True).decode().split('\n')[-2].split()[-1].strip()
                fingerprint_data.append(f"DISK:{disk}")
                
                # Get MAC Address (first active)
                # Simplified for stability, using UUID if possible or machine GUID
                uuid = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().split('\n')[1].strip()
                fingerprint_data.append(f"UUID:{uuid}")
                
            elif self.os_type == "Linux":
                # Linux implementation (placeholder for now as environment is Windows)
                with open("/etc/machine-id", "r") as f:
                    fingerprint_data.append(f"MID:{f.read().strip()}")
                    
        except Exception as e:
            fingerprint_data.append(f"ERR:{str(e)}")

        # Create a SHA-256 hash of the gathered data
        raw_id = "|".join(fingerprint_data)
        hashed_id = hashlib.sha256(raw_id.encode()).hexdigest()
        return hashed_id

    def verify_license(self, license_key, secret_salt="WUCHANG_QUANTUM_SALT"):
        """Verifies if the license key matches the current device."""
        current_hwid = self.get_device_fingerprint()
        expected_key = hashlib.sha256((current_hwid + secret_salt).encode()).hexdigest()
        return license_key == expected_key

if __name__ == "__main__":
    lock = QuantumLock()
    hwid = lock.get_device_fingerprint()
    print(f"Device Fingerprint (HWID): {hwid}")
    print("Share this HWID with the administrator to generate a license.")
