#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_dual_j_images.py

生成雙J形象圖片

功能：
- 使用內部圖片生成 API 生成地端小J和雲端小J的形象圖片
- 管理每日額度使用
- 儲存生成的圖片到系統中
"""

import sys
import json
import os
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


def check_daily_limit(config: Dict[str, Any], usage_data: Dict[str, Any], required_count: int = 1) -> tuple[bool, str]:
    """檢查每日額度"""
    today = str(date.today())
    
    # 如果日期改變，重置每日使用量
    if usage_data.get("last_reset_date") != today:
        usage_data["last_reset_date"] = today
        usage_data["daily_usage"] = 0
    
    daily_usage = usage_data.get("daily_usage", 0)
    daily_limit = config.get("daily_limit", 10)
    
    if daily_usage + required_count > daily_limit:
        return False, f"已達每日額度上限（{daily_limit} 次），今日已使用 {daily_usage} 次，需要 {required_count} 次"
    
    return True, f"今日已使用 {daily_usage}/{daily_limit} 次，將使用 {required_count} 次"


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


def create_little_j_prompt() -> str:
    """建立地端小J形象提示詞"""
    prompt = """A cute anime-style character portrait of a little girl with white hair, representing a local AI assistant named "Little J". 
    
Character design:
- White hair (silver-white color)
- Cute, friendly appearance
- Modern, tech-savvy style
- Professional but approachable
- Suitable for a community development AI assistant
- Clean, simple design
- Transparent background preferred
- Portrait style, suitable for avatar use
- Size: square format, suitable for 256x256 to 512x512 pixels

Style: Modern anime/manga style, clean lines, professional quality, suitable for a nonprofit organization's AI assistant."""
    
    return prompt


def create_jules_prompt() -> str:
    """建立雲端小J (JULES) 形象提示詞"""
    prompt = """A professional AI assistant character portrait representing "JULES" (cloud-based AI assistant). 
    
Character design:
- Modern, professional AI assistant appearance
- Tech-forward, cloud-based theme
- Friendly but professional demeanor
- Suitable for a cloud AI service
- Clean, modern design
- Transparent background preferred
- Portrait style, suitable for avatar use
- Size: square format, suitable for 256x256 to 512x512 pixels

Style: Modern digital art style, professional quality, suitable for a cloud-based AI assistant in a nonprofit organization."""
    
    return prompt


def create_dual_j_collaboration_prompt() -> str:
    """建立雙J協作形象提示詞"""
    prompt = """A professional illustration showing two AI assistants working together in collaboration. 
    
Design elements:
- Two AI assistant characters (one representing local AI "Little J" with white hair, one representing cloud AI "JULES")
- Collaboration theme: working together, sharing information
- Modern, professional style
- Suitable for a nonprofit organization's dual AI system
- Clean, modern design
- Transparent or subtle background
- Horizontal format, suitable for banner or header use
- Size: suitable for 1024x512 or similar banner format

Style: Modern digital illustration, professional quality, showing collaboration and teamwork between local and cloud AI assistants."""
    
    return prompt


def main():
    """主函數"""
    print("=" * 70)
    print("雙J形象圖片生成工具")
    print("=" * 70)
    print()
    
    # 1. 載入配置
    config = load_env_config()
    print(f"📋 使用模型: {config.get('image_model', 'dall-e-3')}")
    print(f"📋 每日額度: {config.get('daily_limit', 10)} 次")
    print()
    
    # 2. 載入使用量追蹤
    usage_data = load_usage_tracking()
    
    # 3. 檢查每日額度（需要生成3張圖片）
    required_count = 3
    can_use, message = check_daily_limit(config, usage_data, required_count)
    print(f"📊 {message}")
    print()
    
    if not can_use:
        print("❌ 無法生成圖片：已達每日額度上限")
        print("💡 提示：請等待明日或調整每日額度設定")
        return 1
    
    # 4. 建立儲存目錄
    output_dir = BASE_DIR / "static" / "images" / "dual_j"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    images_to_generate = [
        {
            "name": "地端小J",
            "filename": "little_j_avatar.png",
            "prompt_func": create_little_j_prompt,
            "size": "1024x1024"
        },
        {
            "name": "雲端小J (JULES)",
            "filename": "jules_avatar.png",
            "prompt_func": create_jules_prompt,
            "size": "1024x1024"
        },
        {
            "name": "雙J協作",
            "filename": "dual_j_collaboration.png",
            "prompt_func": create_dual_j_collaboration_prompt,
            "size": "1024x1024"
        }
    ]
    
    generated_images = []
    
    # 5. 生成每張圖片
    for img_config in images_to_generate:
        print(f"🎨 正在生成 {img_config['name']} 形象圖片...")
        
        # 建立提示詞
        prompt = img_config["prompt_func"]()
        print(f"📝 提示詞：{prompt[:100]}...")
        print()
        
        # 生成圖片
        result = generate_image_with_openai(prompt, config, size=img_config["size"])
        
        if not result.get("success"):
            print(f"❌ 生成失敗: {result.get('error', '未知錯誤')}")
            continue
        
        # 下載並儲存圖片
        image_url = result.get("image_url")
        if not image_url:
            print("❌ 未取得圖片 URL")
            continue
        
        print(f"✅ 圖片生成成功")
        if result.get("revised_prompt"):
            print(f"📝 修正後的提示詞: {result['revised_prompt'][:100]}...")
        print()
        
        # 儲存圖片
        image_file = output_dir / img_config["filename"]
        
        print(f"💾 正在下載圖片至: {image_file.relative_to(BASE_DIR)}")
        if download_image(image_url, image_file):
            print("✅ 圖片已儲存")
            generated_images.append({
                "name": img_config["name"],
                "file": str(image_file.relative_to(BASE_DIR)),
                "url": image_url,
                "prompt": prompt,
                "revised_prompt": result.get("revised_prompt")
            })
        else:
            print("⚠️  圖片下載失敗，但 URL 已記錄")
            # 儲存 URL 到 JSON
            url_file = output_dir / f"{img_config['filename']}_url.json"
            url_file.write_text(
                json.dumps({
                    "url": image_url,
                    "revised_prompt": result.get("revised_prompt"),
                    "generated_at": datetime.now().isoformat(),
                    "prompt": prompt
                }, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            generated_images.append({
                "name": img_config["name"],
                "file": str(url_file.relative_to(BASE_DIR)),
                "url": image_url,
                "prompt": prompt
            })
        
        # 更新使用量
        usage_data["daily_usage"] = usage_data.get("daily_usage", 0) + 1
        usage_data["total_usage"] = usage_data.get("total_usage", 0) + 1
        usage_data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "name": img_config["name"],
            "prompt": prompt,
            "image_file": str(image_file.relative_to(BASE_DIR)),
            "image_url": image_url
        })
        
        print()
        print("-" * 70)
        print()
    
    # 6. 儲存使用量追蹤
    # 只保留最近 100 筆歷史
    if len(usage_data["history"]) > 100:
        usage_data["history"] = usage_data["history"][-100:]
    
    save_usage_tracking(usage_data)
    
    # 7. 建立圖片索引檔案
    index_file = output_dir / "dual_j_images_index.json"
    index_file.write_text(
        json.dumps({
            "generated_at": datetime.now().isoformat(),
            "images": generated_images,
            "usage": {
                "daily_usage": usage_data["daily_usage"],
                "total_usage": usage_data["total_usage"]
            }
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print("=" * 70)
    print("生成完成")
    print("=" * 70)
    print()
    print(f"✅ 已生成 {len(generated_images)} 張圖片")
    print()
    for img in generated_images:
        print(f"📁 {img['name']}: {img['file']}")
    print()
    print(f"📊 今日使用: {usage_data['daily_usage']}/{config['daily_limit']} 次")
    print(f"📋 圖片索引: {index_file.relative_to(BASE_DIR)}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
