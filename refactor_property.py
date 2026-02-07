import sys
import os

file_path = r'J:\共用雲端硬碟\五常雲端空間\wuchang_os\addons\wuchang_core\models\property_management.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace owner_name with owner_id
new_content = content.replace("owner_name = fields.Char('區分所有權人')", "owner_id = fields.Many2one('res.partner', string='區分所有權人')")

# Add committee_partner_id to PropertyCommunity
if "committee_partner_id" not in new_content:
    new_content = new_content.replace(
        "address = fields.Char('社區地址')",
        "address = fields.Char('社區地址')\n    committee_partner_id = fields.Many2one('res.partner', string='管委會(團體客戶)', domain=\"[('property_management_role', '=', 'committee')]\")"
    )

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
