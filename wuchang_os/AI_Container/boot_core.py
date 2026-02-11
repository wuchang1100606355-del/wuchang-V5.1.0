import json
import os
import time
import logging

# Configuration
CONFIG_FILE = "FIVE_ELEMENTS_CONFIG.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FiveElementsBoot")

class ElementCore:
    def __init__(self, name, element, uqui, path):
        self.name = name
        self.element = element
        self.uqui = uqui
        self.path = path
        self.status = "offline"

    def load(self):
        logger.info(f"[{self.element}] Loading {self.name} from {self.path}...")
        # Simulation of loading weights
        time.sleep(0.5) 
        if os.path.exists(os.path.join(BASE_DIR, self.path)):
            self.status = "online"
            logger.info(f"[{self.element}] {self.name} ({self.uqui}) is ONLINE.")
            return True
        else:
            self.status = "error"
            logger.error(f"[{self.element}] Model file not found at {self.path}!")
            return False

def boot_system():
    logger.info("==================================================")
    logger.info("   WUCHANG FIVE ELEMENTS AI MATRIX - BOOT SEQUENCE")
    logger.info("==================================================")
    
    config_path = os.path.join(BASE_DIR, CONFIG_FILE)
    if not os.path.exists(config_path):
        logger.error("Configuration file missing!")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    logger.info(f"System: {config['system_name']} v{config['version']}")
    
    elements = []
    for model_conf in config['models']:
        core = ElementCore(
            model_conf['name'], 
            model_conf['element'], 
            model_conf['uqui'], 
            model_conf['path']
        )
        elements.append(core)

    # Boot Sequence
    all_green = True
    for core in elements:
        if not core.load():
            all_green = False

    logger.info("--------------------------------------------------")
    if all_green:
        logger.info("✅ ALL FIVE ELEMENTS ARE RESONATING.")
        logger.info("   Metal (Logic) | Wood (Growth) | Water (Flow) | Fire (Action) | Earth (Memory)")
        logger.info("   System is ready for independent operation.")
    else:
        logger.warning("⚠️ SYSTEM STABILITY COMPROMISED. Check logs.")
    logger.info("==================================================")

if __name__ == "__main__":
    boot_system()
