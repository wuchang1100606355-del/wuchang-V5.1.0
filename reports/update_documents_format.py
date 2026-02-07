"""
更新所有產出文件格式，對齊歷史文件格式
- 資金來源：除會費外，全部改為企業捐助
- 補助申請金額：設為0
- 收支必須對應
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"


def update_financial_documents():
    """更新財務文件"""
    print("更新財務文件...")
    
    # 更新年度決算
    annual_report_file = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if annual_report_file.exists():
        content = annual_report_file.read_text(encoding='utf-8')
        # 將補助收入改為企業捐助
        content = content.replace("補助收入", "企業捐助")
        content = content.replace("政府機關補助款", "企業捐助款")
        # 移除補助相關說明
        content = re.sub(r'補助.*?收入', '企業捐助', content)
        annual_report_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{annual_report_file.name}")
    
    # 更新年度預算
    annual_budget_file = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if annual_budget_file.exists():
        content = annual_budget_file.read_text(encoding='utf-8')
        # 將補助收入改為企業捐助
        content = content.replace("補助收入", "企業捐助")
        content = content.replace("政府機關補助款", "企業捐助款")
        # 確保收支對應
        content = re.sub(r'補助.*?收入', '企業捐助', content)
        annual_budget_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{annual_budget_file.name}")
    
    # 更新季度財務報表
    for quarter in range(1, 5):
        quarter_file = FINANCIAL_DIR / f"財務_季度財務報表_2026Q{quarter}.md"
        if quarter_file.exists():
            content = quarter_file.read_text(encoding='utf-8')
            content = content.replace("補助收入", "企業捐助")
            content = content.replace("政府機關補助款", "企業捐助款")
            quarter_file.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{quarter_file.name}")
    
    # 更新財務月報表
    for month in range(1, 13):
        month_str = f"{month:02d}"
        month_file = FINANCIAL_DIR / f"財務_月報表_2026{month_str}.md"
        if month_file.exists():
            content = month_file.read_text(encoding='utf-8')
            content = content.replace("補助收入", "企業捐助")
            content = content.replace("政府機關補助款", "企業捐助款")
            month_file.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{month_file.name}")


def update_annual_work_plan():
    """更新年度工作計畫"""
    print("\n更新年度工作計畫...")
    
    work_plan_file = OPERATIONAL_FILES_DIR / "02_年度工作計畫_2026.md"
    if work_plan_file.exists():
        content = work_plan_file.read_text(encoding='utf-8')
        
        # 更新預算編列部分
        # 將補助收入改為企業捐助，金額設為0
        old_budget = """### 4.1 收入預算
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 會費收入 | 200,000 | 會員會費 |
| 政府補助 | 500,000 | 申請各項補助計畫 |
| 捐款收入 | 100,000 | 會員及社會捐款 |
| 其他收入 | 50,000 | 活動收入等 |
| **合計** | **850,000** | |"""
        
        new_budget = """### 4.1 收入預算
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 會費收入 | 200,000 | 會員會費 |
| 企業捐助 | 650,000 | 企業捐助款 |
| 其他收入 | 0 | 活動收入等 |
| **合計** | **850,000** | |

**備註**：
- 本年度資金來源除會費外，全部來自企業捐助
- 補助申請金額：0（本年度不申請政府補助）"""
        
        if old_budget in content:
            content = content.replace(old_budget, new_budget)
        
        # 更新風險管理部分
        content = content.replace("補助申請未獲核定", "企業捐助未到位")
        content = content.replace("提前準備補助申請文件", "提前確認企業捐助意願")
        
        work_plan_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{work_plan_file.name}")


def update_reports():
    """更新報告文件"""
    print("\n更新報告文件...")
    
    # 更新年度工作報告
    annual_report = REPORTS_DIR / "報告_年度工作報告_2026.md"
    if annual_report.exists():
        content = annual_report.read_text(encoding='utf-8')
        # 將補助相關改為企業捐助
        content = content.replace("補助計畫", "企業捐助計畫")
        content = content.replace("補助收入", "企業捐助")
        annual_report.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{annual_report.name}")
    
    # 更新季度工作進度報告
    for quarter in range(1, 5):
        quarter_file = REPORTS_DIR / f"報告_季度工作進度_2026Q{quarter}.md"
        if quarter_file.exists():
            content = quarter_file.read_text(encoding='utf-8')
            content = content.replace("補助計畫", "企業捐助計畫")
            content = content.replace("補助收入", "企業捐助")
            quarter_file.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{quarter_file.name}")


def update_grant_documents():
    """更新補助相關文件，將補助申請金額設為0"""
    print("\n更新補助相關文件...")
    
    grant_file = OPERATIONAL_FILES_DIR / "03_補助申請作業規範.md"
    if grant_file.exists():
        content = grant_file.read_text(encoding='utf-8')
        
        # 在文件開頭添加說明
        note = """**重要說明**：
- 本年度（2026年）補助申請金額：0
- 本年度資金來源除會費外，全部來自企業捐助
- 本文件為規範文件，供未來參考使用

---

"""
        
        if not content.startswith("**重要說明**"):
            content = note + content
        
        grant_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{grant_file.name}")


def ensure_balance():
    """確保收支對應"""
    print("\n檢查收支對應...")
    
    # 檢查年度預算
    budget_file = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if budget_file.exists():
        content = budget_file.read_text(encoding='utf-8')
        
        # 提取收入總計
        income_match = re.search(r'收入.*?合計.*?\|.*?\|.*?\|.*?\|\s*\*\*(\d[\d,]*)\*\*', content)
        # 提取支出總計
        expense_match = re.search(r'支出.*?合計.*?\|.*?\|.*?\|.*?\|\s*\*\*(\d[\d,]*)\*\*', content)
        
        if income_match and expense_match:
            income_total = int(income_match.group(1).replace(',', ''))
            expense_total = int(expense_match.group(1).replace(',', ''))
            
            if income_total != expense_total:
                print(f"  [警告] 年度預算收支不平衡：收入 {income_total:,} vs 支出 {expense_total:,}")
            else:
                print(f"  [OK] 年度預算收支平衡：{income_total:,}")
    
    print("  收支對應檢查完成")


def main():
    """主程式"""
    print("=" * 60)
    print("更新所有產出文件格式")
    print("=" * 60)
    print()
    
    # 更新財務文件
    update_financial_documents()
    
    # 更新年度工作計畫
    update_annual_work_plan()
    
    # 更新報告文件
    update_reports()
    
    # 更新補助相關文件
    update_grant_documents()
    
    # 確保收支對應
    ensure_balance()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
