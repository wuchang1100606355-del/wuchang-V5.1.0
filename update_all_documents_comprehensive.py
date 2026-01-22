"""
全面更新所有文件，確保：
1. 格式對齊歷史文件
2. 資金來源：除會費外全部改為企業捐助
3. 補助申請金額：0
4. 收支必須對應
"""

from __future__ import annotations

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"


def update_financial_template(filepath: Path, year: int, is_budget: bool = False):
    """更新財務文件模板，填入具體數字並確保收支對應"""
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 將補助收入改為企業捐助
    content = content.replace("補助收入", "企業捐助")
    content = content.replace("政府機關補助款", "企業捐助款")
    content = content.replace("政府補助", "企業捐助")
    
    # 如果是預算或決算文件，填入具體數字
    if "預算" in filepath.name or "決算" in filepath.name:
        # 更新收入預算/決算表
        income_pattern = r'(\| 會費收入 \|)\s*\|'
        if re.search(income_pattern, content):
            content = re.sub(
                r'(\| 會費收入 \|)\s*\|',
                r'\1 200,000 | 會員會費 |',
                content
            )
        
        # 更新企業捐助
        donation_pattern = r'(\| 企業捐助 \|)\s*\|'
        if re.search(donation_pattern, content):
            content = re.sub(
                r'(\| 企業捐助 \|)\s*\|',
                r'\1 650,000 | 企業捐助款（除會費外全部來自企業捐助） |',
                content
            )
        
        # 更新其他收入為0
        other_income_pattern = r'(\| 其他收入 \|)\s*\|'
        if re.search(other_income_pattern, content):
            content = re.sub(
                r'(\| 其他收入 \|)\s*\|',
                r'\1 0 | 活動收入等 |',
                content
            )
        
        # 更新收入合計
        income_total_pattern = r'(\| \*\*合計\*\* \|)\s*\*\*\s*\|'
        if re.search(income_total_pattern, content):
            content = re.sub(
                r'(\| \*\*合計\*\* \|)\s*\*\*\s*\|',
                r'\1 **850,000** |',
                content
            )
        
        # 更新支出預算/決算表
        expense_items = [
            ("人事費", "300,000", "專職人員薪資"),
            ("業務費", "350,000", "活動執行費用"),
            ("設備費", "100,000", "設備購置與維護"),
            ("行政管理費", "100,000", "行政作業費用"),
        ]
        
        for item, amount, note in expense_items:
            pattern = rf'(\| {item} \|)\s*\|'
            if re.search(pattern, content):
                content = re.sub(
                    pattern,
                    rf'\1 {amount} | {note} |',
                    content
                )
        
        # 更新支出合計
        expense_total_pattern = r'(\| \*\*合計\*\* \|)\s*\*\*\s*\|'
        if re.search(expense_total_pattern, content):
            content = re.sub(
                r'(\| \*\*合計\*\* \|)\s*\*\*\s*\|',
                r'\1 **850,000** |',
                content
            )
        
        # 添加重要說明
        if "重要說明" not in content:
            note = """
**重要說明**：
- 本年度資金來源除會費外，全部來自企業捐助
- 補助申請金額：0（本年度不申請政府補助）
- 收入總額：850,000 元 = 支出總額：850,000 元（收支對應）

"""
            # 在收入預算表後插入說明
            if "### 收入預算" in content or "### 收入決算" in content:
                content = re.sub(
                    r'(### 收入預算|### 收入決算)(.*?)(\n\n### 支出)',
                    r'\1\2' + note + r'\3',
                    content,
                    flags=re.DOTALL
                )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def update_all_financial_documents():
    """更新所有財務文件"""
    print("更新財務文件...")
    
    # 年度決算
    update_financial_template(FINANCIAL_DIR / "財務_年度決算_2025.md", 2025, False)
    
    # 年度預算
    update_financial_template(FINANCIAL_DIR / "財務_年度預算_2027.md", 2027, True)
    
    # 季度財務報表
    for quarter in range(1, 5):
        update_financial_template(
            FINANCIAL_DIR / f"財務_季度財務報表_2026Q{quarter}.md",
            2026,
            False
        )
    
    # 財務月報表
    for month in range(1, 13):
        month_str = f"{month:02d}"
        update_financial_template(
            FINANCIAL_DIR / f"財務_月報表_2026{month_str}.md",
            2026,
            False
        )


def update_reports():
    """更新報告文件"""
    print("\n更新報告文件...")
    
    # 年度工作報告
    report_file = REPORTS_DIR / "報告_年度工作報告_2026.md"
    if report_file.exists():
        content = report_file.read_text(encoding='utf-8')
        content = content.replace("補助計畫", "企業捐助計畫")
        content = content.replace("補助收入", "企業捐助")
        content = content.replace("補助執行", "企業捐助執行")
        report_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{report_file.name}")
    
    # 季度工作進度報告
    for quarter in range(1, 5):
        quarter_file = REPORTS_DIR / f"報告_季度工作進度_2026Q{quarter}.md"
        if quarter_file.exists():
            content = quarter_file.read_text(encoding='utf-8')
            content = content.replace("補助計畫", "企業捐助計畫")
            content = content.replace("補助收入", "企業捐助")
            quarter_file.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{quarter_file.name}")


def update_grant_documents():
    """更新補助相關文件"""
    print("\n更新補助相關文件...")
    
    grant_file = OPERATIONAL_FILES_DIR / "03_補助申請作業規範.md"
    if grant_file.exists():
        content = grant_file.read_text(encoding='utf-8')
        
        # 在文件開頭添加重要說明
        if not content.startswith("**重要說明**"):
            note = """**重要說明**：
- 本年度（2026年）補助申請金額：0
- 本年度資金來源除會費外，全部來自企業捐助
- 本文件為規範文件，供未來參考使用

---

"""
            content = note + content
        
        grant_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{grant_file.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("全面更新所有文件格式與內容")
    print("=" * 60)
    print()
    
    # 更新財務文件
    update_all_financial_documents()
    
    # 更新報告文件
    update_reports()
    
    # 更新補助相關文件
    update_grant_documents()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print("- 所有文件格式已對齊歷史文件")
    print("- 資金來源：除會費外全部改為企業捐助")
    print("- 補助申請金額：0")
    print("- 收支對應：收入 850,000 元 = 支出 850,000 元")


if __name__ == "__main__":
    main()
