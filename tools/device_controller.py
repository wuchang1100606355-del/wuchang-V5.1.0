import subprocess
import time
import sys
import os

class AndroidPOSController:
    def __init__(self, ip='192.168.50.88', port=39301, adb_path=None):
        self.ip = ip
        self.port = port
        self.device_id = f'{ip}:{port}'
        
        if adb_path:
            self.adb_path = adb_path
        else:
            # Auto-detect ADB
            base_dir = os.path.dirname(os.path.abspath(__file__)) # tools/
            root_dir = os.path.dirname(base_dir) # root
            
            # Candidates for ADB path
            candidates = [
                os.path.join(base_dir, 'platform-tools', 'adb.exe'),
                os.path.join(root_dir, 'platform-tools', 'adb.exe'),
                'adb' # fallback to PATH
            ]
            
            self.adb_path = 'adb'
            for path in candidates:
                if os.path.exists(path) and os.path.isfile(path):
                    self.adb_path = path
                    break
        
        print(f'Using ADB at: {self.adb_path}')

    def _run_adb(self, args):
        cmd = [self.adb_path, '-s', self.device_id] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return 'Error: Timeout'
        except Exception as e:
            return f'Error: {e}'

    def connect(self):
        print(f'Connecting to {self.device_id}...')
        # Try to connect
        try:
            output = subprocess.run([self.adb_path, 'connect', self.device_id], capture_output=True, text=True).stdout.strip()
            if 'connected' in output or 'already connected' in output:
                print(f'Successfully connected to {self.device_id}')
                return True
            else:
                print(f'Connection failed: {output}')
                return False
        except FileNotFoundError:
             print(f'ADB executable not found at {self.adb_path}')
             return False

    def wake_screen(self):
        print('Waking screen...')
        self._run_adb(['shell', 'input', 'keyevent', 'KEYCODE_WAKEUP'])

    def unlock_screen(self):
        print('Unlocking screen (swipe up)...')
        self._run_adb(['shell', 'input', 'swipe', '500', '2000', '500', '100'])

    def go_home(self):
        print('Going Home...')
        self._run_adb(['shell', 'input', 'keyevent', 'KEYCODE_HOME'])

    def launch_app(self, package_name):
        print(f'Launching {package_name}...')
        self._run_adb(['shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'])

    def input_text(self, text):
        print(f'Inputting text: {text}')
        safe_text = text.replace(' ', '%s')
        self._run_adb(['shell', 'input', 'text', safe_text])

    def get_battery_status(self):
        output = self._run_adb(['shell', 'dumpsys', 'battery'])
        level = 'Unknown'
        for line in output.split('\n'):
            if 'level' in line:
                level = line.split(':')[1].strip()
        return f'{level}%'

    def reboot(self):
        print('Rebooting device...')
        self._run_adb(['reboot'])

    def print_status(self):
        print(f'Device: {self.device_id}')
        print(f'Battery: {self.get_battery_status()}')
        focus = self._run_adb(['shell', 'dumpsys', 'window', 'windows', '|', 'grep', '-E', 'mCurrentFocus'])
        print(f'Current Focus: {focus}')

if __name__ == '__main__':
    pos = AndroidPOSController(ip='192.168.50.88', port=39301) 
    if pos.connect():
        pos.wake_screen()
        pos.print_status()
    else:
        print('Failed to connect. Please check IP and Port.')

