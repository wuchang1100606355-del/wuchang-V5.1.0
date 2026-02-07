#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讀取並分析菜單 Excel 檔案"""
import pandas as pd
import os
import json

# 查找菜單檔案
possible_paths = [
    r"C:\Users\o0930\OneDrive\匯出菜單-聊閣社區咖啡重新店-QC_1761234789387.xlsx",
    r"C:\Users\o0930\OneDrive (1)\匯出菜單-聊閣社區咖啡重新店-QC_1761234789387.xlsx",
]

excel_file = None
for path in possible_paths:
    if os.path.exists(path):
        excel_file = path
        break

if not excel_file:
    print("搜尋菜單檔案中...")
    for root, dirs, files in os.walk(r"C:\Users\o0930"):
        if root.count(os.sep) - r"C:\Users\o0930".count(os.sep) > 3:
            del dirs[:]
            continue
        for file in files:
            if "菜單" in file and file.endswith('.xlsx'):
                excel_file = os.path.join(root, file)
                print(f"找到: {excel_file}")
                break
        if excel_file:
            break

if excel_file and os.path.exists(excel_file):
    print(f"\n✓ 分析菜單檔案: {excel_file}\n")
    print("=" * 80)

    # 讀取所有工作表
    xls = pd.ExcelFile(excel_file)
    print(f"工作表: {xls.sheet_names}\n")

    # 讀取第一個工作表
    df = pd.read_excel(excel_file, sheet_name=0)
    print(f"總行數: {len(df)}")
    print(f"欄位: {list(df.columns)}\n")

    print("前 20 列 (含標題):")
    print("-" * 80)
    for idx, row in df.head(20).iterrows():
        print(f"{idx+1:2d}. {row.to_dict()}")
    print("-" * 80)

    # 保存分析結果為 JSON
    output_file = r"C:\wuchang V5.1.0\downloads\menu_analysis.json"
    analysis = {
        "source_file": excel_file,
        "total_rows": len(df),
        "columns": df.columns.tolist(),
        "sheet_names": xls.sheet_names,
        "data": df.to_dict('records')
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 分析結果已保存至: {output_file}")

else:
    print("✗ 無法找到菜單檔案")
    print("預期路徑:")
    for p in possible_paths:
        print(f"  - {p}")
