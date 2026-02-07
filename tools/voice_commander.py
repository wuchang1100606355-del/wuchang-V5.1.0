import threading
import time
import re

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

class VoiceOrderListener:
    def __init__(self, callback):
        self.callback = callback
        self.is_listening = False
        self.recognizer = None
        self.microphone = None
        self.thread = None

        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Adjust for ambient noise automatically
            self.recognizer.dynamic_energy_threshold = True

    def start(self):
        if not SR_AVAILABLE:
            print("[VoiceCommander] speech_recognition library not found. Voice control disabled.")
            return False
        
        try:
            # List microphones to find Bluetooth headset if possible, 
            # but usually default is fine if set in OS.
            self.microphone = sr.Microphone()
            self.is_listening = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            print("[VoiceCommander] Listening for voice orders (Background)...")
            return True
        except Exception as e:
            print(f"[VoiceCommander] Error initializing microphone: {e}")
            return False

    def stop(self):
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=1)

    def _listen_loop(self):
        with self.microphone as source:
            print("[VoiceCommander] Calibrating for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[VoiceCommander] Ready. Speak now.")
            
            while self.is_listening:
                try:
                    # Listen with a timeout to allow loop to check is_listening
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    self._process_audio(audio)
                except sr.WaitTimeoutError:
                    continue # Just loop back
                except Exception as e:
                    print(f"[VoiceCommander] Listen Error: {e}")
                    time.sleep(1)

    def _process_audio(self, audio):
        try:
            # Recognize speech using Google Speech Recognition
            # language='zh-TW' for Traditional Chinese
            text = self.recognizer.recognize_google(audio, language='zh-TW')
            print(f"[VoiceCommander] Heard: {text}")
            
            # Simple Parser
            order = self._parse_order(text)
            if order:
                print(f"[VoiceCommander] Order Recognized: {order}")
                if self.callback:
                    self.callback(order)
            else:
                print("[VoiceCommander] No valid order command found.")

        except sr.UnknownValueError:
            # print("[VoiceCommander] Could not understand audio")
            pass
        except sr.RequestError as e:
            print(f"[VoiceCommander] Service Error: {e}")

    def _parse_order(self, text):
        """
        Simple regex parser for coffee orders.
        Supported patterns: "一杯拿鐵", "兩杯美式", "我要點餐"
        """
        text = text.replace(" ", "") # Remove spaces
        
        # Keywords
        products = {
            "拿鐵": "Latte",
            "美式": "Americano",
            "卡布": "Cappuccino",
            "紅茶": "Black Tea",
            "牛奶": "Milk"
        }
        
        quantities = {
            "一": 1, "二": 2, "兩": 2, "三": 3, "四": 4, "五": 5,
            "1": 1, "2": 2, "3": 3, "4": 4, "5": 5
        }

        found_product = None
        found_qty = 1

        for key, value in products.items():
            if key in text:
                found_product = value
                break
        
        if found_product:
            # Look for quantity
            for q_key, q_val in quantities.items():
                if q_key in text:
                    found_qty = q_val
                    break
            
            return {
                "type": "order",
                "product": found_product,
                "quantity": found_qty,
                "raw_text": text
            }
        
        # Check for system commands
        if "啟動" in text or "開始" in text:
            return {"type": "command", "action": "start", "raw_text": text}
        if "停止" in text or "關閉" in text:
            return {"type": "command", "action": "stop", "raw_text": text}

        return None
