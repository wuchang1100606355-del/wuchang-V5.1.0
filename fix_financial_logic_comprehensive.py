"""
修正財務邏輯：
1. 會務承攬費用應為年度結餘，但協會根本不足以支付營運，需靠捐助營運
2. 捐助額為每月負數向上品食品行申請，如此怎會有結餘
3. 檢討會員減少問題，總幹事回答仍為轉型陣痛，但承諾由其經營之上品食品行捐助
4. 新增去年年初因會員大幅縮減停收會費以維持正常營運
"""

from __future__ import annotations

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"
MEETINGS_DIR = OPERATIONAL_FILES_DIR / "meetings"

CONTRACTOR_COMPANY = "五常物業規劃顧問股份有限公司"
SECRETARY_NAME = "江政隆"
DONOR_COMPANY = "上品食品行"
DONOR_TAX_ID = "34778660"
DONOR_FULL = f"{DONOR_COMPANY}（統一編號：{DONOR_TAX_ID}）"


def calculate_correct_financials():
    """重新計算正確的財務數據"""
    # 收入（不含會務承攬費）
    membership_fee = 0  # 去年年初停收會費
    corporate_donation = 17500
    industry_income = 632500
    instructor_donation = 265123
    other_income = 0
    
    total_income_without_contractor = membership_fee + corporate_donation + industry_income + instructor_donation + other_income
    # 915,123元
    
    # 支出（不含會務承攬費）
    personnel_cost = 0  # 無人事成本
    business_cost_without_contractor = 709912 - 0  # 業務費不含會務承攬費（先假設為709,912，需重新計算）
    # 業務費明細：舞蹈課程331,456元
    dance_course_cost = 331456
    business_cost_other = 709912 - dance_course_cost  # 378,456元（其他業務費）
    
    equipment_cost = 84234
    admin_cost = 80000
    system_cost = 83310
    
    total_expense_without_contractor = personnel_cost + business_cost_without_contractor + equipment_cost + admin_cost + system_cost
    # 957,456元（不含會務承攬費）
    
    # 計算結餘（不含會務承攬費）
    profit_before_contractor = total_income_without_contractor - total_expense_without_contractor
    # 915,123 - 957,456 = -42,333元（虧損）
    
    # 會務承攬費 = 年度結餘（但為負數，所以為0）
    contractor_fee = max(0, profit_before_contractor)  # 0元（因為沒有結餘）
    
    # 實際總支出
    total_expense = total_expense_without_contractor + contractor_fee
    # 957,456元
    
    # 實際結餘
    actual_profit = total_income_without_contractor - total_expense
    # 915,123 - 957,456 = -42,333元（虧損）
    
    # 需要上品食品行捐助的金額
    donor_support_needed = abs(actual_profit)  # 42,333元
    
    return {
        "membership_fee": membership_fee,
        "corporate_donation": corporate_donation,
        "industry_income": industry_income,
        "instructor_donation": instructor_donation,
        "total_income": total_income_without_contractor,
        "contractor_fee": contractor_fee,
        "dance_course_cost": dance_course_cost,
        "business_cost_other": business_cost_other,
        "business_cost_total": business_cost_without_contractor,
        "equipment_cost": equipment_cost,
        "admin_cost": admin_cost,
        "system_cost": system_cost,
        "total_expense": total_expense,
        "profit_before_contractor": profit_before_contractor,
        "actual_profit": actual_profit,
        "donor_support_needed": donor_support_needed
    }


def update_financial_report_2025():
    """更新2025年度決算"""
    print("更新2025年度決算...")
    
    financials = calculate_correct_financials()
    
    filepath = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新收入決算
    content = re.sub(
        r'\| 會費收入 \| 170,400 \| 170,400 \| 0 \| 會員會費（每人每月100元，1月收取全年，142人×1,200元，退會不退費，初始會員數150人） \|',
        f'| 會費收入 | 0 | 0 | 0 | 去年年初因會員大幅縮減停收會費以維持正常營運 |',
        content
    )
    
    # 更新不足額補助
    content = re.sub(
        r'\| 不足額補助 \| 171,933 \| 171,933 \| 0 \| 上品食品行（統一編號：34778660）捐贈（補足年終結餘不足額） \|',
        f'| 不足額補助 | {financials["donor_support_needed"]:,} | {financials["donor_support_needed"]:,} | 0 | {DONOR_FULL}捐贈（補足年度營運虧損，每月負數向上品食品行申請） |',
        content
    )
    
    # 更新收入合計
    new_total_income = financials["total_income"] + financials["donor_support_needed"]
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*1,257,456\*\* \| \*\*1,257,456\*\* \| \*\*0\*\* \|',
        f'| **合計** | **{new_total_income:,}** | **{new_total_income:,}** | **0** |',
        content
    )
    
    # 更新支出決算
    content = re.sub(
        r'\| 業務費 \| 1,011,500 \| 1,009,912 \| -1,588 \| 活動執行費用（含舞蹈運動課程331,456元、會務承攬費300,000元，依協會盈餘計算，最高不超過700,000元，留合理尾數） \|',
        f'| 業務費 | {financials["business_cost_total"]:,} | {financials["business_cost_total"]:,} | 0 | 活動執行費用（含舞蹈運動課程{financials["dance_course_cost"]:,}元，會務承攬費{financials["contractor_fee"]:,}元，因無結餘故會務承攬費為0，留合理尾數） |',
        content
    )
    
    # 更新支出合計
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*1,261,500\*\* \| \*\*1,257,456\*\* \| \*\*-4,044\*\* \|',
        f'| **合計** | **{financials["total_expense"]:,}** | **{financials["total_expense"]:,}** | **0** |',
        content
    )
    
    # 更新重要說明
    content = re.sub(
        r'- 支出總額：1,257,456 元（含舞蹈運動課程331,456元、會務承攬費300,000元，依協會盈餘計算，最高不超過700,000元，除定額支付項目外留合理尾數）',
        f'- 支出總額：{financials["total_expense"]:,} 元（含舞蹈運動課程{financials["dance_course_cost"]:,}元，會務承攬費{financials["contractor_fee"]:,}元，因無結餘故會務承攬費為0，除定額支付項目外留合理尾數）',
        content
    )
    
    content = re.sub(
        r'- 年終結餘：0 元（114年，不足額由上品食品行（統一編號：34778660）捐贈補足）',
        f'- 年終結餘：0 元（114年，不足額由{DONOR_FULL}捐贈補足，協會需靠捐助營運）',
        content
    )
    
    # 更新收入總額說明
    content = re.sub(
        r'- 收入總額：1,257,456 元（會費170,400 \+ 企業捐助17,500 \+ 產業收入632,500 \+ 講師回捐265,123 \+ 不足額補助171,933）',
        f'- 收入總額：{new_total_income:,} 元（會費0 + 企業捐助{financials["corporate_donation"]:,} + 產業收入{financials["industry_income"]:,} + 講師回捐{financials["instructor_donation"]:,} + 不足額補助{financials["donor_support_needed"]:,}）',
        content
    )
    
    # 更新現金出納表
    content = re.sub(
        r'\| 本期收入 \| 1,257,456 \| 會費170,400 \+ 企業捐助17,500 \+ 產業收入632,500 \+ 講師回捐265,123 \+ 不足額補助171,933（上品食品行（統一編號：34778660）捐贈） \|',
        f'| 本期收入 | {new_total_income:,} | 會費0（去年年初停收）+ 企業捐助{financials["corporate_donation"]:,} + 產業收入{financials["industry_income"]:,} + 講師回捐{financials["instructor_donation"]:,} + 不足額補助{financials["donor_support_needed"]:,}（{DONOR_FULL}捐贈，每月負數申請） |',
        content
    )
    
    content = re.sub(
        r'\| 本期支出 \| 1,257,456 \| 人事費0（會務承攬）\+ 業務費1,009,912（含舞蹈課程331,456、會務承攬費300,000，依協會盈餘計算，最高不超過700,000元）\+ 設備費84,234 \+ 行政管理費80,000 \+ 系統維護費83,310 \|',
        f'| 本期支出 | {financials["total_expense"]:,} | 人事費0（會務承攬）+ 業務費{financials["business_cost_total"]:,}（含舞蹈課程{financials["dance_course_cost"]:,}、會務承攬費{financials["contractor_fee"]:,}，因無結餘故為0）+ 設備費{financials["equipment_cost"]:,} + 行政管理費{financials["admin_cost"]:,} + 系統維護費{financials["system_cost"]:,} |',
        content
    )
    
    # 更新基金收支表
    content = re.sub(
        r'\| 本期收入 \| 1,257,456 \| 會費 170,400 \+ 企業捐助 17,500 \+ 產業收入 632,500 \+ 講師回捐 265,123 \+ 不足額補助 171,933（上品食品行（統一編號：34778660）捐贈） \|',
        f'| 本期收入 | {new_total_income:,} | 會費 0（去年年初停收）+ 企業捐助 {financials["corporate_donation"]:,} + 產業收入 {financials["industry_income"]:,} + 講師回捐 {financials["instructor_donation"]:,} + 不足額補助 {financials["donor_support_needed"]:,}（{DONOR_FULL}捐贈，每月負數申請） |',
        content
    )
    
    content = re.sub(
        r'\| 本期支出 \| 1,257,456 \| 人事費 0（會務承攬）\+ 業務費 1,009,912（含舞蹈課程331,456、會務承攬費300,000，依協會盈餘計算，最高不超過700,000元）\+ 設備費 84,234 \+ 行政管理費 80,000 \+ 系統維護費 83,310 \|',
        f'| 本期支出 | {financials["total_expense"]:,} | 人事費 0（會務承攬）+ 業務費 {financials["business_cost_total"]:,}（含舞蹈課程{financials["dance_course_cost"]:,}、會務承攬費{financials["contractor_fee"]:,}，因無結餘故為0）+ 設備費 {financials["equipment_cost"]:,} + 行政管理費 {financials["admin_cost"]:,} + 系統維護費 {financials["system_cost"]:,} |',
        content
    )
    
    # 更新決算說明
    content = re.sub(
        r'- 會費收入：170,400 元（達成率 100%，每人每月100元，1月收取全年，142人×1,200元，退會不退費，初始會員數150人）',
        f'- 會費收入：0 元（去年年初因會員大幅縮減停收會費以維持正常營運）',
        content
    )
    
    content = re.sub(
        r'- 收入總額：1,257,456 元（含不足額補助171,933元，由上品食品行（統一編號：34778660）捐贈）',
        f'- 收入總額：{new_total_income:,} 元（含不足額補助{financials["donor_support_needed"]:,}元，由{DONOR_FULL}捐贈，每月負數申請）',
        content
    )
    
    content = re.sub(
        r'- 業務費：1,009,912 元（預算 1,011,500，含舞蹈運動課程331,456元、會務承攬費300,000元，依協會盈餘計算，最高不超過700,000元，留合理尾數）',
        f'- 業務費：{financials["business_cost_total"]:,} 元（含舞蹈運動課程{financials["dance_course_cost"]:,}元、會務承攬費{financials["contractor_fee"]:,}元，因無結餘故會務承攬費為0，留合理尾數）',
        content
    )
    
    content = re.sub(
        r'- 支出總額：1,257,456 元（含舞蹈運動課程331,456元、會務承攬費300,000元，依協會盈餘計算，最高不超過700,000元，留合理尾數）',
        f'- 支出總額：{financials["total_expense"]:,} 元（含舞蹈運動課程{financials["dance_course_cost"]:,}元、會務承攬費{financials["contractor_fee"]:,}元，因無結餘故會務承攬費為0，留合理尾數）',
        content
    )
    
    content = re.sub(
        r'- 年終結餘：0 元（114年，不足額由上品食品行（統一編號：34778660）捐贈補足）',
        f'- 年終結餘：0 元（114年，不足額由{DONOR_FULL}捐贈補足，協會需靠捐助營運）',
        content
    )
    
    # 更新資金來源說明
    content = re.sub(
        r'- \*\*會費收入\*\*：170,400 元（每人每月100元，1月收取全年，142人×1,200元，退會不退費，初始會員數150人）',
        f'- **會費收入**：0 元（去年年初因會員大幅縮減停收會費以維持正常營運）',
        content
    )
    
    content = re.sub(
        r'- \*\*不足額補助\*\*：171,933 元（由上品食品行（統一編號：34778660）捐贈，補足年終結餘不足額）',
        f'- **不足額補助**：{financials["donor_support_needed"]:,} 元（由{DONOR_FULL}捐贈，補足年度營運虧損，每月負數向上品食品行申請）',
        content
    )
    
    # 更新會務承攬說明
    content = re.sub(
        r'- \*\*承攬費用\*\*：300,000 元（依協會盈餘計算，協會盈餘300,000元，最高不超過700,000元，納入業務費）',
        f'- **承攬費用**：{financials["contractor_fee"]:,} 元（依協會盈餘計算，因協會根本不足以支付營運需靠捐助營運，無結餘故會務承攬費為0，納入業務費）',
        content
    )
    
    content = re.sub(
        r'- \*\*契約規範\*\*：會務承攬契約中規範為協會盈餘金額，但不得超出700,000元整',
        f'- **契約規範**：會務承攬契約中規範為協會盈餘金額，但不得超出700,000元整（因無結餘，故會務承攬費為0）',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      會費收入：0 元（去年年初停收）")
    print(f"      會務承攬費：{financials['contractor_fee']:,} 元（無結餘）")
    print(f"      不足額補助：{financials['donor_support_needed']:,} 元（{DONOR_FULL}）")


def update_meeting_minutes():
    """更新會議記錄"""
    print("\n更新會議記錄...")
    
    financials = calculate_correct_financials()
    
    filepath = MEETINGS_DIR / "meeting_20260117_理監事會會議.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新會員數遞減檢討案
    content = re.sub(
        r'3\. \*\*因應措施\*\*：\n   - 會務由五常物業規劃顧問股份有限公司承攬（契約規範為協會盈餘金額，但不得超出700,000元整）\n   - 總幹事江政隆由公司聘用派駐本會\n   - 希望理事會給予支持，共同度過轉型陣痛期',
        f'3. **因應措施**：\n   - 會務由{CONTRACTOR_COMPANY}承攬（契約規範為協會盈餘金額，但不得超出700,000元整，因無結餘故會務承攬費為0）\n   - 總幹事{SECRETARY_NAME}由公司聘用派駐本會\n   - 總幹事承諾由其經營之{DONOR_FULL}捐助，補足協會營運虧損\n   - 去年年初因會員大幅縮減停收會費以維持正常營運\n   - 希望理事會給予支持，共同度過轉型陣痛期',
        content
    )
    
    content = re.sub(
        r'2\. \*\*原因分析\*\*：此為協會轉型陣痛期，因協會不以吃喝旅遊等福利為施政主軸，部分會員無法適應新政策而選擇退會。',
        f'2. **原因分析**：此為協會轉型陣痛期，因協會不以吃喝旅遊等福利為施政主軸，部分會員無法適應新政策而選擇退會。總幹事回答仍為轉型陣痛，但承諾由其經營之{DONOR_FULL}捐助。',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("修正財務邏輯：會務承攬費與捐助邏輯")
    print("=" * 60)
    print()
    
    financials = calculate_correct_financials()
    
    print("邏輯分析：")
    print(f"1. 會費收入：{financials['membership_fee']:,} 元（去年年初停收）")
    print(f"2. 收入總額（不含捐助）：{financials['total_income']:,} 元")
    print(f"3. 支出總額：{financials['total_expense']:,} 元")
    print(f"4. 結餘（不含會務承攬費）：{financials['profit_before_contractor']:,} 元（虧損）")
    print(f"5. 會務承攬費：{financials['contractor_fee']:,} 元（因無結餘故為0）")
    print(f"6. 需要{DONOR_FULL}捐助：{financials['donor_support_needed']:,} 元（每月負數申請）")
    print()
    
    # 更新財務文件
    update_financial_report_2025()
    
    # 更新會議記錄
    update_meeting_minutes()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n修正摘要：")
    print("- 會費收入：0元（去年年初因會員大幅縮減停收）")
    print("- 會務承攬費：0元（因無結餘，協會需靠捐助營運）")
    print(f"- 不足額補助：{financials['donor_support_needed']:,}元（{DONOR_FULL}，每月負數申請）")
    print("- 總幹事承諾由其經營之上品食品行捐助")


if __name__ == "__main__":
    main()
