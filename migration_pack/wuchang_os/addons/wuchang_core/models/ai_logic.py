# -*- coding: utf-8 -*-
from odoo import models, api, fields
import importlib.util
import os
import logging
import json
import urllib.request
import urllib.parse

_logger = logging.getLogger(__name__)


class WuchangAILogic(models.AbstractModel):
    _name = 'wuchang.ai.logic'
    _description = 'Wuchang AI Logic'

    @api.model
    def _get_ai_mode(self):
        mode = self.env['ir.config_parameter'].sudo().get_param(
            'wuchang.ai_mode') or 'cloud_builtin'
        return mode

    @api.model
    def _get_api_key(self):
        """Retrieves the Google API Key from System Parameters."""
        api_key = self.env['ir.config_parameter'].sudo(
        ).get_param('wuchang.google_api_key')
        if not api_key:
            _logger.warning(
                "Google API Key is not configured in System Parameters (wuchang.google_api_key).")
            return None
        return api_key

    @api.model
    def _supremacy_blocked(self):
        p = self.env['ir.config_parameter'].sudo()
        sup = (p.get_param('wuchang.ai.global_suppression') or '').strip()
        if not sup:
            return False
        try:
            rid = int(p.get_param('wuchang.ai.root.user_id') or '0')
        except Exception:
            rid = 0
        u = self.env.user
        if rid and u and u.id == rid:
            return False
        return True

    @api.model
    def _get_master_logic_path(self):
        path = self.env['ir.config_parameter'].sudo().get_param(
            'wuchang.master_logic_path') or ''
        return path.strip() or None

    @api.model
    def _load_master_module(self):
        path = self._get_master_logic_path()
        if not path:
            return None
        try:
            if not os.path.isfile(path):
                return None
            spec = importlib.util.spec_from_file_location(
                'wuchang_master_logic', path)
            if not spec or not spec.loader:
                return None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        except Exception as e:
            _logger.error(f"Master logic load failed: {e}")
            return None

    @api.model
    def execute_master_logic(self, func_name, *args, **kwargs):
        mod = self._load_master_module()
        if not mod:
            return None
        fn = getattr(mod, func_name, None)
        if callable(fn):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                _logger.error(f"Master logic runtime error: {e}")
                return None
        return None

    @api.model
    def _configure_genai(self):
        """Configures the Google GenAI library, respecting AI mode, and returns module if ready."""
        mode = self._get_ai_mode()
        if mode != 'external_key':
            return None
        api_key = self._get_api_key()
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                return genai
            except Exception as e:
                _logger.error(f"GenAI configuration failed: {e}")
                return None
        return None

    @api.model
    def _get_prompt(self, key, **kwargs):
        """Fetches prompt from wuchang.ai.prompt and formats it."""
        prompt_record = self.env['wuchang.ai.prompt'].sudo().search([('name', '=', key)], limit=1)
        if not prompt_record:
            return None
        try:
            return prompt_record.template.format(**kwargs)
        except Exception as e:
            _logger.error(f"Prompt formatting error for {key}: {e}")
            return prompt_record.template

    @api.model
    def translate_menu(self, menu_text, target_language='English'):
        """Translates menu text to the target language."""
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return "Error during translation: GenAI not available"
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            prompt = self._get_prompt('translation', target_language=target_language, menu_text=menu_text)
            if not prompt:
                prompt = f"Translate the following menu item or description to {target_language}: {menu_text}"
            
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                _logger.error(f"Translation error: {e}")
                return f"Error during translation: {str(e)}"
        elif mode == 'cloud_builtin':
            return f"[{target_language}] {menu_text}"
        else:
            return "Device App mode: 請於裝置端執行此功能"

    @api.model
    def tell_fortune(self, order_details):
        """Generates a fortune based on the order details."""
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return "Your fortune is cloudy today."
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            prompt = self._get_prompt('fortune_telling', order_details=order_details)
            if not prompt:
                prompt = f"Write a short, whimsical fortune for a customer who ordered: {order_details}. Keep it lighthearted."

            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                return "Your fortune is cloudy today."
        elif mode == 'cloud_builtin':
            return f"今日好運：{order_details} 將帶來悠然好心情。"
        else:
            return "Device App mode: 請於裝置端執行此功能"

    @api.model
    def simulate_haggling(self, original_price, customer_offer):
        """Simulates a haggling interaction."""
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return "Let's stick to the price tag."
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            prompt = self._get_prompt('haggling_simulation', customer_offer=customer_offer, original_price=original_price)
            if not prompt:
                prompt = f"A customer offers {customer_offer} for an item priced at {original_price}. Act as a friendly but firm shopkeeper. Accept, reject, or counter-offer. Keep it short."
                
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                return "Let's stick to the price tag."
        elif mode == 'cloud_builtin':
            return "店長評估：小幅折扣可行，請維持品質。"
        else:
            return "Device App mode: 請於裝置端執行此功能"

    @api.model
    def generate_recipe(self, ingredients):
        """Generates a recipe based on provided ingredients."""
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return "Could not cook up a recipe."
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            prompt = self._get_prompt('recipe_generation', ingredients=ingredients)
            if not prompt:
                prompt = f"Create a unique dish recipe using these ingredients: {ingredients}. Provide a name and brief instructions."
                
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                return "Could not cook up a recipe."
        elif mode == 'cloud_builtin':
            return f"特製菜單：{ingredients} — 清新融合，步驟簡易。"
        else:
            return "Device App mode: 請於裝置端執行此功能"

    @api.model
    def analyze_operations(self, operation_data):
        """Analyzes operational data (e.g., sales, feedback)."""
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return "Data too complex to analyze right now."
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            prompt = self._get_prompt('operation_analysis', operation_data=operation_data)
            if not prompt:
                prompt = f"Analyze the following operational data and provide 3 key insights: {operation_data}"
                
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                return "Data too complex to analyze right now."
        elif mode == 'cloud_builtin':
            return f"三點洞察：1) 目標明確 2) 阻礙拆解 3) 時程落地 — {operation_data}"
        else:
            return "Device App mode: 請於裝置端執行此功能"

    @api.model
    def general_generate(self, prompt):
        if self._supremacy_blocked():
            params = self.env['ir.config_parameter'].sudo()
            reason = params.get_param('wuchang.ai.suppress.reason') or ''
            return ('AI壓制中' + (('：' + reason) if reason else ''))
        mode = self._get_ai_mode()
        if mode == 'external_key':
            params = self.env['ir.config_parameter'].sudo()
            model_name = params.get_param(
                'wuchang.gen_model') or 'gemini-1.5-flash'
            keys_raw = params.get_param('wuchang.google_api_keys') or '[]'
            try:
                pool = json.loads(keys_raw)
                if not isinstance(pool, list):
                    pool = []
            except Exception:
                pool = []
            key = ''
            if pool:
                try:
                    idx = int(params.get_param(
                        'wuchang.google_api_rr_index') or '0')
                except Exception:
                    idx = 0
                key = str(pool[idx % len(pool)])
                try:
                    params.set_param(
                        'wuchang.google_api_rr_index', str(idx + 1))
                except Exception:
                    pass
            if not key:
                key = params.get_param('wuchang.google_api_key') or ''
            if not key:
                return ''
            url = 'https://generativelanguage.googleapis.com/v1beta/models/' + \
                urllib.parse.quote(
                    model_name) + ':generateContent?key=' + urllib.parse.quote(key)
            body = json.dumps(
                {'contents': [{'parts': [{'text': str(prompt or '')}]}]})
            req = urllib.request.Request(url, data=body.encode(
                'utf-8'), headers={'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    try:
                        return str(data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text') or '')
                    except Exception:
                        return ''
            except Exception:
                try:
                    url2 = 'https://llm.wuchang.life/api/generate'
                    body2 = json.dumps({'model': str(params.get_param(
                        'wuchang.ollama_model') or 'llama3.1'), 'prompt': str(prompt or ''), 'stream': False})
                    req2 = urllib.request.Request(url2, data=body2.encode(
                        'utf-8'), headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req2, timeout=5) as resp2:
                        data2 = json.loads(resp2.read().decode('utf-8'))
                        return str(data2.get('response') or '')
                except Exception:
                    return '服務暫時忙碌，改以內建口吻：' + str(prompt or '')
        elif mode == 'local_ollama':
            params = self.env['ir.config_parameter'].sudo()
            model_name = params.get_param('wuchang.ollama_model') or 'llama3.1'
            try:
                url = 'https://llm.wuchang.life/api/generate'
                body = json.dumps(
                    {'model': str(model_name), 'prompt': str(prompt or ''), 'stream': False})
                req = urllib.request.Request(url, data=body.encode(
                    'utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    return str(data.get('response') or '')
            except Exception:
                return '幽默補位：把嚴肅的話題換個俏皮角度看待，輕鬆但不失分寸。'
        elif mode == 'master_logic':
            val = self.execute_master_logic('generate', str(prompt or ''))
            return str(val or '')
        elif mode == 'cloud_builtin':
            t = str(prompt or '')
            if '七言絕句' in t:
                return '茶湯清澈映山窗\n香霧輕飄繞指旁\n一口入喉心自靜\n禪風淡淡伴書香'
            if '推薦' in t:
                return '建議搭配「招牌拿鐵」，奶香與茶韻相融，更添雅致。'
            if '未來感' in t:
                return '{"name":"量子琥珀拿鐵","price":180,"desc":"以琥珀糖霜與冷萃融合，入口清亮層次分明。"}'
            if ('支出' in t or 'expense' in t) and 'JSON' in t:
                return '{"reason":"清潔劑","amount":120,"table":"T03"}'
            return t
        else:
            return ''

    @api.model
    def two_stage_generate(self, prompt):
        if self._supremacy_blocked():
            params = self.env['ir.config_parameter'].sudo()
            reason = params.get_param('wuchang.ai.suppress.reason') or ''
            return ('AI壓制中' + (('：' + reason) if reason else ''))
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return ''
            try:
                m = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
                r1 = m.generate_content(str(prompt or ''))
                d1 = str(getattr(r1, 'text', '') or '')
                refine = '閱讀以下草稿，依目標、約束、證據、反例、驗收指標重寫，提升真確性、相關性、完整性與可審計性：\n' + d1
                r2 = m.generate_content(refine)
                return str(getattr(r2, 'text', '') or d1)
            except Exception:
                return ''
        elif mode in ('cloud_builtin', 'local_ollama', 'master_logic'):
            d1 = self.general_generate(str(prompt or ''))
            t = '重寫並提升品質：' + str(d1 or '')
            return self.general_generate(t)
        else:
            return ''

    @api.model
    def refine_only(self, draft):
        if self._supremacy_blocked():
            params = self.env['ir.config_parameter'].sudo()
            reason = params.get_param('wuchang.ai.suppress.reason') or ''
            return ('AI壓制中' + (('：' + reason) if reason else ''))
        mode = self._get_ai_mode()
        text = str(draft or '')
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return text
            try:
                m = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
                refine = '閱讀以下草稿，依目標、約束、證據、反例、驗收指標重寫，保持原意、提高品質與可審計性：\n' + text
                r = m.generate_content(refine)
                return str(getattr(r, 'text', '') or text)
            except Exception:
                return text
        elif mode in ('cloud_builtin', 'local_ollama', 'master_logic'):
            t = '重寫並提升品質：' + text
            return self.general_generate(t)
        else:
            return text

    @api.model
    def satellite_refine(self, draft):
        if self._supremacy_blocked():
            params = self.env['ir.config_parameter'].sudo()
            reason = params.get_param('wuchang.ai.suppress.reason') or ''
            return ('AI壓制中' + (('：' + reason) if reason else ''))
        text = str(draft or '')
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return text
            try:
                m = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
                r_search = m.generate_content(
                    '整理可引用的證據與來源，對以下內容做來源校驗並列清單：\n' + text)
                s1 = str(getattr(r_search, 'text', '') or '')
                r_struct = m.generate_content(
                    '依以下內容與證據，生成大綱與驗收指標，輸出結構化要點：\n' + (s1 or text))
                s2 = str(getattr(r_struct, 'text', '') or '')
                r_critic = m.generate_content(
                    '針對以下大綱做反例與風險檢查，補齊邊界與止損條件：\n' + (s2 or s1))
                s3 = str(getattr(r_critic, 'text', '') or '')
                r_final = m.generate_content(
                    '根據研究/結構/批判三步輸出最終定稿，要求引用、驗收、止損齊備：\n' + '\n'.join([text, s1, s2, s3]))
                return str(getattr(r_final, 'text', '') or s3 or s2 or s1 or text)
            except Exception:
                return text
        else:
            s1 = self.general_generate('證據校驗與引用清單：' + text)
            s2 = self.general_generate('生成大綱與驗收指標：' + (s1 or text))
            s3 = self.general_generate('反例與風險檢查：' + (s2 or s1))
            return self.general_generate('最終定稿（含引用/驗收/止損）：' + '\n'.join([text, s1 or '', s2 or '', s3 or '']))

    @api.model
    def check_vibe(self, current_context):
        """Suggests music or announcements based on the current vibe/context."""
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return "Just play some lo-fi beats."
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            prompt = self._get_prompt('vibe_check', current_context=current_context)
            if not prompt:
                prompt = f"Given the current context: '{current_context}', suggest a song genre and a public announcement to set the mood."
                
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                return "Just play some lo-fi beats."
        elif mode == 'cloud_builtin':
            return "建議：Lo-fi / 公告：歡迎光臨，今日特選清茶。"
        else:
            return "Device App mode: 請於裝置端執行此功能"

    @api.model
    def generate_leftover_special(self, leftovers):
        """Generates a special menu item based on leftover ingredients."""
        mode = self._get_ai_mode()
        if mode == 'external_key':
            genai = self._configure_genai()
            if not genai:
                return "Mystery Stew."
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            prompt = self._get_prompt('leftover_special', leftovers=leftovers)
            if not prompt:
                prompt = f"We have these leftovers: {leftovers}. Invent a 'Special of the Day' name and description to sell them."
                
            try:
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                return "Mystery Stew."
        elif mode == 'cloud_builtin':
            return f"今日特餐：{leftovers} — 清爽重生，限量供應。"
        else:
            return "Device App mode: 請於裝置端執行此功能"
