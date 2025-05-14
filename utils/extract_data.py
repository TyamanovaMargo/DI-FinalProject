import pandas as pd

# Считываем CSV с поддержкой иврита
df = pd.read_csv('sampleOutput-1-100-then-200-381(1).csv', encoding='utf-8')

# Сохраняем в Excel с поддержкой иврита
df.to_excel('output_hebrew.xlsx', index=False, engine='openpyxl')
