
import logging
import sys
import odoo
from odoo import api, SUPERUSER_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    import odoo.tools.config as config
    config.parse_config(['--db_host=wuchang-db', '--db_user=odoo', '--db_password=odoo', '-d', 'wuchang'])
    odoo.service.server.load_server_wide_modules()
    registry = odoo.registry('wuchang')
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        module = env['ir.module.module'].search([('name', '=', 'wuchang_core')])
        if module:
            logger.info(f'Found module wuchang_core. State: {module.state}')
            try:
                module.button_immediate_upgrade()
                env.cr.commit()
                logger.info('Upgrade triggered successfully.')
            except Exception as e:
                logger.error(f'Upgrade failed: {e}')
                # Sometimes immediate upgrade raises because it reloads registry
                pass
        else:
            logger.error('Module wuchang_core not found in database.')

