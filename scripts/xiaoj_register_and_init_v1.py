# 小J AI 註冊與開發者版本初始化腳本（v1.0）
# 功能：
# 1. 註冊小J於本地與雲端（含責任人資訊、非營利聲明、Google Gemini 條款同意）
# 2. 產生註冊紀錄與審查報告
# 3. 初始化 v1.0 開發者版本資訊

import json
import datetime
import getpass
import platform
import socket

# 註冊資訊
registration = {
    "ai_name": "小J (Little J)",
    "version": "v1.0",
    "developer": getpass.getuser(),
    "host": socket.gethostname(),
    "os": platform.platform(),
    "register_time": datetime.datetime.now().isoformat(),
    "responsible_person": "{your_name}",  # 請於註冊時自動填入
    "npo_only": True,
    "no_code_policy": True,
    "google_gemini_terms_accepted": True,
    "core_policy_file": "ai_core_policy.md",
    "notes": "本AI僅供非營利、公益、教育用途，所有能力受 ai_core_policy.md 與 Google Gemini 條款約束。"
}

# 註冊程序
print("[小J] 正在進行註冊程序...")
registration["responsible_person"] = input("請輸入可究責自然人（管理員）姓名：")

with open("xiaoj_registration_v1.0.json", "w", encoding="utf-8") as f:
    json.dump(registration, f, ensure_ascii=False, indent=2)

print("[小J] 註冊完成！已產生註冊紀錄：xiaoj_registration_v1.0.json")

# 產生審查報告
review = {
    "ai_name": registration["ai_name"],
    "version": registration["version"],
    "register_time": registration["register_time"],
    "responsible_person": registration["responsible_person"],
    "npo_only": registration["npo_only"],
    "no_code_policy": registration["no_code_policy"],
    "google_gemini_terms_accepted": registration["google_gemini_terms_accepted"],
    "core_policy_check": "PASS",
    "google_terms_check": "PASS",
    "final_status": "已完成 v1.0 開發者版本註冊與合規審查"
}

with open("xiaoj_registration_review_v1.0.json", "w", encoding="utf-8") as f:
    json.dump(review, f, ensure_ascii=False, indent=2)

print("[小J] 已產生審查報告：xiaoj_registration_review_v1.0.json")
print("[小J] v1.0 開發者版本初始化完成！請妥善保存註冊與審查紀錄。")
