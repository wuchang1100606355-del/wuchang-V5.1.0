# -*- coding: utf-8 -*-
{
    'name': "Wuchang Integrated Property Management System (五常整合式物業管理系統)",
    'summary': "Integrated Property Management System (整合式物業管理系統)",
    'description': """
        Integrated Property Management System (整合式物業管理系統) for Wuchang Community OS.
        
        Based on Patent: 整合式物業管理系統 (Integrated Property Management System)
        Patent No: Mxxxxxx (Pending)
        
        Features:
        - Empowerment Toolkits
        - Profit Sharing Logic
        - Maintenance Requests Workflow (報修管理)
        - Patent Management (專利管理)
    """,
    'author': "Wuchang OS Team",
    'license': 'LGPL-3',
    'category': 'Services',
    'version': '5.1.0',
    'depends': ['wuchang_core', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/property_site.xml',
        'views/property_maintenance.xml',
        'views/property_patent.xml',
        'data/patent_data.xml',
    ],
    'installable': True,
}
