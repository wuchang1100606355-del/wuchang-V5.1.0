import os
import subprocess
import time
import sys
import glob
import random
import urllib.request
import csv
import base64
import io

# Configuration
OPENVPN_PATH = r"C:\Program Files\OpenVPN Connect\ovpnconnector.exe"
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configs")
VPNGATE_API_URL = "http://www.vpngate.net/api/iphone/"


def log(message):
    print(f"[小j]: {message}")


def fetch_vpngate_configs():
    log(f"Attempting to fetch fresh keys from {VPNGATE_API_URL}...")
    try:
        response = urllib.request.urlopen(VPNGATE_API_URL, timeout=15)
        data = response.read().decode('utf-8')

        # The API returns a CSV with a header.
        # We need to skip the first line (comments) and find the header
        lines = data.splitlines()
        csv_lines = [line for line in lines if not line.startswith(
            '*') and not line.startswith('#')]

        # Sometimes the file starts with comments, real header starts with #HostName, but we filtered #
        # Let's try to parse manually looking for the header line index if the simple filter fails
        # Actually, VPNGate CSV usually has a header line starting with #HostName.

        # Let's re-read properly
        header_line_index = -1
        for i, line in enumerate(lines):
            if line.startswith("#HostName"):
                header_line_index = i
                break

        if header_line_index == -1:
            log("Error: Could not find CSV header in response.")
            return False

        # Get header and clean it (remove #)
        header = lines[header_line_index].lstrip('#').split(',')

        count = 0
        # Parse the rest
        for line in lines[header_line_index+1:]:
            if not line or line.startswith('*'):
                continue

            parts = line.split(',')
            if len(parts) != len(header):
                continue

            row = dict(zip(header, parts))

            if 'OpenVPN_ConfigData_Base64' in row:
                b64_data = row['OpenVPN_ConfigData_Base64']
                try:
                    config_content = base64.b64decode(b64_data).decode('utf-8')

                    # Create a filename
                    country = row.get('CountryShort', 'Unknown')
                    ip = row.get('IP', '0.0.0.0')
                    filename = f"vpngate_{country}_{ip}.ovpn"
                    filepath = os.path.join(CONFIG_DIR, filename)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(config_content)

                    count += 1
                except Exception as e:
                    continue

        log(f"Successfully fetched and saved {count} new configuration files.")
        return count > 0

    except Exception as e:
        log(f"Failed to fetch from VPN Gate: {e}")
        return False


def find_configs():
    return glob.glob(os.path.join(CONFIG_DIR, "*.ovpn"))


def connect(config_path):
    if not os.path.exists(OPENVPN_PATH):
        log(f"Error: Could not find OpenVPN Connector at {OPENVPN_PATH}")
        return False

    log(f"Preparing to connect with: {os.path.basename(config_path)}")

    # 1. Stop any existing connection first to be safe
    log("Ensuring previous connections are closed...")
    subprocess.run([OPENVPN_PATH, "stop"], capture_output=True)
    time.sleep(2)

    # 2. Set Config
    log("Setting configuration...")
    # The profile path must be absolute
    abs_config_path = os.path.abspath(config_path)

    cmd_set = [OPENVPN_PATH, "set-config", "profile", abs_config_path]
    result = subprocess.run(cmd_set, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Failed to set config: {result.stderr}")
        return False

    # 3. Start Connection
    log("Initiating connection... (This might take a moment)")
    cmd_start = [OPENVPN_PATH, "start"]

    try:
        # We run it and wait a bit
        result = subprocess.run(
            cmd_start, capture_output=True, text=True, timeout=15)
        # OpenVPN Connect CLI often returns immediately or waits.
        # If it returns 0, it usually means the command was accepted.
        if result.returncode == 0:
            log("✨ Connection command sent. Waiting for tunnel to establish...")

            # Verify connection by checking IP change
            original_ip = get_public_ip()

            # Wait loop for IP change (max 30 seconds)
            for i in range(6):
                time.sleep(5)
                current_ip = get_public_ip()
                if current_ip and current_ip != original_ip:
                    log(f"🎉 Success! IP changed from {original_ip} to {current_ip}")
                    return True
                log(f"Waiting for IP change... (Current: {current_ip})")

            log("⚠️  Connection timed out or IP didn't change.")
            return False
        else:
            log(
                f"Warning: Command finished with code {result.returncode}. Output: {result.stdout} {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        log("Command timed out (this might be normal if it keeps running).")
    except Exception as e:
        log(f"Error starting VPN: {e}")
        return False

    log("Please check your IP to confirm the switch!")
    return True


def get_public_ip():
    try:
        return urllib.request.urlopen('https://api.ipify.org', timeout=3).read().decode('utf8')
    except Exception:
        return None


def main():
    log("Starting automatic IP pairing sequence...")

    # Get initial IP
    initial_ip = get_public_ip()
    log(f"Current Public IP: {initial_ip}")

    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    configs = find_configs()

    if not configs:
        log("No local configs found. Initiating global search protocol...")
        if fetch_vpngate_configs():
            configs = find_configs()
        else:
            log("⚠️  Could not fetch configs automatically.")
            log("Please check your internet connection or try adding .ovpn files manually.")
            return

    log(f"Found {len(configs)} configuration(s).")

    # Analyze available countries
    countries = {}
    for c in configs:
        # Filename format: vpngate_COUNTRY_IP.ovpn
        fname = os.path.basename(c)
        parts = fname.split('_')
        if len(parts) >= 2:
            code = parts[1]
            if code not in countries:
                countries[code] = []
            countries[code].append(c)

    log("Available regions: " +
        ", ".join([f"{k}({len(v)})" for k, v in countries.items()]))

    # Argument handling for country selection
    target_country = None
    if len(sys.argv) > 1:
        # Check if first arg is a country code
        arg = sys.argv[1].upper()
        if arg in countries:
            target_country = arg
        else:
            # If not a country code, maybe it's a "retry" or something, but we ignore for now
            pass

    if target_country:
        log(f"Targeting region: {target_country}")
        candidates = countries[target_country]
    else:
        # Default behavior: Random, but maybe prefer US/JP/KR
        # If we have US, let's prefer it for "Foreign" requests unless specified otherwise?
        # No, random is safer to distribute load, but for "payment" US is often king.
        # Let's just pick random for now unless user asked.
        candidates = configs

    selected_config = random.choice(candidates)
    connect(selected_config)


if __name__ == "__main__":
    main()
