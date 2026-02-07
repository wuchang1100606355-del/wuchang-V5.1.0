import pandas as pd
import os

file_path = 'J:\\共用雲端硬碟\\五常雲端空間\\匯出菜單-聊閣社區咖啡重新店-QC_1760535925901.xlsx'

try:
    xl = pd.ExcelFile(file_path)
    
    # Read '主商品項目'
    print('\n--- Sheet: 主商品項目 (Main Items) ---')
    df_items = xl.parse('主商品項目')
    print(df_items.head(10).to_markdown(index=False, numalign='left', stralign='left'))
    print(f'Columns: {df_items.columns.tolist()}')

    # Read '加購題型選項組合'
    print('\n--- Sheet: 加購題型選項組合 (Option Groups) ---')
    df_groups = xl.parse('加購題型選項組合')
    print(df_groups.head(5).to_markdown(index=False, numalign='left', stralign='left'))

except Exception as e:
    print(f'Error reading Excel file: {e}')

