#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_homepage_image.py

為首頁生成圖片

功能：
- 使用內部圖片生成 API（OpenAI DALL-E 或其他）
- 管理每日額度使用
- 根據合規資料生成首頁圖片
- 儲存生成的圖片
"""

import sys
import json
import os
import base64
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

# 設定 UTF-8 編碼輸出
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

BASE_DIR = Path(__file__).resolve().parent


def load_env_config() -> Dict[str, Any]:
    """載入環境配置"""
    config = {
        "api_key": os.getenv("WUCHANG_LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("WUCHANG_LLM_BASE_URL") or "https://api.openai.com/v1",
        "image_model": os.getenv("WUCHANG_IMAGE_MODEL", "dall-e-3"),
        "daily_limit": int(os.getenv("WUCHANG_IMAGE_DAILY_LIMIT", "10")),
    }
    return config


def load_usage_tracking() -> Dict[str, Any]:
    """載入使用量追蹤"""
    usage_file = BASE_DIR / "image_generation_usage.json"
    if usage_file.exists():
        try:
            return json.loads(usage_file.read_text(encoding="utf-8"))
        except:
            pass
    
    return {
        "last_reset_date": str(date.today()),
        "daily_usage": 0,
        "total_usage": 0,
        "history": []
    }


def save_usage_tracking(usage_data: Dict[str, Any]):
    """儲存使用量追蹤"""
    usage_file = BASE_DIR / "image_generation_usage.json"
    usage_file.write_text(
        json.dumps(usage_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def check_daily_limit(config: Dict[str, Any], usage_data: Dict[str, Any]) -> tuple[bool, str]:
    """檢查每日額度"""
    today = str(date.today())
    
    # 如果日期改變，重置每日使用量
    if usage_data.get("last_reset_date") != today:
        usage_data["last_reset_date"] = today
        usage_data["daily_usage"] = 0
    
    daily_usage = usage_data.get("daily_usage", 0)
    daily_limit = config.get("daily_limit", 10)
    
    if daily_usage >= daily_limit:
        return False, f"已達每日額度上限（{daily_limit} 次），今日已使用 {daily_usage} 次"
    
    return True, f"今日已使用 {daily_usage}/{daily_limit} 次"


def generate_image_with_openai(
    prompt: str,
    config: Dict[str, Any],
    size: str = "1024x1024",
    quality: str = "standard",
    style: str = "vivid"
) -> Dict[str, Any]:
    """使用 OpenAI DALL-E 生成圖片"""
    if not config.get("api_key"):
        return {
            "success": False,
            "error": "未設定 API Key（請設定 WUCHANG_LLM_API_KEY 或 OPENAI_API_KEY）"
        }
    
    api_url = f"{config['base_url']}/images/generations"
    
    payload = {
        "model": config.get("image_model", "dall-e-3"),
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "style": style,
        "n": 1
    }
    
    try:
        import json as json_lib
        req = Request(api_url, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {config['api_key']}")
        
        raw = json_lib.dumps(payload).encode("utf-8")
        
        with urlopen(req, data=raw, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            data = json_lib.loads(body)
            
            if "data" in data and len(data["data"]) > 0:
                return {
                    "success": True,
                    "image_url": data["data"][0].get("url"),
                    "revised_prompt": data["data"][0].get("revised_prompt"),
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "error": "API 回應格式異常",
                    "response": data
                }
    
    except URLError as e:
        return {
            "success": False,
            "error": f"網路錯誤: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"生成圖片失敗: {e}"
        }


def download_image(image_url: str, save_path: Path) -> bool:
    """下載圖片"""
    try:
        req = Request(image_url)
        with urlopen(req, timeout=30) as resp:
            image_data = resp.read()
            save_path.write_bytes(image_data)
            return True
    except Exception as e:
        print(f"⚠️  下載圖片失敗: {e}")
        return False


def create_homepage_image_prompt(compliance_data: Dict[str, Any]) -> str:
    """根據合規資料建立首頁圖片提示詞"""
    org_name = compliance_data.get("organization", {}).get("name", "五常社區發展協會")
    mission = compliance_data.get("mission", {}).get("mission", "促進社區發展")
    core_values = compliance_data.get("mission", {}).get("core_values", [])
    vision = compliance_data.get("mission", {}).get("vision", "")
    
    # 建立提示詞
    prompt_parts = [
        "A modern, professional homepage banner image for a community development association in Taiwan.",
        "The image should convey:",
        f"- Community development and digital inclusion ({', '.join(core_values) if core_values else '科技平權'})",
        "- Warm, welcoming atmosphere",
        "- Modern technology and traditional community values",
        "- Professional, trustworthy appearance",
        "Style: Clean, modern design with warm colors, suitable for a nonprofit organization website homepage.",
        "No text overlay, image only."
    ]
    
    prompt = " ".join(prompt_parts)
    
    return prompt


def main():
    """主函數"""
    print("=" * 70)
    print("首頁圖片生成工具")
    print("=" * 70)
    print()
    
    # 1. 載入配置
    config = load_env_config()
    print(f"📋 使用模型: {config.get('image_model', 'dall-e-3')}")
    print(f"📋 每日額度: {config.get('daily_limit', 10)} 次")
    print()
    
    # 2. 載入使用量追蹤
    usage_data = load_usage_tracking()
    
    # 3. 檢查每日額度
    can_use, message = check_daily_limit(config, usage_data)
    print(f"📊 {message}")
    print()
    
    if not can_use:
        print("❌ 無法生成圖片：已達每日額度上限")
        print("💡 提示：請等待明日或調整每日額度設定")
        return 1
    
    # 4. 載入合規資料
    compliance_file = BASE_DIR / "compliance_data.json"
    if not compliance_file.exists():
        print("❌ 找不到合規資料檔案（compliance_data.json）")
        return 1
    
    compliance_data = json.loads(compliance_file.read_text(encoding="utf-8"))
    print("✅ 已載入合規資料")
    print()
    
    # 5. 建立提示詞
    prompt = create_homepage_image_prompt(compliance_data)
    print("📝 圖片提示詞：")
    print("-" * 70)
    print(prompt)
    print("-" * 70)
    print()
    
    # 6. 生成圖片
    print("🎨 正在生成圖片...")
    result = generate_image_with_openai(prompt, config)
    
    if not result.get("success"):
        print(f"❌ 生成失敗: {result.get('error', '未知錯誤')}")
        return 1
    
    # 7. 下載並儲存圖片
    image_url = result.get("image_url")
    if not image_url:
        print("❌ 未取得圖片 URL")
        return 1
    
    print(f"✅ 圖片生成成功")
    if result.get("revised_prompt"):
        print(f"📝 修正後的提示詞: {result['revised_prompt']}")
    print()
    
    # 建立儲存目錄
    output_dir = BASE_DIR / "static" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 儲存圖片
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_file = output_dir / f"homepage_banner_{timestamp}.png"
    
    print(f"💾 正在下載圖片至: {image_file.relative_to(BASE_DIR)}")
    if download_image(image_url, image_file):
        print("✅ 圖片已儲存")
    else:
        print("⚠️  圖片下載失敗，但 URL 已記錄")
        # 儲存 URL 到 JSON
        url_file = output_dir / f"homepage_banner_{timestamp}_url.json"
        url_file.write_text(
            json.dumps({
                "url": image_url,
                "revised_prompt": result.get("revised_prompt"),
                "generated_at": datetime.now().isoformat(),
                "prompt": prompt
            }, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    # 8. 更新使用量
    usage_data["daily_usage"] = usage_data.get("daily_usage", 0) + 1
    usage_data["total_usage"] = usage_data.get("total_usage", 0) + 1
    usage_data["history"].append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "image_file": str(image_file.relative_to(BASE_DIR)),
        "image_url": image_url
    })
    
    # 只保留最近 100 筆歷史
    if len(usage_data["history"]) > 100:
        usage_data["history"] = usage_data["history"][-100:]
    
    save_usage_tracking(usage_data)
    
    print()
    print("=" * 70)
    print("生成完成")
    print("=" * 70)
    print()
    print(f"📁 圖片位置: {image_file.relative_to(BASE_DIR)}")
    print(f"🌐 圖片 URL: {image_url}")
    print(f"📊 今日使用: {usage_data['daily_usage']}/{config['daily_limit']} 次")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
