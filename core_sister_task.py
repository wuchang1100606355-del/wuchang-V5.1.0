import time
import logging
import sys
import threading
from pathlib import Path

# Configure logging
# - On Linux Odoo servers, `/var/lib/odoo/` is common.
# - On Windows/dev machines, fall back to a local `logs/` folder.
default_log_path = Path("/var/lib/odoo/core_sister.log")
if sys.platform.startswith("win") or not default_log_path.parent.exists():
    default_log_path = Path(__file__).resolve().parent / "logs" / "core_sister_task.log"
default_log_path.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(default_log_path),
    level=logging.INFO,
    format="%(asctime)s - CoreSister - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def run_maintenance(env):
    logger.info('Core Sister taking over maintenance tasks.')
    
    # 1. Upgrade wuchang_core module
    try:
        logger.info('Step 1: Checking wuchang_core module status...')
        module = env['ir.module.module'].search([('name', '=', 'wuchang_core')])
        if module:
            if module.state != 'installed':
                logger.info(f'Module state is {module.state}. Upgrading...')
                module.button_immediate_upgrade()
                env.cr.commit()
                logger.info('Module upgraded successfully.')
            else:
                logger.info('Module is already installed. Forcing update to ensure fields...')
                module.button_immediate_upgrade()
                env.cr.commit()
                logger.info('Module update forced.')
        else:
            logger.error('Module wuchang_core not found!')
    except Exception as e:
        logger.error(f'Error upgrading module: {str(e)}')
    
    time.sleep(5) # Proceed slowly

    # 2. Cleanup Non-Jurisdiction Partners
    try:
        logger.info('Step 2: Cleaning up non-jurisdiction partners...')
        committees = env['res.partner'].search([
            ('property_management_role', '=', 'committee'),
            ('name', 'not like', '五常社區發展協會')
        ])
        
        count = 0
        for comm in committees:
            logger.info(f'Marking non-jurisdiction committee inactive: {comm.name}')
            comm.active = False
            count += 1
            
        logger.info(f'Processed {count} non-jurisdiction committees.')
        env.cr.commit()
    except Exception as e:
        logger.error(f'Error cleaning partners: {str(e)}')

    time.sleep(5)

    # 3. Build Spatiotemporal Index
    try:
        logger.info('Step 3: Building Spatiotemporal Index...')
        ai_guard = env['wuchang.ai.hallucination.monitor'].search([], limit=1)
        if not ai_guard:
            ai_guard = env['wuchang.ai.hallucination.monitor'].create({'name': 'Core Monitor'})
        
        if hasattr(ai_guard, 'action_build_system_index'):
            ai_guard.action_build_system_index()
            env.cr.commit()
            logger.info('Spatiotemporal index built successfully.')
        else:
            logger.error('action_build_system_index method not found on AI Guard.')
    except Exception as e:
        logger.error(f'Error building index: {str(e)}')

    logger.info('Core Sister maintenance cycle completed. Standing by.')

def _main() -> int:
    # This script is designed to be executed inside an Odoo environment where `env` exists.
    # If you run it directly, we fail loudly with instructions rather than silently doing nothing.
    logger.error("No Odoo `env` provided. Run inside Odoo shell/server action and call run_maintenance(env).")
    return 2


if __name__ == "__main__":
    raise SystemExit(_main())

