admin = env['res.users'].search([('login', '=', 'admin')]); admin.write({'login': 'admin@wuchang.life', 'password': 'poiuY92926'}); env.cr.commit(); print('Admin updated')
