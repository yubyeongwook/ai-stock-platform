import pandas as pd

# CSV 파일을 읽어서 엑셀로 저장
csv_file = "us_market_news_2026-03-14_19-21-39.csv"
excel_file = "us_market_news_2026-03-14_19-21-39.xlsx"

df = pd.read_csv(csv_file)
df.to_excel(excel_file, index=False)

print(f"엑셀 파일로 저장 완료: {excel_file}")
