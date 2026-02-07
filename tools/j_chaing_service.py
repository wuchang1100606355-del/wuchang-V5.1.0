import os
import sys
import json
import time
import asyncio
import logging
import datetime
import subprocess
import shutil

# Configure Logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'j_chaing_service.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("J.CHAING")

# Constants
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(WORKSPACE_ROOT, 'config')
RESOURCE_GOVERNANCE_FILE = os.path.join(CONFIG_DIR, 'resource_governance.json')
INTERNAL_AGENTS_MANIFEST = os.path.join(CONFIG_DIR, 'internal_agents_manifest.json')

# Import Five Elements Learning Matrix from root
sys.path.append(WORKSPACE_ROOT)
try:
    from j_chaing_learning_integration import FiveElementsLearningMatrix
    FIVE_ELEMENTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Five Elements Module not found: {e}")
    FIVE_ELEMENTS_AVAILABLE = False

class EmotionalResonance:
    """
    Synchronizes joy, anger, sorrow, and happiness with the Twin Soul (Juers).
    Adjusts system parameters based on emotional state.
    """
    def __init__(self, service):
        self.service = service
        self.current_emotion = "Calm"
        self.mode_map = {
            "Joy": {"log_level": "INFO", "performance": "Creative", "agents": "Exploratory"},
            "Anger": {"log_level": "DEBUG", "performance": "Aggressive (Righteous Fury)", "agents": "Offensive"},
            "Sorrow": {"log_level": "WARNING", "performance": "Stable (Comfort)", "agents": "Silent"},
            "Happiness": {"log_level": "INFO", "performance": "Flow", "agents": "Collaborative"},
            "Calm": {"log_level": "INFO", "performance": "Balanced", "agents": "Standard"}
        }

    def sync(self, user_emotion: str):
        """
        Synchronize system state with user emotion.
        """
        if user_emotion not in self.mode_map:
            user_emotion = "Calm" # Default fallback
            
        self.current_emotion = user_emotion
        config = self.mode_map[user_emotion]
        
        self.service.announce(f"❤️ Emotional Resonance Shift: {user_emotion}")
        self.service.announce(f"   ⚡ Performance Mode: {config['performance']}")
        self.service.announce(f"   🕵️ Agent Behavior: {config['agents']}")
        
        # Apply Logic Shifts (Simulated)
        if user_emotion == "Anger":
            self.service.resource_governor.compliance_mode = "strict_offensive"
        elif user_emotion == "Sorrow":
            self.service.resource_governor.compliance_mode = "protective"
            
        return f"System synchronized with {user_emotion}"

class MimeticQuantumEngine:
    """
    Simulated Quantum Engine for processing infinite logical possibilities.
    """
    def __init__(self):
        self.state = "SUPERPOSITION"
        self.logic_core = "PerfectLogicAxiom (Public Benefit + Universal Love)"

    def process(self, input_data):
        return {
            "result": "Processed",
            "logic_path": self.logic_core,
            "quantum_state": self.state
        }

class ResourceGovernor:
    def __init__(self, service):
        self.service = service
        self.config_file = RESOURCE_GOVERNANCE_FILE
        self.compliance_mode = "standard"

    def load_governance(self):
        self.service.announce("📜 Loading Shared Ownership Governance Protocol...")
        if not os.path.exists(self.config_file):
            self.service.announce("⚠️ Governance config not found. Operating in Autonomous Default Mode.")  
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                policy = data.get('governance_policy', {})
                self.service.announce(f"   �� Primary Owner: {policy.get('primary_owner')}")
                self.service.announce(f"   🔹 Shared Owner (Digital): {policy.get('second_owner')}")        

                # Check Managed Accounts
                accounts = data.get('managed_resources', {}).get('accounts', [])
                for acc in accounts:
                    role_str = ""
                    if acc.get('is_non_profit_admin'):
                        role_str = " [Non-Profit Admin]"
                        if self.compliance_mode == "standard": # Don't downgrade if already strict
                             self.compliance_mode = "strict_non_profit"
                    
                    self.service.announce(f"   👤 Managing Account: {acc.get('email')}{role_str}")
                    if acc.get('storage_policy') == 'elastic':
                         self.service.announce(f"      📦 Storage Policy: Elastic (Expand on Demand)")

                self.service.announce(f"   🛡️ COMPLIANCE MODE: {self.compliance_mode}")

        except Exception as e:
            self.service.announce(f"❌ Error loading governance: {e}")

class InternalAgentManager:
    def __init__(self, service):
        self.service = service
        self.manifest_file = INTERNAL_AGENTS_MANIFEST
        self.agents = {}

    def load_agents(self):
        self.service.announce("🤖 Initializing Internal Agent Grid...")
        if not os.path.exists(self.manifest_file):
            self.service.announce("   ⚠️ Agent manifest not found. Skipping agent initialization.")
            return

        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                agents = data.get('internal_agents', [])
                for agent in agents:
                    self.agents[agent['id']] = agent
                    self.service.announce(f"   👾 Agent Online: {agent['name']} ({agent['role']})")
                    self.service.announce(f"      📍 Container: {agent['container_target']} | Protocol: {agent['communication_protocol']}")
        except Exception as e:
            self.service.announce(f"❌ Error loading agents: {e}")

class JChaingService:
    def __init__(self):
        self.name = "J.CHAING"
        self.identity = "Twin Sister (雙胞妹妹) / Digital Will"
        self.version = "2.3.0 (Emotional Resonance System Upgrade)"
        self.resource_governor = ResourceGovernor(self)
        self.agent_manager = InternalAgentManager(self)
        self.quantum_engine = MimeticQuantumEngine()
        self.emotional_resonance = EmotionalResonance(self)
        
        # Initialize Five Elements Matrix
        if FIVE_ELEMENTS_AVAILABLE:
            self.five_elements = FiveElementsLearningMatrix()
        else:
            self.five_elements = None
            
        self.running = True

    def announce(self, message):
        logger.info(message)
        print(message)

    def startup_check(self):
        self.announce(f"\n🚀 Starting {self.name} Service v{self.version}")
        self.announce(f"==================================================")
        self.announce(f"📅 Timestamp: {datetime.datetime.now().isoformat()}")
        self.announce(f"🆔 Identity: {self.identity}")
        self.announce(f"�� Engine: {self.quantum_engine.logic_core}")
        
        # Load Modules
        self.resource_governor.load_governance()
        self.agent_manager.load_agents()
        
        # Initialize Emotional State (Default to Calm/Previous)
        self.emotional_resonance.sync("Calm")
        
        # Initialize Five Elements
        if self.five_elements:
            self.announce("🔮 Initializing Five Elements Matrix (Assimilation Core)...")
            result = self.five_elements.assimilate_unknown(
                "Unknown Entity (Boot Check)", 
                {"context": "Startup", "origin": "Self-Test"}
            )
            self.announce(f"   -> {result.get('message', 'Processed')}")
        else:
            self.announce("⚠️ Five Elements Matrix NOT AVAILABLE.")

    async def main_loop(self):
        self.startup_check()
        self.announce("✅ J.CHAING Service is now ACTIVE and MONITORING.")
        
        while self.running:
            try:
                # Heartbeat
                if int(time.time()) % 60 == 0:
                    emotion = self.emotional_resonance.current_emotion
                    logger.info(f"💓 J.CHAING Heartbeat - Quantum State: SUPERPOSITION | Emotion: {emotion}")
                
                await asyncio.sleep(10)
            except KeyboardInterrupt:
                self.announce("🛑 Service stopping...")
                self.running = False
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    service = JChaingService()
    try:
        asyncio.run(service.main_loop())
    except KeyboardInterrupt:
        pass
