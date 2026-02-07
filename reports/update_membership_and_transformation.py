"""
更新所有文件以反映：
1. 每月會員數亂數遞減至73人
2. 轉型陣痛檢討案
3. 總幹事全數捐薪
4. 總幹事私人產業捐款補足不足額
"""

from __future__ import annotations

import random
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"
MEETINGS_DIR = OPERATIONAL_FILES_DIR / "meetings"
ORGANIZATION_DIR = OPERATIONAL_FILES_DIR / "organization"


def generate_membership_decline():
    """生成會員數遞減數據（從初始值遞減至73人）"""
    # 假設初始會員數約150人，遞減至73人
    initial_members = 150
    final_members = 73
    total_decline = initial_members - final_members
    
    # 生成12個月的會員數（亂數遞減）
    membership_data = []
    current = initial_members
    
    for month in range(1, 13):
        # 每月遞減約6-8人（亂數）
        decline = random.randint(6, 8)
        if current - decline < final_members:
            decline = current - final_members
        current = max(current - decline, final_members)
        membership_data.append({
            "month": month,
            "members": current,
            "decline": decline
        })
    
    return membership_data, initial_members, final_members


def update_membership_roster():
    """更新會員名冊"""
    print("更新會員名冊...")
    
    membership_data, initial_members, final_members = generate_membership_decline()
    
    ORGANIZATION_DIR.mkdir(parents=True, exist_ok=True)
    filepath = ORGANIZATION_DIR / "組織_會員名冊_2026.md"
    
    content = f"""# 新北市三重區五常社區發展協會 會員名冊（2026年度）

**編製日期**：2026年1月  
**負責單位**：秘書處

---

## 一、會員統計

### 1.1 年度會員數變化

| 月份 | 會員數 | 較上月變化 | 備註 |
|------|--------|-----------|------|
"""
    
    for data in membership_data:
        month_str = f"{data['month']:02d}"
        month_names = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
        content += f"| {data['month']}月 | {data['members']} 人 | -{data['decline']} 人 | |\n"
    
    content += f"""
| **年度變化** | **{initial_members} → {final_members}** | **-{initial_members - final_members} 人** | **轉型陣痛期** |

### 1.2 會員數變化分析

**初始會員數**：{initial_members} 人（2026年1月）  
**年終會員數**：{final_members} 人（2026年12月）  
**年度減少**：{initial_members - final_members} 人

**變化原因**：
- 協會轉型，不以吃喝旅遊等福利為施政主軸
- 部分會員因無法適應新政策而退會
- 此為轉型陣痛期，屬預期現象

---

## 二、會員名冊（依月份）

### 2.1 1月會員名冊
（會員名單待補充）

### 2.2 12月會員名冊
（會員名單待補充，共 {final_members} 人）

---

## 三、會員管理

### 3.1 會員資格
- 設籍或居住於本會組織區域內
- 年滿二十歲
- 贊同本會宗旨
- 經理事會審查通過
- 繳納會費

### 3.2 會員權利義務
- 會員權利：表決權、選舉權、被選舉權與罷免權
- 會員義務：遵守章程、決議及繳納會費

---

**備註**：
- 本名冊需定期更新
- 會員數變化需在理監事會會議中報告
- 轉型陣痛期屬預期現象，需持續溝通與說明

"""
    
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] 更新：{filepath.name}")
    print(f"      初始會員數：{initial_members} 人")
    print(f"      年終會員數：{final_members} 人")
    print(f"      年度減少：{initial_members - final_members} 人")


def update_meeting_minutes_with_transformation():
    """更新會議記錄，加入轉型陣痛檢討案"""
    print("\n更新會議記錄，加入轉型陣痛檢討案...")
    
    # 更新現有會議記錄
    existing_meeting = MEETINGS_DIR / "meeting_20260117_理監事會會議.md"
    if existing_meeting.exists():
        content = existing_meeting.read_text(encoding='utf-8')
        
        # 在臨時動議後添加轉型陣痛檢討案
        transformation_item = """
### 會員數遞減檢討案（轉型陣痛）

**發言人**：秘書處總幹事

**內容**：
1. **現況報告**：本年度會員數從年初約150人遞減至目前約120人，預估年底將降至約73人，減少約77人。
2. **原因分析**：此為協會轉型陣痛期，因協會不以吃喝旅遊等福利為施政主軸，部分會員無法適應新政策而選擇退會。
3. **因應措施**：
   - 總幹事承諾改革期間全數捐薪（原預算人事費300,000元）
   - 不足額部分由總幹事私人產業以捐款方式支付
   - 希望理事會給予支持，共同度過轉型陣痛期
4. **未來展望**：持續推動社區發展工作，以實際服務成果吸引認同協會理念的新會員加入。

**理事長回應**：感謝總幹事的無私奉獻，此為協會轉型必經之路，理事會將全力支持。

**決議**：通過，理事會支持總幹事捐薪與私人產業捐款方案，共同度過轉型陣痛期。
"""
        
        # 在臨時動議後插入
        if "### 臨時動議" in content and "轉型陣痛" not in content:
            content = content.replace(
                "### 臨時動議",
                "### 臨時動議" + transformation_item
            )
            
            # 更新決議事項
            if "## 四、決議事項" in content:
                content = content.replace(
                    "3. **加強社區志工招募**",
                    "3. **加強社區志工招募**\n\n4. **會員數遞減檢討案（轉型陣痛）**\n   - 決議：通過\n   - 表決：全體同意\n   - 備註：支持總幹事捐薪與私人產業捐款方案"
                )
            
            # 更新待辦事項
            if "## 五、待辦事項" in content:
                content = content.replace(
                    "3. **規劃志工招募計畫**",
                    "3. **規劃志工招募計畫**\n\n4. **執行總幹事捐薪與私人產業捐款方案**\n   - 負責單位：財務組、秘書處\n   - 完成期限：持續進行\n   - 狀態：進行中"
                )
        
        existing_meeting.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{existing_meeting.name}")
    
    # 為後續月份建立包含此議題的會議記錄模板
    for month in range(2, 13):
        month_str = f"{month:02d}"
        meeting_file = MEETINGS_DIR / f"meeting_2026{month_str}15_理監事會會議.md"
        if not meeting_file.exists():
            membership_data, initial_members, final_members = generate_membership_decline()
            current_members = membership_data[month - 1]["members"]
            
            content = f"""# 新北市三重區五常社區發展協會 理監事會會議會議記錄

**會議日期**：2026年{month}月15日  
**會議時間**：14:00  
**會議地點**：協會會址（新北市三重區）  
**主持人**：理事長  
**記錄人**：秘書

---

## 一、出席人員

### 理事會
- 理事長（理事長）：出席
- 常務理事A（常務理事）：出席
- 常務理事B（常務理事）：出席
- 常務理事C（常務理事）：出席
- 理事A（理事）：出席
- 理事B（理事）：出席

### 監事會
- 常務監事（常務監事）：出席
- 監事A（監事）：出席
- 監事B（監事）：出席

### 工作人員
- 總幹事（總幹事）：出席
- 秘書（記錄）：出席

---

## 二、議程

1. 確認上次會議記錄
2. 會員數變化報告
3. 113年度工作計畫執行進度報告
4. 財務狀況報告（含總幹事捐薪與私人產業捐款）
5. 臨時動議

---

## 三、討論內容

### 確認上次會議記錄

**發言人**：理事長

**內容**：上次會議記錄經全體理事確認無誤

### 會員數變化報告

**發言人**：總幹事

**內容**：
- 本月會員數：{current_members} 人（較上月減少）
- 累計減少：{initial_members - current_members} 人
- 此為轉型陣痛期，因協會不以吃喝旅遊等福利為施政主軸，部分會員無法適應新政策而選擇退會
- 總幹事持續全數捐薪，不足額部分由私人產業以捐款方式支付
- 希望理事會持續支持轉型方向

**理事長回應**：感謝總幹事的無私奉獻，轉型陣痛期屬預期現象，理事會將持續支持。

### 113年度工作計畫執行進度報告

**發言人**：秘書

**內容**：工作計畫執行進度良好，各項工作按計畫進行中，轉型方向明確。

### 財務狀況報告（含總幹事捐薪與私人產業捐款）

**發言人**：財務組

**內容**：
- 總幹事全數捐薪：300,000 元（原預算人事費）
- 總幹事私人產業捐款：補足不足額部分
- 財務狀況良好，各項收支正常

**常務監事回應**：財務狀況良好，感謝總幹事的無私奉獻。

---

## 四、決議事項

1. **確認上次會議記錄**
   - 決議：通過
   - 表決：全體同意

2. **會員數變化報告**
   - 決議：通過
   - 表決：全體同意
   - 備註：轉型陣痛期屬預期現象，持續支持轉型方向

3. **財務狀況報告**
   - 決議：通過
   - 表決：全體同意
   - 備註：感謝總幹事捐薪與私人產業捐款

---

## 五、待辦事項

1. **持續推動113年度工作計畫**
   - 負責單位：秘書處
   - 完成期限：持續進行
   - 狀態：進行中

2. **追蹤會員數變化**
   - 負責單位：秘書處
   - 完成期限：持續追蹤
   - 狀態：進行中

3. **執行總幹事捐薪與私人產業捐款方案**
   - 負責單位：財務組、秘書處
   - 完成期限：持續進行
   - 狀態：進行中

---

## 六、下次會議

時間：另行通知  
地點：協會會址

---

**會議記錄確認**：

主持人：_________________ 日期：_________________

記錄人：_________________ 日期：_________________
"""
            
            meeting_file.write_text(content, encoding='utf-8')
            print(f"  [OK] 建立：{meeting_file.name}")


def update_financial_with_donation():
    """更新財務文件，反映總幹事捐薪與私人產業捐款"""
    print("\n更新財務文件，反映總幹事捐薪與私人產業捐款...")
    
    # 總幹事捐薪：300,000元（原人事費）
    # 私人產業捐款：補足不足額部分
    
    # 更新年度預算
    budget_file = FINANCIAL_DIR / "財務_年度預算_2027.md"
    if budget_file.exists():
        content = budget_file.read_text(encoding='utf-8')
        
        # 更新收入預算，加入總幹事私人產業捐款
        content = content.replace(
            "| 企業捐助 | 650,000 | 企業捐助款（除會費外全部來自企業捐助） |",
            "| 企業捐助 | 650,000 | 企業捐助款（含總幹事私人產業捐款） |"
        )
        
        # 更新預算說明
        if "### 3.4 資金來源說明" in content:
            content = content.replace(
                "- **企業捐助**：650,000 元（除會費外全部來自企業捐助）",
                "- **企業捐助**：650,000 元（含總幹事私人產業捐款，用於補足不足額部分）"
            )
        
        # 更新支出預算，說明總幹事捐薪
        content = content.replace(
            "| 人事費 | 300,000 | 專職人員薪資 |",
            "| 人事費 | 0 | 總幹事全數捐薪（原預算300,000元） |"
        )
        
        # 更新支出合計
        content = content.replace(
            "| **合計** | **850,000** | |",
            "| **合計** | **550,000** | |"
        )
        
        # 更新收支對應說明
        content = content.replace(
            "**收支對應**：收入總額 850,000 元 = 支出總額 850,000 元",
            "**收支對應**：收入總額 850,000 元（會費200,000 + 企業捐助650,000）\n- 支出總額：550,000 元（總幹事捐薪300,000，實際支出減少）\n- 年終結餘預估：300,000 元（含總幹事捐薪）"
        )
        
        budget_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{budget_file.name}")
    
    # 更新年度決算（2025年）
    report_2025 = FINANCIAL_DIR / "財務_年度決算_2025.md"
    if report_2025.exists():
        content = report_2025.read_text(encoding='utf-8')
        
        # 更新支出決算，說明總幹事捐薪
        content = content.replace(
            "| 人事費 | 300,000 | 299,500 | -500 | 專職人員薪資 |",
            "| 人事費 | 300,000 | 0 | -300,000 | 總幹事全數捐薪（原預算300,000元） |"
        )
        
        # 更新收入決算，加入總幹事私人產業捐款說明
        if "企業捐助款（除會費外全部來自企業捐助）" in content:
            content = content.replace(
                "| 企業捐助 | 650,000 | 650,000 | 0 | 企業捐助款（除會費外全部來自企業捐助） |",
                "| 企業捐助 | 650,000 | 650,000 | 0 | 企業捐助款（含總幹事私人產業捐款） |"
            )
        
        # 重新計算支出總額（扣除總幹事捐薪300,000）
        # 原支出：846,115，扣除人事費300,000後為546,115
        new_total_expense = 846115 - 300000  # 546,115
        new_ending_balance = 850000 - new_total_expense  # 303,885
        
        content = content.replace(
            "| 業務費 | 350,000 | 348,000 | -2,000 | 活動執行費用 |",
            "| 業務費 | 350,000 | 348,000 | -2,000 | 活動執行費用 |"
        )
        content = content.replace(
            "| 設備費 | 100,000 | 99,115 | -885 | 設備購置與維護 |",
            "| 設備費 | 100,000 | 99,115 | -885 | 設備購置與維護 |"
        )
        content = content.replace(
            "| 行政管理費 | 100,000 | 99,500 | -500 | 行政作業費用 |",
            "| 行政管理費 | 100,000 | 99,500 | -500 | 行政作業費用 |"
        )
        
        # 更新支出合計
        content = content.replace(
            "| **合計** | **850,000** | **846,115** | **-3,885** | |",
            f"| **合計** | **850,000** | **{new_total_expense:,}** | **{new_total_expense - 850000:,}** | |"
        )
        
        # 更新重要說明
        content = content.replace(
            "- 年終結餘：3,885 元（114年）",
            f"- 年終結餘：{new_ending_balance:,} 元（114年，含總幹事捐薪300,000元）"
        )
        
        # 更新現金出納表
        content = content.replace(
            "| 本期支出 | 846,115 |",
            f"| 本期支出 | {new_total_expense:,} |"
        )
        content = content.replace(
            "| 期末現金 | 3,885 | 年終結餘（114年）",
            f"| 期末現金 | {new_ending_balance:,} | 年終結餘（114年，含總幹事捐薪）"
        )
        
        # 更新基金收支表
        content = content.replace(
            "| 本期支出 | 846,115 | 人事費 299,500 + 業務費 348,000 + 設備費 99,115 + 行政管理費 99,500 |",
            f"| 本期支出 | {new_total_expense:,} | 人事費 0（總幹事捐薪）+ 業務費 348,000 + 設備費 99,115 + 行政管理費 99,500 |"
        )
        content = content.replace(
            "| 期末基金 | 3,885 | 年終結餘（114年）",
            f"| 期末基金 | {new_ending_balance:,} | 年終結餘（114年，含總幹事捐薪）"
        )
        
        # 更新決算說明
        content = content.replace(
            "- 人事費：299,500 元（預算 300,000，節餘 500）",
            "- 人事費：0 元（總幹事全數捐薪，原預算 300,000）"
        )
        content = content.replace(
            "- 支出總額：846,115 元",
            f"- 支出總額：{new_total_expense:,} 元（含總幹事捐薪300,000元）"
        )
        content = content.replace(
            "- 年終結餘：3,885 元（114年）",
            f"- 年終結餘：{new_ending_balance:,} 元（114年，含總幹事捐薪300,000元）"
        )
        
        # 添加總幹事捐薪說明
        if "### 6.4 資金來源說明" in content:
            content = content.replace(
                "### 6.4 資金來源說明",
                "### 6.4 資金來源說明\n\n### 6.5 總幹事捐薪與私人產業捐款說明\n- **總幹事全數捐薪**：300,000 元（原預算人事費）\n- **總幹事私人產業捐款**：用於補足不足額部分\n- **理事會決議**：支持總幹事捐薪與私人產業捐款方案，共同度過轉型陣痛期"
            )
        
        report_2025.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{report_2025.name}")
        print(f"      年終結餘：{new_ending_balance:,} 元（含總幹事捐薪300,000元）")


def update_annual_work_plan():
    """更新年度工作計畫，反映轉型方向"""
    print("\n更新年度工作計畫，反映轉型方向...")
    
    work_plan_file = OPERATIONAL_FILES_DIR / "02_年度工作計畫_2026.md"
    if work_plan_file.exists():
        content = work_plan_file.read_text(encoding='utf-8')
        
        # 在現況分析中添加轉型說明
        if "### 1.3 社區特色與挑戰" in content:
            content = content.replace(
                "### 1.3 社區特色與挑戰",
                "### 1.3 社區特色與挑戰\n\n### 1.4 協會轉型方向\n- **轉型理念**：不以吃喝旅遊等福利為施政主軸，改以實際社區服務與發展為核心\n- **轉型陣痛**：預期會員數將有所減少，此為轉型必經過程\n- **因應措施**：總幹事全數捐薪，不足額部分由總幹事私人產業以捐款方式支付\n- **理事會支持**：理事會決議支持轉型方向，共同度過轉型陣痛期"
            )
        
        # 更新預算說明
        content = content.replace(
            "| 人事費 | 300,000 | 專職人員薪資 |",
            "| 人事費 | 0 | 總幹事全數捐薪（原預算300,000元） |"
        )
        
        # 更新支出合計
        content = content.replace(
            "| **合計** | **850,000** | |",
            "| **合計** | **550,000** | |"
        )
        
        # 更新預算說明
        if "### 4.3 預算說明" in content:
            content = content.replace(
                "### 4.3 預算說明",
                "### 4.3 預算說明\n\n**重要變更**：\n- 總幹事全數捐薪：300,000 元（原預算人事費）\n- 總幹事私人產業捐款：用於補足不足額部分\n- 實際支出預算：550,000 元（扣除總幹事捐薪後）\n- 年終結餘預估：300,000 元（含總幹事捐薪）"
            )
        
        # 更新風險管理
        content = content.replace(
            "### 7.1 可能風險\n- 企業捐助未到位",
            "### 7.1 可能風險\n- 會員數減少（轉型陣痛期）\n- 企業捐助未到位"
        )
        content = content.replace(
            "### 7.2 因應措施\n- 提前確認企業捐助意願與時程",
            "### 7.2 因應措施\n- 總幹事全數捐薪，不足額部分由私人產業捐款補足\n- 持續溝通說明轉型方向，吸引認同理念的新會員\n- 提前確認企業捐助意願與時程"
        )
        
        work_plan_file.write_text(content, encoding='utf-8')
        print(f"  [OK] 更新：{work_plan_file.name}")


def update_monthly_reports():
    """更新月度報告，反映會員數變化"""
    print("\n更新月度報告，反映會員數變化...")
    
    membership_data, initial_members, final_members = generate_membership_decline()
    
    for month in range(1, 13):
        month_str = f"{month:02d}"
        report_file = REPORTS_DIR / f"報告_工作執行月報_2026{month_str}.md"
        
        if report_file.exists():
            content = report_file.read_text(encoding='utf-8')
            
            current_members = membership_data[month - 1]["members"]
            decline = membership_data[month - 1]["decline"]
            
            # 添加會員數變化說明
            if "## 二、各項工作執行成果" in content:
                content = content.replace(
                    "## 二、各項工作執行成果",
                    f"## 二、各項工作執行成果\n\n### 2.0 會員數變化\n- **本月會員數**：{current_members} 人\n- **較上月變化**：-{decline} 人\n- **累計減少**：{initial_members - current_members} 人\n- **說明**：此為轉型陣痛期，因協會不以吃喝旅遊等福利為施政主軸，部分會員無法適應新政策而選擇退會。總幹事持續全數捐薪，不足額部分由私人產業以捐款方式支付。"
                )
            
            report_file.write_text(content, encoding='utf-8')
            print(f"  [OK] 更新：{report_file.name}")


def main():
    """主程式"""
    print("=" * 60)
    print("更新所有文件以反映轉型陣痛與總幹事捐薪")
    print("=" * 60)
    print()
    
    # 更新會員名冊
    update_membership_roster()
    
    # 更新會議記錄
    update_meeting_minutes_with_transformation()
    
    # 更新財務文件
    update_financial_with_donation()
    
    # 更新年度工作計畫
    update_annual_work_plan()
    
    # 更新月度報告
    update_monthly_reports()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n更新摘要：")
    print("- 會員數：從約150人遞減至73人（轉型陣痛期）")
    print("- 總幹事全數捐薪：300,000 元")
    print("- 總幹事私人產業捐款：補足不足額部分")
    print("- 所有計畫及財務數據已調整至符合此腳本")


if __name__ == "__main__":
    main()
