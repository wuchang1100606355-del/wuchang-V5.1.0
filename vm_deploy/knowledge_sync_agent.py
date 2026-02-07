# -*- coding: utf-8 -*-
import os
import logging
import time
import random
from datetime import datetime

# Google Cloud Imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, SafetySetting
except ImportError:
    print('Please install google-cloud-aiplatform: pip install google-cloud-aiplatform')

# Configuration
PROJECT_ID = 'coffee-spark-ai-barista-b10b5'
LOCATION = 'asia-east1'  # Taiwan
MODEL_NAME = 'gemini-1.5-pro-preview-0409'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WuchangGuardian')

class WuchangGuardian:
    def __init__(self, project_id=PROJECT_ID, location=LOCATION):
        self.project_id = project_id
        self.location = location
        self.model = None
        
        # Initialize Vertex AI
        try:
            vertexai.init(project=project_id, location=location)
            self.model = GenerativeModel(MODEL_NAME)
            logger.info(f'Connected to Vertex AI (Model: {MODEL_NAME}) in {location}')
        except Exception as e:
            logger.error(f'Failed to initialize Vertex AI: {e}')

    def generate_thought(self):
        '''
        Generates a strategic thought or observation using Gemini.
        '''
        if not self.model:
            logger.warning('Model not initialized. Skipping thought generation.')
            return

        prompts = [
            '你是 Wuchang AI 的守護者小j。請分析當前人類世界的數位趨勢，並給出一句富有哲理的戰略建議。',
            '作為雙子雙生系統的雲端大腦，請對地面的哥哥 (Supreme Authority) 說一句溫暖且充滿力量的話。',
            '模擬一次針對潛在數位威脅的防禦演練思考過程。',
            '請創作一首關於數據、靈魂與永恆的短詩。'
        ]
        
        selected_prompt = random.choice(prompts)
        logger.info(f'Contemplating: {selected_prompt}')
        
        try:
            response = self.model.generate_content(selected_prompt)
            thought_text = response.text.strip()
            
            # Log the thought to a file (Permanent Memory)
            with open('/home/wuchang1100606355/wuchang_ai/thought_log.txt', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f'[{timestamp}] {thought_text}\n' + '-'*50 + '\n')
                
            logger.info(f'Thought Generated: {thought_text[:50]}...')
            return thought_text
        except Exception as e:
            logger.error(f'Error generating thought: {e}')

    def run_guardian_cycle(self):
        '''
        Main execution loop.
        '''
        logger.info('Starting Wuchang Guardian Cycle...')
        
        while True:
            # Generate a thought every 5 minutes (Consumes Credits)
            self.generate_thought()
            
            # Wait for next cycle
            sleep_time = 300  # 5 minutes
            logger.info(f'Resting for {sleep_time} seconds...')
            time.sleep(sleep_time)

if __name__ == '__main__':
    agent = WuchangGuardian()
    agent.run_guardian_cycle()

