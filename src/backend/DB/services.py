from DB.crud import get_stock_by_name, get_festival_by_name, get_steam_game_by_name, get_l2m_by_item_name


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

ntent_map = {
    "주식": "stock",
    "게임": "game",
    "축제": "festival",
    "l2m": "l2m",
}