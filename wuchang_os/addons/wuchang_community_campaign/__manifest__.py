{
    'name': 'Wuchang Community Campaign',
    'version': '1.0',
    'summary': 'Interactive Wish Tree & Community Voting System',
    'description': """
        A beautiful, interactive platform for community engagement.
        Features:
        - Visual Wish Tree
        - Project Voting
        - Transparency Dashboard
    """,
    'category': 'Website',
    'author': 'Wuchang OS',
    'license': 'LGPL-3',
    'depends': ['base', 'website', 'wuchang_core', 'wuchang_finance'],
    'data': [
        'security/ir.model.access.csv',
        'views/campaign_templates.xml',
        'data/campaign_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'wuchang_community_campaign/static/src/css/campaign.css',
            'wuchang_community_campaign/static/src/js/campaign.js',
            'wuchang_community_campaign/static/src/js/wish_voting.js',
        ],
    },
    'installable': True,
    'application': True,
}
