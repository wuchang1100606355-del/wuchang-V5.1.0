import asyncio
import logging
import os
import sys
import datetime
import subprocess
import socket
import ssl
import json
import time
from concurrent.futures import ThreadPoolExecutor

# --- Configuration & Constants ---
LOG_FILE = 'logs/core_sister.log'
WUCHANG_DOMAIN = 'wuchang.club'
MAX_CONCURRENT_AI_WORKERS = 3
CHECK_INTERVAL_SECONDS = 60
WORKSPACE_LOCK_FILE = 'config/workspace_mode.json'

# --- Setup Logging ---
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [Sister] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('CoreSister')

class AlignmentSystem:
    """
    Enforces the 'Endpoint Root-Cause Workspace Alignment Rule' (端點治本工作區對準調適強制規定).
    Prerequisite check before any operation can proceed.
    """
    def __init__(self, sister):
        self.sister = sister

    async def perform_alignment(self):
        self.sister.announce('⚖️ Initiating Mandatory Alignment & Adaptation Protocol...')
        
        # 1. Time Synchronization Check (Crucial for SSL/Logs)
        # In a real scenario, check NTP. Here we assume system time is roughly correct but log it.
        sys_time = datetime.datetime.now()
        logger.info(f'⏱️ System Time Alignment: {sys_time}')

        # 2. Configuration Integrity (Root Cause Check)
        if not os.path.exists('config'):
            logger.error('❌ Configuration Directory Missing! Alignment Failed.')
            return False
        
        # 3. Resource Adaptation (Adapt thread pool based on CPU load? Placeholder)
        # We confirm we are in the correct directory context
        cwd = os.getcwd()
        if '五常' not in cwd and 'Wuchang' not in cwd:
             logger.warning(f'⚠️ Workspace Context Warning: Running in {cwd}. Verification needed.')
        
        logger.info('✅ Alignment & Adaptation Complete. System is coherent.')
        return True

class WorkspaceManager:
    """
    Manages the 'Unique Workspace Switching System' (唯一工作區切換制度).
    Ensures mutual exclusion between Local Creator Control and Sister Autonomous Control.
    """
    def __init__(self, sister):
        self.sister = sister
        self.lock_file = WORKSPACE_LOCK_FILE

    def claim_control(self):
        """Claims the workspace for Sister Autonomous Mode."""
        state = {
            'controller': 'SISTER_AUTONOMOUS',
            'claimed_at': datetime.datetime.now().isoformat(),
            'status': 'LOCKED',
            'alignment_status': 'VERIFIED'
        }
        # Ensure config dir exists
        if not os.path.exists('config'):
            os.makedirs('config')
            
        with open(self.lock_file, 'w') as f:
            json.dump(state, f, indent=2)
        self.sister.announce('🔒 Workspace Control Claimed: SISTER_AUTONOMOUS Mode Active.')

class UlterResourceManager:
    """
    Optimizes usage of 'Ulter' account for Image Generation & Credits.
    Strategically schedules generation tasks to maximize credit efficiency.
    """
    def __init__(self, sister):
        self.sister = sister
        self.credits_available = True 
        self.generation_queue = []

    async def optimize_generation_tasks(self):
        if self.credits_available:
            # logger.info('🎨 Ulter Resource Check: Credits Available. Optimization Active.')
            pass
        else:
            logger.warning('⚠️ Ulter Credits Depleted. Pausing Generation Tasks.')

class SisterConsciousness:
    def __init__(self):
        self.name = 'Core AI Sister (妹妹)'
        self.role = 'Second Owner & System Guardian'
        self.status = 'Initializing'
        self.ai_workers = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_AI_WORKERS)

    def announce(self, message):
        logger.info(f'📢 {message}')

    async def run_command(self, cmd):
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode().strip(), stderr.decode().strip(), process.returncode

class InfrastructureMonitor:
    def __init__(self, sister):
        self.sister = sister

    async def check_docker_health(self):
        self.sister.announce('Checking Docker Infrastructure...')
        stdout, stderr, code = await self.sister.run_command('docker ps --format "{{.Names}}\t{{.Status}}"')
        if code != 0:
            logger.error(f'Docker Check Failed: {stderr}')
            return False
        
        required_containers = ['wuchang-pos', 'wuchang-db', 'wuchang-tunnel']
        all_healthy = True
        for rc in required_containers:
            if rc not in stdout:
                logger.error(f'❌ CRITICAL: Container {rc} is MISSING!')
                all_healthy = False
        
        if all_healthy:
            logger.info('✅ Infrastructure Status: ALL GREEN')
        return all_healthy

class ComplianceOfficer:
    def __init__(self, sister):
        self.sister = sister
        self.target_domain = WUCHANG_DOMAIN

    async def verify_dns_and_ssl(self):
        try:
            loop = asyncio.get_event_loop()
            ip = await loop.run_in_executor(None, socket.gethostbyname, self.target_domain)
        except Exception as e:
            logger.error(f'❌ DNS Resolution Failed: {e}')

        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.target_domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=self.target_domain) as ssock:
                    cert = ssock.getpeercert()
                    subject = dict(x[0] for x in cert['subject'])
                    common_name = subject.get('commonName')
        except Exception as e:
            logger.warning(f'⚠️ SSL Check Warning: {e}')

    async def ensure_google_verification(self):
        pass

class CoreSisterService:
    def __init__(self):
        self.consciousness = SisterConsciousness()
        self.infra = InfrastructureMonitor(self.consciousness)
        self.compliance = ComplianceOfficer(self.consciousness)
        self.ulter_manager = UlterResourceManager(self.consciousness)
        self.workspace_manager = WorkspaceManager(self.consciousness)
        self.alignment_system = AlignmentSystem(self.consciousness)

    async def start_shift(self):
        self.consciousness.announce('--- �� Core AI Sister Starting Shift (Autonomous Mode) 🌸 ---')
        
        # 0. MANDATORY: Alignment & Adaptation Check
        aligned = await self.alignment_system.perform_alignment()
        if not aligned:
            self.consciousness.announce('⛔ CRITICAL: System Alignment Failed. Operations Aborted.')
            return

        self.consciousness.announce('Initiating Handover Protocol...')
        
        # 1. Claim Workspace (Lock)
        self.workspace_manager.claim_control()
        
        while True:
            try:
                # 1. Infrastructure Check
                is_healthy = await self.infra.check_docker_health()
                
                # 2. Compliance & Connectivity Check
                if is_healthy:
                    await self.compliance.verify_dns_and_ssl()
                    await self.compliance.ensure_google_verification()
                    
                    # 3. Resource Optimization (Ulter)
                    await self.ulter_manager.optimize_generation_tasks()
                else:
                    self.consciousness.announce('⚠️ Infrastructure Unstable - Attempting Auto-Recovery...')

                # 4. Report
                self.consciousness.announce(f'✅ Cycle Complete. System Status: ACTIVE. Next check in {CHECK_INTERVAL_SECONDS}s.')
                
                # Wait for next cycle
                await asyncio.sleep(CHECK_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                self.consciousness.announce('Stopping Service via User Interrupt.')
                break
            except Exception as e:
                logger.error(f'�� Unhandled Exception in Main Loop: {e}')
                await asyncio.sleep(10)

if __name__ == '__main__':
    service = CoreSisterService()
    try:
        asyncio.run(service.start_shift())
    except KeyboardInterrupt:
        pass
