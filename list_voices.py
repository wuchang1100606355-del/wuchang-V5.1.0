import pyttsx3
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print('Available Voices:')
    for voice in voices:
        print(f'- ID: {voice.id}')
        print(f'  Name: {voice.name}')
        print(f'  Languages: {voice.languages}')
except Exception as e:
    print(f'Error listing voices: {e}')
