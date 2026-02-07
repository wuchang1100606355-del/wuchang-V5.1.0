import pyttsx3
import sys

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        
        # Try to find a Chinese voice
        voices = engine.getProperty('voices')
        target_voice = None
        for voice in voices:
            if 'Chinese' in voice.name or 'Taiwan' in voice.name or 'Han' in voice.name:
                target_voice = voice.id
                break
        
        if target_voice:
            engine.setProperty('voice', target_voice)
            
        print(f'[TTS]: {text}')
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        speak(text)
    else:
        # If no arguments, read from stdin (for piping)
        if not sys.stdin.isatty():
            for line in sys.stdin:
                speak(line.strip())
