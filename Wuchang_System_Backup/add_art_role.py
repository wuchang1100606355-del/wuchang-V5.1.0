import json
import os

CONFIG_PATH = 'wuchang_os/double_j_config.json'

def add_art_role():
    if not os.path.exists(CONFIG_PATH):
        print(f'Error: Config file not found at {CONFIG_PATH}')
        return

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'community_roles' not in config:
            config['community_roles'] = {}
            
        config['community_roles']['art_consultant'] = {
            'name': '教育及美術顧問 (Education and Art Consultant)',
            'access_level': 'Consultant',
            'tier_ref': 'core_vip',
            'capabilities': [
                'UI/UX Design Review',
                'Asset Management',
                'Art Direction',
                'Educational Content Review'
            ],
            'persona': '具備深厚藝術涵養與教育熱忱的顧問。負責為五常社區的視覺呈現與教育內容提供專業指導，確保美感與功能並重。'
        }
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print('Successfully added Education and Art Consultant role to configuration.')
        
    except Exception as e:
        print(f'Error updating config: {e}')

if __name__ == '__main__':
    add_art_role()
