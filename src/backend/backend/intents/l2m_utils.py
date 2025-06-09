# intents/l2m_utils.py

import json
import os

def load_json(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

SERVER_MAP = load_json("l2m_server.json")
ITEM_MAP = load_json("l2m_items.json")

def get_server_id_by_name(name: str) -> int:
    return SERVER_MAP.get(name)

def get_item_code_by_name(name: str) -> int:
    return ITEM_MAP.get(name)
