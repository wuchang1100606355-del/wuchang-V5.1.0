import os
import re

# 1. Update finance.py (Add fields and waterfall logic)
finance_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\finance.py'
with open(finance_path, 'r', encoding='utf-8') as f:
    finance_content = f.read()

# Add fields
if 'association_balance' not in finance_content:
    fields_marker = "balance_whc = fields.Float(string='幸福幣餘額 (WHC)', readonly=True)"
    new_fields = """    balance_whc = fields.Float(string='幸福幣餘額 (WHC)', readonly=True)

    # --- Deficit Coverage Hierarchy (Waterfall) ---
    association_balance = fields.Float(string='協會支援準備金 (Association Reserve)', default=0.0)
    head_office_balance = fields.Float(string='總店支援準備金 (Head Office Reserve)', default=0.0)"""
    finance_content = finance_content.replace(fields_marker, new_fields)

# Add logic method
if 'def register_expense' not in finance_content:
    # Append to end of CommunityFundAccount class, before WuchangCoinTransaction
    class_end_marker = "    total_whc_circulation = fields.Float("
    # Find the end of fields definition or insert before the next class
    split_point = "class WuchangCoinTransaction"
    
    logic_code = """
    def register_expense(self, amount, reason):
        \"\"\"
        處理支出並執行瀑布流赤字支應邏輯：
        仁義店基金 (Fund) -> 協會 (Association) -> 總店 (Head Office)
        \"\"\"
        self.ensure_one()
        
        # 1. 仁義店 (基金池) 扣款
        self.balance_twd -= amount
        
        # 2. 檢查是否需要協會支應
        if self.balance_twd < 0:
            deficit = abs(self.balance_twd)
            # 從協會轉移填補
            self.association_balance -= deficit
            self.balance_twd += deficit  # 回補至 0
            
            # 紀錄支應 (可選)
            # self.env['wuchang.transparency.log'].create(...)
            
            # 3. 檢查是否需要總店支應
            if self.association_balance < 0:
                deficit_assoc = abs(self.association_balance)
                # 從總店轉移填補
                self.head_office_balance -= deficit_assoc
                self.association_balance += deficit_assoc  # 回補至 0

"""
    if split_point in finance_content:
        finance_content = finance_content.replace(split_point, logic_code + "\n\n" + split_point)

with open(finance_path, 'w', encoding='utf-8') as f:
    f.write(finance_content)
print("finance.py updated.")

# 2. Update pos_expense.py (Trigger deduction)
expense_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\pos_expense.py'
with open(expense_path, 'r', encoding='utf-8') as f:
    expense_content = f.read()

# Locate create method and inject logic
if 'fund.register_expense' not in expense_content:
    # We look for the loop inside create
    target_loop = "            if rec.amount is None or rec.amount <= 0:\n                raise ValueError('金額必須為正數')"
    
    injection = """            if rec.amount is None or rec.amount <= 0:
                raise ValueError('金額必須為正數')
            
            # Trigger Fund Logic if strictly controlled store
            if rec.pos_config_id.wuchang_store_mode == 'fund':
                fund = self.env['community.fund.account'].search([('account_type', '=', 'general')], limit=1)
                if fund:
                    fund.register_expense(rec.amount, rec.reason or 'Store Expense')"""
    
    expense_content = expense_content.replace(target_loop, injection)

with open(expense_path, 'w', encoding='utf-8') as f:
    f.write(expense_content)
print("pos_expense.py updated.")

# 3. Update pos_config_ext.py (Ensure Revenue Injection)
# Previous toolcall might have failed or search index was stale. Let's ensure it's there.
config_path = r'c:\wuchang V5.1.0\wuchang_os\addons\wuchang_core\models\pos_config_ext.py'
with open(config_path, 'r', encoding='utf-8') as f:
    config_content = f.read()

# Replace pass with actual logic
if "pass" in config_content and "fund.balance_twd += order.amount_total" not in config_content:
    # Look for the specific block
    block_start = "            # 這裡簡單模擬：實際邏輯應該是 TWD 增加，而非 WHC 增加，需視 wuchang_finance 邏輯調整"
    
    # We want to replace everything from block_start down to the end of the method (indentation sensitive)
    # Using a simpler replace on the 'pass' line if it's unique enough in context
    
    target_pass = "            # fund.balance_twd += order.amount_total (需透過 write)\n            pass"
    new_logic = """            # 執行收入注入
            fund.sudo().write({'balance_twd': fund.balance_twd + order.amount_total})"""
            
    if target_pass in config_content:
        config_content = config_content.replace(target_pass, new_logic)
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("pos_config_ext.py updated.")
    else:
        print("pos_config_ext.py pass block not found (might be already patched).")
else:
    print("pos_config_ext.py already has logic.")

