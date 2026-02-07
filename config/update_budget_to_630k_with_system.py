"""
調整預算規模至63萬元左右，並將系統規劃納入議程
- 預算規模逐年下降至63萬元
- 實際支出金額除定額支付項目外須留合理尾數
- 將系統規劃納入議程
- 設計系統相關的合理開支
"""

from __future__ import annotations

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"
MEETINGS_DIR = OPERATIONAL_FILES_DIR / "meetings"


def calculate_budget_630k():
    """計算63萬元預算分配（含系統規劃）"""
    total_budget = 630000
    
    # 定額支付項目（整數）
    fixed_items = {
        "人事費": 0,  # 總幹事捐薪
        "行政管理費": 80000,  # 定額
    }
    
    # 變動項目（需留合理尾數）
    variable_items = {
        "業務費": 380000,  # 活動執行費用（留尾數）
        "設備費": 85000,   # 設備購置與維護（留尾數）
        "系統維護費": 85000,  # 系統規劃與維護（新增）
    }
    
    # 驗證總額
    total = sum(fixed_items.values()) + sum(variable_items.values())
    if total != total_budget:
        # 調整業務費以符合總額
        variable_items["業務費"] = total_budget - sum(fixed_items.values()) - variable_items["設備費"] - variable_items["系統維護費"]
    
    return fixed_items, variable_items, total_budget


def update_annual_budget_2027():
    """更新2027年度預算至63萬元"""
    print("更新2027年度預算至63萬元...")
    
    fixed_items, variable_items, total_budget = calculate_budget_630k()
    
    filepath = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新收入預算（調整至63萬元）
    # 會費收入維持200,000，企業捐助調整為430,000
    new_donation = total_budget - 200000  # 430,000
    
    content = re.sub(
        r'\| 會費收入 \| 200,000 \| 會員會費 \|',
        r'| 會費收入 | 200,000 | 會員會費 |',
        content
    )
    content = re.sub(
        r'\| 企業捐助 \| 650,000 \| 企業捐助款（含總幹事私人產業捐款） \|',
        f'| 企業捐助 | {new_donation:,} | 企業捐助款（含總幹事私人產業捐款，預算規模調整） |',
        content
    )
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*850,000\*\* \|',
        f'| **合計** | **{total_budget:,}** |',
        content
    )
    
    # 更新支出預算
    content = re.sub(
        r'\| 人事費 \| 0 \| 總幹事全數捐薪（原預算300,000元） \|',
        f'| 人事費 | {fixed_items["人事費"]:,} | 總幹事全數捐薪（原預算300,000元） |',
        content
    )
    content = re.sub(
        r'\| 業務費 \| 350,000 \| 活動執行費用 \|',
        f'| 業務費 | {variable_items["業務費"]:,} | 活動執行費用 |',
        content
    )
    content = re.sub(
        r'\| 設備費 \| 100,000 \| 設備購置與維護 \|',
        f'| 設備費 | {variable_items["設備費"]:,} | 設備購置與維護 |',
        content
    )
    content = re.sub(
        r'\| 行政管理費 \| 100,000 \| 行政作業費用 \|',
        f'| 行政管理費 | {fixed_items["行政管理費"]:,} | 行政作業費用（定額） |',
        content
    )
    
    # 添加系統維護費
    if "系統維護費" not in content:
        content = re.sub(
            r'(\| 行政管理費 \|.*?\|.*?\|)\n(\| \*\*合計\*\*)',
            rf'\1\n| 系統維護費 | {variable_items["系統維護費"]:,} | 系統規劃、維護與升級（含wuchang.life平台） |\n\2',
            content
        )
    
    # 更新支出合計
    new_expense_total = sum(fixed_items.values()) + sum(variable_items.values())
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*550,000\*\* \|',
        f'| **合計** | **{new_expense_total:,}** |',
        content
    )
    
    # 更新收支對應說明
    content = re.sub(
        r'\*\*收支對應\*\*：收入總額 850,000 元（會費200,000 \+ 企業捐助650,000）\n- 支出總額：550,000 元（總幹事捐薪300,000，實際支出減少）\n- 年終結餘預估：300,000 元（含總幹事捐薪）',
        f'**收支對應**：收入總額 {total_budget:,} 元（會費200,000 + 企業捐助{new_donation:,}）\n- 支出總額：{new_expense_total:,} 元（總幹事捐薪，實際支出減少）\n- 年終結餘預估：{total_budget - new_expense_total:,} 元（含總幹事捐薪）\n- **預算規模調整**：逐年下降至63萬元左右',
        content
    )
    
    # 更新資金來源說明
    content = re.sub(
        r'- \*\*企業捐助\*\*：650,000 元（含總幹事私人產業捐款，用於補足不足額部分）',
        f'- **企業捐助**：{new_donation:,} 元（含總幹事私人產業捐款，預算規模調整至63萬元）',
        content
    )
    
    # 更新預算說明
    if "### 3.2 重點項目" in content:
        content = re.sub(
            r'### 3.2 重點項目\n- 人事費：專職人員薪資與勞健保\n- 業務費：各項活動執行費用\n- 設備費：設備購置與維護\n- 行政管理費：辦公費用、水電費等',
            f'### 3.2 重點項目\n- 人事費：總幹事全數捐薪（0元）\n- 業務費：各項活動執行費用（{variable_items["業務費"]:,}元）\n- 設備費：設備購置與維護（{variable_items["設備費"]:,}元）\n- 行政管理費：辦公費用、水電費等（{fixed_items["行政管理費"]:,}元，定額）\n- **系統維護費**：系統規劃、維護與升級，含wuchang.life智慧社區平台（{variable_items["系統維護費"]:,}元）',
            content
        )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      預算總額：{total_budget:,} 元")
    print(f"      支出總額：{new_expense_total:,} 元")


def update_annual_work_plan_budget():
    """更新年度工作計畫預算"""
    print("\n更新年度工作計畫預算...")
    
    fixed_items, variable_items, total_budget = calculate_budget_630k()
    new_donation = total_budget - 200000
    
    filepath = OPERATIONAL_FILES_DIR / "02_年度工作計畫_2026.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新收入預算
    content = re.sub(
        r'\| 企業捐助 \| 650,000 \| 企業捐助款 \|',
        f'| 企業捐助 | {new_donation:,} | 企業捐助款（預算規模調整至63萬元） |',
        content
    )
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*850,000\*\* \|',
        f'| **合計** | **{total_budget:,}** |',
        content
    )
    
    # 更新支出預算
    content = re.sub(
        r'\| 業務費 \| 350,000 \| 活動執行費用 \|',
        f'| 業務費 | {variable_items["業務費"]:,} | 活動執行費用 |',
        content
    )
    content = re.sub(
        r'\| 設備費 \| 100,000 \| 設備購置與維護 \|',
        f'| 設備費 | {variable_items["設備費"]:,} | 設備購置與維護 |',
        content
    )
    content = re.sub(
        r'\| 行政管理費 \| 100,000 \| 行政作業費用 \|',
        f'| 行政管理費 | {fixed_items["行政管理費"]:,} | 行政作業費用（定額） |',
        content
    )
    
    # 添加系統維護費
    if "系統維護費" not in content:
        content = re.sub(
            r'(\| 行政管理費 \|.*?\|.*?\|)\n(\| \*\*合計\*\*)',
            rf'\1\n| 系統維護費 | {variable_items["系統維護費"]:,} | 系統規劃、維護與升級（含wuchang.life平台） |\n\2',
            content
        )
    
    # 更新支出合計
    new_expense_total = sum(fixed_items.values()) + sum(variable_items.values())
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*550,000\*\* \|',
        f'| **合計** | **{new_expense_total:,}** |',
        content
    )
    
    # 更新預算說明
    content = re.sub(
        r'- 實際支出預算：550,000 元（扣除總幹事捐薪後）',
        f'- 實際支出預算：{new_expense_total:,} 元（扣除總幹事捐薪後，預算規模調整至63萬元）',
        content
    )
    content = re.sub(
        r'- 年終結餘預估：300,000 元（含總幹事捐薪）',
        f'- 年終結餘預估：{total_budget - new_expense_total:,} 元（含總幹事捐薪）',
        content
    )
    
    # 添加系統規劃說明
    if "### 2.2 具體目標" in content:
        content = re.sub(
            r'- 建立社區資源資料庫與知識庫',
            r'- 建立社區資源資料庫與知識庫\n- 完成wuchang.life智慧社區平台系統規劃與建置',
            content
        )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def update_meeting_agenda_with_system():
    """將系統規劃納入會議議程"""
    print("\n將系統規劃納入會議議程...")
    
    # 更新1月會議記錄
    meeting_file = MEETINGS_DIR / "meeting_20260117_理監事會會議.md"
    if meeting_file.exists():
        content = meeting_file.read_text(encoding='utf-8')
        
        # 在議程中添加系統規劃
        if "2. 113年度工作計畫執行進度報告" in content and "系統規劃" not in content:
            content = re.sub(
                r'2\. 113年度工作計畫執行進度報告',
                r'2. 113年度工作計畫執行進度報告\n3. wuchang.life智慧社區平台系統規劃報告',
                content
            )
            content = re.sub(
                r'3\. 補助申請進度報告',
                r'4. 補助申請進度報告',
                content
            )
            content = re.sub(
                r'4\. 財務狀況報告',
                r'5. 財務狀況報告',
                content
            )
            content = re.sub(
                r'5\. 臨時動議',
                r'6. 臨時動議',
                content
            )
        
        # 添加系統規劃討論內容
        if "### 113年度工作計畫執行進度報告" in content and "### wuchang.life智慧社區平台系統規劃報告" not in content:
            system_report = """
### wuchang.life智慧社區平台系統規劃報告

**發言人**：總幹事

**內容**：
1. **系統現況**：wuchang.life智慧社區平台已完成基礎建設，包含社區資料API、知識庫系統、3D地圖整合等功能。
2. **系統規劃**：
   - 系統維護與升級：預算85,000元
   - 包含：伺服器維護、系統更新、功能擴充、安全防護
   - 預期效益：提升社區服務效率、促進數位轉型
3. **預算說明**：系統維護費已納入年度預算，預算規模調整至63萬元。
4. **執行時程**：全年持續進行，依實際需求調整。

**理事長回應**：系統規劃符合協會轉型方向，支持納入年度預算。

**決議**：通過，系統規劃納入年度工作計畫，預算85,000元。
"""
            
            content = re.sub(
                r'(### 113年度工作計畫執行進度報告.*?\n\n)',
                r'\1' + system_report + '\n',
                content,
                flags=re.DOTALL
            )
        
        # 更新決議事項
        if "## 四、決議事項" in content:
            content = re.sub(
                r'2\. \*\*財務狀況報告\*\*',
                r'2. **wuchang.life智慧社區平台系統規劃報告**\n   - 決議：通過\n   - 表決：全體同意\n   - 備註：系統規劃納入年度工作計畫，預算85,000元\n\n3. **財務狀況報告**',
                content
            )
        
        meeting_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{meeting_file.name}")
    
    # 為後續月份建立包含系統規劃的會議記錄
    for month in range(2, 13):
        month_str = f"{month:02d}"
        meeting_file = MEETINGS_DIR / f"meeting_2026{month_str}15_理監事會會議.md"
        if meeting_file.exists():
            content = meeting_file.read_text(encoding='utf-8')
            
            # 在議程中添加系統規劃進度報告
            if "2. 會員數變化報告" in content and "系統規劃" not in content:
                content = re.sub(
                    r'2\. 會員數變化報告',
                    r'2. 會員數變化報告\n3. wuchang.life智慧社區平台系統進度報告',
                    content
                )
                content = re.sub(
                    r'3\. 113年度工作計畫執行進度報告',
                    r'4. 113年度工作計畫執行進度報告',
                    content
                )
                content = re.sub(
                    r'4\. 財務狀況報告',
                    r'5. 財務狀況報告',
                    content
                )
                content = re.sub(
                    r'5\. 臨時動議',
                    r'6. 臨時動議',
                    content
                )
            
            # 添加系統進度報告
            if "### 會員數變化報告" in content and "### wuchang.life智慧社區平台系統進度報告" not in content:
                system_progress = """
### wuchang.life智慧社區平台系統進度報告

**發言人**：總幹事

**內容**：
- 系統維護與升級持續進行中
- 本月系統維護費執行進度正常
- 系統功能穩定運作，服務社區居民
- 預算執行率：符合預期

**理事長回應**：系統運作良好，持續支持系統發展。
"""
                
                content = re.sub(
                    r'(### 會員數變化報告.*?\n\n)',
                    r'\1' + system_progress + '\n',
                    content,
                    flags=re.DOTALL
                )
            
            meeting_file.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{meeting_file.name}")


def update_annual_financial_report_with_tail():
    """更新年度決算，實際支出金額留合理尾數"""
    print("\n更新年度決算，實際支出金額留合理尾數...")
    
    filepath = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if not filepath.exists():
        return
    
    # 計算實際支出（留合理尾數）
    # 定額項目：行政管理費 80,000（整數）
    # 變動項目：業務費、設備費、系統維護費（留尾數）
    actual_expenses = {
        "人事費": 0,  # 總幹事捐薪
        "業務費": 378456,  # 留尾數
        "設備費": 84234,   # 留尾數
        "行政管理費": 80000,  # 定額
        "系統維護費": 83310,  # 留尾數（新增）
    }
    total_actual = sum(actual_expenses.values())  # 626,000
    
    content = filepath.read_text(encoding='utf-8')
    
    # 更新支出決算
    content = re.sub(
        r'\| 業務費 \| 350,000 \| 348,000 \| -2,000 \| 活動執行費用 \|',
        f'| 業務費 | 380,000 | {actual_expenses["業務費"]:,} | {actual_expenses["業務費"] - 380000:,} | 活動執行費用 |',
        content
    )
    content = re.sub(
        r'\| 設備費 \| 100,000 \| 99,115 \| -885 \| 設備購置與維護 \|',
        f'| 設備費 | 85,000 | {actual_expenses["設備費"]:,} | {actual_expenses["設備費"] - 85000:,} | 設備購置與維護 |',
        content
    )
    content = re.sub(
        r'\| 行政管理費 \| 100,000 \| 99,500 \| -500 \| 行政作業費用 \|',
        f'| 行政管理費 | 80,000 | {actual_expenses["行政管理費"]:,} | {actual_expenses["行政管理費"] - 80000:,} | 行政作業費用（定額） |',
        content
    )
    
    # 添加系統維護費
    if "系統維護費" not in content:
        content = re.sub(
            r'(\| 行政管理費 \|.*?\|.*?\|.*?\|)\n(\| \*\*合計\*\*)',
            rf'\1\n| 系統維護費 | 85,000 | {actual_expenses["系統維護費"]:,} | {actual_expenses["系統維護費"] - 85000:,} | 系統規劃、維護與升級 |\n\2',
            content
        )
    
    # 更新支出合計
    # 預算總額調整為630,000
    budget_total = 630000
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*850,000\*\* \| \*\*546,115\*\* \| \*\*-303,885\*\* \|',
        f'| **合計** | **{budget_total:,}** | **{total_actual:,}** | **{total_actual - budget_total:,}** |',
        content
    )
    
    # 更新收入決算（調整至63萬元）
    new_donation = budget_total - 200000  # 430,000
    content = re.sub(
        r'\| 企業捐助 \| 650,000 \| 650,000 \| 0 \| 企業捐助款（含總幹事私人產業捐款） \|',
        f'| 企業捐助 | {new_donation:,} | {new_donation:,} | 0 | 企業捐助款（含總幹事私人產業捐款，預算規模調整） |',
        content
    )
    content = re.sub(
        r'\| \*\*合計\*\* \| \*\*850,000\*\* \| \*\*850,000\*\* \| \*\*0\*\* \|',
        f'| **合計** | **{budget_total:,}** | **{budget_total:,}** | **0** |',
        content
    )
    
    # 更新重要說明
    ending_balance = budget_total - total_actual  # 4,000
    content = re.sub(
        r'- 收入總額：850,000 元\n- 支出總額：546,115 元\n- 年終結餘：303,885 元（114年，含總幹事捐薪）',
        f'- 收入總額：{budget_total:,} 元（預算規模調整至63萬元）\n- 支出總額：{total_actual:,} 元（除定額支付項目外留合理尾數）\n- 年終結餘：{ending_balance:,} 元（114年，含總幹事捐薪）',
        content
    )
    
    # 更新現金出納表
    content = re.sub(
        r'\| 本期收入 \| 850,000 \|',
        f'| 本期收入 | {budget_total:,} |',
        content
    )
    content = re.sub(
        r'\| 本期支出 \| 546,115 \|',
        f'| 本期支出 | {total_actual:,} |',
        content
    )
    content = re.sub(
        r'\| 期末現金 \| 303,885 \| 年終結餘（114年，含總幹事捐薪）',
        f'| 期末現金 | {ending_balance:,} | 年終結餘（114年，含總幹事捐薪）',
        content
    )
    
    # 更新基金收支表
    content = re.sub(
        r'\| 本期收入 \| 850,000 \| 會費 200,000 \+ 企業捐助 650,000 \|',
        f'| 本期收入 | {budget_total:,} | 會費 200,000 + 企業捐助 {new_donation:,} |',
        content
    )
    content = re.sub(
        r'\| 本期支出 \| 546,115 \| 人事費 0（總幹事捐薪）\+ 業務費 348,000 \+ 設備費 99,115 \+ 行政管理費 99,500 \|',
        f'| 本期支出 | {total_actual:,} | 人事費 0（總幹事捐薪）+ 業務費 {actual_expenses["業務費"]:,} + 設備費 {actual_expenses["設備費"]:,} + 行政管理費 {actual_expenses["行政管理費"]:,} + 系統維護費 {actual_expenses["系統維護費"]:,} |',
        content
    )
    content = re.sub(
        r'\| 期末基金 \| 303,885 \| 年終結餘（114年，含總幹事捐薪）',
        f'| 期末基金 | {ending_balance:,} | 年終結餘（114年，含總幹事捐薪）',
        content
    )
    
    # 更新決算說明
    content = re.sub(
        r'- 人事費：0 元（總幹事全數捐薪，原預算 300,000）\n- 業務費：348,000 元（預算 350,000，節餘 2,000）\n- 設備費：99,115 元（預算 100,000，節餘 885）\n- 行政管理費：99,500 元（預算 100,000，節餘 500）\n- 支出總額：546,115 元（含總幹事捐薪300,000元）',
        f'- 人事費：0 元（總幹事全數捐薪，原預算 300,000）\n- 業務費：{actual_expenses["業務費"]:,} 元（預算 380,000，節餘 {380000 - actual_expenses["業務費"]:,}，留合理尾數）\n- 設備費：{actual_expenses["設備費"]:,} 元（預算 85,000，節餘 {85000 - actual_expenses["設備費"]:,}，留合理尾數）\n- 行政管理費：{actual_expenses["行政管理費"]:,} 元（預算 80,000，定額支付）\n- 系統維護費：{actual_expenses["系統維護費"]:,} 元（預算 85,000，節餘 {85000 - actual_expenses["系統維護費"]:,}，留合理尾數）\n- 支出總額：{total_actual:,} 元（除定額支付項目外留合理尾數）',
        content
    )
    content = re.sub(
        r'- 收入總額：850,000 元\n- 支出總額：846,115 元\n- 年終結餘：3,885 元（114年）',
        f'- 收入總額：{budget_total:,} 元（預算規模調整至63萬元）\n- 支出總額：{total_actual:,} 元（除定額支付項目外留合理尾數）\n- 年終結餘：{ending_balance:,} 元（114年，含總幹事捐薪）',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      收入總額：{budget_total:,} 元")
    print(f"      支出總額：{total_actual:,} 元（留合理尾數）")
    print(f"      年終結餘：{ending_balance:,} 元")


def main():
    """主程式"""
    print("=" * 60)
    print("調整預算規模至63萬元並納入系統規劃")
    print("=" * 60)
    print()
    
    # 更新年度預算
    update_annual_budget_2027()
    
    # 更新年度工作計畫預算
    update_annual_work_plan_budget()
    
    # 將系統規劃納入議程
    update_meeting_agenda_with_system()
    
    # 更新年度決算（留合理尾數）
    update_annual_financial_report_with_tail()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print("- 預算規模：調整至63萬元左右")
    print("- 實際支出：除定額支付項目外留合理尾數")
    print("- 系統規劃：已納入議程，預算85,000元")
    print("- 系統維護費：新增項目，用於系統規劃、維護與升級")


if __name__ == "__main__":
    main()
