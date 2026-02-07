"""
統計上品食品行總捐助金額（包含初期投資）
"""

from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"

DONOR_COMPANY = "上品食品行"
DONOR_TAX_ID = "34778660"
DONOR_FULL = f"{DONOR_COMPANY}（統一編號：{DONOR_TAX_ID}）"

# 初期投資項目（從帳本記錄）
INITIAL_INVESTMENTS = [
    {
        "date": "2024/03/18",
        "item": "拆除工程及垃圾清運",
        "amount": 68000,
        "description": "拆除工程費用（含垃圾清運3車，每車14,000元，共42,000元；小工工資每天2,200元共3天，共6,600元；工具、袋子、便當等費用約19,400元，因有志工協助故需提供便當）"
    },
    {
        "date": "2024/06/12",
        "item": "木工材料費",
        "amount": 195000,
        "description": "店裝潢初期投資"
    },
    {
        "date": "2024/07/01",
        "item": "水電工程（自行施工）",
        "amount": 62300,
        "description": "全店8平方電線、220v高壓電6迴路、110v 8迴路、水管8分壓接管、軌道燈3排、圓頂燈兩座（自行施工，完工日期僅作參考）"
    },
    {
        "date": "2024/07/01",
        "item": "披土及噴漆材料費（自行施工）",
        "amount": 45000,
        "description": "全戶2次披土家手工噴漆材料費（自行施工，無工資成本）"
    },
    {
        "date": "2024",
        "item": "吧檯設計及材料、後方櫃體總成",
        "amount": 60000,
        "description": "吧檯設計及材料費、後方櫃體總成"
    },
    {
        "date": "2024",
        "item": "自行施工材料費（釘工）",
        "amount": 60000,
        "description": "自行釘工材料費（自行施工，無工資成本；若委外施作，市價25萬元以上）"
    },
    # 可繼續添加其他投資項目
]


def extract_donation_amounts():
    """提取所有上品食品行捐助金額"""
    donations = []
    
    # 2025年決算
    filepath_2025 = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if filepath_2025.exists():
        content = filepath_2025.read_text(encoding='utf-8')
        
        # 提取上品食品行捐助金額
        match = re.search(r'\| 上品食品行捐助 \| (\d+(?:,\d+)?) \| (\d+(?:,\d+)?) \|', content)
        if match:
            amount = int(match.group(2).replace(',', ''))
            donations.append({
                "year": "2025",
                "type": "決算",
                "amount": amount,
                "description": "上品食品行捐助（含原企業捐助17,500元，補足年終結餘不足額）"
            })
    
    # 2027年預算（預估需要補足的金額）
    filepath_2027 = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if filepath_2027.exists():
        content = filepath_2027.read_text(encoding='utf-8')
        
        # 提取預估需要補足的金額
        match = re.search(r'年終結餘預估：-(\d+(?:,\d+)?) 元（需由上品食品行', content)
        if match:
            amount = int(match.group(1).replace(',', ''))
            donations.append({
                "year": "2027",
                "type": "預算（預估需要）",
                "amount": amount,
                "description": "預估需要上品食品行捐助補足年終結餘不足額"
            })
    
    return donations


def main():
    """主程式"""
    print("=" * 70)
    print(f"統計{DONOR_FULL}總投入金額（含捐助與初期投資）")
    print("=" * 70)
    print()
    
    # 1. 提取財務文件中的捐助金額
    donations = extract_donation_amounts()
    
    # 2. 初期投資項目
    print("一、初期投資項目：")
    print()
    initial_total = 0
    for i, inv in enumerate(INITIAL_INVESTMENTS, 1):
        print(f"{i}. {inv['item']}")
        print(f"   日期：{inv['date']}")
        print(f"   金額：{inv['amount']:,} 元")
        print(f"   說明：{inv['description']}")
        print()
        initial_total += inv['amount']
    
    print(f"初期投資小計：{initial_total:,} 元")
    print()
    print("=" * 70)
    print()
    
    # 3. 財務文件中的捐助金額
    print("二、財務文件中的捐助金額：")
    print()
    donation_total = 0
    if donations:
        for i, donation in enumerate(donations, 1):
            print(f"{i}. {donation['year']}年 {donation['type']}")
            print(f"   金額：{donation['amount']:,} 元")
            print(f"   說明：{donation['description']}")
            print()
            donation_total += donation['amount']
    else:
        print("未找到上品食品行捐助記錄")
    
    if donations:
        print(f"財務捐助小計：{donation_total:,} 元")
        print()
    
    print("=" * 70)
    
    # 4. 總計
    grand_total = initial_total + donation_total
    print(f"總投入金額：{grand_total:,} 元")
    print(f"  - 初期投資：{initial_total:,} 元")
    print(f"  - 財務捐助：{donation_total:,} 元")
    print("=" * 70)
    print()
    
    # 5. 詳細分析
    print("詳細分析：")
    print()
    
    # 初期投資分析
    print("初期投資項目：")
    for inv in INITIAL_INVESTMENTS:
        print(f"  - {inv['date']} {inv['item']}：{inv['amount']:,} 元")
    print()
    
    # 財務捐助分析
    if any(d['year'] == '2025' for d in donations):
        donation_2025 = next(d for d in donations if d['year'] == '2025')
        print("財務捐助明細（2025年）：")
        print(f"  - 實際捐助：{donation_2025['amount']:,} 元")
        print(f"    * 含原企業捐助：17,500 元")
        print(f"    * 不足額補助：{donation_2025['amount'] - 17500:,} 元")
        print()
    
    if any(d['year'] == '2027' for d in donations):
        donation_2027 = next(d for d in donations if d['year'] == '2027')
        print(f"財務預估（2027年）：")
        print(f"  - 預估需要：{donation_2027['amount']:,} 元（預算，尚未實際捐助）")
        print()
    
    print("備註：")
    print("- 初期投資：實際投入金額（含材料費及小工工資）")
    print("- 自行施工：用戶自行施工部分無工資成本（木工、水電、披土噴漆、釘工等）")
    print("- 自行施工說明：用戶表示「自己圈工錢給自己有點白癡所以就不算了」，")
    print("  因此統計中未計算用戶自行施工的人工成本")
    print("- 市價參考：自行釘工部分若委外施作，市價約25萬元以上")
    print("- 財務捐助：2025年為實際決算金額，2027年為預算預估")
    print("- 總投入金額不含用戶自行施工的人工成本（含木工、水電、披土噴漆、釘工等）")
    print("- 總投入金額不含2027年預估金額（尚未實際捐助）")
    print("- 若含自行施工人工成本市值，總投入金額將大幅增加（估計可增加數十萬至上百萬）")


if __name__ == "__main__":
    main()
