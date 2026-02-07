import json
import matplotlib.pyplot as plt

def analyze_stats(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'Analysis Report for {data['date']}')
    print('-' * 30)
    print(f'Total Revenue: ')
    
    print('\n[Income Sources]')
    for source, amount in data['income_sources'].items():
        percentage = (amount / data['total_revenue']) * 100
        print(f'{source}:  ({percentage:.1f}%)')
        
    print('\n[Platform Performance]')
    for platform in data['platforms']:
        if platform['revenue'] > 0:
            percentage = (platform['revenue'] / data['total_revenue']) * 100
            print(f'{platform['name']}:  ({percentage:.1f}%) - {platform['orders']} Orders')

if __name__ == '__main__':
    analyze_stats(r'C:\wuchang V5.1.0\wuchang_os\legacy_data\legacy_dashboard_stats.json')