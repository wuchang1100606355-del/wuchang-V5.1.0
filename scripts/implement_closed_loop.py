import os

# 1. Update ir.model.access.csv (Restrict Access)
acl_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\security\ir.model.access.csv'
with open(acl_path, 'r', encoding='utf-8') as f:
    acl_content = f.read()

# Change: access_community_fund_account,community.fund.account,model_community_fund_account,base.group_user,1,1,1,1
# To:     access_community_fund_account,community.fund.account,model_community_fund_account,base.group_user,1,0,0,0
old_perm = 'access_community_fund_account,community.fund.account,model_community_fund_account,base.group_user,1,1,1,1'
new_perm = 'access_community_fund_account,community.fund.account,model_community_fund_account,base.group_user,1,0,0,0'

if old_perm in acl_content:
    acl_content = acl_content.replace(old_perm, new_perm)
    with open(acl_path, 'w', encoding='utf-8') as f:
        f.write(acl_content)
    print("ACL updated: Write access revoked.")
else:
    print("ACL not updated (pattern not found or already changed).")

# 2. Update finance.py (Add inject_revenue, override write/create)
finance_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\finance.py'
with open(finance_path, 'r', encoding='utf-8') as f:
    finance_content = f.read()

# Add imports if missing
if 'from odoo.exceptions import AccessError' not in finance_content:
    finance_content = finance_content.replace('from odoo import models, fields, api', 'from odoo import models, fields, api\nfrom odoo.exceptions import AccessError, UserError')

# Add inject_revenue and write/create overrides
if 'def inject_revenue' not in finance_content:
    # Find where to insert (before register_expense or inside the class)
    target = 'def register_expense(self, amount, reason):'
    
    # We define the new methods
    new_methods = """    @api.model
    def create(self, vals):
        # Closed Loop Logic Check
        if not self.env.su and not self.env.context.get('little_j_audit'):
            raise AccessError('基金池封閉收支：僅小J (System) 可寫入。')
        return super(CommunityFundAccount, self).create(vals)

    def write(self, vals):
        # Closed Loop Logic Check
        if not self.env.su and not self.env.context.get('little_j_audit'):
            raise AccessError('基金池封閉收支：僅小J (System) 可寫入。')
        return super(CommunityFundAccount, self).write(vals)

    def inject_revenue(self, amount, source_desc):
        \"\"\"
        合規收入注入端口 (Revenue Port)
        \"\"\"
        self.ensure_one()
        # Logic Check: Positive Amount
        if amount <= 0:
            raise UserError('Logic Error: Revenue amount must be positive.')
            
        # Execute via sudo (Little J privilege)
        self.sudo().with_context(little_j_audit=True).write({
            'balance_twd': self.balance_twd + amount
        })
        # TODO: Add transparency log here if needed
        
    def register_expense(self, amount, reason):
        \"\"\"
        合規支出扣款端口 (Expense Port)
        \"\"\"
        self.ensure_one()
        # Logic Check: Positive Amount
        if amount <= 0:
            raise UserError('Logic Error: Expense amount must be positive.')

        # Execute via sudo (Little J privilege)
        # Note: We need to use sudo() to READ the balances for the waterfall logic as well if read is restricted (but read is 1 in ACL)
        # However, writing requires sudo.
        
        # Calculate new balances
        new_balance_twd = self.balance_twd - amount
        assoc_deduction = 0.0
        head_deduction = 0.0
        
        # Waterfall Logic Calculation
        if new_balance_twd < 0:
            deficit = abs(new_balance_twd)
            new_balance_twd = 0.0
            
            # Check Association
            if self.association_balance >= deficit:
                assoc_deduction = deficit
            else:
                assoc_deduction = self.association_balance
                remaining_deficit = deficit - self.association_balance
                head_deduction = remaining_deficit
        
        # Apply changes via sudo
        vals = {
            'balance_twd': new_balance_twd,
            'association_balance': self.association_balance - assoc_deduction,
            'head_office_balance': self.head_office_balance - head_deduction
        }
        self.sudo().with_context(little_j_audit=True).write(vals)
"""
    # Replace the old register_expense with the new set of methods
    # Note: We need to be careful with indentation and replacing the exact block
    # Since I just added register_expense in the previous turn, I can replace it.
    
    # Let's use regex or string split to find the old register_expense block
    # It starts with '    def register_expense' and ends before 'class WuchangCoinTransaction'
    # BUT, simple replacement is safer.
    
    if target in finance_content:
        # We replace the function definition line and assume the rest follows until next class
        # This is risky. Let's append the new methods BEFORE register_expense, and then replace register_expense.
        pass # Logic handled below
        
    # Let's just append these to the class. The previous register_expense is at the end of the class.
    # We will replace the whole previous register_expense block.
    
    import re
    # Regex to capture the whole method: def register_expense... until end of indentation
    # But finding the exact string range is easier if we know what we wrote.
    # I wrote:
    # def register_expense(self, amount, reason):
    #     """
    #     處理支出並執行瀑布流赤字支應邏輯：
    # ...
    #             self.association_balance += deficit_assoc  # 回補至 0
    
    # Let's try to locate the start and the end (next class or EOF)
    start_idx = finance_content.find('    def register_expense')
    end_idx = finance_content.find('class WuchangCoinTransaction')
    
    if start_idx != -1 and end_idx != -1:
        # Extract the old block
        old_block = finance_content[start_idx:end_idx]
        # Construct new block (which includes create/write/inject/register)
        # Note: register_expense is RE-IMPLEMENTED with sudo and context.
        finance_content = finance_content.replace(old_block, new_methods + "\n\n")
        
        with open(finance_path, 'w', encoding='utf-8') as f:
            f.write(finance_content)
        print("finance.py updated with compliant ports and logic checks.")
    else:
        print("Could not locate register_expense block for replacement.")

# 3. Update pos_config_ext.py (Use inject_revenue)
config_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\pos_config_ext.py'
with open(config_path, 'r', encoding='utf-8') as f:
    config_content = f.read()

old_logic = "fund.sudo().write({'balance_twd': fund.balance_twd + order.amount_total})"
new_logic = "fund.inject_revenue(order.amount_total, f'POS Order {order.name}')"

if old_logic in config_content:
    config_content = config_content.replace(old_logic, new_logic)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("pos_config_ext.py updated to use inject_revenue.")
else:
    print("pos_config_ext.py target logic not found.")

# 4. Update pos_expense.py (Use register_expense, which is already there, but we updated the definition)
# The call site in pos_expense.py is: fund.register_expense(rec.amount, rec.reason or 'Store Expense')
# This is already correct and compatible with the new definition.

