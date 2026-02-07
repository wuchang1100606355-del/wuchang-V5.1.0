import socket
import requests
import json
import time
import os
import platform
import sys

# ==========================================
# ⚔️ 五常 (Wuchang) 控制核心 V5.4
# 代號：Gemini-Twin (雙模版：語音/文字自動切換)
# 狀態：Python 3.14 相容修正版 (修復靈魂錯置)
# ==========================================

# 嘗試匯入語音模組，如果失敗則切換至文字模式
# 這是為了防止在 Python 3.14 上因為 PyAudio 安裝失敗而導致程式崩潰
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    print("⚠️ 警告：找不到語音驅動 (PyAudio/pyttsx3)。")
    print("   (這在 Python 3.14 上是正常的，我們將切換至文字模式)")
    VOICE_AVAILABLE = False
except Exception as e:
    print(f"⚠️ 語音模組載入失敗 ({e})。將切換至 [文字終端模式]。")
    VOICE_AVAILABLE = False

# --- ☁️ 記憶路徑配置區 ---
# 系統會依序檢查以下路徑，找到第一個存在的就使用
POSSIBLE_PATHS = [
    r"J:\共用雲端硬碟\五常雲端空間",      # 優先 1：Google Drive 掛載路徑
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

if CURRENT_HOSTNAME == SERVER_HOSTNAME:
    MODE = "伺服器"
    CONTROL_NIC_IP = SERVER_IP
    LOCAL_LLM_URL = "http://localhost:11434/v1/chat/completions"
    PRIMARY_MODEL = "gemma:2b" 
    FALLBACK_MODEL = "qwen:0.5b"
else:
    MODE = "筆電"
    CONTROL_NIC_IP = "0.0.0.0" 
    LOCAL_LLM_URL = "http://localhost:11434/v1/chat/completions"
    PRIMARY_MODEL = "little-j:latest"
    FALLBACK_MODEL = "llama3"

# 目標 IoT 設備 IP
TARGET_DEVICE_IP = "192.168.50.249"

# --- 🗣️ 初始化語音引擎 ---
engine = None
if VOICE_AVAILABLE:
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        for voice in voices:
            if "Chinese" in voice.name or "Han" in voice.name or "Taiwan" in voice.name:
                engine.setProperty('voice', voice.id)
                break
    except:
        # 如果初始化失敗，也切換回 False
        VOICE_AVAILABLE = False

def speak(text):
    """小J 的嘴巴 (若無語音則只印出文字)"""
    print(f"🤖 小J ({MODE}) 說：{text}")
    if VOICE_AVAILABLE and engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except: pass

def load_cloud_memory():
    print(f"🔍 正在搜尋記憶路徑...")
    valid_path = None
    
    # 搜尋路徑
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            valid_path = path
            print(f"📂 鎖定路徑: {valid_path}")
            break
            
    if not valid_path:
        print("❌ 找不到記憶路徑，將使用預設人格。")
        return None

    memory_content = ""
    # 讀取檔案
    for filename in [MEMORY_FILE, IDENTITY_FILE]:
        full_path = os.path.join(valid_path, filename)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    memory_content += f.read() + "\n"
                print(f"📖 讀取成功: {filename}")
            except: pass
            
    return memory_content

def call_local_llm(user_input, model_name, cloud_memory):
    # 根據是否有記憶來決定 Prompt
    if cloud_memory:
        base_prompt = cloud_memory
    else:
        base_prompt = f"你是五常社區的{MODE}端AI。指揮官是「哥哥」。"

    system_prompt = base_prompt + """
    【重要指令】
    你必須嚴格只回傳以下 JSON 格式，不要有 Markdown：
    {
        "action": "on" | "off" | "none",
        "reply": "繁體中文回應內容"
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
    except: return None

def send_physical_signal(action):
    if action == "none": return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((CONTROL_NIC_IP, 0))
            s.settimeout(2)
            print(f"⚡ 連線設備 {TARGET_DEVICE_IP} 發送: {action}")
            s.connect((TARGET_DEVICE_IP, 80))
            msg = f"SET_STATE={action}\n"
            s.sendall(msg.encode())
    except Exception as e:
        print(f"❌ 發送異常: {e}")

def main():
    print("\n" + "="*40)
    print(f"   ⚔️  五常小J 控制核心 V5.4 ({MODE}版)  ⚔️")
    if not VOICE_AVAILABLE:
        print("   🔇 語音驅動未就緒 (已自動切換至文字模式)")
        print("      (提示: Python 3.14 暫不支援語音套件，請直接打字)")
    else:
        print("   🎤 語音模式已啟動")
    print("="*40)

    cloud_memory = load_cloud_memory()
    active_model = PRIMARY_MODEL
    
    # 測試大腦
    print(f"🧠 正在連結大腦 ({active_model})...")
    if call_local_llm("測試", active_model, cloud_memory) in ["MODEL_NOT_FOUND", None]:
        print(f"⚠️ 切換備用模型: {FALLBACK_MODEL}")
        active_model = FALLBACK_MODEL
    
    speak(f"小J {MODE} 模式上線。指揮官，請下令。")

    # --- 主迴圈 (支援 語音 或 文字) ---
    # 如果有語音就用 Recognizer，沒有就 None
    r = sr.Recognizer() if VOICE_AVAILABLE else None
    
    while True:
        user_text = ""
        
        if VOICE_AVAILABLE:
            print("\n👂 聆聽中... (您可以說話)")
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio = r.listen(source, phrase_time_limit=10)
                    print("🔄 辨識中...")
                    user_text = r.recognize_google(audio, language="zh-TW")
            except sr.UnknownValueError: pass
            except KeyboardInterrupt: break
            except: 
                # 如果麥克風出錯，暫時切換輸入
                print("\n⚠️ 麥克風異常，請直接輸入文字：")
                user_text = input("指揮官 > ")
        else:
            # 純文字模式
            print("\n⌨️  請輸入指令 (輸入 exit 離開):")
            try:
                user_text = input("指揮官 > ")
            except KeyboardInterrupt: break

        if not user_text: continue
        if user_text.lower() in ["exit", "quit"]:
            speak("小J 登出。")
            break

        print(f"🗣️ 指揮官說：{user_text}")
        
        # 思考與執行
        res_str = call_local_llm(user_text, active_model, cloud_memory)
        
        if res_str and res_str != "MODEL_NOT_FOUND":
            try:
                res = json.loads(res_str)
                # 執行物理動作
                if res.get("action") in ["on", "off"]:
                    send_physical_signal(res["action"])
                # 回應
                speak(res.get("reply", "收到"))
            except: 
                print("❌ 回應解析失敗")

if __name__ == "__main__":
    main()