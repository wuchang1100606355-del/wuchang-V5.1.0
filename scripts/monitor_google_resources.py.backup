#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google 非營利組織資源監控腳本
監控 Google Workspace、Google Ads、GCP 資源使用情況
合規要求：符合 Google 非營利組織合規要求
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 項目根目錄
ROOT_DIR = Path(__file__).parent.parent
LOGS_DIR = ROOT_DIR / "logs"
REPORTS_DIR = ROOT_DIR / "reports"

# 確保目錄存在
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


class GoogleWorkspaceMonitor:
    """Google Workspace 資源監控"""
    
    def __init__(self):
        self.domain = "wuchang.life"
        self.free_storage_per_user = 5 * 1024  # 5 TB in GB
        self.max_users = None  # 無限制
        
    def check_storage_usage(self) -> Dict:
        """檢查儲存空間使用情況"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "total_users": 0,
            "total_storage_used_gb": 0,
            "total_storage_limit_gb": 0,
            "storage_usage_percent": 0,
            "users": []
        }
        
        # TODO: 整合 Google Workspace Admin SDK API
        # 目前返回模擬數據
        logger.info("檢查 Google Workspace 儲存空間使用...")
        
        # 模擬數據（實際應從 API 獲取）
        result["total_users"] = 10
        result["total_storage_used_gb"] = 150  # 假設使用 150 GB
        result["total_storage_limit_gb"] = self.free_storage_per_user * result["total_users"]
        result["storage_usage_percent"] = (
            result["total_storage_used_gb"] / result["total_storage_limit_gb"] * 100
            if result["total_storage_limit_gb"] > 0 else 0
        )
        
        logger.info(f"儲存空間使用: {result['total_storage_used_gb']} GB / {result['total_storage_limit_gb']} GB ({result['storage_usage_percent']:.2f}%)")
        
        return result
    
    def check_email_usage(self) -> Dict:
        """檢查電子郵件使用情況"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "domain": self.domain,
            "daily_emails_sent": 0,
            "monthly_emails_sent": 0,
            "storage_used_gb": 0,
            "threats_blocked": 0
        }
        
        # TODO: 整合 Google Workspace Admin SDK API
        logger.info("檢查電子郵件使用情況...")
        
        # 模擬數據
        result["daily_emails_sent"] = 50
        result["monthly_emails_sent"] = 1500
        result["storage_used_gb"] = 20
        result["threats_blocked"] = 5
        
        return result
    
    def get_report(self) -> Dict:
        """獲取完整報告"""
        return {
            "workspace": {
                "storage": self.check_storage_usage(),
                "email": self.check_email_usage()
            }
        }


class GoogleAdsMonitor:
    """Google Ads (Grants) 資源監控"""
    
    def __init__(self):
        self.monthly_grant = 10000  # $10,000 USD
        self.max_cpc = 2.00  # 最高每次點擊 $2.00
        
    def check_grant_usage(self) -> Dict:
        """檢查 Grants 額度使用情況"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "monthly_grant": self.monthly_grant,
            "used_amount": 0,
            "remaining_amount": self.monthly_grant,
            "usage_percent": 0,
            "daily_spend": [],
            "campaigns": []
        }
        
        # TODO: 整合 Google Ads API
        logger.info("檢查 Google Grants 使用情況...")
        
        # 模擬數據
        result["used_amount"] = 2500  # 假設已使用 $2,500
        result["remaining_amount"] = self.monthly_grant - result["used_amount"]
        result["usage_percent"] = (result["used_amount"] / self.monthly_grant) * 100
        
        logger.info(f"Grants 使用: ${result['used_amount']:.2f} / ${self.monthly_grant:.2f} ({result['usage_percent']:.2f}%)")
        
        return result
    
    def check_campaign_performance(self) -> Dict:
        """檢查廣告活動表現"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "total_campaigns": 0,
            "active_campaigns": 0,
            "total_clicks": 0,
            "total_impressions": 0,
            "avg_ctr": 0,
            "total_conversions": 0,
            "conversion_rate": 0
        }
        
        # TODO: 整合 Google Ads API
        logger.info("檢查廣告活動表現...")
        
        # 模擬數據
        result["total_campaigns"] = 5
        result["active_campaigns"] = 3
        result["total_clicks"] = 1250
        result["total_impressions"] = 50000
        result["avg_ctr"] = (result["total_clicks"] / result["total_impressions"] * 100) if result["total_impressions"] > 0 else 0
        result["total_conversions"] = 25
        result["conversion_rate"] = (result["total_conversions"] / result["total_clicks"] * 100) if result["total_clicks"] > 0 else 0
        
        return result
    
    def get_report(self) -> Dict:
        """獲取完整報告"""
        return {
            "ads": {
                "grant_usage": self.check_grant_usage(),
                "performance": self.check_campaign_performance()
            }
        }


class GCPMonitor:
    """Google Cloud Platform 資源監控"""
    
    def __init__(self):
        self.free_tier_limits = {
            "compute_engine": {
                "e2_micro_instances": 1,
                "storage_gb": 30
            },
            "cloud_storage": {
                "standard_storage_gb": 5,
                "class_a_operations": 5000,
                "class_b_operations": 50000
            },
            "cloud_sql": {
                "db_f1_micro_instances": 1,
                "storage_gb": 10
            },
            "cloud_functions": {
                "invocations": 2000000,
                "gb_seconds": 400000,
                "ghz_seconds": 200000
            }
        }
        
    def check_free_tier_usage(self) -> Dict:
        """檢查免費額度使用情況"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # TODO: 整合 Google Cloud Billing API
        logger.info("檢查 GCP 免費額度使用...")
        
        # 模擬數據
        result["services"] = {
            "compute_engine": {
                "used_instances": 1,
                "limit_instances": 1,
                "usage_percent": 100
            },
            "cloud_storage": {
                "used_gb": 3.5,
                "limit_gb": 5,
                "usage_percent": 70
            },
            "cloud_functions": {
                "used_invocations": 500000,
                "limit_invocations": 2000000,
                "usage_percent": 25
            }
        }
        
        return result
    
    def check_billing(self) -> Dict:
        """檢查帳單和成本"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "current_month_cost": 0,
            "free_tier_used": True,
            "paid_resources": []
        }
        
        # TODO: 整合 Google Cloud Billing API
        logger.info("檢查 GCP 帳單...")
        
        # 模擬數據
        result["current_month_cost"] = 0  # 假設完全使用免費額度
        result["free_tier_used"] = True
        
        return result
    
    def get_report(self) -> Dict:
        """獲取完整報告"""
        return {
            "gcp": {
                "free_tier": self.check_free_tier_usage(),
                "billing": self.check_billing()
            }
        }


class GoogleResourceMonitor:
    """Google 資源監控主類"""
    
    def __init__(self):
        self.workspace = GoogleWorkspaceMonitor()
        self.ads = GoogleAdsMonitor()
        self.gcp = GCPMonitor()
        
    def generate_report(self) -> Dict:
        """生成完整監控報告"""
        logger.info("=" * 80)
        logger.info("開始生成 Google 非營利組織資源監控報告")
        logger.info("=" * 80)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "organization": "新北市三重區五常社區發展協會",
            "domain": "wuchang.life",
            "compliance": "Google 非營利組織合規",
            "resources": {}
        }
        
        # 收集各項資源使用情況
        try:
            report["resources"]["workspace"] = self.workspace.get_report()
        except Exception as e:
            logger.error(f"Google Workspace 監控失敗: {e}")
            report["resources"]["workspace"] = {"error": str(e)}
        
        try:
            report["resources"]["ads"] = self.ads.get_report()
        except Exception as e:
            logger.error(f"Google Ads 監控失敗: {e}")
            report["resources"]["ads"] = {"error": str(e)}
        
        try:
            report["resources"]["gcp"] = self.gcp.get_report()
        except Exception as e:
            logger.error(f"GCP 監控失敗: {e}")
            report["resources"]["gcp"] = {"error": str(e)}
        
        # 生成摘要
        report["summary"] = self._generate_summary(report)
        
        return report
    
    def _generate_summary(self, report: Dict) -> Dict:
        """生成摘要"""
        summary = {
            "total_monthly_value": 0,
            "workspace_status": "正常",
            "ads_status": "正常",
            "gcp_status": "正常",
            "alerts": []
        }
        
        # 計算總價值
        # Google Workspace: 假設 10 使用者 × $6/月 = $60/月
        # Google Grants: $10,000/月
        # GCP Always Free: 約 $50/月
        summary["total_monthly_value"] = 60 + 10000 + 50
        
        # 檢查告警
        workspace = report["resources"].get("workspace", {})
        if workspace.get("workspace", {}).get("storage", {}).get("storage_usage_percent", 0) > 80:
            summary["alerts"].append("Google Workspace 儲存空間使用超過 80%")
            summary["workspace_status"] = "警告"
        
        ads = report["resources"].get("ads", {})
        if ads.get("ads", {}).get("grant_usage", {}).get("usage_percent", 0) < 20:
            summary["alerts"].append("Google Grants 使用率低於 20%，建議優化廣告策略")
        
        gcp = report["resources"].get("gcp", {})
        if gcp.get("gcp", {}).get("billing", {}).get("current_month_cost", 0) > 0:
            summary["alerts"].append("GCP 產生付費成本，請檢查資源使用")
            summary["gcp_status"] = "警告"
        
        return summary
    
    def save_report(self, report: Dict) -> Path:
        """保存報告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"google_resources_report_{timestamp}.json"
        filepath = REPORTS_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"報告已保存: {filepath}")
        return filepath
    
    def print_summary(self, report: Dict):
        """打印摘要"""
        summary = report.get("summary", {})
        
        print("\n" + "=" * 80)
        print("  Google 非營利組織資源使用摘要")
        print("=" * 80)
        print(f"\n  組織: {report.get('organization', 'N/A')}")
        print(f"  網域: {report.get('domain', 'N/A')}")
        print(f"  報告時間: {report.get('timestamp', 'N/A')}")
        print(f"\n  每月總價值: ${summary.get('total_monthly_value', 0):,.2f} USD")
        print(f"\n  服務狀態:")
        print(f"    - Google Workspace: {summary.get('workspace_status', 'N/A')}")
        print(f"    - Google Ads: {summary.get('ads_status', 'N/A')}")
        print(f"    - Google Cloud: {summary.get('gcp_status', 'N/A')}")
        
        alerts = summary.get("alerts", [])
        if alerts:
            print(f"\n  告警:")
            for alert in alerts:
                print(f"    ⚠ {alert}")
        else:
            print(f"\n  ✅ 無告警")
        
        print("\n" + "=" * 80)


def main():
    """主函數"""
    monitor = GoogleResourceMonitor()
    
    # 生成報告
    report = monitor.generate_report()
    
    # 保存報告
    report_path = monitor.save_report(report)
    
    # 打印摘要
    monitor.print_summary(report)
    
    logger.info("監控完成")
    return report


if __name__ == "__main__":
    main()
