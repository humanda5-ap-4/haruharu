import os
import requests
import time
import json
from dotenv import load_dotenv
#from backend.intents.stock_utils import get_stock_code_by_name, get_name_by_stock_code

# ⏰ 여유 시간 (5분) & 유효기간 (24시간)
TOKEN_EXPIRE_BUFFER = 300
TOKEN_VALID_SECONDS = 60 * 60 * 24  # 24시간

# 📦 .env 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

APPKEY = os.getenv("appkey")
APPSECRET = os.getenv("appsecret")
TOKEN_FILE = os.getenv("TOKEN_FILE", "access_token.txt")

print("✅ [DEBUG] appkey:", repr(APPKEY))
print("✅ [DEBUG] appsecret:", repr(APPSECRET[:10]) + "...")


# ✅ 토큰 불러오기 또는 새로 발급
def get_access_token() -> str:
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                token_data = json.load(f)
            if time.time() < token_data["expires_at"] - TOKEN_EXPIRE_BUFFER:
                print("✅ 기존 토큰 재사용")
                return token_data["access_token"]
        except Exception as e:
            print("⚠️ 토큰 파일 읽기 실패:", e)

    return request_new_token()


# ✅ 새 토큰 발급
def request_new_token() -> str:
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"Content-Type": "application/json"}
    data = {
        "grant_type": "client_credentials",
        "appkey": APPKEY,
        "appsecret": APPSECRET
    }

    res = requests.post(url, headers=headers, data=json.dumps(data))
    if res.status_code == 200:
        token = res.json().get("access_token")
        if token:
            with open(TOKEN_FILE, "w") as f:
                json.dump({
                    "access_token": token,
                    "expires_at": time.time() + TOKEN_VALID_SECONDS
                }, f)
            print("✅ 새 토큰 발급 완료")
            return token
    print("❌ 토큰 발급 실패")
    print(res.text)
    return None


# ✅ 주식 정보 조회
def get_stock_info(stock_code: str, access_token: str) -> dict:
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {access_token}",
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code
    }

    res = requests.get(url, headers=headers, params=params)
    if res.status_code != 200:
        print(f"❌ 주식 정보 조회 실패 ({stock_code})")
        print(res.text)
        return {}
    return res.json().get("output", {})


# 🧪 실행 테스트
if __name__ == "__main__":
    # 회사명으로 종목 조회 (ex: 챗봇 입력값)
    input_name = "삼성전자"  # <- 여기 입력만 바꾸면 됨
    stock_code = get_stock_code_by_name(input_name)

    if not stock_code:
        print(f"❌ '{input_name}' 에 해당하는 종목코드가 없습니다.")
        exit()

    token = get_access_token()
    if not token:
        print("❌ 유효한 토큰이 없어 조회 불가")
        exit()

    stock_data = get_stock_info(stock_code, token)
    if not stock_data:
        print("❌ 주식 데이터를 불러오지 못했습니다.")
        exit()

    # 종목코드를 회사명으로 매핑 (API 실패 시에도 대비)
    display_name = (
        stock_data.get("hts_kor_isnm")
        or get_name_by_stock_code(stock_code)
        or f"종목코드: {stock_code}"
    )

    price = stock_data.get("stck_prpr", "N/A")
    change = stock_data.get("prdy_vrss", "0")
    rate = stock_data.get("prdy_ctrt", "0")

    print(f"📈 {display_name} ({stock_code})")
    print(f"💰 현재가: {price}원")
    print(f"📉 전일 대비: {change}원")
    print(f"📊 등락률: {rate}%")
