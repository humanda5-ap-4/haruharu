import requests
import json
import csv
import os
from dotenv import load_dotenv


load_dotenv() 
appkey = os.getenv("APP_KEY")
appsecret =  os.getenv("APP_SECRET")


TOKEN_FILE = "access_token.txt"

def get_new_access_token():
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "appsecret": appsecret
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        token = response.json().get("access_token", None)
        if token:
            with open(TOKEN_FILE, "w") as f:
                f.write(token)
            print(" 새 토큰 발급 완료")
            return token
    else:
        print("❌ 토큰 발급 실패")
        print(response.text)
        return None

def load_access_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    else:
        return get_new_access_token()

def load_stock_code_mapping(csv_file):
    stock_code_mapping = {}
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # 헤더 스킵
        for row in reader:
            if len(row) >= 3:
                stock_code_mapping[row[0].strip()] = row[1].strip()
    return stock_code_mapping

def get_stock_code_by_name(stock_name, mapping):
    return mapping.get(stock_name, None)

def get_stock_info_by_name(stock_name, access_token, stock_code_mapping, retry=True):
    stock_code = get_stock_code_by_name(stock_name, stock_code_mapping)
    if not stock_code:
        print(f"❌ {stock_name} 종목 코드 찾을 수 없음")
        return

    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/search-stock-info"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "appkey": appkey,
        "appsecret": appsecret,
        "tr_id": "FHKST01010100",
        "custtype": "P"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code
    }

    response = requests.get(url, headers=headers, params=params)
    result_text = response.text

    if (
        (response.status_code == 500 and "기간이 만료된 token" in result_text)
        or response.status_code == 401
    ) and retry:
        print("🔄 토큰 만료됨, 새로 발급받아 재시도 중...")
        new_token = get_new_access_token()
        if new_token:
            get_stock_info_by_name(stock_name, new_token, stock_code_mapping, retry=False)
        else:
            print("❌ 새 토큰 발급 실패")

    else:
        print(f"❌ API 호출 실패 (Status {response.status_code})")
        print(result_text)



access_token = load_access_token()
CSV_PATH = os.path.join(os.path.dirname(__file__), "kospi_kosdaq_stocks.csv")
stock_code_mapping = load_stock_code_mapping(CSV_PATH)




