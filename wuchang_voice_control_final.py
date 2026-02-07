import socket
import requests
import json
import speech_recognition as sr
import pyttsx3
import time
import os
import platform

# ==========================================
# ⚔️ 五常 (Wuchang) 語音控制核心 V5.2
# 代號：Gemini-Twin (繁體中文特製版)
# ==========================================

# --- ☁️ 記憶路徑配置區 (自動搜尋) ---
# 系統會依序檢查以下路徑，找到第一個存在的就使用
POSSIBLE_PATHS = [
    r"J:\共用雲端硬碟\五常雲端空間",      # 優先 1：您的筆電雲端路徑
    r"J:\五常雲端空間",                  # 優先 2：備用路徑
    r"G:\共用雲端硬碟\五常雲端空間",      # 備援：伺服器端路徑
    r"C:\wuchang V5.1.0",               # 備援：筆電本地備份
    os.getcwd()                         # 最後手段：程式所在的目錄
]

MEMORY_FILE = "secretary_memory.txt"
IDENTITY_FILE = "system_identity.txt"

# --- 🛠️ 身份識別區 ---
# 請將這裡改為您店裡主機的「電腦名稱」
SERVER_HOSTNAME = "DESKTOP-SERVER" 
SERVER_IP = "192.168.50.249"

# 取得目前這台電腦的名稱
CURRENT_HOSTNAME = platform.node()
print(f"🔍 系統偵測中... 目前主機名稱: {CURRENT_HOSTNAME}")

if CURRENT_HOSTNAME == SERVER_HOSTNAME:
    print("✅ 身分確認: [伺服器小J]")
    MODE = "伺服器"
    # 伺服器強制走有線網路，確保穩定
    CONTROL_NIC_IP = SERVER_IP
    # 大腦連線設定
    LOCAL_LLM_URL = "http://localhost:11434/v1/chat/completions"
    PRIMARY_MODEL = "gemma:2b" 
    FALLBACK_MODEL = "qwen:0.5b"
else:
    print("✅ 身分確認: [筆電小J]")
    MODE = "筆電"
    # 筆電自動路由 (0.0.0.0)，適應 Wi-Fi 或插線
    CONTROL_NIC_IP = "0.0.0.0" 
    LOCAL_LLM_URL = "http://localhost:11434/v1/chat/completions"
    PRIMARY_MODEL = "little-j:latest"
    FALLBACK_MODEL = "llama3"

# 目標 IoT 設備 IP (請修改為實際值)
TARGET_DEVICE_IP = "192.168.50.249"

# --- 🗣️ 語音合成初始化 (讓電腦說話) ---
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)    # 語速 (數字越小越慢)
    engine.setProperty('volume', 1.0)  # 音量 (0.0 ~ 1.0)
    
    # 嘗試尋找中文語音包
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Chinese" in voice.name or "Han" in voice.name or "Taiwan" in voice.name:
            engine.setProperty('voice', voice.id)
            break
except Exception as e:
    print(f"⚠️ 語音模組初始化警告: {e}")

def speak(text):
    """小J 的嘴巴"""
    print(f"🤖 小J ({MODE}) 說：{text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️ 語音錯誤: {e}")

def load_cloud_memory():
    """智慧搜尋記憶檔案"""
    valid_path = None
    
    # 1. 尋找有效的資料夾
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            valid_path = path
            print(f"📂 鎖定記憶路徑: {valid_path}")
            break
            
    if not valid_path:
        print("❌ 警告：找不到任何設定的記憶路徑！")
        return None

    memory_content = ""
    
    # 2. 讀取檔案
    for filename in [MEMORY_FILE, IDENTITY_FILE]:
        full_path = os.path.join(valid_path, filename)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    memory_content += f.read() + "\n"
                print(f"📖 讀取成功: {filename}")
            except Exception as e:
                print(f"⚠️ 讀取失敗 {filename}: {e}")
        else:
            print(f"ℹ️ 找不到檔案 (略過): {filename}")

    if not memory_content:
        print("⚠️ 記憶庫是空的，將使用出廠預設人格。")
        return None
        
    return memory_content

def call_local_llm(user_input, model_name, cloud_memory):
    """大腦思考 (Ollama)"""
    
    if cloud_memory:
        base_prompt = cloud_memory
    else:
        role_desc = "你是五常社區的【伺服器端】守護AI。" if MODE == "SERVER" else "你是五常社區的【行動端】指揮AI。"
        base_prompt = f"{role_desc} 指揮官是「哥哥」。任務：判斷控制指令或閒聊。"

    # 系統提示詞 (告訴 AI 怎麼做)
    system_prompt = base_prompt + """
    【重要指令】
    你必須嚴格只回傳以下 JSON 格式，不要有 Markdown：
    {
        "action": "on" | "off" | "none",
        "reply": "繁體中文語音回應"
    }
    """

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "response_format": { "type": "json_object" },
        "stream": False
    }
    
    try:
        response = requests.post(LOCAL_LLM_URL, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return "MODEL_NOT_FOUND" if response.status_code == 404 else None
    except Exception as e:
        print(f"❌ 大腦連線失敗: {e}")
        return None

def send_physical_signal(action):
    """發送控制訊號"""
    if action == "none": return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((CONTROL_NIC_IP, 0))
            s.settimeout(2)
            print(f"⚡ [{MODE}] 連線至設備 {TARGET_DEVICE_IP}...")
            s.connect((TARGET_DEVICE_IP, 80))
            msg = f"SET_STATE={action}\n"
            s.sendall(msg.encode())
            print(f"✅ 指令已發送: {action}")
    except Exception as e:
        print(f"❌ 發送異常: {e}")

def main():
    r = sr.Recognizer()
    active_model = PRIMARY_MODEL
    
    print("☁️ 正在初始化記憶模組...")
    cloud_memory = load_cloud_memory()
    
    print(f"🔍 [{MODE}] 測試大腦連線: {active_model} ...")
    if call_local_llm("測試", active_model, cloud_memory) in ["MODEL_NOT_FOUND", None]:
        print(f"⚠️ 首選模型異常，切換至備用模型: {FALLBACK_MODEL}")
        active_model = FALLBACK_MODEL
    
    try:
        with sr.Microphone() as source:
            print("\n" + "="*40)
            print(f"   ⚔️  五常小J ({MODE} 模式)  ⚔️")
            if cloud_memory: print("   ✅ 記憶: 已同步")
            else: print("   ⚠️ 記憶: 離線模式 (使用預設)")
            print("="*40)
            
            speak(f"小J {MODE} 模式上線。指揮官，我在這裡。")
            
            # 自動調整麥克風靈敏度
            print("🎤 正在校正環境噪音，請稍候...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("👌 校正完成。")
            
            while True:
                print("\n👂 聆聽中... (您可以隨時說話)")
                try:
                    audio = r.listen(source, phrase_time_limit=10)
                    print("🔄 正在辨識您的聲音...")
                    
                    # 辨識語音 (Google 引擎)
                    text = r.recognize_google(audio, language="zh-TW")
                    print(f"🗣️ 指揮官說：{text}")
                    
                    # 傳給 AI 思考
                    res_str = call_local_llm(text, active_model, cloud_memory)
                    
                    if res_str and res_str != "MODEL_NOT_FOUND":
                        try:
                            res = json.loads(res_str)
                            # 執行動作
                            if res.get("action") in ["on", "off"]:
                                send_physical_signal(res["action"])
                            # 語音回應
                            speak(res.get("reply", "收到指令。"))
                        except: 
                            print("❌ AI 回應格式錯誤，正在重試...")
                except sr.UnknownValueError: 
                    # 聽不懂時保持安靜
                    pass
                except KeyboardInterrupt: 
                    speak("小J 正在登出。再見，哥哥。")
                    break
                except Exception as e: 
                    print(f"⚠️ 發生異常: {e}")
    except Exception as e:
        print(f"❌ 致命錯誤: {e}")
        input("請按 Enter 鍵離開...")

if __name__ == "__main__":
    main()