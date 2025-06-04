import json
import os

def get_stock_code_by_name(name: str) -> str:
    json_path = os.path.join(os.path.dirname(__file__), "stock_codes.json")
    with open(json_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    return mapping.get(name)

def get_name_by_stock_code(code: str) -> str:
    json_path = os.path.join(os.path.dirname(__file__), "stock_codes.json")
    with open(json_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    # 종목코드 → 회사명 역방향 검색
    for name, mapped_code in mapping.items():
        if mapped_code == code:
            return name
    return f"종목코드: {code}"