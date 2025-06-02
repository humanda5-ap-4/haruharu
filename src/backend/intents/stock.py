from intents import stock_api
import os

def handle(query: str, entities: list):
    stock_name = None
    for ent in entities:
        if ent.get("type") == "종목명":
            stock_name = ent.get("value")
            break

    if not stock_name:
        return "어떤 종목의 정보를 원하시는지 알려주세요."

    try:
        access_token = os.getenv("ACCESS_TOKEN")
        appkey = os.getenv("APP_KEY")
        appsecret = os.getenv("APP_SECRET")

        stock_code_mapping = stock_api.load_stock_code_mapping()
        stock_code = stock_code_mapping.get(stock_name)

        if not stock_code:
            return f"{stock_name} 종목 코드를 찾을 수 없습니다."

        info = stock_api.get_stock_info_by_code(stock_code, access_token, appkey, appsecret)

        if not info:
            return f"{stock_name} 종목 정보를 가져올 수 없습니다."

        return f"{stock_name} 현재가 {info['price']}원, 전일 대비 {info['diff']}원, 등락률 {info['rate']}% 입니다."

    except Exception as e:
        print("ERROR in stock.handle:", e)
        return "주식 정보를 가져오는 중 오류가 발생했습니다."
