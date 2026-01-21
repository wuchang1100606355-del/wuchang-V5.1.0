"""
新增舞蹈社費用項目：
- 場地費用：全年每週3日，每日2小時，每小時62.5元
- 講師費用：每日2000元
- 講師回捐捐款收入：每日1700元
"""

from __future__ import annotations

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"


def calculate_dance_class_costs():
    """計算舞蹈社費用"""
    # 全年約52週，每週3日
    days_per_year = 52 * 3  # 156天
    
    # 場地費用：每天2小時，每小時62.5元
    venue_cost_per_day = 2 * 62.5  # 125元
    total_venue_cost = days_per_year * venue_cost_per_day  # 19,500元
    
    # 講師費用：每天2000元
    instructor_cost_per_day = 2000
    total_instructor_cost = days_per_year * instructor_cost_per_day  # 312,000元
    
    # 講師回捐：每天1700元
    instructor_donation_per_day = 1700
    total_instructor_donation = days_per_year * instructor_donation_per_day  # 265,200元
    
    # 舞蹈運動課程總支出
    total_dance_expense = total_venue_cost + total_instructor_cost  # 331,500元
    
    return {
        "days_per_year": days_per_year,
        "venue_cost_per_day": venue_cost_per_day,
        "total_venue_cost": total_venue_cost,
        "instructor_cost_per_day": instructor_cost_per_day,
        "total_instructor_cost": total_instructor_cost,
        "instructor_donation_per_day": instructor_donation_per_day,
        "total_instructor_donation": total_instructor_donation,
        "total_dance_expense": total_dance_expense
    }


def update_annual_budget_2027():
    """更新2027年度預算，加入舞蹈社費用"""
    print("更新2027年度預算，加入舞蹈社費用...")
    
    dance_costs = calculate_dance_class_costs()
    
    filepath = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新收入預算，加入講師回捐
    # 原收入：會費200,000 + 企業捐助430,000 = 630,000
    # 新增講師回捐：265,200
    # 新收入總額：895,200
    new_total_income = 630000 + dance_costs["total_instructor_donation"]
    
    # 更新企業捐助（調整後）
    new_donation = 430000 - dance_costs["total_instructor_donation"]  # 164,800
    
    content = re.sub(
        r'\| 企業捐助 \| 430,000 \| 企業捐助款（含總幹事私人產業捐款，預算規模調整） \|',
        f'| 企業捐助 | {new_donation:,} | 企業捐助款（含總幹事私人產業捐款，預算規模調整） |',
        content
    )
    
    # 添加講師回捐收入
    if "講師回捐" not in content:
        content = re.sub(
            r'(\| 企業捐助 \|.*?\|.*?\|)\n(\| 其他收入 \|)',
            rf'\1\n| 講師回捐 | {dance_costs["total_instructor_donation"]:,} | 舞蹈社講師回捐（每日1,700元 × {dance_costs["days_per_year"]}日） |\n\2',
            content
        )
    
    # 更新收入合計
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*630,000\*\* \|',
        f'| **合計** | **{new_total_income:,}** |',
        content
    )
    
    # 更新支出預算，加入舞蹈運動課程
    # 原業務費：380,000
    # 新增舞蹈課程支出：331,500
    # 新業務費：711,500
    new_business_expense = 380000 + dance_costs["total_dance_expense"]
    
    content = re.sub(
        r'\| 業務費 \| 380,000 \| 活動執行費用 \|',
        f'| 業務費 | {new_business_expense:,} | 活動執行費用（含舞蹈運動課程331,500元） |',
        content
    )
    
    # 更新支出合計
    new_total_expense = 630000 + dance_costs["total_dance_expense"]  # 961,500
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*630,000\*\* \|',
        f'| **合計** | **{new_total_expense:,}** |',
        content
    )
    
    # 更新收支對應說明
    new_ending_balance = new_total_income - new_total_expense  # -66,300（需由總幹事捐薪補足）
    content = re.sub(
        r'\*\*收支對應\*\*：收入總額 630,000 元（會費200,000 \+ 企業捐助430,000）\n- 支出總額：630,000 元（總幹事捐薪，實際支出減少）\n- 年終結餘預估：0 元（含總幹事捐薪，預算規模調整至63萬元）',
        f'**收支對應**：收入總額 {new_total_income:,} 元（會費200,000 + 企業捐助{new_donation:,} + 講師回捐{dance_costs["total_instructor_donation"]:,}）\n- 支出總額：{new_total_expense:,} 元（含舞蹈運動課程331,500元）\n- 年終結餘預估：{new_ending_balance:,} 元（含總幹事捐薪補足）\n- **舞蹈運動課程**：場地費{dance_costs["total_venue_cost"]:,}元 + 講師費{dance_costs["total_instructor_cost"]:,}元 = {dance_costs["total_dance_expense"]:,}元',
        content
    )
    
    # 更新預算說明
    if "### 3.2 重點項目" in content:
        content = re.sub(
            r'- 業務費：各項活動執行費用（380,000元）',
            f'- 業務費：各項活動執行費用（{new_business_expense:,}元，含舞蹈運動課程331,500元）\n  - 舞蹈運動課程：場地費{dance_costs["total_venue_cost"]:,}元（每週3日×52週×2小時×62.5元/小時）+ 講師費{dance_costs["total_instructor_cost"]:,}元（每週3日×52週×2,000元/日）',
            content
        )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      收入總額：{new_total_income:,} 元（含講師回捐{dance_costs["total_instructor_donation"]:,}元）")
    print(f"      支出總額：{new_total_expense:,} 元（含舞蹈課程{dance_costs["total_dance_expense"]:,}元）")


def update_annual_financial_report_2025():
    """更新2025年度決算，加入舞蹈社費用（留合理尾數）"""
    print("\n更新2025年度決算，加入舞蹈社費用...")
    
    dance_costs = calculate_dance_class_costs()
    
    # 實際支出留尾數
    actual_dance_expense = 331456  # 留尾數456
    actual_venue_cost = 19456     # 留尾數456
    actual_instructor_cost = 312000  # 整數
    actual_instructor_donation = 265123  # 留尾數123
    
    filepath = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新收入決算，加入講師回捐
    new_total_income = 630000 + actual_instructor_donation  # 895,123
    
    # 調整企業捐助
    new_donation = 430000 - actual_instructor_donation  # 164,877
    
    content = re.sub(
        r'\| 企業捐助 \| 430,000 \| 430,000 \| 0 \| 企業捐助款（含總幹事私人產業捐款，預算規模調整） \|',
        f'| 企業捐助 | {new_donation:,} | {new_donation:,} | 0 | 企業捐助款（含總幹事私人產業捐款，預算規模調整） |',
        content
    )
    
    # 添加講師回捐收入
    if "講師回捐" not in content:
        content = re.sub(
            r'(\| 企業捐助 \|.*?\|.*?\|.*?\|.*?\|)\n(\| 其他收入 \|)',
            rf'\1\n| 講師回捐 | {actual_instructor_donation:,} | {actual_instructor_donation:,} | 0 | 舞蹈社講師回捐 |\n\2',
            content
        )
    
    # 更新收入合計
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*630,000\*\* \| \*\*630,000\*\* \| \*\*0\*\* \|',
        f'| **合計** | **{new_total_income:,}** | **{new_total_income:,}** | **0** |',
        content
    )
    
    # 更新支出決算，業務費加入舞蹈課程
    # 原業務費：378,456
    # 新增舞蹈課程：331,456
    # 新業務費：709,912
    new_business_expense = 378456 + actual_dance_expense
    
    content = re.sub(
        r'\| 業務費 \| 380,000 \| 378,456 \| -1,544 \| 活動執行費用 \|',
        f'| 業務費 | 711,500 | {new_business_expense:,} | {new_business_expense - 711500:,} | 活動執行費用（含舞蹈運動課程{actual_dance_expense:,}元） |',
        content
    )
    
    # 更新支出合計
    new_total_expense = 626000 + actual_dance_expense  # 957,456
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*630,000\*\* \| \*\*626,000\*\* \| \*\*-4,000\*\* \|',
        f'| **合計** | **{new_total_expense:,}** | **{new_total_expense:,}** | **0** |',
        content
    )
    
    # 更新重要說明
    new_ending_balance = new_total_income - new_total_expense  # -62,333
    content = re.sub(
        r'- 收入總額：630,000 元（預算規模調整至63萬元）\n- 支出總額：626,000 元（除定額支付項目外留合理尾數）\n- 年終結餘：4,000 元（114年，含總幹事捐薪）',
        f'- 收入總額：{new_total_income:,} 元（含講師回捐{actual_instructor_donation:,}元）\n- 支出總額：{new_total_expense:,} 元（含舞蹈運動課程{actual_dance_expense:,}元，留合理尾數）\n- 年終結餘：{new_ending_balance:,} 元（114年，含總幹事捐薪補足）\n- **舞蹈運動課程**：場地費{actual_venue_cost:,}元 + 講師費{actual_instructor_cost:,}元 = {actual_dance_expense:,}元',
        content
    )
    
    # 更新現金出納表
    content = re.sub(
        r'\| 本期收入 \| 630,000 \|',
        f'| 本期收入 | {new_total_income:,} |',
        content
    )
    content = re.sub(
        r'\| 本期支出 \| 626,000 \|',
        f'| 本期支出 | {new_total_expense:,} |',
        content
    )
    content = re.sub(
        r'\| 期末現金 \| 4,000 \| 年終結餘（114年，含總幹事捐薪）',
        f'| 期末現金 | {new_ending_balance:,} | 年終結餘（114年，含總幹事捐薪補足）',
        content
    )
    
    # 更新基金收支表
    content = re.sub(
        r'\| 本期收入 \| 630,000 \| 會費 200,000 \+ 企業捐助 430,000 \|',
        f'| 本期收入 | {new_total_income:,} | 會費 200,000 + 企業捐助 {new_donation:,} + 講師回捐 {actual_instructor_donation:,} |',
        content
    )
    content = re.sub(
        r'\| 本期支出 \| 626,000 \| 人事費 0（總幹事捐薪）\+ 業務費 378,456 \+ 設備費 84,234 \+ 行政管理費 80,000 \+ 系統維護費 83,310 \|',
        f'| 本期支出 | {new_total_expense:,} | 人事費 0（總幹事捐薪）+ 業務費 {new_business_expense:,}（含舞蹈課程{actual_dance_expense:,}）+ 設備費 84,234 + 行政管理費 80,000 + 系統維護費 83,310 |',
        content
    )
    content = re.sub(
        r'\| 期末基金 \| 4,000 \| 年終結餘（114年，含總幹事捐薪）',
        f'| 期末基金 | {new_ending_balance:,} | 年終結餘（114年，含總幹事捐薪補足）',
        content
    )
    
    # 更新決算說明
    content = re.sub(
        r'- 業務費：378,456 元（預算 380,000，節餘 1,544，留合理尾數）',
        f'- 業務費：{new_business_expense:,} 元（預算 711,500，含舞蹈運動課程{actual_dance_expense:,}元，留合理尾數）\n  - 舞蹈運動課程明細：場地費{actual_venue_cost:,}元 + 講師費{actual_instructor_cost:,}元',
        content
    )
    content = re.sub(
        r'- 收入總額：630,000 元（預算規模調整至63萬元）\n- 支出總額：626,000 元（除定額支付項目外留合理尾數）\n- 年終結餘：4,000 元（114年，含總幹事捐薪）',
        f'- 收入總額：{new_total_income:,} 元（含講師回捐{actual_instructor_donation:,}元）\n- 支出總額：{new_total_expense:,} 元（含舞蹈運動課程{actual_dance_expense:,}元，留合理尾數）\n- 年終結餘：{new_ending_balance:,} 元（114年，含總幹事捐薪補足）',
        content
    )
    
    # 更新收入執行情況
    content = re.sub(
        r'- 企業捐助：650,000 元（達成率 100%）',
        f'- 企業捐助：{new_donation:,} 元（達成率 100%）\n- 講師回捐：{actual_instructor_donation:,} 元（達成率 100%）',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      收入總額：{new_total_income:,} 元（含講師回捐{actual_instructor_donation:,}元）")
    print(f"      支出總額：{new_total_expense:,} 元（含舞蹈課程{actual_dance_expense:,}元）")
    print(f"      年終結餘：{new_ending_balance:,} 元")


def update_annual_work_plan():
    """更新年度工作計畫，加入舞蹈運動課程"""
    print("\n更新年度工作計畫，加入舞蹈運動課程...")
    
    dance_costs = calculate_dance_class_costs()
    
    filepath = OPERATIONAL_FILES_DIR / "02_年度工作計畫_2026.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新收入預算
    new_total_income = 630000 + dance_costs["total_instructor_donation"]  # 895,200
    new_donation = 430000 - dance_costs["total_instructor_donation"]  # 164,800
    
    content = re.sub(
        r'\| 企業捐助 \| 430,000 \| 企業捐助款（預算規模調整至63萬元） \|',
        f'| 企業捐助 | {new_donation:,} | 企業捐助款（預算規模調整至63萬元） |',
        content
    )
    
    # 添加講師回捐收入
    if "講師回捐" not in content:
        content = re.sub(
            r'(\| 企業捐助 \|.*?\|.*?\|)\n(\| 其他收入 \|)',
            rf'\1\n| 講師回捐 | {dance_costs["total_instructor_donation"]:,} | 舞蹈社講師回捐 |\n\2',
            content
        )
    
    # 更新收入合計
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*630,000\*\* \|',
        f'| **合計** | **{new_total_income:,}** |',
        content
    )
    
    # 更新支出預算，業務費加入舞蹈課程
    new_business_expense = 380000 + dance_costs["total_dance_expense"]  # 711,500
    
    content = re.sub(
        r'\| 業務費 \| 380,000 \| 活動執行費用 \|',
        f'| 業務費 | {new_business_expense:,} | 活動執行費用（含舞蹈運動課程331,500元） |',
        content
    )
    
    # 更新支出合計
    new_total_expense = 630000 + dance_costs["total_dance_expense"]  # 961,500
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*630,000\*\* \|',
        f'| **合計** | **{new_total_expense:,}** |',
        content
    )
    
    # 更新預算說明
    new_ending_balance = new_total_income - new_total_expense  # -66,300
    content = re.sub(
        r'- 實際支出預算：630,000 元（扣除總幹事捐薪後，預算規模調整至63萬元）',
        f'- 實際支出預算：{new_total_expense:,} 元（含舞蹈運動課程331,500元）',
        content
    )
    content = re.sub(
        r'- 年終結餘預估：0 元（含總幹事捐薪）',
        f'- 年終結餘預估：{new_ending_balance:,} 元（含總幹事捐薪補足）',
        content
    )
    
    # 添加舞蹈運動課程說明
    if "### 2.2 具體目標" in content:
        content = re.sub(
            r'- 辦理高齡關懷活動至少 12 場次',
            r'- 辦理高齡關懷活動至少 12 場次\n- 辦理舞蹈運動課程（每週3日，全年156日，每日2小時）',
            content
        )
    
    # 添加舞蹈運動課程工作項目
    if "## 三、工作項目與執行計畫" in content:
        dance_project = """
### 3.6 舞蹈運動課程

#### 3.6.1 課程規劃
- **開課頻率**：每週3日，全年約156日
- **課程時段**：每日2小時
- **場地費用**：每小時62.5元，每日125元，全年19,500元
- **講師費用**：每日2,000元，全年312,000元
- **講師回捐**：每日1,700元，全年265,200元

#### 3.6.2 執行方式
- 提供社區居民舞蹈運動課程
- 促進社區健康與活力
- 講師回捐支持協會運作

#### 3.6.3 預期效益
- 服務社區居民至少156場次
- 促進社區健康生活
- 增加協會收入來源
"""
        
        # 在最後一個工作項目後添加
        if "### 3.5" in content and "### 3.6" not in content:
            content = re.sub(
                r'(### 3\.5.*?\n\n)',
                r'\1' + dance_project + '\n',
                content,
                flags=re.DOTALL
            )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("新增舞蹈社費用項目")
    print("=" * 60)
    print()
    
    dance_costs = calculate_dance_class_costs()
    print(f"舞蹈社費用計算：")
    print(f"  全年天數：{dance_costs['days_per_year']} 日（每週3日 × 52週）")
    print(f"  場地費用：{dance_costs['total_venue_cost']:,} 元（每日{dance_costs['venue_cost_per_day']}元）")
    print(f"  講師費用：{dance_costs['total_instructor_cost']:,} 元（每日{dance_costs['instructor_cost_per_day']:,}元）")
    print(f"  講師回捐：{dance_costs['total_instructor_donation']:,} 元（每日{dance_costs['instructor_donation_per_day']:,}元）")
    print(f"  總支出：{dance_costs['total_dance_expense']:,} 元")
    print()
    
    # 更新年度預算
    update_annual_budget_2027()
    
    # 更新年度決算
    update_annual_financial_report_2025()
    
    # 更新年度工作計畫
    update_annual_work_plan()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print("- 舞蹈運動課程已納入業務費")
    print("- 場地費用：19,500 元（全年）")
    print("- 講師費用：312,000 元（全年）")
    print("- 講師回捐收入：265,200 元（全年）")
    print("- 總支出：331,500 元（場地費 + 講師費）")


if __name__ == "__main__":
    main()
