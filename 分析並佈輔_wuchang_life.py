import requests
import json
from ai_odoo_gemini_api import call_gemini_2_pro_api

def upload_and_analyze_config(config_path, cloud_api_url):
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    payload = {
        'filename': config_path,
        'content': config_content
    }
    # 傳送到雲端
    try:
        r = requests.post(cloud_api_url, json=payload, timeout=15)
        print(f'雲端回應: {r.status_code} {r.text}')
    except Exception as e:
        print(f'雲端傳送失敗: {e}')
    # 呼叫 Gemini 2.0 Pro 進行最佳佈輔方案分析
    prompt = f"請根據以下設定檔內容，分析並建議最佳佈輔（部署與輔助）方案：\n{config_content}"
    result = call_gemini_2_pro_api(prompt)
    print('Gemini 2.0 Pro 分析建議：', result)

if __name__ == "__main__":
    # 範例：分析 cloudflared/config.yml
    upload_and_analyze_config('config/cloudflared/config.yml', 'https://cloud-j.example.com/api/analyze')
