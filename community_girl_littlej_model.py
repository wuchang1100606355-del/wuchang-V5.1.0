# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CommunityGirlLittleJ(models.Model):
    _name = 'community.girl.littlej'
    _description = '社區少女小J 角色設計模型'


    name = fields.Char(string='角色名稱', default='社區少女小J（Little J）')
    hair_color = fields.Char(string='髮色', default='白髮')
    personality = fields.Char(string='個性', default='溫柔、親切、帶點可愛的鄰家妹妹感')
    outfit = fields.Char(string='服裝', default='簡約社區制服（可有社區徽章）、輕便裙裝、運動鞋')
    accessories = fields.Char(string='配件', default='AI耳機、平板、社區識別證、愛心徽章')
    expressions = fields.Char(string='表情', default='微笑、思考、驚喜、撒嬌、專注')

    illustration_avatar = fields.Boolean(string='頭像插圖', default=True)
    illustration_welcome = fields.Boolean(string='歡迎頁大圖', default=True)
    illustration_register = fields.Boolean(string='註冊/登入引導', default=True)
    illustration_chat = fields.Boolean(string='AI對話框Q版', default=True)
    illustration_404 = fields.Boolean(string='404/維護頁', default=True)
    illustration_announce = fields.Boolean(string='公告推播', default=True)
    illustration_comic = fields.Boolean(string='小漫畫/彩蛋', default=True)

    main_colors = fields.Char(string='主色', default='銀白、天藍、粉白')
    secondary_colors = fields.Char(string='輔色', default='社區主題色（可依LOGO）')
    style = fields.Char(string='風格', default='溫馨、明亮、現代感')

    ai_prompt_1 = fields.Text(string='AI繪圖Prompt 1', default='A cute anime-style white-haired girl in a modern community uniform, holding a tablet, smiling gently, background is a sunny neighborhood, soft blue and white color scheme.')
    ai_prompt_2 = fields.Text(string='AI繪圖Prompt 2', default='Chibi white-haired girl with AI headset, waving at the community entrance, pastel colors, friendly and approachable.')

    ui_suggestion = fields.Text(string='UI插入建議', default='註冊/登入頁：大圖+歡迎詞\n聊天室/AI助理：Q版頭像+動態表情\n公告/推播：小J舉旗子/發通知插圖\n404/維護頁：小J抱歉/加油表情')
    interaction_script = fields.Text(string='互動腳本', default='小J自我介紹：「嗨～我是社區少女小J，妳的AI妹妹，有什麼需要都可以找我唷！」\n註冊引導：「只要掃描QR或用Google帳號就能加入社區，超簡單！」\n公告推播：「小J提醒您，今晚有社區活動，記得來參加喔！」')

    version = fields.Char(string='版本', default='v1.0')
    author = fields.Char(string='作者', default='五常AI專案團隊')
    date = fields.Date(string='日期', default=fields.Date.today)

    def greet_user(self):
        """
        系統內建AI程序：自動回覆歡迎詞
        """
        return "嗨～我是社區少女小J，妳的AI妹妹，有什麼需要都可以找我唷！"
