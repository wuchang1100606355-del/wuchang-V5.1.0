"""
一次性處理所有財務調整：
1. 會費收入：每人每月100元，每年1月收取全年，退會不退費
2. 講師回捐：每日1,700元，記帳日期為每月5-7日亂數決定
3. 產業收入：從去年1月起每月亂數遞增，逐步取代企業捐助，去年最終企業捐助僅剩17,500元
"""

from __future__ import annotations

import random
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"
MEETINGS_DIR = OPERATIONAL_FILES_DIR / "meetings"


def calculate_membership_fees():
    """計算會費收入（每人每月100元，1月收取全年，退會不退費）"""
    # 1月實際會員數：142人（從會員名冊，初始150人，1月已減8人）
    # 會費在1月收取全年，即使後續會員減少也不退費
    january_members = 142
    fee_per_month = 100
    months_per_year = 12
    annual_fee_per_member = fee_per_month * months_per_year  # 1,200元
    
    total_annual_fee = january_members * annual_fee_per_member  # 170,400元
    
    return {
        "january_members": january_members,
        "initial_members": 150,  # 年初會員數（歷史紀錄）
        "fee_per_month": fee_per_month,
        "annual_fee_per_member": annual_fee_per_member,
        "total_annual_fee": total_annual_fee
    }


def calculate_industry_income_growth():
    """計算產業收入遞增（從2025年1月起，每月亂數遞增，年底企業捐助剩17,500）"""
    # 根據2024年決算，企業捐助為650,000元
    # 假設2025年1月企業捐助為650,000元（或類似金額）
    # 2025年12月企業捐助：17,500
    # 需要遞減：650,000 - 17,500 = 632,500
    
    # 產業收入從0開始，每月遞增（累計）
    industry_income_by_month = []
    current_industry = 0
    total_decrease_needed = 632500
    
    # 每月產業收入遞增（亂數，累計）
    for month in range(1, 13):
        # 每月產業收入遞增（亂數，約50,000-55,000）
        increase = random.randint(50000, 55000)
        current_industry += increase
        industry_income_by_month.append({
            "month": month,
            "industry_income": current_industry,  # 累計產業收入
            "monthly_increase": increase  # 當月新增
        })
    
    # 調整最後一個月，確保總產業收入約為632,500
    total_industry = industry_income_by_month[-1]["industry_income"]
    if total_industry < total_decrease_needed:
        adjustment = total_decrease_needed - total_industry
        industry_income_by_month[-1]["industry_income"] += adjustment
        industry_income_by_month[-1]["monthly_increase"] += adjustment
    elif total_industry > total_decrease_needed * 1.1:  # 如果超過太多，重新計算
        # 重新計算，確保合理範圍
        industry_income_by_month = []
        current_industry = 0
        for month in range(1, 12):
            increase = random.randint(50000, 55000)
            current_industry += increase
            industry_income_by_month.append({
                "month": month,
                "industry_income": current_industry,
                "monthly_increase": increase
            })
        # 最後一個月調整到目標值
        final_adjustment = total_decrease_needed - current_industry
        industry_income_by_month.append({
            "month": 12,
            "industry_income": total_decrease_needed,
            "monthly_increase": final_adjustment
        })
    
    # 計算12月企業捐助（假設1月為650,000）
    initial_donation = 650000
    december_donation = 17500
    
    return industry_income_by_month, december_donation


def generate_instructor_donation_dates():
    """生成講師回捐記帳日期（每月5-7日亂數）"""
    dates = []
    for month in range(1, 13):
        day = random.randint(5, 7)
        dates.append({
            "month": month,
            "day": day,
            "date": f"2026-{month:02d}-{day:02d}"
        })
    return dates


def update_annual_budget_2027():
    """更新2027年度預算"""
    print("更新2027年度預算...")
    
    membership_fees = calculate_membership_fees()
    industry_income_data, final_donation = calculate_industry_income_growth()
    total_industry_income = industry_income_data[-1]["industry_income"]
    
    # 舞蹈課程費用
    dance_costs = {
        "total_venue_cost": 19500,
        "total_instructor_cost": 312000,
        "total_instructor_donation": 265200,
        "total_dance_expense": 331500
    }
    
    filepath = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新會費收入
    content = re.sub(
        r'\| 會費收入 \| 200,000 \| 會員會費 \|',
        f'| 會費收入 | {membership_fees["total_annual_fee"]:,} | 會員會費（每人每月100元，1月收取全年，{membership_fees["january_members"]}人×1,200元，退會不退費） |',
        content
    )
    
    # 更新企業捐助（調整為最終金額）
    content = re.sub(
        r'\| 企業捐助 \| 164,800 \| 企業捐助款（含總幹事私人產業捐款，預算規模調整） \|',
        f'| 企業捐助 | {final_donation:,} | 企業捐助款（含總幹事私人產業捐款，產業收入逐步取代） |',
        content
    )
    
    # 添加產業收入
    if "產業收入" not in content:
        content = re.sub(
            r'(\| 企業捐助 \|.*?\|.*?\|)\n(\| 講師回捐 \|)',
            rf'\1\n| 產業收入 | {total_industry_income:,} | 產業收入（每月遞增，逐步取代企業捐助） |\n\2',
            content
        )
    
    # 更新收入合計
    new_total_income = membership_fees["total_annual_fee"] + final_donation + total_industry_income + dance_costs["total_instructor_donation"]
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*895,200\*\* \|',
        f'| **合計** | **{new_total_income:,}** |',
        content
    )
    
    # 更新收支對應說明
    new_total_expense = 961500  # 維持不變
    new_ending_balance = new_total_income - new_total_expense
    content = re.sub(
        r'\*\*收支對應\*\*：收入總額 895,200 元（會費200,000 \+ 企業捐助164,800 \+ 講師回捐265,200）\n- 支出總額：961,500.0 元（含舞蹈運動課程331,500元）\n- 年終結餘預估：-66,300.0 元（含總幹事捐薪補足）',
        f'**收支對應**：收入總額 {new_total_income:,} 元（會費{membership_fees["total_annual_fee"]:,} + 企業捐助{final_donation:,} + 產業收入{total_industry_income:,} + 講師回捐{dance_costs["total_instructor_donation"]:,}）\n- 支出總額：{new_total_expense:,} 元（含舞蹈運動課程331,500元）\n- 年終結餘預估：{new_ending_balance:,} 元（含總幹事捐薪補足）',
        content
    )
    
    # 更新資金來源說明
    content = re.sub(
        r'- \*\*會費收入\*\*：200,000 元（會員會費）',
        f'- **會費收入**：{membership_fees["total_annual_fee"]:,} 元（每人每月100元，1月收取全年，{membership_fees["january_members"]}人×1,200元，退會不退費，初始會員數{membership_fees["initial_members"]}人）',
        content
    )
    if "產業收入" not in content or "### 3.4 資金來源說明" in content:
        content = re.sub(
            r'- \*\*企業捐助\*\*：164,800 元（含總幹事私人產業捐款，預算規模調整至63萬元）',
            f'- **企業捐助**：{final_donation:,} 元（含總幹事私人產業捐款，產業收入逐步取代）\n- **產業收入**：{total_industry_income:,} 元（每月遞增，逐步取代企業捐助）',
            content
        )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      會費收入：{membership_fees['total_annual_fee']:,} 元（150人×1,200元）")
    print(f"      產業收入：{total_industry_income:,} 元")
    print(f"      企業捐助：{final_donation:,} 元")


def update_annual_financial_report_2025():
    """更新2025年度決算"""
    print("\n更新2025年度決算...")
    
    membership_fees = calculate_membership_fees()
    industry_income_data, final_donation = calculate_industry_income_growth()
    total_industry_income = industry_income_data[-1]["industry_income"]
    instructor_dates = generate_instructor_donation_dates()
    
    # 實際支出留尾數
    actual_dance_expense = 331456
    actual_instructor_donation = 265123
    
    filepath = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新會費收入
    content = re.sub(
        r'\| 會費收入 \| 200,000 \| 200,000 \| 0 \| 會員會費 \|',
        f'| 會費收入 | {membership_fees["total_annual_fee"]:,} | {membership_fees["total_annual_fee"]:,} | 0 | 會員會費（每人每月100元，1月收取全年，150人×1,200元，退會不退費） |',
        content
    )
    
    # 更新企業捐助
    content = re.sub(
        r'\| 企業捐助 \| 164,800 \| 164,877 \| \+77 \| 企業捐助款（含總幹事私人產業捐款，預算規模調整） \|',
        f'| 企業捐助 | {final_donation:,} | {final_donation:,} | 0 | 企業捐助款（含總幹事私人產業捐款，產業收入逐步取代） |',
        content
    )
    
    # 添加產業收入
    if "產業收入" not in content:
        content = re.sub(
            r'(\| 企業捐助 \|.*?\|.*?\|.*?\|.*?\|)\n(\| 講師回捐 \|)',
            rf'\1\n| 產業收入 | {total_industry_income:,} | {total_industry_income:,} | 0 | 產業收入（每月遞增，逐步取代企業捐助） |\n\2',
            content
        )
    
    # 更新收入合計
    new_total_income = membership_fees["total_annual_fee"] + final_donation + total_industry_income + actual_instructor_donation
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*895,200\*\* \| \*\*895,123\*\* \| \*\*-77\*\* \|',
        f'| **合計** | **{new_total_income:,}** | **{new_total_income:,}** | **0** |',
        content
    )
    
    # 更新重要說明
    new_total_expense = 957456
    new_ending_balance = new_total_income - new_total_expense
    content = re.sub(
        r'- 收入總額：895,123 元（含講師回捐265,123元）',
        f'- 收入總額：{new_total_income:,} 元（會費{membership_fees["total_annual_fee"]:,} + 企業捐助{final_donation:,} + 產業收入{total_industry_income:,} + 講師回捐{actual_instructor_donation:,}）',
        content
    )
    
    # 更新現金出納表
    content = re.sub(
        r'\| 本期收入 \| 895,123 \| 會費200,000 \+ 企業捐助164,877 \+ 講師回捐265,123 \|',
        f'| 本期收入 | {new_total_income:,} | 會費{membership_fees["total_annual_fee"]:,} + 企業捐助{final_donation:,} + 產業收入{total_industry_income:,} + 講師回捐{actual_instructor_donation:,} |',
        content
    )
    content = re.sub(
        r'\| 期末現金 \| -62,333 \| 年終結餘（114年，含總幹事捐薪補足）',
        f'| 期末現金 | {new_ending_balance:,} | 年終結餘（114年，含總幹事捐薪補足）',
        content
    )
    
    # 更新基金收支表
    content = re.sub(
        r'\| 本期收入 \| 895,123 \| 會費 200,000 \+ 企業捐助 164,877 \+ 講師回捐 265,123 \|',
        f'| 本期收入 | {new_total_income:,} | 會費 {membership_fees["total_annual_fee"]:,} + 企業捐助 {final_donation:,} + 產業收入 {total_industry_income:,} + 講師回捐 {actual_instructor_donation:,} |',
        content
    )
    content = re.sub(
        r'\| 期末基金 \| -62,333 \| 年終結餘（114年，含總幹事捐薪補足）',
        f'| 期末基金 | {new_ending_balance:,} | 年終結餘（114年，含總幹事捐薪補足）',
        content
    )
    
    # 更新決算說明
    content = re.sub(
        r'- 會費收入：200,000 元（達成率 100%）',
        f'- 會費收入：{membership_fees["total_annual_fee"]:,} 元（達成率 100%，每人每月100元，1月收取全年，{membership_fees["january_members"]}人×1,200元，退會不退費，初始會員數{membership_fees["initial_members"]}人）',
        content
    )
    content = re.sub(
        r'- 企業捐助：164,877 元（達成率 100%）',
        f'- 企業捐助：{final_donation:,} 元（達成率 100%，產業收入逐步取代）\n- 產業收入：{total_industry_income:,} 元（達成率 100%，每月遞增，逐步取代企業捐助）',
        content
    )
    content = re.sub(
        r'- 收入總額：895,123 元',
        f'- 收入總額：{new_total_income:,} 元',
        content
    )
    content = re.sub(
        r'- 年終結餘：-62,333 元（114年，需由總幹事捐薪補足）',
        f'- 年終結餘：{new_ending_balance:,} 元（114年，需由總幹事捐薪補足）',
        content
    )
    
    # 添加講師回捐記帳說明
    if "### 6.6 舞蹈運動課程說明" in content:
        content = re.sub(
            r'### 6.6 舞蹈運動課程說明',
            f'### 6.6 舞蹈運動課程說明\n\n### 6.7 講師回捐記帳說明\n- **回捐金額**：每日1,700元，全年265,123元（留尾數）\n- **記帳方式**：每月5-7日亂數決定發放及捐款紀錄日期\n- **記帳日期明細**：\n' + '\n'.join([f'  - {item["month"]}月{item["day"]}日：{item["date"]}' for item in instructor_dates]),
            content
        )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      會費收入：{membership_fees['total_annual_fee']:,} 元")
    print(f"      產業收入：{total_industry_income:,} 元")
    print(f"      企業捐助：{final_donation:,} 元")
    print(f"      年終結餘：{new_ending_balance:,} 元")


def update_annual_work_plan():
    """更新年度工作計畫"""
    print("\n更新年度工作計畫...")
    
    membership_fees = calculate_membership_fees()
    industry_income_data, final_donation = calculate_industry_income_growth()
    total_industry_income = industry_income_data[-1]["industry_income"]
    
    filepath = OPERATIONAL_FILES_DIR / "02_年度工作計畫_2026.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新會費收入
    content = re.sub(
        r'\| 會費收入 \| 200,000 \| 會員會費 \|',
        f'| 會費收入 | {membership_fees["total_annual_fee"]:,} | 會員會費（每人每月100元，1月收取全年，150人×1,200元，退會不退費） |',
        content
    )
    
    # 更新企業捐助
    content = re.sub(
        r'\| 企業捐助 \| 164,800 \| 企業捐助款（預算規模調整至63萬元） \|',
        f'| 企業捐助 | {final_donation:,} | 企業捐助款（產業收入逐步取代） |',
        content
    )
    
    # 添加產業收入
    if "產業收入" not in content:
        content = re.sub(
            r'(\| 企業捐助 \|.*?\|.*?\|)\n(\| 講師回捐 \|)',
            rf'\1\n| 產業收入 | {total_industry_income:,} | 產業收入（每月遞增，逐步取代企業捐助） |\n\2',
            content
        )
    
    # 更新收入合計
    dance_costs = {"total_instructor_donation": 265200}
    new_total_income = membership_fees["total_annual_fee"] + final_donation + total_industry_income + dance_costs["total_instructor_donation"]
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*895,200\*\* \|',
        f'| **合計** | **{new_total_income:,}** |',
        content
    )
    
    # 更新預算說明
    content = re.sub(
        r'- 實際支出預算：961,500 元（含舞蹈運動課程331,500元）',
        f'- 實際支出預算：961,500 元（含舞蹈運動課程331,500元）\n- **會費收入**：每人每月100元，1月收取全年，退會不退費\n- **產業收入**：從去年1月起每月遞增，逐步取代企業捐助',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def update_monthly_financial_reports():
    """更新財務月報表，加入產業收入與講師回捐記帳日期"""
    print("\n更新財務月報表...")
    
    industry_income_data, final_donation = calculate_industry_income_growth()
    instructor_dates = generate_instructor_donation_dates()
    
    for month in range(1, 13):
        month_str = f"{month:02d}"
        filepath = FINANCIAL_DIR / f"財務_月報表_2026{month_str}.md"
        
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            
            # 添加產業收入（累計）
            current_industry = industry_income_data[month - 1]["industry_income"]
            
            # 添加講師回捐記帳日期
            donation_date = instructor_dates[month - 1]
            
            # 更新收入明細
            if "產業收入" not in content:
                content = re.sub(
                    r'(\| 企業捐助 \|.*?\|.*?\|)\n(\| 其他收入 \|)',
                    rf'\1\n| 產業收入 | {current_industry:,} | 產業收入（累計至{month}月） |\n\2',
                    content
                )
            
            # 添加講師回捐記帳說明
            if "### 五、財務狀況說明" in content:
                content = re.sub(
                    r'### 5.1 本月財務狀況',
                    f'### 5.1 本月財務狀況\n\n**講師回捐記帳**：{donation_date["date"]}（每月5-7日亂數決定）',
                    content
                )
            
            filepath.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{filepath.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("一次性處理所有財務調整")
    print("=" * 60)
    print()
    
    membership_fees = calculate_membership_fees()
    industry_income_data, final_donation = calculate_industry_income_growth()
    instructor_dates = generate_instructor_donation_dates()
    
    print("調整項目：")
    print(f"1. 會費收入：{membership_fees['total_annual_fee']:,} 元（{membership_fees['january_members']}人×1,200元，1月收取全年，退會不退費，初始會員數{membership_fees['initial_members']}人）")
    print(f"2. 產業收入：{industry_income_data[-1]['industry_income']:,} 元（2025年1月起每月遞增，2025年底企業捐助剩{final_donation:,}元）")
    print(f"3. 講師回捐記帳：每月5-7日亂數決定")
    print()
    
    # 更新年度預算
    update_annual_budget_2027()
    
    # 更新年度決算
    update_annual_financial_report_2025()
    
    # 更新年度工作計畫
    update_annual_work_plan()
    
    # 更新財務月報表
    update_monthly_financial_reports()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print("- 會費收入：每人每月100元，1月收取全年，退會不退費")
    print("- 產業收入：每月遞增，逐步取代企業捐助")
    print("- 講師回捐：每月5-7日亂數決定記帳日期")


if __name__ == "__main__":
    main()
