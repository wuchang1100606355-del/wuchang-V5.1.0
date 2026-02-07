"""
刪除企業捐助，全改由上品食品行認列
"""

from __future__ import annotations

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"
MEETINGS_DIR = OPERATIONAL_FILES_DIR / "meetings"

DONOR_COMPANY = "上品食品行"
DONOR_TAX_ID = "34778660"
DONOR_FULL = f"{DONOR_COMPANY}（統一編號：{DONOR_TAX_ID}）"


def update_financial_report_2025():
    """更新2025年度決算"""
    print("更新2025年度決算...")
    
    filepath = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 刪除企業捐助行，合併到上品食品行捐助
    # 先讀取當前的企業捐助金額
    match = re.search(r'\| 企業捐助 \| (\d+(?:,\d+)?) \| (\d+(?:,\d+)?) \|', content)
    if match:
        corporate_donation = int(match.group(2).replace(',', ''))
    else:
        corporate_donation = 17500
    
    # 刪除企業捐助行
    content = re.sub(
        r'\| 企業捐助 \|.*?\|\n',
        '',
        content
    )
    
    # 更新不足額補助，合併企業捐助金額
    content = re.sub(
        r'\| 不足額補助 \| (\d+(?:,\d+)?) \| (\d+(?:,\d+)?) \| 0 \| 上品食品行（統一編號：34778660）捐贈（補足年度營運虧損，每月負數向上品食品行申請） \|',
        lambda m: f'| 上品食品行捐助 | {int(m.group(2).replace(",", "")) + corporate_donation:,} | {int(m.group(2).replace(",", "")) + corporate_donation:,} | 0 | {DONOR_FULL}捐贈（含原企業捐助{corporate_donation:,}元，補足年度營運虧損，每月負數向上品食品行申請） |',
        content
    )
    
    # 更新收入總額說明
    content = re.sub(
        r'- 收入總額：(\d+(?:,\d+)?) 元（會費0 \+ 企業捐助(\d+(?:,\d+)?) \+ 產業收入(\d+(?:,\d+)?) \+ 講師回捐(\d+(?:,\d+)?) \+ 不足額補助(\d+(?:,\d+)?)）',
        lambda m: f'- 收入總額：{int(m.group(1).replace(",", "")):,} 元（會費0 + 上品食品行捐助{int(m.group(2).replace(",", "")) + int(m.group(5).replace(",", "")):,} + 產業收入{m.group(3)} + 講師回捐{m.group(4)}）',
        content
    )
    
    # 更新現金出納表
    content = re.sub(
        r'會費0（去年年初停收）\+ 企業捐助(\d+(?:,\d+)?) \+ 產業收入(\d+(?:,\d+)?) \+ 講師回捐(\d+(?:,\d+)?) \+ 不足額補助(\d+(?:,\d+)?)（上品食品行（統一編號：34778660）捐贈，每月負數申請）',
        lambda m: f'會費0（去年年初停收）+ 上品食品行捐助{int(m.group(1).replace(",", "")) + int(m.group(4).replace(",", "")):,}（{DONOR_FULL}，每月負數申請）+ 產業收入{m.group(2)} + 講師回捐{m.group(3)}',
        content
    )
    
    # 更新基金收支表
    content = re.sub(
        r'會費 0（去年年初停收）\+ 企業捐助 (\d+(?:,\d+)?) \+ 產業收入 (\d+(?:,\d+)?) \+ 講師回捐 (\d+(?:,\d+)?) \+ 不足額補助 (\d+(?:,\d+)?)（上品食品行（統一編號：34778660）捐贈，每月負數申請）',
        lambda m: f'會費 0（去年年初停收）+ 上品食品行捐助 {int(m.group(1).replace(",", "")) + int(m.group(4).replace(",", "")):,}（{DONOR_FULL}，每月負數申請）+ 產業收入 {m.group(2)} + 講師回捐 {m.group(3)}',
        content
    )
    
    # 更新資金來源說明
    content = re.sub(
        r'- \*\*企業捐助\*\*：(\d+(?:,\d+)?) 元（產業收入逐步取代）',
        '',
        content
    )
    
    content = re.sub(
        r'- \*\*不足額補助\*\*：(\d+(?:,\d+)?) 元（由上品食品行（統一編號：34778660）捐贈，補足年度營運虧損，每月負數向上品食品行申請）',
        lambda m: f'- **上品食品行捐助**：{int(m.group(1).replace(",", "")) + corporate_donation:,} 元（{DONOR_FULL}，含原企業捐助{corporate_donation:,}元，補足年度營運虧損，每月負數向上品食品行申請）',
        content
    )
    
    # 更新重要說明
    content = re.sub(
        r'- 本年度資金來源除會費外，全部來自企業捐助與講師回捐',
        f'- 本年度資金來源除會費外，全部來自{DONOR_FULL}捐助與講師回捐',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      企業捐助已刪除，合併到上品食品行捐助")


def update_financial_budget_2027():
    """更新2027年度預算"""
    print("\n更新2027年度預算...")
    
    filepath = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if not filepath.exists():
        return
    
    content = filepath.read_text(encoding='utf-8')
    
    # 刪除企業捐助行
    content = re.sub(
        r'\| 企業捐助 \|.*?\|\n',
        '',
        content
    )
    
    # 更新不足額補助
    content = re.sub(
        r'- \*\*不足額補助\*\*：由上品食品行（統一編號：34778660）捐贈補足',
        f'- **上品食品行捐助**：由{DONOR_FULL}捐贈補足（含原企業捐助）',
        content
    )
    
    # 更新資金來源說明
    content = re.sub(
        r'- \*\*企業捐助\*\*：17,500 元（產業收入逐步取代）',
        '',
        content
    )
    
    # 更新重要說明
    content = re.sub(
        r'- 本年度資金來源除會費外，來自企業捐助、產業收入與講師回捐',
        f'- 本年度資金來源除會費外，來自{DONOR_FULL}捐助、產業收入與講師回捐',
        content
    )
    
    # 更新收支對應
    content = re.sub(
        r'收入總額 1,085,600 元（會費170,400 \+ 企業捐助17,500 \+ 產業收入632,500 \+ 講師回捐265,200）',
        f'收入總額 1,085,600 元（會費170,400 + 上品食品行捐助17,500 + 產業收入632,500 + 講師回捐265,200）',
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
    
    # 刪除企業捐助相關內容
    content = re.sub(
        r'\| 企業捐助 \|.*?\|\n',
        '',
        content
    )
    
    content = re.sub(
        r'- \*\*企業捐助\*\*：17,500 元（產業收入逐步取代）',
        '',
        content
    )
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("刪除企業捐助，全改由上品食品行認列")
    print("=" * 60)
    print()
    print(f"捐助單位：{DONOR_FULL}")
    print()
    
    # 更新財務文件
    update_financial_report_2025()
    update_financial_budget_2027()
    
    # 更新年度工作計畫
    update_annual_work_plan()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print("- 企業捐助已刪除")
    print(f"- 全部改由{DONOR_FULL}認列")
    print("- 原企業捐助金額已合併到上品食品行捐助")


if __name__ == "__main__":
    main()
