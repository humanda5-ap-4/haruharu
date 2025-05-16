# src/backend/main.py 또는 별도 insert_json.py
import json
from DB.crud import insert_event

def load_and_insert_from_json(path, category="축제"):
    with open(path, encoding="utf-8") as f:
        data_list = json.load(f)

    for item in data_list:
        insert_event(item, category)

if __name__ == "__main__":
    load_and_insert_from_json("nlp/data/festivals.json", category="축제")
