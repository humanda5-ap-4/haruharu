from DB.crud import get_stock_by_name, get_festival_by_name, get_steam_game_by_name, get_l2m_by_item_name
from utils.vector_search import vector_search

def handle_stock(db, user_query):
    matches = vector_search("stock", user_query)
    if not matches:
        return "적절한 회사명을 찾지 못했습니다."
    stock_name, _ = matches[0]
    stock = get_stock_by_name(db, stock_name)
    if stock:
        return f"{stock.stock_name} 현재 가격은 {stock.price}원입니다."
    return f"{stock_name}에 대한 정보를 찾을 수 없습니다."

def handle_most_expensive_stock(db, entities, text):
    result = db.execute("SELECT name, price FROM stocks ORDER BY price DESC LIMIT 1").fetchone()
    if result:
        return f"가장 비싼 주식은 {result.name}이고, 가격은 {result.price}원입니다."
    else:
        return "주식 데이터를 찾을 수 없습니다."
    
    
def handle_game(db, user_query):
    matches = vector_search("game", user_query)
    if not matches:
        return "게임 이름을 찾지 못했습니다."
    game_name, _ = matches[0]
    g = get_steam_game_by_name(db, game_name)
    if g:
        return f"{g.game_name} - 할인율: {g.discount_rate*100:.1f}%, 현재가: {g.discounted_price}원"
    return f"{game_name}에 대한 정보를 찾을 수 없습니다."

def handle_item(db, user_query):
    matches = vector_search("item", user_query)
    if not matches:
        return "아이템 이름을 찾지 못했습니다."
    item_name, _ = matches[0]
    items = get_l2m_by_item_name(db, item_name)
    if items:
        return "\n".join([f"{i.item_name} (서버: {i.server_name}) → {i.now_mi_nuit_price}원" for i in items])
    return f"{item_name}에 대한 아이템 정보를 찾을 수 없습니다."

def handle_festival(db, user_query):
    matches = vector_search("festival", user_query)
    if not matches:
        return "축제 이름을 찾지 못했습니다."
    name, _ = matches[0]
    f = get_festival_by_name(db, name)
    if f:
        return f"{f.festival_name} - {f.festival_loc} ({f.start_date} ~ {f.fin_date})"
    return f"{name}에 대한 축제 정보를 찾을 수 없습니다."

intent_handlers = {
    "주식": handle_stock,
    "게임": handle_game,
    "아이템": handle_item,
    "축제": handle_festival,
}
