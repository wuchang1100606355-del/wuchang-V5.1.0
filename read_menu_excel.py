import pandas as pd
import os

file_path = 'J:\\共用雲端硬碟\\五常雲端空間\\匯出菜單-聊閣社區咖啡重新店-QC_1760535925901.xlsx'

try:
    # Read the Excel file
    xl = pd.ExcelFile(file_path)
    print(f'Sheet names: {xl.sheet_names}')

    # Read the first sheet
    df = xl.parse(xl.sheet_names[0])
    
    # Display the first few rows and columns to understand structure
    print('\nFirst 5 rows:')
    print(df.head().to_markdown(index=False, numalign='left', stralign='left'))
    
    # Try to find relevant columns like 'Product Name', 'Price', 'Category'
    print('\nColumns:')
    print(df.columns.tolist())

except Exception as e:
    print(f'Error reading Excel file: {e}')

