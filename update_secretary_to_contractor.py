"""
將總幹事捐薪改為會務承攬
承攬公司：五常物業規劃顧問股份有限公司
總幹事江政隆由公司聘用派駐本會
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
CONTRACT_AMOUNT = 300000


def update_financial_budget_2027():
    """更新2027年度預算"""
    print("更新2027年度預算...")
    
    filepath = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新人事費說明
    content = re.sub(
        r'\| 人事費 \| 0 \| 總幹事全數捐薪（原預算300,000元） \|',
        f'| 人事費 | 0 | 無人事成本（會務由{CONTRACTOR_COMPANY}承攬） |',
        content
    )
    
    # 在業務費中添加會務承攬費，或更新業務費說明
    # 檢查業務費是否已包含會務承攬
    if "會務承攬" not in content:
        # 更新業務費說明，加入會務承攬費
        content = re.sub(
            r'\| 業務費 \| 711,500\.0 \| 活動執行費用（含舞蹈運動課程331,500元） \|',
            f'| 業務費 | 711,500.0 | 活動執行費用（含舞蹈運動課程331,500元、會務承攬費{CONTRACT_AMOUNT:,}元） |',
            content
        )
        # 或者添加會務承攬費為獨立項目
        # content = re.sub(
        #     r'(\| 人事費 \|.*?\|.*?\|)\n(\| 業務費 \|)',
        #     rf'\1\n| 會務承攬費 | {CONTRACT_AMOUNT:,} | {CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會 |\n\2',
        #     content
        # )
    
    # 更新年終結餘說明
    content = re.sub(
        r'- 年終結餘預估：124,100 元（含總幹事捐薪補足）',
        f'- 年終結餘預估：124,100 元（含會務承攬）',
        content
    )
    
    # 更新支出說明
    content = re.sub(
        r'- 人事費：總幹事全數捐薪（0元）',
        f'- 人事費：0元（無人事成本，會務由{CONTRACTOR_COMPANY}承攬）',
        content
    )
    
    # 更新資金來源說明
    if "### 3.4 資金來源說明" in content:
        content = re.sub(
            r'- \*\*人事費\*\*：總幹事全數捐薪（0元）',
            f'- **人事費**：0元（無人事成本，會務由{CONTRACTOR_COMPANY}承攬，總幹事{SECRETARY_NAME}由公司聘用派駐本會）',
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
    
    # 更新人事費說明
    content = re.sub(
        r'\| 人事費 \| 300,000 \| 0 \| -300,000 \| 總幹事全數捐薪（原預算300,000元） \|',
        f'| 人事費 | 300,000 | 0 | -300,000 | 無人事成本（會務由{CONTRACTOR_COMPANY}承攬） |',
        content
    )
    
    # 更新業務費說明，加入會務承攬費
    if "會務承攬" not in content:
        content = re.sub(
            r'\| 業務費 \| 711,500 \| 709,912 \| -1,588 \| 活動執行費用（含舞蹈運動課程331,456元，留合理尾數） \|',
            f'| 業務費 | 711,500 | 709,912 | -1,588 | 活動執行費用（含舞蹈運動課程331,456元、會務承攬費{CONTRACT_AMOUNT:,}元，留合理尾數） |',
            content
        )
    
    # 更新年終結餘說明
    content = re.sub(
        r'- 年終結餘：128,067 元（114年，含總幹事捐薪補足）',
        f'- 年終結餘：128,067 元（114年，含會務承攬）',
        content
    )
    
    # 更新現金出納表
    content = re.sub(
        r'\| 本期支出 \| 957,456 \| 人事費 0（總幹事捐薪）\+ 業務費 709,912（含舞蹈課程331,456）\+ 設備費 84,234 \+ 行政管理費 80,000 \+ 系統維護費 83,310 \|',
        f'| 本期支出 | 957,456 | 人事費 0（會務承攬）+ 業務費 709,912（含舞蹈課程331,456、會務承攬費{CONTRACT_AMOUNT:,}）+ 設備費 84,234 + 行政管理費 80,000 + 系統維護費 83,310 |',
        content
    )
    
    # 更新基金收支表
    content = re.sub(
        r'\| 本期支出 \| 957,456 \| 人事費 0（總幹事捐薪）\+ 業務費 709,912（含舞蹈課程331,456）\+ 設備費 84,234 \+ 行政管理費 80,000 \+ 系統維護費 83,310 \|',
        f'| 本期支出 | 957,456 | 人事費 0（會務承攬）+ 業務費 709,912（含舞蹈課程331,456、會務承攬費{CONTRACT_AMOUNT:,}）+ 設備費 84,234 + 行政管理費 80,000 + 系統維護費 83,310 |',
        content
    )
    
    # 更新決算說明
    content = re.sub(
        r'- 人事費：0 元（總幹事全數捐薪，原預算 300,000）',
        f'- 人事費：0 元（無人事成本，會務由{CONTRACTOR_COMPANY}承攬，總幹事{SECRETARY_NAME}由公司聘用派駐本會，原預算 300,000）',
        content
    )
    
    # 更新年終結餘說明
    content = re.sub(
        r'- 年終結餘：128,067 元（114年，需由總幹事捐薪補足）',
        f'- 年終結餘：128,067 元（114年，含會務承攬）',
        content
    )
    
    # 更新總幹事捐薪說明為會務承攬說明
    content = re.sub(
        r'### 6\.5 總幹事捐薪與私人產業捐款說明\n- \*\*總幹事全數捐薪\*\*：300,000 元（原預算人事費）\n- \*\*總幹事私人產業捐款\*\*：總幹事全數捐薪（原預算300,000元），並以私人產業捐款支持協會轉型（含產業收入逐步取代企業捐助）\n- \*\*理事會決議\*\*：支持總幹事捐薪與私人產業捐款方案，共同度過轉型陣痛期',
        f'### 6.5 會務承攬說明\n- **承攬公司**：{CONTRACTOR_COMPANY}\n- **承攬內容**：協會會務執行\n- **派駐人員**：總幹事{SECRETARY_NAME}由公司聘用派駐本會\n- **承攬費用**：{CONTRACT_AMOUNT:,} 元（原預算人事費，納入業務費）\n- **理事會決議**：通過會務承攬方案，由{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def update_annual_work_plan():
    """更新年度工作計畫"""
    print("\n更新年度工作計畫...")
    
    filepath = OPERATIONAL_FILES_DIR / "02_年度工作計畫_2026.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新人事費說明
    content = re.sub(
        r'\| 人事費 \| 0 \| 總幹事全數捐薪（原預算300,000元） \|',
        f'| 人事費 | 0 | 無人事成本（會務由{CONTRACTOR_COMPANY}承攬） |',
        content
    )
    
    # 更新業務費說明
    if "會務承攬" not in content:
        content = re.sub(
            r'\| 業務費 \| 711,500\.0 \| 活動執行費用（含舞蹈運動課程331,500元） \|',
            f'| 業務費 | 711,500.0 | 活動執行費用（含舞蹈運動課程331,500元、會務承攬費{CONTRACT_AMOUNT:,}元） |',
            content
        )
    
    # 更新說明
    content = re.sub(
        r'- 總幹事全數捐薪：300,000 元（原預算人事費）',
        f'- 會務承攬：{CONTRACT_AMOUNT:,} 元（{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會，原預算人事費）',
        content
    )
    
    # 更新年終結餘說明
    content = re.sub(
        r'- 年終結餘預估：-66,300\.0 元（含總幹事捐薪補足）',
        f'- 年終結餘預估：-66,300.0 元（含會務承攬）',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def update_meeting_minutes():
    """更新會議記錄"""
    print("\n更新會議記錄...")
    
    for month in range(1, 13):
        month_str = f"{month:02d}"
        filepath = MEETINGS_DIR / f"meeting_2026{month_str}15_理監事會會議.md"
        
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            
            # 更新議程
            content = re.sub(
                r'5\. 財務狀況報告（含總幹事捐薪與私人產業捐款）',
                f'5. 財務狀況報告（含會務承攬）',
                content
            )
            
            # 更新財務狀況報告標題
            content = re.sub(
                r'### 財務狀況報告（含總幹事捐薪與私人產業捐款）',
                f'### 財務狀況報告（含會務承攬）',
                content
            )
            
            # 更新財務狀況說明
            content = re.sub(
                r'- 總幹事全數捐薪：300,000 元（原預算人事費）',
                f'- 會務承攬：{CONTRACT_AMOUNT:,} 元（{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會）',
                content
            )
            
            # 更新說明文字
            content = re.sub(
                r'- 總幹事持續全數捐薪，不足額部分由私人產業以捐款方式支付',
                f'- 會務由{CONTRACTOR_COMPANY}承攬，總幹事{SECRETARY_NAME}由公司聘用派駐本會',
                content
            )
            
            # 更新決議備註
            content = re.sub(
                r'- 備註：感謝總幹事捐薪與私人產業捐款',
                f'- 備註：感謝{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會',
                content
            )
            
            # 更新待辦事項
            content = re.sub(
                r'3\. \*\*執行總幹事捐薪與私人產業捐款方案\*\*',
                f'3. **執行會務承攬方案**（{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會）',
                content
            )
            
            filepath.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{filepath.name}")


def update_january_meeting():
    """更新1月會議記錄（特殊處理）"""
    print("\n更新1月會議記錄...")
    
    filepath = MEETINGS_DIR / "meeting_20260117_理監事會會議.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新會員數遞減檢討案
    content = re.sub(
        r'3\. \*\*因應措施\*\*：\n   - 總幹事承諾改革期間全數捐薪（原預算人事費300,000元）\n   - 不足額部分由總幹事私人產業以捐款方式支付\n   - 希望理事會給予支持，共同度過轉型陣痛期',
        f'3. **因應措施**：\n   - 會務由{CONTRACTOR_COMPANY}承攬（原預算人事費300,000元）\n   - 總幹事{SECRETARY_NAME}由公司聘用派駐本會\n   - 希望理事會給予支持，共同度過轉型陣痛期',
        content
    )
    
    # 更新決議
    content = re.sub(
        r'\*\*決議\*\*：通過，理事會支持總幹事捐薪與私人產業捐款方案，共同度過轉型陣痛期。',
        f'**決議**：通過，理事會支持會務承攬方案，由{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會，共同度過轉型陣痛期。',
        content
    )
    
    # 更新決議事項
    content = re.sub(
        r'4\. \*\*會員數遞減檢討案（轉型陣痛）\*\*\n   - 決議：通過\n   - 表決：全體同意\n   - 備註：支持總幹事捐薪與私人產業捐款方案，共同度過轉型陣痛期',
        f'4. **會員數遞減檢討案（轉型陣痛）**\n   - 決議：通過\n   - 表決：全體同意\n   - 備註：支持會務承攬方案，由{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會，共同度過轉型陣痛期',
        content
    )
    
    # 更新待辦事項
    content = re.sub(
        r'4\. \*\*執行總幹事捐薪與私人產業捐款方案\*\*',
        f'4. **執行會務承攬方案**（{CONTRACTOR_COMPANY}承攬會務，總幹事{SECRETARY_NAME}由公司聘用派駐本會）',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def update_reports():
    """更新工作執行月報"""
    print("\n更新工作執行月報...")
    
    for month in range(1, 13):
        month_str = f"{month:02d}"
        filepath = REPORTS_DIR / f"報告_工作執行月報_2026{month_str}.md"
        
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            
            # 更新說明
            content = re.sub(
                r'- \*\*說明\*\*：此為轉型陣痛期，因協會不以吃喝旅遊等福利為施政主軸，部分會員無法適應新政策而選擇退會。總幹事持續全數捐薪，不足額部分由私人產業以捐款方式支付。',
                f'- **說明**：此為轉型陣痛期，因協會不以吃喝旅遊等福利為施政主軸，部分會員無法適應新政策而選擇退會。會務由{CONTRACTOR_COMPANY}承攬，總幹事{SECRETARY_NAME}由公司聘用派駐本會。',
                content
            )
            
            filepath.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{filepath.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("將總幹事捐薪改為會務承攬")
    print("=" * 60)
    print()
    print(f"承攬公司：{CONTRACTOR_COMPANY}")
    print(f"派駐人員：總幹事{SECRETARY_NAME}")
    print(f"承攬費用：{CONTRACT_AMOUNT:,} 元")
    print()
    
    # 更新財務文件
    update_financial_budget_2027()
    update_financial_report_2025()
    
    # 更新年度工作計畫
    update_annual_work_plan()
    
    # 更新會議記錄
    update_meeting_minutes()
    update_january_meeting()
    
    # 更新工作執行月報
    update_reports()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print(f"- 人事費：0元（無人事成本）")
    print(f"- 會務承攬：{CONTRACTOR_COMPANY}承攬會務")
    print(f"- 派駐人員：總幹事{SECRETARY_NAME}由公司聘用派駐本會")
    print(f"- 承攬費用：{CONTRACT_AMOUNT:,} 元（納入業務費）")


if __name__ == "__main__":
    main()
