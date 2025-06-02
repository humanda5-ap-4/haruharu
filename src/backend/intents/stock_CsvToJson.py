import pandas as pd
import json

# CSV 파일 로드
df = pd.read_csv("C:/Users/human/haruharu1/src/backend/intents/kospi_kosdaq_stocks.csv")


# 'Stock Name'을 키로, 'Stock Symbol'을 값으로 딕셔너리 생성
stock_dict = dict(zip(df["Stock Name"], df["Stock Symbol"]))

# JSON 파일로 저장
with open("stock_map.json", "w", encoding="utf-8") as f:
    json.dump(stock_dict, f, ensure_ascii=False, indent=2)

print("✅ stock_map.json 생성 완료!")