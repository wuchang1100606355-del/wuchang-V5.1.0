"""
更新會務承攬契約規範：協會盈餘金額，但不得超出70萬元整
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
MAX_CONTRACT_FEE = 700000  # 70萬元整


def calculate_contract_fee(total_income, total_expense_excluding_contract):
    """計算會務承攬費：協會盈餘金額，但不得超出70萬元整"""
    profit = total_income - total_expense_excluding_contract
    contract_fee = min(profit, MAX_CONTRACT_FEE)
    return contract_fee, profit


def update_financial_budget_2027():
    """更新2027年度預算"""
    print("更新2027年度預算...")
    
    filepath = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新業務費說明
    content = re.sub(
        r'\| 業務費 \| 1,011,500\.0 \| 活動執行費用（含舞蹈運動課程331,500元、會務承攬費300,000元） \|',
        f'| 業務費 | 1,011,500.0 | 活動執行費用（含舞蹈運動課程331,500元、會務承攬費300,000元，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元） |',
        content
    )
    
    # 更新支出總額說明
    content = re.sub(
        r'- 支出總額：1,261,500 元（含舞蹈運動課程331,500元、會務承攬費300,000元）',
        f'- 支出總額：1,261,500 元（含舞蹈運動課程331,500元、會務承攬費300,000元，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元）',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def update_financial_report_2025():
    """更新2025年度決算"""
    print("\n更新2025年度決算...")
    
    filepath = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 計算會務承攬費
    # 收入：1,257,456元
    # 支出（不含會務承攬費）：1,257,456 - 300,000 = 957,456元
    total_income = 1257456
    total_expense_excluding_contract = 957456
    contract_fee, profit = calculate_contract_fee(total_income, total_expense_excluding_contract)
    
    # 更新業務費說明
    content = re.sub(
        r'\| 業務費 \| 1,011,500 \| 1,009,912 \| -1,588 \| 活動執行費用（含舞蹈運動課程331,456元、會務承攬費300,000元，留合理尾數） \|',
        f'| 業務費 | 1,011,500 | 1,009,912 | -1,588 | 活動執行費用（含舞蹈運動課程331,456元、會務承攬費{contract_fee:,}元，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元，留合理尾數） |',
        content
    )
    
    # 更新支出總額說明
    content = re.sub(
        r'- 支出總額：1,257,456 元（含舞蹈運動課程331,456元、會務承攬費300,000元，除定額支付項目外留合理尾數）',
        f'- 支出總額：1,257,456 元（含舞蹈運動課程331,456元、會務承攬費{contract_fee:,}元，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元，除定額支付項目外留合理尾數）',
        content
    )
    
    # 更新現金出納表
    content = re.sub(
        r'\| 本期支出 \| 1,257,456 \| 人事費0（會務承攬）\+ 業務費1,009,912（含舞蹈課程331,456、會務承攬費300,000）\+ 設備費84,234 \+ 行政管理費80,000 \+ 系統維護費83,310 \|',
        f'| 本期支出 | 1,257,456 | 人事費0（會務承攬）+ 業務費1,009,912（含舞蹈課程331,456、會務承攬費{contract_fee:,}，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元）+ 設備費84,234 + 行政管理費80,000 + 系統維護費83,310 |',
        content
    )
    
    # 更新基金收支表
    content = re.sub(
        r'\| 本期支出 \| 1,257,456 \| 人事費 0（會務承攬）\+ 業務費 1,009,912（含舞蹈課程331,456、會務承攬費300,000）\+ 設備費 84,234 \+ 行政管理費 80,000 \+ 系統維護費 83,310 \|',
        f'| 本期支出 | 1,257,456 | 人事費 0（會務承攬）+ 業務費 1,009,912（含舞蹈課程331,456、會務承攬費{contract_fee:,}，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元）+ 設備費 84,234 + 行政管理費 80,000 + 系統維護費 83,310 |',
        content
    )
    
    # 更新決算說明
    content = re.sub(
        r'- 業務費：1,009,912 元（預算 1,011,500，含舞蹈運動課程331,456元、會務承攬費300,000元，留合理尾數）',
        f'- 業務費：1,009,912 元（預算 1,011,500，含舞蹈運動課程331,456元、會務承攬費{contract_fee:,}元，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元，留合理尾數）',
        content
    )
    
    content = re.sub(
        r'- 支出總額：1,257,456 元（含舞蹈運動課程331,456元、會務承攬費300,000元，留合理尾數）',
        f'- 支出總額：1,257,456 元（含舞蹈運動課程331,456元、會務承攬費{contract_fee:,}元，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元，留合理尾數）',
        content
    )
    
    # 更新會務承攬說明
    content = re.sub(
        r'- \*\*承攬費用\*\*：300,000 元（原預算人事費，納入業務費）',
        f'- **承攬費用**：{contract_fee:,} 元（依協會盈餘計算，協會盈餘{profit:,}元，最高不超過{MAX_CONTRACT_FEE:,}元，納入業務費）\n- **契約規範**：會務承攬契約中規範為協會盈餘金額，但不得超出{MAX_CONTRACT_FEE:,}元整',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      協會盈餘：{profit:,} 元")
    print(f"      會務承攬費：{contract_fee:,} 元（最高不超過{MAX_CONTRACT_FEE:,}元）")


def update_annual_work_plan():
    """更新年度工作計畫"""
    print("\n更新年度工作計畫...")
    
    filepath = OPERATIONAL_FILES_DIR / "02_年度工作計畫_2026.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新業務費說明
    content = re.sub(
        r'\| 業務費 \| 1,011,500\.0 \| 活動執行費用（含舞蹈運動課程331,500元、會務承攬費300,000元） \|',
        f'| 業務費 | 1,011,500.0 | 活動執行費用（含舞蹈運動課程331,500元、會務承攬費300,000元，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元） |',
        content
    )
    
    # 更新會務承攬說明
    content = re.sub(
        r'- 會務承攬：300,000 元（五常物業規劃顧問股份有限公司承攬會務，總幹事江政隆由公司聘用派駐本會，原預算人事費）',
        f'- 會務承攬：依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元整（{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會，契約規範為協會盈餘金額，但不得超出{MAX_CONTRACT_FEE:,}元整）',
        content
    )
    
    # 更新實際支出預算說明
    content = re.sub(
        r'- 實際支出預算：1,261,500\.0 元（含舞蹈運動課程331,500元、會務承攬費300,000元）',
        f'- 實際支出預算：1,261,500.0 元（含舞蹈運動課程331,500元、會務承攬費300,000元，依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元）',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def update_meeting_minutes():
    """更新會議記錄"""
    print("\n更新會議記錄...")
    
    for month in range(2, 13):  # 2月到12月
        month_str = f"{month:02d}"
        filepath = MEETINGS_DIR / f"meeting_2026{month_str}15_理監事會會議.md"
        
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            
            # 更新財務狀況說明
            content = re.sub(
                r'- 會務承攬：300,000 元（五常物業規劃顧問股份有限公司承攬會務，總幹事江政隆由公司聘用派駐本會）',
                f'- 會務承攬：依協會盈餘計算，最高不超過{MAX_CONTRACT_FEE:,}元整（{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會，契約規範為協會盈餘金額，但不得超出{MAX_CONTRACT_FEE:,}元整）',
                content
            )
            
            filepath.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{filepath.name}")


def update_january_meeting():
    """更新1月會議記錄"""
    print("\n更新1月會議記錄...")
    
    filepath = MEETINGS_DIR / "meeting_20260117_理監事會會議.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新會員數遞減檢討案
    content = re.sub(
        r'   - 會務由五常物業規劃顧問股份有限公司承攬（原預算人事費300,000元）',
        f'   - 會務由{CONTRACTOR_COMPANY}承攬（契約規範為協會盈餘金額，但不得超出{MAX_CONTRACT_FEE:,}元整）',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("更新會務承攬契約規範")
    print("=" * 60)
    print()
    print(f"承攬公司：{CONTRACTOR_COMPANY}")
    print(f"派駐人員：總幹事{SECRETARY_NAME}")
    print(f"契約規範：協會盈餘金額，但不得超出{MAX_CONTRACT_FEE:,}元整")
    print()
    
    # 更新財務文件
    update_financial_budget_2027()
    update_financial_report_2025()
    
    # 更新年度工作計畫
    update_annual_work_plan()
    
    # 更新會議記錄
    update_meeting_minutes()
    update_january_meeting()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print(f"- 會務承攬費：依協會盈餘計算")
    print(f"- 最高限額：{MAX_CONTRACT_FEE:,}元整")
    print(f"- 契約規範：協會盈餘金額，但不得超出{MAX_CONTRACT_FEE:,}元整")


if __name__ == "__main__":
    main()
