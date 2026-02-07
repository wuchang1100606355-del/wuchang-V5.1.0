{
    'name': 'Wuchang Life',
    'version': '1.0.0',
    'summary': 'Wuchang Life beta v1.0.0',
    'description': """
        Wuchang Life Public Welfare System
         ==================================
         Core Features:
         1. Free Building Management Committee Software (免費大樓管委會管理軟體)
         2. Free Local Business Management Software (免費在地商家管理軟體)
            * Condition: Merchants participating in the Fund Pool Distribution enjoy FOREVER FREE access.
            * (承諾：參加「基金池分配」之商家，享「永久免費」使用權)
         3. Professional Maintenance & Customization Services (專業維運與客製化服務)
         
         This module provides the public landing and core integration for Wuchang Community.
    """,
    'author': 'Wuchang',
    'license': 'LGPL-3',
    'website': 'https://wuchang.community',
    'depends': ['website'],
    'data': [
        'views/life_templates.xml',
        'views/record_hall_templates.xml',
        'views/workspace_templates.xml',
        'data/menu.xml',
        'data/workspace_menu.xml',
    ],
    'installable': True,
}
