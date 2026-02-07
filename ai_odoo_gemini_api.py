import requests

ODDO_API_KEY_URL = "http://localhost:8069/api/ai_key"  # 依實際Odoo API調整
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent"

def get_gemini_api_key_from_odoo():
    """從Odoo取得Gemini 2.0 Pro的API金鑰"""
    try:
        resp = requests.get(ODDO_API_KEY_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("api_key")
    except Exception as e:
        print(f"[小j] 取得Odoo金鑰失敗: {e}")
        return None

def call_gemini_2_pro_api(prompt, api_key=None):
    """呼叫Gemini 2.0 Pro API，回傳結果"""
    if api_key is None:
        api_key = get_gemini_api_key_from_odoo()
    if not api_key:
        print("[小j] 無法取得Gemini API金鑰，請檢查Odoo設定！")
        return None
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[小j] 呼叫Gemini 2.0 Pro失敗: {e}")
        return None
