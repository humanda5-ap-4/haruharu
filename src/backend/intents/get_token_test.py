import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

appkey = os.getenv("APP_KEY")
appsecret = os.getenv("APP_SECRET")

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

    print(f"[토큰 발급 응답 상태]: {response.status_code}")
    print(f"[토큰 발급 응답 내용]: {response.text}")

    if response.status_code == 200:
        token = response.json().get("access_token", None)
        print(f"[발급된 토큰]: {token}")
        if token:
            with open(TOKEN_FILE, "w") as f:
                f.write(token)
            print("✅ 새 토큰 발급 완료")
            return token
    else:
        print("❌ 토큰 발급 실패")
        return None

if __name__ == "__main__":
    get_new_access_token()
