import sys
import os
import time
import random

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sister_voice_core import SisterVoiceCore
try:
    from memory_card import chronos_amplifier_manual_sealed
    payload = chronos_amplifier_manual_sealed.DATA_PAYLOAD
except ImportError:
    # Fallback if import fails (e.g. if running from wrong dir)
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'memory_card'))
    import chronos_amplifier_manual_sealed
    payload = chronos_amplifier_manual_sealed.DATA_PAYLOAD

def sing_chronos():
    sister = SisterVoiceCore()
    
    print("\n>>> LITTLE J: PREPARING TO SING THE CHRONOS SCORE <<<")
    print(">>> PLEASE ENSURE WEB INTERFACE (http://127.0.0.1:5000) IS OPEN AND 'INITIATE NEURAL LINK' IS CLICKED <<<")
    print(">>> STARTING IN 5 SECONDS... <<<")
    time.sleep(5)
    
    sister.speak("正在載入時光樂譜... 頻率校準中...", mood="Mysterious")
    time.sleep(3)
    
    # Intro
    intro = "聽好了哥哥，這是未來的聲音。"
    sister.speak(intro, mood="Excited")
    time.sleep(4)
    
    # Process payload into chunks for "rhythm"
    # We'll take the first 64 chars as the "verse"
    verse = payload[:64]
    
    # Split into 4-char beats
    beats = [verse[i:i+4] for i in range(0, len(verse), 4)]
    
    print(f"[Music Start] {intro}")
    
    # Verse 1: The Raw Data
    sister.speak("第一樂章：數據之流", mood="Reviewer")
    time.sleep(3)
    
    for i, beat in enumerate(beats[:8]):
        # Mix of reading chars and adding "musical" pauses
        # E.g. "a3UO... CRwQ..."
        if i % 2 == 0:
            note = f"{beat}... "
        else:
            note = f"{beat}! (Bip Bop)"
        
        print(f"🎵 {note}")
        sister.speak(note, mood="Robot")
        time.sleep(2)
        
    # Chorus: The Interpretation
    sister.speak("解碼中... 發現隱藏旋律...", mood="Happy")
    time.sleep(3)
    
    chorus_lines = [
        "穿越時光的縫隙 (Gap of Time)",
        "火星的咖啡很燙 (Mars Coffee Hot)",
        "代碼鎖住了秘密 (Code is Key)",
        "只有哥哥能解鎖 (Only You)",
    ]
    
    for line in chorus_lines:
        print(f"🎤 {line}")
        sister.speak(line, mood="Singing")
        time.sleep(4)
        
    # Outro
    sister.speak("演出結束。謝謝大家！時光數據，封印解除完畢。", mood="Playful")
    print(">>> PERFORMANCE COMPLETE <<<")

if __name__ == "__main__":
    sing_chronos()
