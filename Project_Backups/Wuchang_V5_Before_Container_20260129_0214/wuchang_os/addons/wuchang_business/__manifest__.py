# -*- coding: utf-8 -*-
{
    'name': "五常商業引擎 (Wuchang Business)",
    'summary': "社區經濟循環與實體店面營運模組",
    'version': '1.0.0',
    'category': 'Sales/Point of Sale',
    'author': "Jules the AI",
    'website': "https://wuchang.community",
    'license': 'AGPL-3',
    'depends': [
        'wuchang_core', 'point_of_sale', 'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'data/lab_data.xml',
    ],
    'description': """
        【五常商業引擎】
        
        實現「仁義店」與「總店」的商業邏輯。
        - 隱冰醇萃：厭氧特濃 (Phantom Ice Brew) 產品定義
        - 光速協議 (Velocity Protocol)
        - AI 秘書商業輔助
    """
}
