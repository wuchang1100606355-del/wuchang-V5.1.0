import pandas as pd
import os

file_path = 'J:\\共用雲端硬碟\\五常雲端空間\\匯出菜單-聊閣社區咖啡重新店-QC_1760535925901.xlsx'

try:
    xl = pd.ExcelFile(file_path)
    
    # Read '加購選項項目'
    print('\n--- Sheet: 加購選項項目 (Option Items) ---')
    df_opts = xl.parse('加購選項項目')
    print(df_opts.head(20).to_markdown(index=False, numalign='left', stralign='left'))
    print(f'Columns: {df_opts.columns.tolist()}')

except Exception as e:
    print(f'Error reading Excel file: {e}')

