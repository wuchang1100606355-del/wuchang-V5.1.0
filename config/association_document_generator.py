"""
新北市三重區五常社區發展協會 法定文件自動生成系統

功能：
1. 依據法定頻率生成完整營運期間應產出文件
2. 建立文件模板
3. 自動生成文件清單
4. 追蹤文件產出狀態
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# 系統基礎路徑
BASE_DIR = Path(__file__).resolve().parent
OPERATIONAL_FILES_DIR = BASE_DIR / "association_operational_files"
FINANCIAL_DIR = OPERATIONAL_FILES_DIR / "financial"
REPORTS_DIR = OPERATIONAL_FILES_DIR / "reports"
ACTIVITIES_DIR = OPERATIONAL_FILES_DIR / "activities"
GRANTS_DIR = OPERATIONAL_FILES_DIR / "grants"
ORGANIZATION_DIR = OPERATIONAL_FILES_DIR / "organization"
MEETINGS_DIR = OPERATIONAL_FILES_DIR / "meetings"


class DocumentGenerator:
    """法定文件生成系統"""
    
    def __init__(self, year: int = 2026):
        self.year = year
        self.operational_files_dir = OPERATIONAL_FILES_DIR
        
        # 建立目錄結構
        self.financial_dir = FINANCIAL_DIR
        self.reports_dir = REPORTS_DIR
        self.activities_dir = ACTIVITIES_DIR
        self.grants_dir = GRANTS_DIR
        self.organization_dir = ORGANIZATION_DIR
        self.meetings_dir = MEETINGS_DIR
        
        for dir_path in [self.financial_dir, self.reports_dir, self.activities_dir, 
                         self.grants_dir, self.organization_dir, self.meetings_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def generate_annual_documents(self) -> List[Dict[str, Any]]:
        """生成年度文件"""
        documents = []
        
        # 1. 年度工作計畫（1月）
        doc = {
            "type": "年度工作計畫",
            "file": f"02_年度工作計畫_{self.year}.md",
            "due_date": f"{self.year}-01-31",
            "status": "已建立" if self.year == 2026 else "待建立",
            "category": "年度文件"
        }
        documents.append(doc)
        
        # 2. 年度決算（3月，上年度）
        doc = {
            "type": "年度決算",
            "file": f"financial/財務_年度決算_{self.year-1}.md",
            "due_date": f"{self.year}-03-31",
            "status": "待建立",
            "category": "年度文件"
        }
        documents.append(doc)
        
        # 3. 年度預算（11月，下年度）
        doc = {
            "type": "年度預算",
            "file": f"financial/財務_年度預算_{self.year+1}.md",
            "due_date": f"{self.year}-11-30",
            "status": "待建立",
            "category": "年度文件"
        }
        documents.append(doc)
        
        # 4. 年度工作報告（12月）
        doc = {
            "type": "年度工作報告",
            "file": f"reports/報告_年度工作報告_{self.year}.md",
            "due_date": f"{self.year}-12-31",
            "status": "待建立",
            "category": "年度文件"
        }
        documents.append(doc)
        
        # 5. 會員名冊（1月）
        doc = {
            "type": "會員名冊",
            "file": f"organization/組織_會員名冊_{self.year}.md",
            "due_date": f"{self.year}-01-31",
            "status": "待建立",
            "category": "年度文件"
        }
        documents.append(doc)
        
        return documents
    
    def generate_quarterly_documents(self) -> List[Dict[str, Any]]:
        """生成季度文件"""
        documents = []
        
        quarters = [
            (1, "Q1", f"{self.year}-04-15"),
            (2, "Q2", f"{self.year}-07-15"),
            (3, "Q3", f"{self.year}-10-15"),
            (4, "Q4", f"{self.year+1}-01-15")
        ]
        
        for quarter_num, quarter_code, due_date in quarters:
            # 季度工作進度報告
            doc = {
                "type": "季度工作進度報告",
                "file": f"reports/報告_季度工作進度_{self.year}{quarter_code}.md",
                "due_date": due_date,
                "status": "待建立",
                "category": "季度文件",
                "quarter": quarter_num
            }
            documents.append(doc)
            
            # 季度財務報表
            doc = {
                "type": "季度財務報表",
                "file": f"financial/財務_季度財務報表_{self.year}{quarter_code}.md",
                "due_date": due_date,
                "status": "待建立",
                "category": "季度文件",
                "quarter": quarter_num
            }
            documents.append(doc)
        
        return documents
    
    def generate_monthly_documents(self) -> List[Dict[str, Any]]:
        """生成月度文件"""
        documents = []
        
        for month in range(1, 13):
            month_str = f"{month:02d}"
            
            # 財務月報表（每月5日）
            doc = {
                "type": "財務月報表",
                "file": f"financial/財務_月報表_{self.year}{month_str}.md",
                "due_date": f"{self.year}-{month_str}-05",
                "status": "待建立",
                "category": "月度文件",
                "month": month
            }
            documents.append(doc)
            
            # 理監事會會議記錄（每月15日）
            doc = {
                "type": "理監事會會議記錄",
                "file": f"meetings/meeting_{self.year}{month_str}15_理監事會會議.md",
                "due_date": f"{self.year}-{month_str}-22",  # 會議後7日
                "status": "待建立",
                "category": "月度文件",
                "month": month
            }
            documents.append(doc)
            
            # 工作執行月報（每月25日）
            doc = {
                "type": "工作執行月報",
                "file": f"reports/報告_工作執行月報_{self.year}{month_str}.md",
                "due_date": f"{self.year}-{month_str}-25",
                "status": "待建立",
                "category": "月度文件",
                "month": month
            }
            documents.append(doc)
        
        return documents
    
    def generate_document_list(self) -> Dict[str, Any]:
        """生成完整文件清單"""
        annual_docs = self.generate_annual_documents()
        quarterly_docs = self.generate_quarterly_documents()
        monthly_docs = self.generate_monthly_documents()
        
        all_documents = annual_docs + quarterly_docs + monthly_docs
        
        # 統計
        stats = {
            "total": len(all_documents),
            "annual": len(annual_docs),
            "quarterly": len(quarterly_docs),
            "monthly": len(monthly_docs),
            "by_category": {},
            "by_status": {}
        }
        
        for doc in all_documents:
            category = doc["category"]
            status = doc["status"]
            
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        return {
            "year": self.year,
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "documents": all_documents
        }
    
    def generate_document_templates(self) -> None:
        """生成文件模板"""
        print("=" * 60)
        print(f"生成 {self.year} 年度文件模板...")
        print("=" * 60)
        
        # 生成年度決算模板
        self._generate_annual_financial_report_template()
        
        # 生成年度預算模板
        self._generate_annual_budget_template()
        
        # 生成年度工作報告模板
        self._generate_annual_work_report_template()
        
        # 生成季度文件模板
        self._generate_quarterly_report_template()
        self._generate_quarterly_financial_report_template()
        
        # 生成月度文件模板
        self._generate_monthly_report_template()
        self._generate_monthly_financial_report_template()
        
        print("\n文件模板生成完成！")
    
    def _generate_annual_financial_report_template(self) -> None:
        """生成年度決算模板"""
        template = f"""# 新北市三重區五常社區發展協會 {self.year-1}年度決算書

**年度**：{self.year-1}年度（{self.year-1}年1月1日至{self.year-1}年12月31日）  
**編製日期**：{self.year}年3月  
**負責單位**：財務組

---

## 一、收支決算表

### 收入決算
| 項目 | 預算數 | 決算數 | 差異 | 說明 |
|------|--------|--------|------|------|
| 會費收入 | | | | |
| 補助收入 | | | | |
| 捐款收入 | | | | |
| 事業收入 | | | | |
| 其他收入 | | | | |
| **合計** | | | | |

### 支出決算
| 項目 | 預算數 | 決算數 | 差異 | 說明 |
|------|--------|--------|------|------|
| 人事費 | | | | |
| 業務費 | | | | |
| 設備費 | | | | |
| 行政管理費 | | | | |
| 其他支出 | | | | |
| **合計** | | | | |

---

## 二、資產負債表

| 項目 | 金額 | 備註 |
|------|------|------|
| **資產** | | |
| 現金 | | |
| 銀行存款 | | |
| 應收款項 | | |
| 其他資產 | | |
| **負債** | | |
| 應付款項 | | |
| 其他負債 | | |
| **淨值** | | |

---

## 三、現金出納表

| 項目 | 金額 | 備註 |
|------|------|------|
| 期初現金 | | |
| 本期收入 | | |
| 本期支出 | | |
| 期末現金 | | |

---

## 四、財產目錄

| 財產名稱 | 數量 | 取得日期 | 取得金額 | 備註 |
|---------|------|---------|---------|------|
| | | | | |

---

## 五、基金收支表

| 項目 | 金額 | 備註 |
|------|------|------|
| 期初基金 | | |
| 本期收入 | | |
| 本期支出 | | |
| 期末基金 | | |

---

## 六、決算說明

（說明決算執行情況、差異原因、改善建議等）

---

**備註**：
- 本決算書需經監事會審核
- 需提會員大會通過
- 需報主管機關備查
"""
        
        filepath = self.financial_dir / f"財務_年度決算_{self.year-1}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"  [OK] 年度決算模板：{filepath.name}")
    
    def _generate_annual_budget_template(self) -> None:
        """生成年度預算模板"""
        template = f"""# 新北市三重區五常社區發展協會 {self.year+1}年度預算書

**年度**：{self.year+1}年度（{self.year+1}年1月1日至{self.year+1}年12月31日）  
**編製日期**：{self.year}年11月  
**負責單位**：財務組

---

## 一、收支預算表

### 收入預算
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 會費收入 | | |
| 補助收入 | | |
| 捐款收入 | | |
| 事業收入 | | |
| 其他收入 | | |
| **合計** | | |

### 支出預算
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 人事費 | | |
| 業務費 | | |
| 設備費 | | |
| 行政管理費 | | |
| 其他支出 | | |
| **合計** | | |

---

## 二、員工待遇表

| 職稱 | 人數 | 月薪 | 年終獎金 | 其他 | 合計 |
|------|------|------|---------|------|------|
| | | | | | |

---

## 三、預算說明

（說明預算編列依據、重點項目、預期效益等）

---

**備註**：
- 本預算書需經理監事會審議
- 需提會員大會通過
- 需報主管機關核備
"""
        
        filepath = self.financial_dir / f"財務_年度預算_{self.year+1}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"  [OK] 年度預算模板：{filepath.name}")
    
    def _generate_annual_work_report_template(self) -> None:
        """生成年度工作報告模板"""
        template = f"""# 新北市三重區五常社區發展協會 {self.year}年度工作報告

**年度**：{self.year}年度（{self.year}年1月1日至{self.year}年12月31日）  
**編製日期**：{self.year}年12月  
**負責單位**：秘書處

---

## 一、年度工作執行概況

### 1.1 工作目標達成情況
（說明年度工作目標達成情況）

### 1.2 主要工作項目
（列出主要工作項目及執行成果）

### 1.3 工作亮點
（說明年度工作亮點與創新）

---

## 二、各項工作執行成果

### 2.1 社區福利服務
（說明社區福利服務執行成果）

### 2.2 社區環境改善
（說明社區環境改善執行成果）

### 2.3 社區文化活動
（說明社區文化活動執行成果）

### 2.4 智慧社區服務
（說明智慧社區服務執行成果）

### 2.5 資源調查與需求評估
（說明資源調查與需求評估執行成果）

---

## 三、財務執行情況

### 3.1 收入執行
（說明收入執行情況）

### 3.2 支出執行
（說明支出執行情況）

### 3.3 財務狀況
（說明財務狀況）

---

## 四、補助計畫執行成果

### 4.1 補助計畫執行概況
（說明補助計畫執行概況）

### 4.2 補助計畫成果
（說明補助計畫成果）

---

## 五、檢討與建議

### 5.1 工作檢討
（說明工作檢討）

### 5.2 改善建議
（說明改善建議）

### 5.3 下年度工作方向
（說明下年度工作方向）

---

**備註**：
- 本報告需經理監事會審核
- 需提會員大會報告
- 需報主管機關備查
"""
        
        filepath = self.reports_dir / f"報告_年度工作報告_{self.year}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"  [OK] 年度工作報告模板：{filepath.name}")
    
    def _generate_quarterly_report_template(self) -> None:
        """生成季度報告模板"""
        for quarter in range(1, 5):
            quarter_code = f"Q{quarter}"
            template = f"""# 新北市三重區五常社區發展協會 {self.year}年第{quarter}季工作進度報告

**期間**：{self.year}年第{quarter}季  
**編製日期**：{self.year}年{quarter*3}月  
**負責單位**：秘書處

---

## 一、本季工作執行概況

### 1.1 工作目標
（說明本季工作目標）

### 1.2 執行進度
（說明本季執行進度）

### 1.3 達成情況
（說明本季達成情況）

---

## 二、各項工作執行成果

### 2.1 社區福利服務
（說明本季社區福利服務執行成果）

### 2.2 社區環境改善
（說明本季社區環境改善執行成果）

### 2.3 社區文化活動
（說明本季社區文化活動執行成果）

### 2.4 智慧社區服務
（說明本季智慧社區服務執行成果）

---

## 三、財務執行情況

### 3.1 本季收入
（說明本季收入情況）

### 3.2 本季支出
（說明本季支出情況）

### 3.3 預算執行率
（說明預算執行率）

---

## 四、檢討與建議

### 4.1 本季檢討
（說明本季檢討）

### 4.2 改善建議
（說明改善建議）

### 4.3 下季工作重點
（說明下季工作重點）

---

**備註**：
- 本報告需經理監事會審核
- 需報主管機關備查
"""
            
            filepath = self.reports_dir / f"報告_季度工作進度_{self.year}{quarter_code}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"  [OK] 季度工作進度報告模板：{filepath.name}")
    
    def _generate_quarterly_financial_report_template(self) -> None:
        """生成季度財務報表模板"""
        for quarter in range(1, 5):
            quarter_code = f"Q{quarter}"
            template = f"""# 新北市三重區五常社區發展協會 {self.year}年第{quarter}季財務報表

**期間**：{self.year}年第{quarter}季  
**編製日期**：{self.year}年{quarter*3}月  
**負責單位**：財務組

---

## 一、本季收支明細

### 1.1 本季收入
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 會費收入 | | |
| 補助收入 | | |
| 捐款收入 | | |
| 事業收入 | | |
| 其他收入 | | |
| **合計** | | |

### 1.2 本季支出
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 人事費 | | |
| 業務費 | | |
| 設備費 | | |
| 行政管理費 | | |
| 其他支出 | | |
| **合計** | | |

### 1.3 本季收支結餘
| 項目 | 金額（新台幣） |
|------|--------------|
| 本季收入 | |
| 本季支出 | |
| 本季結餘 | |

---

## 二、預算執行情況

### 2.1 收入預算執行率
| 項目 | 預算數 | 決算數 | 執行率 | 說明 |
|------|--------|--------|--------|------|
| 會費收入 | | | | |
| 補助收入 | | | | |
| 捐款收入 | | | | |
| 其他收入 | | | | |
| **合計** | | | | |

### 2.2 支出預算執行率
| 項目 | 預算數 | 決算數 | 執行率 | 說明 |
|------|--------|--------|--------|------|
| 人事費 | | | | |
| 業務費 | | | | |
| 設備費 | | | | |
| 行政管理費 | | | | |
| **合計** | | | | |

---

## 三、財務狀況說明

### 3.1 本季財務狀況
（說明本季財務狀況）

### 3.2 預算執行檢討
（說明預算執行檢討）

### 3.3 改善建議
（說明改善建議）

---

**備註**：
- 本報表需經監事會審核
- 需報主管機關備查
"""
            
            filepath = self.financial_dir / f"財務_季度財務報表_{self.year}{quarter_code}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"  [OK] 季度財務報表模板：{filepath.name}")
    
    def _generate_monthly_report_template(self) -> None:
        """生成月度報告模板"""
        for month in range(1, 13):
            month_str = f"{month:02d}"
            template = f"""# 新北市三重區五常社區發展協會 {self.year}年{month}月工作執行月報

**期間**：{self.year}年{month}月  
**編製日期**：{self.year}年{month}月25日  
**負責單位**：活動組

---

## 一、本月工作執行概況

### 1.1 工作目標
（說明本月工作目標）

### 1.2 執行進度
（說明本月執行進度）

### 1.3 達成情況
（說明本月達成情況）

---

## 二、各項工作執行成果

### 2.1 活動辦理
（說明本月活動辦理情況）

### 2.2 服務提供
（說明本月服務提供情況）

### 2.3 資源整合
（說明本月資源整合情況）

---

## 三、檢討與建議

### 3.1 本月檢討
（說明本月檢討）

### 3.2 改善建議
（說明改善建議）

### 3.3 下月工作重點
（說明下月工作重點）

---

**備註**：
- 本報告需經理監事會審核
"""
            
            filepath = self.reports_dir / f"報告_工作執行月報_{self.year}{month_str}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"  [OK] 工作執行月報模板：{filepath.name}")
    
    def _generate_monthly_financial_report_template(self) -> None:
        """生成財務月報表模板"""
        month_names = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
        for month in range(1, 13):
            month_str = f"{month:02d}"
            template = f"""# 新北市三重區五常社區發展協會 {self.year}年{month_names[month]}月財務月報表

**期間**：{self.year}年{month}月  
**編製日期**：{self.year}年{month}月5日  
**負責單位**：財務組

---

## 一、本月收支明細

### 1.1 本月收入
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 會費收入 | | |
| 補助收入 | | |
| 捐款收入 | | |
| 事業收入 | | |
| 其他收入 | | |
| **合計** | | |

### 1.2 本月支出
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 人事費 | | |
| 業務費 | | |
| 設備費 | | |
| 行政管理費 | | |
| 其他支出 | | |
| **合計** | | |

### 1.3 本月收支結餘
| 項目 | 金額（新台幣） |
|------|--------------|
| 本月收入 | |
| 本月支出 | |
| 本月結餘 | |

---

## 二、累計收支

### 2.1 累計收入
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 會費收入 | | |
| 補助收入 | | |
| 捐款收入 | | |
| 事業收入 | | |
| 其他收入 | | |
| **合計** | | |

### 2.2 累計支出
| 項目 | 金額（新台幣） | 備註 |
|------|--------------|------|
| 人事費 | | |
| 業務費 | | |
| 設備費 | | |
| 行政管理費 | | |
| 其他支出 | | |
| **合計** | | |

### 2.3 累計結餘
| 項目 | 金額（新台幣） |
|------|--------------|
| 累計收入 | |
| 累計支出 | |
| 累計結餘 | |

---

## 三、銀行對帳

### 3.1 銀行存款
| 銀行名稱 | 帳號 | 期初餘額 | 本期存入 | 本期支出 | 期末餘額 |
|---------|------|---------|---------|---------|---------|
| | | | | | |

### 3.2 現金
| 項目 | 金額（新台幣） |
|------|--------------|
| 期初現金 | |
| 本期收入 | |
| 本期支出 | |
| 期末現金 | |

---

## 四、預算執行情況

### 4.1 收入預算執行率
| 項目 | 年度預算 | 累計決算 | 執行率 | 說明 |
|------|---------|---------|--------|------|
| 會費收入 | | | | |
| 補助收入 | | | | |
| 捐款收入 | | | | |
| 其他收入 | | | | |
| **合計** | | | | |

### 4.2 支出預算執行率
| 項目 | 年度預算 | 累計決算 | 執行率 | 說明 |
|------|---------|---------|--------|------|
| 人事費 | | | | |
| 業務費 | | | | |
| 設備費 | | | | |
| 行政管理費 | | | | |
| **合計** | | | | |

---

## 五、財務狀況說明

### 5.1 本月財務狀況
（說明本月財務狀況）

### 5.2 預算執行檢討
（說明預算執行檢討）

### 5.3 改善建議
（說明改善建議）

---

**備註**：
- 本報表需經監事會審核
- 需報主管機關備查
"""
            
            filepath = self.financial_dir / f"財務_月報表_{self.year}{month_str}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"  [OK] 財務月報表模板：{filepath.name}")


def main():
    """主程式"""
    year = 2026
    
    print("=" * 60)
    print("新北市三重區五常社區發展協會 法定文件生成系統")
    print("=" * 60)
    print(f"目標年度：{year}")
    print()
    
    generator = DocumentGenerator(year=year)
    
    # 生成文件清單
    print("生成文件清單...")
    document_list = generator.generate_document_list()
    
    # 顯示統計
    stats = document_list["statistics"]
    print(f"\n文件統計：")
    print(f"  總文件數：{stats['total']} 個")
    print(f"  年度文件：{stats['annual']} 個")
    print(f"  季度文件：{stats['quarterly']} 個")
    print(f"  月度文件：{stats['monthly']} 個")
    print()
    
    # 儲存文件清單
    list_file = OPERATIONAL_FILES_DIR / f"17_法定文件清單_{year}.json"
    with open(list_file, 'w', encoding='utf-8') as f:
        json.dump(document_list, f, ensure_ascii=False, indent=2)
    print(f"文件清單已儲存至：{list_file}")
    print()
    
    # 生成文件模板
    generator.generate_document_templates()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
