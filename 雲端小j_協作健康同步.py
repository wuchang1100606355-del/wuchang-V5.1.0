
import requests
import json
from datetime import datetime
from ai_odoo_gemini_api import call_gemini_2_pro_api

def sync_health_to_cloud(local_report_path, cloud_api_url):
    with open(local_report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    payload = {
        'timestamp': datetime.now().isoformat(),
        'local_health': report
    }
    try:
        # 先同步健康報告到雲端
        r = requests.post(cloud_api_url, json=payload, timeout=10)
        print('雲端同步結果:', r.status_code, r.text)
        # 呼叫 Gemini 2.0 Pro 進行健康報告分析
        prompt = f"請根據以下健康報告，給出簡短的建議：\n{json.dumps(report, ensure_ascii=False, indent=2)}"
        gemini_result = call_gemini_2_pro_api(prompt)
        print('Gemini 2.0 Pro 分析建議:', gemini_result)
    except Exception as e:
        print('雲端同步失敗:', e)

if __name__ == "__main__":
    # 測試用，請將cloud_api_url換成實際雲端小j API
    sync_health_to_cloud('system_health_report.json', 'https://cloud-j.example.com/api/health')
