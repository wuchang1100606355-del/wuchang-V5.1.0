import os
import time
import datetime
import json
import shutil
import subprocess
from device_controller import AndroidPOSController
from web_commander import WebCommander
try:
    from voice_commander import VoiceOrderListener
except ImportError:
    VoiceOrderListener = None

class StoreApprentice:
    def __init__(self):
        self.name = 'Store Apprentice (Little J Node)'
        # NIC 1: POS Control
        self.pos = AndroidPOSController(ip='192.168.50.88', port=39301)
        # NIC 2: Web Control
        self.web = WebCommander(headless=False) # Visible for screen control
        self.is_running = True
        self.nics = self._detect_nics()
        
        # Voice Control
        self.voice = None
        if VoiceOrderListener:
            self.voice = VoiceOrderListener(self._handle_voice_order)

        # Command Bridge Paths
        self.root_dir = 'remote_command_center'
        self.inbox_dir = os.path.join(self.root_dir, 'inbox')
        self.processed_dir = os.path.join(self.root_dir, 'processed')
        self.logs_dir = os.path.join(self.root_dir, 'logs')
        
        self._setup_environment()

    def _detect_nics(self):
        # Placeholder for NIC detection logic
        # In real scenario, use netifaces or subprocess('ipconfig')
        return "Dual NICs Detected (Simulated)"

    def _setup_environment(self):
        for d in [self.inbox_dir, self.processed_dir, self.logs_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = f'[{timestamp}] [Apprentice] {message}'
        print(msg)
        # Also write to daily log file
        log_file = os.path.join(self.logs_dir, f'daily_{datetime.datetime.now().strftime("%Y%m%d")}.log')
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(msg + '\n')
        except:
            pass

    def start_shift(self):
        self.log(f'{self.name} starting shift...')
        self.log(f'Active NICs: {self.nics}')

        # 1. Connect POS
        if self.pos.connect():
            self.log('POS Connected (LAN).')
        else:
            self.log('POS Connection Failed (Will retry).')

        # 2. Start Web Commander
        if self.web.start():
            self.log('Web Commander Online (WAN).')
            self.web.open_url('about:blank') # Start blank

        # 3. Start Voice Listener
        if self.voice:
            if self.voice.start():
                self.log('Voice Commander Listening (Bluetooth Headset).')
            else:
                self.log('Voice Commander Failed to Start.')

        # 4. Main Loop
        while self.is_running:
            try:
                self._check_cloud_commands()
                self._report_status()
                time.sleep(5) # Check every 5 seconds for responsiveness
            except KeyboardInterrupt:
                self.log('Shift ended by user.')
                self.is_running = False
                self.web.close()
                if self.voice: self.voice.stop()
            except Exception as e:
                self.log(f'Critical Loop Error: {e}')
                time.sleep(10)

    def _handle_voice_order(self, order):
        """Callback for when a voice order is recognized"""
        self.log(f"VOICE COMMAND RECEIVED: {order}")
        
        if order['type'] == 'order':
            product = order['product']
            qty = order['quantity']
            self.log(f"Processing Order: {qty} x {product}")
            
            # Action: Simulate clicking on Web POS
            # In real usage, this would find the element by text and click it
            # self.web.page.click(f"text={product}") 
            
            # Feedback
            self.log(f"Order for {product} added to queue.")
            
        elif order['type'] == 'command':
            action = order['action']
            if action == 'stop':
                self.log("Voice requested stop.")
                # self.is_running = False # Optional: let voice stop the system

    def _check_cloud_commands(self):
        # Scan inbox for JSON command files
        if not os.path.exists(self.inbox_dir): return

        files = [f for f in os.listdir(self.inbox_dir) if f.endswith('.json')]
        for filename in files:
            filepath = os.path.join(self.inbox_dir, filename)
            self.log(f'Received command: {filename}')

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cmd_data = json.load(f)

                # Execute
                result = self._execute_action(cmd_data)
                self.log(f'Execution Result: {result}')

                # Archive
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                shutil.move(filepath, os.path.join(self.processed_dir, f'{timestamp}_{filename}'))

            except Exception as e:
                self.log(f'Failed to process {filename}: {e}')
                # Move to logs as error
                shutil.move(filepath, os.path.join(self.logs_dir, f'ERROR_{filename}')) 

    def _execute_action(self, cmd):
        action = cmd.get('action')
        target = cmd.get('target')
        params = cmd.get('params', {})

        if action == 'run_process':
            # Control Foreground Execution
            cmd_line = params.get('command')
            if cmd_line:
                self.log(f'Launching Process: {cmd_line}')
                subprocess.Popen(cmd_line, shell=True)
                return 'Process Launched'

        elif action == 'set_view':
            # Control Screen Content (Customer vs Staff)
            view_type = params.get('type')
            if view_type == 'customer':
                self.web.open_url('https://wuchang.life') # Placeholder
                return 'Switched to Customer View'
            elif view_type == 'staff':
                self.web.open_url('https://google.com') # Placeholder for backend       
                return 'Switched to Staff View'
            elif view_type == 'url':
                url = params.get('url')
                self.web.open_url(url)
                return f'Navigated to {url}'

        elif action == 'pos_control':
            if target == 'wake':
                self.pos.wake_screen()
                return 'POS Screen Woken'
            elif target == 'battery':
                return self.pos.get_battery_status()

        elif action == 'system_control':
            if target == 'shutdown':
                self.is_running = False
                return 'Shutting down Apprentice...'

        return 'Unknown Command'

    def _report_status(self):
        # Write a heartbeat file for remote monitoring
        status_file = os.path.join(self.root_dir, 'status.md')
        voice_status = 'Listening' if (self.voice and self.voice.is_listening) else 'Inactive'
        content = f'''# Store Apprentice Status
**Last Update**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Node Name**: {self.name}
**Modules**:
- POS: {'Connected' if True else 'Disconnected'}
- Web: {'Online' if self.web.browser else 'Offline'}
- Voice: {voice_status}

## Remote Command Authority
**Current Mode**: Remote Ready
**Control Channels**:
1. **Screen View**: `set_view` (customer/staff)
2. **Process**: `run_process`
3. **POS**: `pos_control`
4. **Voice**: Bluetooth Headset Input Active

To issue a command, upload a JSON file to `inbox/`.
'''
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    apprentice = StoreApprentice()
    apprentice.start_shift()
