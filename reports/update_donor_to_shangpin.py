"""
將不足部分企業捐贈改為上品食品行（統一編號：34778660）捐贈
"""

from __future__ import annotations

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"
MEETINGS_DIR = OPERATIONAL_FILES_DIR / "meetings"

DONOR_NAME = "上品食品行"
DONOR_TAX_ID = "34778660"
DONOR_FULL = f"{DONOR_NAME}（統一編號：{DONOR_TAX_ID}）"


def update_financial_budget_2027():
    """更新2027年度預算"""
    print("更新2027年度預算...")
    
    filepath = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新企業捐助說明
    content = re.sub(
        r'\| 企業捐助 \| 17,500 \| 企業捐助款（含總幹事私人產業捐款，產業收入逐步取代） \|',
        f'| 企業捐助 | 17,500 | 企業捐助款（產業收入逐步取代） |',
        content
    )
    
    # 更新年終結餘說明
    content = re.sub(
        r'- 年終結餘預估：-175,900 元（需由總幹事私人產業捐款補足）',
        f'- 年終結餘預估：-175,900 元（需由{DONOR_FULL}捐贈補足）',
        content
    )
    
    # 更新資金來源說明
    content = re.sub(
        r'- \*\*企業捐助\*\*：17,500 元（含總幹事私人產業捐款，產業收入逐步取代）',
        f'- **企業捐助**：17,500 元（產業收入逐步取代）\n- **不足額補助**：由{DONOR_FULL}捐贈補足',
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
    
    # 更新企業捐助說明
    content = re.sub(
        r'\| 企業捐助 \| 17,500 \| 17,500 \| 0 \| 企業捐助款（含總幹事私人產業捐款，產業收入逐步取代） \|',
        f'| 企業捐助 | 17,500 | 17,500 | 0 | 企業捐助款（產業收入逐步取代） |',
        content
    )
    
    # 添加不足額補助收入項目
    if "不足額補助" not in content or "上品食品行" not in content:
        content = re.sub(
            r'(\| 企業捐助 \|.*?\|.*?\|.*?\|.*?\|)\n(\| 產業收入 \|)',
            rf'\1\n| 不足額補助 | 171,933 | 171,933 | 0 | {DONOR_FULL}捐贈（補足年終結餘不足額） |\n\2',
            content
        )
    
    # 更新收入合計
    new_total_income = 1085523 + 171933  # 原收入 + 不足額補助
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*1,085,523\*\* \| \*\*1,085,523\*\* \| \*\*0\*\* \|',
        f'| **合計** | **{new_total_income:,}** | **{new_total_income:,}** | **0** |',
        content
    )
    
    # 更新重要說明
    content = re.sub(
        r'- 收入總額：1,085,523 元（會費170,400 \+ 企業捐助17,500 \+ 產業收入632,500 \+ 講師回捐265,123）',
        f'- 收入總額：{new_total_income:,} 元（會費170,400 + 企業捐助17,500 + 產業收入632,500 + 講師回捐265,123 + 不足額補助171,933）',
        content
    )
    
    # 更新年終結餘說明
    new_ending_balance = new_total_income - 1257456  # 收入 - 支出
    content = re.sub(
        r'- 年終結餘：-171,933 元（114年，需由總幹事私人產業捐款補足）',
        f'- 年終結餘：{new_ending_balance:,} 元（114年，不足額由{DONOR_FULL}捐贈補足）',
        content
    )
    
    # 更新現金出納表
    content = re.sub(
        r'\| 本期收入 \| 1,085,523 \| 會費170,400 \+ 企業捐助17,500 \+ 產業收入632,500 \+ 講師回捐265,123 \|',
        f'| 本期收入 | {new_total_income:,} | 會費170,400 + 企業捐助17,500 + 產業收入632,500 + 講師回捐265,123 + 不足額補助171,933（{DONOR_FULL}捐贈） |',
        content
    )
    content = re.sub(
        r'\| 期末現金 \| -171,933 \| 年終結餘（114年，需由總幹事私人產業捐款補足） \|',
        f'| 期末現金 | {new_ending_balance:,} | 年終結餘（114年，不足額由{DONOR_FULL}捐贈補足） |',
        content
    )
    
    # 更新基金收支表
    content = re.sub(
        r'\| 本期收入 \| 1,085,523 \| 會費 170,400 \+ 企業捐助 17,500 \+ 產業收入 632,500 \+ 講師回捐 265,123 \|',
        f'| 本期收入 | {new_total_income:,} | 會費 170,400 + 企業捐助 17,500 + 產業收入 632,500 + 講師回捐 265,123 + 不足額補助 171,933（{DONOR_FULL}捐贈） |',
        content
    )
    content = re.sub(
        r'\| 期末基金 \| -171,933 \| 年終結餘（114年，需由總幹事私人產業捐款補足） \|',
        f'| 期末基金 | {new_ending_balance:,} | 年終結餘（114年，不足額由{DONOR_FULL}捐贈補足） |',
        content
    )
    
    # 更新決算說明
    content = re.sub(
        r'- 收入總額：1,085,523 元',
        f'- 收入總額：{new_total_income:,} 元（含不足額補助171,933元，由{DONOR_FULL}捐贈）',
        content
    )
    content = re.sub(
        r'- 年終結餘：-171,933 元（114年，需由總幹事私人產業捐款補足）',
        f'- 年終結餘：{new_ending_balance:,} 元（114年，不足額由{DONOR_FULL}捐贈補足）',
        content
    )
    
    # 更新資金來源說明
    content = re.sub(
        r'- \*\*企業捐助\*\*：17,500 元（含總幹事私人產業捐款，產業收入逐步取代）',
        f'- **企業捐助**：17,500 元（產業收入逐步取代）\n- **不足額補助**：171,933 元（由{DONOR_FULL}捐贈，補足年終結餘不足額）',
        content
    )
    
    # 更新會務承攬說明
    if "### 6.5 會務承攬說明" in content:
        content = re.sub(
            r'### 6\.5 會務承攬說明',
            f'### 6.5 會務承攬說明\n\n### 6.6 不足額補助說明\n- **補助來源**：{DONOR_FULL}捐贈\n- **補助金額**：171,933 元（補足年終結餘不足額）\n- **補助用途**：用於補足年度收支差額\n- **理事會決議**：通過，感謝{DONOR_FULL}捐贈補足不足額部分',
            content
        )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      不足額補助：171,933 元（由{DONOR_FULL}捐贈）")
    print(f"      年終結餘：{new_ending_balance:,} 元")


def update_annual_work_plan():
    """更新年度工作計畫"""
    print("\n更新年度工作計畫...")
    
    filepath = OPERATIONAL_FILES_DIR / "02_年度工作計畫_2026.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新說明
    content = re.sub(
        r'- 總幹事私人產業捐款：用於補足不足額部分',
        f'- 不足額補助：由{DONOR_FULL}捐贈補足不足額部分',
        content
    )
    
    # 更新年終結餘說明
    content = re.sub(
        r'- 年終結餘預估：-175,900\.0 元（需由總幹事私人產業捐款補足）',
        f'- 年終結餘預估：-175,900.0 元（需由{DONOR_FULL}捐贈補足）',
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
                r'- 總幹事私人產業捐款：補足不足額部分',
                f'- 不足額補助：由{DONOR_FULL}捐贈補足不足額部分',
                content
            )
            
            filepath.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{filepath.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("將不足部分企業捐贈改為上品食品行捐贈")
    print("=" * 60)
    print()
    print(f"捐贈單位：{DONOR_FULL}")
    print(f"補助用途：補足年終結餘不足額")
    print()
    
    # 更新財務文件
    update_financial_budget_2027()
    update_financial_report_2025()
    
    # 更新年度工作計畫
    update_annual_work_plan()
    
    # 更新會議記錄
    update_meeting_minutes()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print(f"- 不足額補助：由{DONOR_FULL}捐贈")
    print(f"- 補助用途：補足年終結餘不足額")
    print(f"- 2025年補助金額：171,933 元")


if __name__ == "__main__":
    main()
