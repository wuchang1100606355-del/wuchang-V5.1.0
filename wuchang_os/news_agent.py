import requests
import xml.etree.ElementTree as ET
import json
import logging
import os
from datetime import datetime

# Configuration
RSS_URL = 'https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant'
OUTPUT_FILE = r'C:\wuchang V5.1.0\wuchang_os\news_feed.json'
LOG_FILE = r'C:\wuchang V5.1.0\wuchang_os\system_status_detailed.log'

# Setup Logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

def fetch_news():
    try:
        logging.info('Double J Interviewer: Starting news fetch...')
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = []
        
        for item in root.findall('.//item')[:10]: # Top 10 news
            title = item.find('title').text if item.find('title') is not None else 'No Title'
            link = item.find('link').text if item.find('link') is not None else '#'
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            
            items.append({
                'title': title,
                'link': link,
                'pubDate': pubDate,
                'source': 'Google News'
            })
            
        # Save to JSON
        feed_data = {
            'updated': datetime.now().isoformat(),
            'items': items
        }
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(feed_data, f, ensure_ascii=False, indent=2)
            
        logging.info(f'Double J Interviewer: Successfully fetched {len(items)} news items.')
        print(f'Successfully fetched {len(items)} news items.')
        return True
        
    except Exception as e:
        logging.error(f'Double J Interviewer Error: {e}')
        print(f'Error: {e}')
        return False

if __name__ == '__main__':
    fetch_news()
