from DB.crud import get_stock_by_name, get_festival_by_name, get_steam_game_by_name, get_l2m_by_item_name

def handle_stock(db, ents):
    # 'COMPANY' 엔티티는 기업명, 'STOCK'은 주가 관련 단어(무시 가능)
    company_names = [e['value'] for e in ents if e['type'] == 'COMPANY']
    if not company_names:
        return None
    stock_data = get_stock_by_name(db, company_names[0])
    if not stock_data:
        return None
    return {"type": "stock", "name": stock_data.stock_name, "price": stock_data.price}

def handle_festival(db, ents):
    # 'EVENT', 'LOCATION' 모두 축제 관련 단어
    festival_names = [e['value'] for e in ents if e['type'] in ['EVENT', 'LOCATION']]
    if not festival_names:
        return None
    festivals = []
    for name in festival_names:
        f = get_festival_by_name(db, name)
        if f:
            festivals.append({
                "name": f.festival_name,
                "location": f.festival_loc,
                "start": f.start_date,
                "end": f.fin_date
            })
    return {"type": "festival", "data": festivals} if festivals else None

def handle_game(db, ents):
    game_names = [e['value'] for e in ents if e['type'] == 'GAME']
    if not game_names:
        return None
    games = []
    for name in game_names:
        g = get_steam_game_by_name(db, name)
        if g:
            games.append({
                "name": g.game_name,
                "discount": g.discount_rate * 100,
                "price": g.discounted_price
            })
    return {"type": "game", "data": games} if games else None

def handle_l2m(db, ents):
    item_names = [e['value'] for e in ents if e['type'] in ['GAME', 'ITEM']]
    if not item_names:
        return None
    items = []
    for name in item_names:
        results = get_l2m_by_item_name(db, name)
        for i in results:
            items.append({
                "name": i.item_name,
                "server": i.server_name,
                "price": i.now_mi_nuit_price
            })
    return {"type": "l2m", "data": items} if items else None

def generate_answer(intent: str, result):
    if result is None:
        return "죄송합니다. 관련된 정보를 찾지 못했어요."

    if intent == "stock":
        return f"{result['name']}의 현재 주가는 약 {result['price']:,}원입니다."

    if intent == "game":
        return "\n".join([
            f" {g['name']} - {g['discount']:.1f}% 할인 중! 현재 가격: {g['price']:,}원"
            for g in result['data']
        ])

    if intent == "festival":
        return "\n".join([
            f" {f['name']} 축제\n 장소: {f['location']}\n🗓 일정: {f['start']} ~ {f['end']}"
            for f in result['data']
        ])

    if intent == "l2m":
        return "\n".join([
            f"🛡 {i['name']} (서버: {i['server']})\n 현재 시세: {i['price']:,}원"
            for i in result['data']
        ])

    return "죄송해요. 요청하신 정보를 이해하지 못했어요."

intent_map = {
    "주식": "stock",
    "게임": "game",
    "축제": "festival",
    "l2m": "l2m",
}