# jules_voice_processor.py 
# Wuchang Neural Link - Auditory Module 
# 負責將實體世界的聲波轉換為 STAPS 神經訊號 
 
import time 
import queue 
import threading 
import speech_recognition as sr 
from staps_kernel_service import StapsKernel, NeuralSignal 
 
class JulesEars: 
     def __init__(self): 
         self.kernel = StapsKernel() # 連接大腦 (Singleton) 
         self.recognizer = sr.Recognizer() 
         self.microphone = sr.Microphone() 
         self.audio_queue = queue.Queue() 
         self.is_listening = False 
         
         # 優化識別參數 
         self.recognizer.energy_threshold = 4000 
         self.recognizer.dynamic_energy_threshold = True 
 
     def _listen_loop(self): 
         """ 
         [生產者] 專注於監聽麥克風，將音訊丟入緩衝區 
         """ 
         print("[JULES] Auditory cortex online. Calibrating noise levels...") 
         with self.microphone as source: 
             self.recognizer.adjust_for_ambient_noise(source, duration=1) 
             print("[JULES] Calibration complete. Listening for commands...") 
             
             while self.is_listening: 
                 try: 
                     # 監聽 (非阻塞模式由執行緒實現) 
                     audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=5) 
                     self.audio_queue.put(audio) 
                     # print("[EAR] Audio captured -> Queue") 
                 except sr.WaitTimeoutError: 
                     pass 
                 except Exception as e: 
                     print(f"[EAR ERROR] {e}") 
 
     def _process_loop(self): 
         """ 
         [消費者] 從緩衝區取出音訊 -> 轉文字 -> 寫入 STAPS 核心 
         """ 
         while self.is_listening: 
             try: 
                 # 阻塞直到有音訊進來 
                 audio = self.audio_queue.get(timeout=1) 
             except queue.Empty: 
                 continue 
 
             try: 
                 # 調用 STT 引擎 (這裡使用 Google 引擎，未來可換成本地 Whisper) 
                 text = self.recognizer.recognize_google(audio, language="zh-TW") 
                 
                 if text: 
                     print(f"\n[JULES HEARD] >> \"{text}\"") 
                     
                     # === 關鍵：注入核心 === 
                     # 這將觸發 STAPS 的 O(1) 寫入 
                     # 使用 run_until_complete 是因為我們在非 async 函數中調用 async 方法 
                     import asyncio 
                     asyncio.run(self.kernel.broadcast( 
                         intent="VOICE_COMMAND", 
                         payload={"text": text, "confidence": 1.0} 
                     )) 
                     
             except sr.UnknownValueError: 
                 pass # 沒聽清楚，忽略 
             except sr.RequestError as e: 
                 print(f"[NETWORK ERROR] Could not request results; {e}") 
 
     def start(self): 
         self.is_listening = True 
         
         # 啟動聽覺執行緒 
         t_listen = threading.Thread(target=self._listen_loop) 
         t_listen.daemon = True # 主程式結束時自動關閉 
         t_listen.start() 
         
         # 啟動解析執行緒 
         t_process = threading.Thread(target=self._process_loop) 
         t_process.daemon = True 
         t_process.start() 
         
         print("[SYSTEM] Jules Voice Processor Started. Background threads active.") 
 
if __name__ == "__main__": 
     ears = JulesEars() 
     ears.start() 
     
     # 保持主程式運行，模擬 OS 常駐 
     try: 
         while True: 
             time.sleep(1) 
     except KeyboardInterrupt: 
         print("\n[SYSTEM] Shutting down auditory module...")

