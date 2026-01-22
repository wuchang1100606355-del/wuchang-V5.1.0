#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_pos_option_tables.py

將表1和表2根據題型代碼結合

表1：題型選項和組合名稱
表2：詳細選項配置
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


# 表1：題型選項和組合名稱
TABLE1 = {
    "03913341": "S/M15/L45+溫度+甜度",
    "03913342": "S/M20/L50+溫度+甜度",
    "03913343": "拿鐵咖啡",
    "03913344": "S/M20/L55+溫度+甜度",
    "03913345": "S/M25/L65+溫度+甜度",
    "03913346": "M/L5+溫度+甜度",
    "03913347": "M/L10+溫度+甜度",
    "03913348": "M/L15+溫度+甜度",
    "03913349": "果醬口味",
    "03913350": "甜度",
    "03913351": "加口味10",
    "03913352": "加口味15",
    "03913353": "加口味20",
}

# 表2：詳細選項配置（根據圖片描述建立）
TABLE2 = {
    "03913341": [
        {"category": "尺寸", "detail": "S", "simple": "S", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400569"},
        {"category": "尺寸", "detail": "M+15", "simple": "M", "value": "15", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400570"},
        {"category": "尺寸", "detail": "L+45", "simple": "L", "value": "45", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400572"},
        {"category": "溫度", "detail": "去冰", "simple": "去冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400571"},
        {"category": "溫度", "detail": "少冰", "simple": "少冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400573"},
        {"category": "溫度", "detail": "正常冰", "simple": "正常冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400574"},
        {"category": "溫度", "detail": "溫", "simple": "溫", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400575"},
        {"category": "溫度", "detail": "熱", "simple": "熱", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400576"},
        {"category": "甜度", "detail": "無糖", "simple": "無糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400577"},
        {"category": "甜度", "detail": "正常糖", "simple": "正常糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400578"},
        {"category": "甜度", "detail": "少糖", "simple": "少糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400579"},
        {"category": "甜度", "detail": "半糖", "simple": "半糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400580"},
    ],
    "03913342": [
        {"category": "尺寸", "detail": "S", "simple": "S", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400581"},
        {"category": "尺寸", "detail": "M+20", "simple": "M", "value": "20", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400582"},
        {"category": "尺寸", "detail": "L+50", "simple": "L", "value": "50", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400583"},
        {"category": "溫度", "detail": "去冰", "simple": "去冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400584"},
        {"category": "溫度", "detail": "少冰", "simple": "少冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400585"},
        {"category": "溫度", "detail": "正常冰", "simple": "正常冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400586"},
        {"category": "溫度", "detail": "溫", "simple": "溫", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400587"},
        {"category": "溫度", "detail": "熱", "simple": "熱", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400588"},
        {"category": "甜度", "detail": "無糖", "simple": "無糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400589"},
        {"category": "甜度", "detail": "正常糖", "simple": "正常糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400590"},
        {"category": "甜度", "detail": "少糖", "simple": "少糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400591"},
        {"category": "甜度", "detail": "半糖", "simple": "半糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400592"},
    ],
    "03913343": [
        {"category": "產品", "detail": "拿鐵咖啡", "simple": "拿鐵咖啡", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400593"},
    ],
    "03913344": [
        {"category": "尺寸", "detail": "S", "simple": "S", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400594"},
        {"category": "尺寸", "detail": "M+20", "simple": "M", "value": "20", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400595"},
        {"category": "尺寸", "detail": "L+55", "simple": "L", "value": "55", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400596"},
        {"category": "溫度", "detail": "去冰", "simple": "去冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400597"},
        {"category": "溫度", "detail": "少冰", "simple": "少冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400598"},
        {"category": "溫度", "detail": "正常冰", "simple": "正常冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400599"},
        {"category": "溫度", "detail": "溫", "simple": "溫", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400600"},
        {"category": "溫度", "detail": "熱", "simple": "熱", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400601"},
        {"category": "甜度", "detail": "無糖", "simple": "無糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400602"},
        {"category": "甜度", "detail": "正常糖", "simple": "正常糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400603"},
        {"category": "甜度", "detail": "少糖", "simple": "少糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400604"},
        {"category": "甜度", "detail": "半糖", "simple": "半糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400605"},
    ],
    "03913345": [
        {"category": "尺寸", "detail": "S", "simple": "S", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400606"},
        {"category": "尺寸", "detail": "M+25", "simple": "M", "value": "25", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400607"},
        {"category": "尺寸", "detail": "L+65", "simple": "L", "value": "65", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400608"},
        {"category": "溫度", "detail": "去冰", "simple": "去冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400609"},
        {"category": "溫度", "detail": "少冰", "simple": "少冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400610"},
        {"category": "溫度", "detail": "正常冰", "simple": "正常冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400611"},
        {"category": "溫度", "detail": "溫", "simple": "溫", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400612"},
        {"category": "溫度", "detail": "熱", "simple": "熱", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400613"},
        {"category": "甜度", "detail": "無糖", "simple": "無糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400614"},
        {"category": "甜度", "detail": "正常糖", "simple": "正常糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400615"},
        {"category": "甜度", "detail": "少糖", "simple": "少糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400616"},
        {"category": "甜度", "detail": "半糖", "simple": "半糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400617"},
    ],
    "03913346": [
        {"category": "尺寸", "detail": "M", "simple": "M", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400618"},
        {"category": "尺寸", "detail": "L+5", "simple": "L", "value": "5", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400619"},
        {"category": "溫度", "detail": "去冰", "simple": "去冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400620"},
        {"category": "溫度", "detail": "少冰", "simple": "少冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400621"},
        {"category": "溫度", "detail": "正常冰", "simple": "正常冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400622"},
        {"category": "溫度", "detail": "溫", "simple": "溫", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400623"},
        {"category": "溫度", "detail": "熱", "simple": "熱", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400624"},
        {"category": "甜度", "detail": "無糖", "simple": "無糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400625"},
        {"category": "甜度", "detail": "正常糖", "simple": "正常糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400626"},
        {"category": "甜度", "detail": "少糖", "simple": "少糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400627"},
        {"category": "甜度", "detail": "半糖", "simple": "半糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400628"},
    ],
    "03913347": [
        {"category": "尺寸", "detail": "M", "simple": "M", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400629"},
        {"category": "尺寸", "detail": "L+10", "simple": "L", "value": "10", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400630"},
        {"category": "溫度", "detail": "去冰", "simple": "去冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400631"},
        {"category": "溫度", "detail": "少冰", "simple": "少冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400632"},
        {"category": "溫度", "detail": "正常冰", "simple": "正常冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400633"},
        {"category": "溫度", "detail": "溫", "simple": "溫", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400634"},
        {"category": "溫度", "detail": "熱", "simple": "熱", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400635"},
        {"category": "甜度", "detail": "無糖", "simple": "無糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400636"},
        {"category": "甜度", "detail": "正常糖", "simple": "正常糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400637"},
        {"category": "甜度", "detail": "少糖", "simple": "少糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400638"},
        {"category": "甜度", "detail": "半糖", "simple": "半糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400639"},
    ],
    "03913348": [
        {"category": "尺寸", "detail": "M", "simple": "M", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400640"},
        {"category": "尺寸", "detail": "L+15", "simple": "L", "value": "15", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400641"},
        {"category": "溫度", "detail": "去冰", "simple": "去冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400642"},
        {"category": "溫度", "detail": "少冰", "simple": "少冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400643"},
        {"category": "溫度", "detail": "正常冰", "simple": "正常冰", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400644"},
        {"category": "溫度", "detail": "溫", "simple": "溫", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400645"},
        {"category": "溫度", "detail": "熱", "simple": "熱", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400646"},
        {"category": "甜度", "detail": "無糖", "simple": "無糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400647"},
        {"category": "甜度", "detail": "正常糖", "simple": "正常糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400648"},
        {"category": "甜度", "detail": "少糖", "simple": "少糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400649"},
        {"category": "甜度", "detail": "半糖", "simple": "半糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400650"},
    ],
    "03913349": [
        {"category": "口味選擇", "detail": "花生", "simple": "花生", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400651"},
        {"category": "口味選擇", "detail": "巧克力", "simple": "巧克力", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400652"},
        {"category": "口味選擇", "detail": "奶油", "simple": "奶油", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400653"},
        {"category": "口味選擇", "detail": "辣味", "simple": "辣味", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400654"},
    ],
    "03913350": [
        {"category": "甜度", "detail": "無糖", "simple": "無糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400655"},
        {"category": "甜度", "detail": "正常糖", "simple": "正常糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400656"},
        {"category": "甜度", "detail": "少糖", "simple": "少糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400657"},
        {"category": "甜度", "detail": "半糖", "simple": "半糖", "value": "0", "type": "單", "bool": "Y", "code": "QC_OL_1_QC_OG_4400658"},
    ],
    "03913351": [
        {"category": "加口味", "detail": "焦糖+10", "simple": "焦糖", "value": "10", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400659"},
        {"category": "加口味", "detail": "香草+10", "simple": "香草", "value": "10", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400660"},
        {"category": "加口味", "detail": "愛爾蘭+10", "simple": "愛爾蘭", "value": "10", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400661"},
        {"category": "加口味", "detail": "榛果+10", "simple": "榛果", "value": "10", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400662"},
        {"category": "加口味", "detail": "黑糖+10", "simple": "黑糖", "value": "10", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400663"},
    ],
    "03913352": [
        {"category": "加口味", "detail": "交錯+15", "simple": "交錯", "value": "15", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400664"},
        {"category": "加口味", "detail": "焦糖+15", "simple": "焦糖", "value": "15", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400665"},
        {"category": "加口味", "detail": "榛果+15", "simple": "榛果", "value": "15", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400666"},
        {"category": "加口味", "detail": "愛爾蘭+15", "simple": "愛爾蘭", "value": "15", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400667"},
        {"category": "加口味", "detail": "香草+15", "simple": "香草", "value": "15", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400668"},
        {"category": "加口味", "detail": "黑糖+15", "simple": "黑糖", "value": "15", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400669"},
    ],
    "03913353": [
        {"category": "加口味", "detail": "交錯+20", "simple": "交錯", "value": "20", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400670"},
        {"category": "加口味", "detail": "焦糖+20", "simple": "焦糖", "value": "20", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400671"},
        {"category": "加口味", "detail": "香草+20", "simple": "香草", "value": "20", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400672"},
        {"category": "加口味", "detail": "榛果+20", "simple": "榛果", "value": "20", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400673"},
        {"category": "加口味", "detail": "愛爾蘭+20", "simple": "愛爾蘭", "value": "20", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400674"},
        {"category": "加口味", "detail": "黑糖+20", "simple": "黑糖", "value": "20", "type": "雙", "bool": "N", "code": "QC_OL_1_QC_OG_4400675"},
    ],
}


def merge_tables():
    """合併表1和表2"""
    print("=" * 70)
    print("合併表1和表2（根據題型代碼）")
    print("=" * 70)
    print()
    
    merged_data = []
    
    for option_id, combination_name in TABLE1.items():
        if option_id in TABLE2:
            options = TABLE2[option_id]
            for option in options:
                merged_item = {
                    "題型代碼": option_id,
                    "題型選項組合名稱": combination_name,
                    "類別": option["category"],
                    "詳細選項": option["detail"],
                    "簡化選項": option["simple"],
                    "數值": option["value"],
                    "選項類型": option["type"],
                    "布林值": option["bool"],
                    "選項代碼": option["code"],
                }
                merged_data.append(merged_item)
        else:
            # 如果表2中沒有對應的選項，仍然加入基本信息
            merged_item = {
                "題型代碼": option_id,
                "題型選項組合名稱": combination_name,
                "類別": "",
                "詳細選項": "",
                "簡化選項": "",
                "數值": "",
                "選項類型": "",
                "布林值": "",
                "選項代碼": "",
            }
            merged_data.append(merged_item)
    
    return merged_data


def generate_markdown_table(data):
    """產生 Markdown 表格"""
    if not data:
        return ""
    
    # 表頭
    headers = list(data[0].keys())
    header_row = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    
    # 資料行
    rows = [header_row, separator]
    for item in data:
        row = "| " + " | ".join(str(item.get(h, "")) for h in headers) + " |"
        rows.append(row)
    
    return "\n".join(rows)


def generate_json(data):
    """產生 JSON 格式"""
    return json.dumps(data, ensure_ascii=False, indent=2)


def main():
    """主函數"""
    print("=" * 70)
    print("POS 選項表格合併工具")
    print("=" * 70)
    print()
    
    # 合併表格
    log("正在合併表1和表2...", "PROGRESS")
    merged_data = merge_tables()
    
    log(f"合併完成，共 {len(merged_data)} 筆資料", "OK")
    print()
    
    # 產生 Markdown 表格
    markdown_table = generate_markdown_table(merged_data)
    
    # 儲存 Markdown 檔案
    md_file = BASE_DIR / "pos_options_merged.md"
    md_content = f"""# POS 選項表格（合併後）

**產生時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 合併說明

本表格是根據題型代碼將表1（題型選項組合名稱）和表2（詳細選項配置）合併而成。

## 合併後的表格

{markdown_table}

## 統計資訊

- **題型代碼數量：** {len(TABLE1)}
- **總選項數量：** {len(merged_data)}
- **合併時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    md_file.write_text(md_content, encoding="utf-8")
    log(f"Markdown 表格已儲存: {md_file}", "OK")
    
    # 儲存 JSON 檔案
    json_file = BASE_DIR / "pos_options_merged.json"
    json_content = generate_json(merged_data)
    json_file.write_text(json_content, encoding="utf-8")
    log(f"JSON 資料已儲存: {json_file}", "OK")
    
    # 顯示統計
    print()
    print("=" * 70)
    print("【統計資訊】")
    print("=" * 70)
    print()
    
    category_count = {}
    for item in merged_data:
        category = item.get("類別", "")
        if category:
            category_count[category] = category_count.get(category, 0) + 1
    
    print("類別分布：")
    for category, count in sorted(category_count.items()):
        print(f"  {category}: {count} 個選項")
    
    print()
    print(f"總題型代碼: {len(TABLE1)}")
    print(f"總選項數: {len(merged_data)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
