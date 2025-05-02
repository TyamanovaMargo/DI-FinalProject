import pandas as pd
from translate import Translator

# Загрузка данных
df = pd.read_excel("/Users/margotiamanova/Desktop/DI-FinalProject/output_with_features2.xls")

# Инициализация переводчика
translator = Translator(from_lang="he", to_lang="en")

# Функция для перевода текста
def translate_text(text):
    try:
        if pd.isna(text):
            return text
        return translator.translate(str(text))
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Столбцы для перевода
columns_to_translate = ['Address', 'Seller', 'City', 'Neighborhood']
for col in columns_to_translate:
    df[col] = df[col].apply(translate_text)

# Сохраняем результат
df.to_csv("/Users/margotiamanova/Desktop/DI-FinalProject/translated_file.csv", index=False, encoding='utf-8-sig')

print("Translation complete! File saved.")





