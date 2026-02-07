# Internal Institution Configuration
# 內部機構設定

class InstitutionConfig:
    # 系統之母重新總店 (基金池外)
    SYSTEM_MOTHER_STORE = "上品聊國咖啡館 (基金池外的系統之母重新總店)"
    
    # 主公司 POS 仁義分店 (User Specified Name)
    MASTER_POS_STORE = "上品寮國仁義分店"
    
    # 主公司 (協會)
    MASTER_COMPANY = "新北市五常社區發展協會 (主公司)"
    
    # 相關連結
    MAP_LINK = "https://www.google.com/maps/place/204,+Section+3,+Chongxin+Rd,+Sanchong+District,+New+Taipei+City/@25.0818,121.4898,15z"
    
    @staticmethod
    def get_pos_token_data():
        return {
            "role": "MERCHANT",
            "shop_name": InstitutionConfig.MASTER_POS_STORE,
            "org_name": InstitutionConfig.SYSTEM_MOTHER_STORE
        }
