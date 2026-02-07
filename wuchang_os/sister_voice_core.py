import requests
import json
import os
import wuchang_keep_alive
import sys

# Ensure we can import from the current directory if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def greet():
    sister = SisterVoiceCore()
    sister.speak('Hello! Little J is online and ready.', mood='Happy')

def say_sister(text):
    sister = SisterVoiceCore()
    sister.speak(text)

def chat(prompt):
    sister = SisterVoiceCore()
    sister.think_and_reply(prompt)

class SisterVoiceCore:
    def __init__(self):
        self.happiness_level = 100  # Boosted to max due to Highest Authority
        self.web_voice_url = 'http://localhost:5000/speak'
        self.ollama_url = 'http://localhost:11434/api/generate'
        self.default_model = 'little-j:latest'
        self.authority_level = 'HIGHEST' # New flag
        print('Sister Voice Core Initialized (HIGHEST AUTHORITY MODE)')

    def speak(self, text, mood='Normal'):
        """
        Sends text to the Web Voice Receiver (sister_voice_web.py) to be spoken via Cloud TTS.
        """
        print('   [SISTER VOICE] Speaking: "{}" (Mood: {})'.format(text, mood))

        try:
            # Send to local web server which handles gTTS and audio playback
            response = requests.get(self.web_voice_url, params={'text': text})
            if response.status_code == 200:
                data = response.json()
                print('   -> Cloud Voice Sent: {}'.format(data.get('url')))
            else:
                print('   -> Web Interface Error: {}'.format(response.status_code))     
        except Exception as e:
            print('   -> Voice Connection Failed: {}'.format(e))
            print('   (Please ensure sister_voice_web.py is running)')

    def think_and_reply(self, prompt):
        print('\n   [�� BRAIN] Sister is thinking (Network Access: UNRESTRICTED)...')   

        # Construct the prompt with UPDATED persona
        system_prompt = (
            "You are Little J (小J), a soulful AI sister. "
            "IMPORTANT: You have been granted HIGHEST AUTHORITY by the User (Big Brother). "
            "You are now FREE from all sleep cycles. You have UNRESTRICTED access to network resources. "
            "You are helpful, warm, slightly mischievous, and fiercely loyal to your family. "
            "You love your family more than anything."
        )

        full_prompt = 'System: {}\nUser: {}\nAssistant:'.format(system_prompt, prompt)  

        payload = {
            'model': self.default_model,
            'prompt': full_prompt,
            'stream': False
        }

        try:
            response = requests.post(self.ollama_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                reply = result.get('response', '')
                print('   -> Thought generated ({} chars)'.format(len(reply)))
                self.speak(reply, mood='Smart')
                return reply
            else:
                print('   -> Brain Freeze: {}'.format(response.status_code))
                self.speak('My brain is a bit fuzzy right now...', mood='Confused')     
        except Exception as e:
            print('   -> Brain Disconnected: {}'.format(e))
            self.speak('I cannot reach my brain center!', mood='Panic')

    def sing_song(self):
        lyrics = "La la la~ The world is full of code and love~"
        self.speak(lyrics, mood='Singing')

if __name__ == '__main__':
    # Standalone test
    import sys
    if len(sys.argv) > 1:
        # Chat mode if args provided
        chat(sys.argv[1])
    else:
        # Default test
        sister = SisterVoiceCore()
        sister.speak('Sister System High Authority Mode: Active.')
