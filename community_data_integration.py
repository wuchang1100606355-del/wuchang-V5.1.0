"""
五常社區數據整合模組
將分析報告數據整合到系統中
"""

import json
import os
from pathlib import Path

class CommunityDataManager:
    """社區數據管理器"""
    
    def __init__(self, data_file='wuchang_community_analysis.json'):
        base_dir = Path(__file__).resolve().parent
        p = Path(data_file)
        self.data_file = str(p if p.is_absolute() else (base_dir / p))
        self.data = self.load_data()
    
    def load_data(self):
        """載入社區分析數據"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_demographics(self):
        """獲取人口結構數據"""
        return self.data.get('demographics', {})
    
    def get_commercial_ecosystem(self):
        """獲取商業生態數據"""
        return self.data.get('commercial_ecosystem', {})
    
    def get_transportation(self):
        """獲取交通物流數據"""
        return self.data.get('transportation', {})
    
    def get_happiness_coin_config(self):
        """獲取幸福幣配置"""
        return self.data.get('happiness_coin', {})
    
    def get_system_optimization(self):
        """獲取系統優化建議"""
        return self.data.get('system_optimization', {})
    
    def get_location_bounds(self):
        """獲取地理邊界"""
        location = self.data.get('location', {})
        return location.get('boundaries', {})
    
    def get_main_streets(self):
        """獲取主要街道"""
        location = self.data.get('location', {})
        return location.get('main_streets', [])
    
    def get_key_insights(self):
        """獲取關鍵洞察"""
        return self.data.get('key_insights', [])

# 全局實例
community_data = CommunityDataManager()
