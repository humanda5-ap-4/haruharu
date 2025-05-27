from DB.crud import get_stock_by_name, get_festival_by_name, get_steam_game_by_name, get_l2m_by_item_name


def handle_stock(db, ents):
    company_names = [e['value'] for e in ents if e['type'] == 'COMPANY']
    if not company_names:
        return "조회할 회사 이름을 찾지 못했습니다."
    stock_data = get_stock_by_name(db, company_names[0])
    if stock_data:
        return f"{stock_data.stock_name} 현재 가격은 {stock_data.price}원입니다."
    return f"{company_names[0]}의 주식 정보를 찾을 수 없습니다."

def handle_festival(db, ents):
    festival_names = [e['value'] for e in ents if e['type'] in ['EVENT', 'LOCATION']]
    if not festival_names:
        return "조회할 축제명이나 장소를 찾지 못했습니다."
    festivals = []
    for name in festival_names:
        f = get_festival_by_name(db, name)
        if f:
            festivals.append(f)
    if festivals:
        return "\n".join([f"{f.festival_name} - {f.festival_loc} ({f.start_date} ~ {f.fin_date})" for f in festivals])
    return "해당 축제 정보를 찾을 수 없습니다."

def handle_game(db, ents):
    game_names = [e['value'] for e in ents if e['type'] == 'GAME']
    if not game_names:
        return "조회할 게임 이름을 찾지 못했습니다."
    games = []
    for name in game_names:
        g = get_steam_game_by_name(db, name)
        if g:
            games.append(g)
    if games:
        return "\n".join([f"{g.game_name} - 할인율: {g.discount_rate*100:.1f}%, 할인된 가격: {g.discounted_price}원" for g in games])
    return "해당 게임 할인 정보를 찾을 수 없습니다."

def handle_l2m(db, ents):
    item_names = [e['value'] for e in ents if e['type'] in ['GAME', 'ITEM']]
    if not item_names:
        return "조회할 아이템 이름을 찾지 못했습니다."
    items = []
    for name in item_names:
        items += get_l2m_by_item_name(db, name)
    if items:
        return "\n".join([f"{i.item_name} (서버: {i.server_name}) 현재 시세: {i.now_mi_nuit_price}원" for i in items])
    return "해당 아이템 정보를 찾을 수 없습니다."
# 매핑 딕셔너리
intent_handlers = {
    "주식": handle_stock,
    "축제": handle_festival,
    "이벤트": handle_festival,
    "게임": handle_game,
    "아이템": handle_l2m,
}
