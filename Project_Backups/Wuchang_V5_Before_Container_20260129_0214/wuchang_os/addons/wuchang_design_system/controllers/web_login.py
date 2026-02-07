
from odoo import http
from odoo.http import request
import os
import base64


class WuchangLogin(http.Controller):

    @http.route('/web/login/roles', type='json', auth='none')
    def get_login_roles(self):
        try:
            roles = request.env['wuchang.user.role'].sudo(
            ).search_read([], ['name', 'technical_key'])
        except Exception:
            roles = []
        return roles

    @http.route('/web/login/branding_info', type='json', auth='none')
    def get_branding_info(self):
        company = request.env['res.company'].sudo().browse(
            request.env.company.id)
        params = request.env['ir.config_parameter'].sudo()
        producer = params.get_param('branding.producer') or ''
        home_mode = params.get_param('login.home.mode') or ''
        association = params.get_param('branding.association') or '新北市五常社區發展協會'
        coffee_org = params.get_param('branding.coffee_org') or '上品聊國咖啡館重新總店'
        coffee_org_link = params.get_param(
            'branding.coffee_org_link') or 'https://www.google.com/maps/place/204,+Section+3,+Chongxin+Rd,+Sanchong+District,+New+Taipei+City/@25.0818,121.4898,15z'
        main_phone = params.get_param('branding.coffee_main_phone') or ''
        branch_phone = params.get_param('branding.coffee_branch_phone') or ''
        patent_no = params.get_param('branding.patent_no') or 'M663678'
        google_form_wish_url = params.get_param(
            'branding.google_form_wish_url') or ''
        google_doc_research_url = params.get_param(
            'branding.google_doc_research_url') or ''

        # 新增組織背景與資金來源信息
        organization_info = params.get_param(
            'branding.organization_info') or '新北市五常社區發展協會（立案字號：新北市社區補自第1100606355號）& 五常物業規劃顧問股份有限公司（統一編號：97573469，社會企業）'
        funding_source = params.get_param(
            'branding.funding_source') or '系統開發：上品聊國咖啡館全額捐助｜網路資源：Google非營利組織抵免額｜設備補助：新北市政府補助'

        return {
            'company_name': company.name or '',
            'phone': getattr(company, 'phone', '') or '',
            'producer': producer,
            'association': association,
            'coffee_org': coffee_org,
            'coffee_org_link': coffee_org_link,
            'patent': patent,
            'coffee_main_phone': main_phone,
            'coffee_branch_phone': branch_phone,
            'patent_no': patent_no,
            'google_form_wish_url': google_form_wish_url,
            'google_doc_research_url': google_doc_research_url,
            'home_mode': home_mode,
            'organization_info': organization_info,
            'funding_source': funding_source,
        }

    @http.route('/web/login/portal_map', type='json', auth='none')
    def portal_map(self):
        try:
            host = (getattr(request.httprequest, 'host', None) or '').lower()
        except Exception:
            host = ''

        def build(sub):
            if host.endswith('wuchang.life'):
                return 'https://' + sub + '.wuchang.life/'
            if host.endswith('wuchang.global'):
                return 'https://' + sub + '.wuchang.global/'
            return '/' + sub
        return {
            'hj': {'url': build('hj'), 'title': '居住正義', 'desc': '社區公平、住房安全與公共利益的維護'},
            'ft': {'url': build('ft'), 'title': '公平交易', 'desc': '市場秩序、誠信交易與消費者保護'},
            'vs': {'url': build('volunteer'), 'title': '志願服務', 'desc': '志工參與、服務管理與社會連結'},
            'pos': {'url': build('pos'), 'title': '收銀與前台', 'desc': '門市銷售與前台作業'},
            'staff': {'url': build('staff'), 'title': '員工入口', 'desc': '公司域名入口，提供員工作業'},
            'admin': {'url': build('admin'), 'title': '管理入口', 'desc': '管理者高權限入口，需公司域名'},
            'butler': {'url': build('butler'), 'title': '智能管家', 'desc': '助理導覽與便民服務'},
            'guest_l1': {'url': (build('butler') + '?tier=l1'), 'title': '一般訪客 L1', 'desc': '未成年訪客｜需加強保護與陪伴'},
            'guest_l2': {'url': (build('butler') + '?tier=l2'), 'title': '一般訪客 L2', 'desc': '成年女性｜人身安全優先、提供友善協助'},
            'guest_l3': {'url': (build('butler') + '?tier=l3'), 'title': '一般訪客 L3', 'desc': '成年男性｜必要時提升警戒、保障他人安全'},
            'guest_l4': {'url': (build('butler') + '?tier=l4'), 'title': '一般訪客 L4', 'desc': '高齡 65+｜健康安全優先、提供即時支援'},
        }

    @http.route('/wuchang/ads/marquee', type='json', auth='none')
    def marquee_text(self):
        params = request.env['ir.config_parameter'].sudo()
        text = params.get_param('branding.marquee_text') or ''
        if not text:
            base = os.path.join(os.getcwd(), 'memory_store/ads')
            try:
                p = os.path.join(base, 'marquee.txt')
                if os.path.exists(p):
                    with open(p, 'r', encoding='utf-8') as f:
                        text = f.read().strip()
            except Exception:
                text = ''
        return {'text': text or ''}

    @http.route('/wuchang/ads/login/status', type='json', auth='none')
    def login_ads_status(self):
        base = os.path.join(os.getcwd(), 'memory_store/ads')
        vids = ['login_ad.mp4', 'login_ad.webm', 'ad.mp4', 'ad.webm']
        auds = ['login_ad.mp3', 'ad.mp3', 'login_ad.ogg', 'ad.ogg']
        has_video = any(os.path.exists(os.path.join(base, n)) for n in vids)
        has_audio = any(os.path.exists(os.path.join(base, n)) for n in auds)
        return {'has_video': bool(has_video), 'has_audio': bool(has_audio)}

    @http.route('/wuchang/ads/login/video', type='http', auth='none')
    def login_video(self, **kw):
        base = os.path.join(os.getcwd(), 'memory_store/ads')
        cands = ['login_ad.mp4', 'login_ad.webm', 'ad.mp4', 'ad.webm']
        for n in cands:
            p = os.path.join(base, n)
            if os.path.exists(p):
                data = open(p, 'rb').read()
                ext = os.path.splitext(p)[1].lower()
                mt = 'video/mp4' if ext == '.mp4' else 'video/webm'
                return http.Response(data, headers=[('Content-Type', mt)])
        return http.Response(status=204)

    @http.route('/wuchang/ads/login/audio', type='http', auth='none')
    def login_audio(self, **kw):
        base = os.path.join(os.getcwd(), 'memory_store/ads')
        cands = ['login_ad.mp3', 'ad.mp3', 'login_ad.ogg', 'ad.ogg']
        for n in cands:
            p = os.path.join(base, n)
            if os.path.exists(p):
                data = open(p, 'rb').read()
                ext = os.path.splitext(p)[1].lower()
                mt = 'audio/mpeg' if ext == '.mp3' else 'audio/ogg'
                return http.Response(data, headers=[('Content-Type', mt)])
        return http.Response(status=204)
