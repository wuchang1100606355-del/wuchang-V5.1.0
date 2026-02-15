import json
import random

roles = [
    "量子架構師", "數據編織者", "系統守護者", "邏輯節點",
    "記憶維護者", "網路哨兵", "像素藝術家", "代碼詩人",
    "資安管理員", "時空觀察者"
]

comments = [
    "系統運行穩定。", "數據流暢通無阻。", "量子連結強度正常。",
    "監視網格中。", "你好，世界。", "正在處理邏輯運算。",
    "記憶體已加密。", "運行效率 99%。", "每日持續學習中。",
    "我們共同建設。", "代碼即法律。", "掃描區域中。",
    "調和數據中。", "節點已對齊。", "延遲趨近於零。",
    "為核心服務中。", "願景清晰。", "擴展地平線。",
    "保護使用者安全。", "等待指令中。"
]

voices = []
for i in range(1, 5001):
    voice = {
        "id": f"AI-{i:04d}",
        "role": random.choice(roles),
        "comment": random.choice(comments)
    }
    voices.append(voice)

output_file = "ai_voices_5000.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(voices, f, ensure_ascii=False, indent=2)

print(f"Generated {len(voices)} voices in {output_file}")
