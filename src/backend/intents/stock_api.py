import os
import requests
import json
import csv
from dotenv import load_dotenv
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "kospi_kosdaq_stocks.csv")


load_dotenv()

appkey = os.getenv("APP_KEY")
appsecret = os.getenv("APP_SECRET")

import requests
import json


def load_stock_code_mapping(csv_path=CSV_PATH) -> dict:
    mapping = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["Stock Name"].strip()] = row["Stock Symbol"].strip()
    return mapping

def get_stock_info_by_code(stock_code: str, access_token: str, appkey: str, appsecret: str) -> dict:
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "appkey": appkey,
        "appsecret": appsecret,
        "tr_id": "FHKST01010100",
        "custtype": "P",
    }

    params = {
        "fid_cond_mrkt_div_code": "J",  # KOSPI/KOSDAQ 공통 코드
        "fid_input_iscd": stock_code,
    }

    res = requests.get(url, headers=headers, params=params)
    try:
        data = res.json()
        if data.get("rt_cd") == "0":
                print("✅ 현재가 조회 성공")
                print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
                print("❌ API 오류 발생")
                print(f"에러코드: {data.get('msg_cd')}, 메시지: {data.get('msg1')}")
    except Exception as e:
        print("❌ JSON 파싱 에러:", e)
        return None