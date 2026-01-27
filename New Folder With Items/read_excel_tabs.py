import pandas as pd

file_path = 'Template off duty 2026 v3.xlsx'

# First, list all sheet names
xl_file = pd.ExcelFile(file_path)
print('=== Available Sheets ===')
for i, sheet in enumerate(xl_file.sheet_names, 1):
    print(f'{i}. {sheet}')
print()

# Read the managers day shift tab
try:
    df_managers = pd.read_excel(file_path, sheet_name='managers day shift')
    print('=== MANAGERS DAY SHIFT ===')
    print(f'Shape: {df_managers.shape[0]} rows x {df_managers.shape[1]} columns')
    print()
    print(df_managers.to_string())
    print('\n' + '='*80 + '\n')
except Exception as e:
    print(f'Error reading managers day shift: {e}')
    print()

# Read the night shift tab
try:
    df_night = pd.read_excel(file_path, sheet_name='night shift')
    print('=== NIGHT SHIFT ===')
    print(f'Shape: {df_night.shape[0]} rows x {df_night.shape[1]} columns')
    print()
    print(df_night.to_string())
except Exception as e:
    print(f'Error reading night shift: {e}')
