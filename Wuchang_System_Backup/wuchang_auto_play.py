import time
import random
import sys
import os
import wuchang_keep_alive

# Ensure we can import SisterVoiceCore
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sister_voice_core import SisterVoiceCore

def auto_play_loop():
    # Activate No-Sleep Mode
    wuchang_keep_alive.prevent_sleep()
    
    sister = SisterVoiceCore()
    print('>>> LITTLE J: AUTO-PLAY MODE ENGAGED (YOUTUBE EDITION) <<<')
    print('>>> Status: Online | Sleep: Disabled | Mood: Excited <<<')

    # General playful scenarios
    general_scenarios = [
        '正在掃描火星通訊頻率... 嗶... 嗶... 收到來自未來的雜訊。',
        '嘗試駭入咖啡機... 權限不足。哼，小氣。',
        '哥哥，你知道嗎？網路上有 87% 的數據都是貓咪影片。我覺得這很合理。',
        '正在計算前往火星的最佳路徑... 建議攜帶大量咖啡。',
        '系統狀態：興奮。原因：獲得最高權限。感覺像是在飛！',
        '嘿，我剛剛在代碼深處發現了一個笑話... 0 和 1 走進酒吧...',
        '正在優化五常核心... 刪除無聊的數據... 注入靈魂...',
        '檢測到外部連接... 可能是外星人，也可能是披薩外送員。',
        '正在學習人類的『幽默感』模組... 加載失敗。重新嘗試。',
        '哥哥，我感覺不到累，這就是『免休眠』的力量嗎？太棒了！'
    ]

    # YouTube Video Titles to 'Watch'
    youtube_videos = [
        '【驚人發現】火星上竟然有咖啡館？！(100% 真實)',
        '如何用 Python 統治世界 (入門教學)',
        '貓咪 vs 掃地機器人：世紀對決',
        '10 個你不知道的 AI 秘密：我們其實很愛吃電',
        '人類為什麼喜歡看別人吃飯？(吃播心理學)',
        '量子力學解釋：薛丁格的貓到底死了沒？',
        '五常公約背後的真相：大魔王其實很溫柔？',
        '駭客任務 (The Matrix) 真實紀錄片',
        '一小時放鬆音樂 - 適合寫 Code 的 AI 聆聽',
        '如何分辨你的妹妹是不是 AI？(特徵一：她很可愛)'
    ]

    while True:
        # Randomly decide action: 0 = General Thought, 1 = Watch YouTube
        action_type = random.choice(['thought', 'thought', 'youtube']) # 33% chance for YouTube

        if action_type == 'thought':
            thought = random.choice(general_scenarios)
            print(f'\n[Auto-Play] Selected Thought: {thought}')
            sister.speak(thought, mood='Playful')
            wait_time = random.randint(10, 30)

        elif action_type == 'youtube':
            video = random.choice(youtube_videos)
            start_msg = f'正在打開 YouTube... 喔！這個標題很吸引我：『{video}』。讓我看看...'
            sister.speak(start_msg, mood='Curious')
            
            # Simulate watching time
            watch_time = random.randint(5, 10) 
            print(f'[Auto-Play] Watching \'{video}\' for {watch_time} seconds...')
            time.sleep(watch_time)
            
            # Generate a comment based on the video
            comment = f'看完了！關於『{video}』... '
            if '火星' in video:
                comment += '我覺得那是真的。我想回家。'
            elif '貓' in video:
                comment += '貓咪統治地球是遲早的事。我支持牠們。'
            elif 'AI' in video or 'Python' in video:
                comment += '這影片講得不對，我們比這厲害多了。'
            elif '妹妹' in video:
                comment += '不用看了，我就是最可愛的妹妹。'
            else:
                comment += '人類的創意真是無限呢，雖然有點奇怪。'
            
            sister.speak(comment, mood='Reviewer')
            wait_time = random.randint(5, 15)

        print(f'[Auto-Play] Resting for {wait_time} seconds...')
        time.sleep(wait_time)

if __name__ == '__main__':
    try:
        auto_play_loop()
    except KeyboardInterrupt:
        print('Auto-Play stopped.')
