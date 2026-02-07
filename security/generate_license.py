import hashlib
import sys
import os

def generate_license(target_hwid, secret_salt="WUCHANG_QUANTUM_SALT"):
    """Generates a license key for a specific hardware ID."""
    license_key = hashlib.sha256((target_hwid + secret_salt).encode()).hexdigest()
    return license_key

def main():
    print("=== Quantum Spacetime License Generator ===")
    
    target_hwid = ""
    if len(sys.argv) >= 2:
        target_hwid = sys.argv[1]
    else:
        print("\nPlease enter the Device Fingerprint (HWID) from the target computer.")
        target_hwid = input("HWID: ").strip()
    
    if not target_hwid:
        print("Error: No HWID provided.")
        input("Press Enter to exit...")
        return

    key = generate_license(target_hwid)
    print(f"\n[SUCCESS] License Key Generated!")
    print(f"Key: {key}")
    
    # Save to file
    with open("quantum_license.key", "w") as f:
        f.write(key)
    
    print("\n'quantum_license.key' has been saved in this folder.")
    print("Please copy this file to the target computer alongside the installer.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
