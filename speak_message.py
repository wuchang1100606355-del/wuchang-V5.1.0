import pyttsx3
import sys

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Try to find Hanhan or a Chinese voice
    for voice in voices:
        if 'Hanhan' in voice.name or 'Chinese' in voice.name or 'zh' in voice.languages:
            engine.setProperty('voice', voice.id)
            break
    
    engine.setProperty('rate', 160) # Slightly faster
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        speak(text)
    else:
        print("Usage: python speak_message.py <text>")
