from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from DB.db import SessionLocal
from DB.models import StockInfo, SteamDiscountedGames, L2m, FestivalInfo

model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

def fetch_names_from_db(db: Session, model_cls, attr_name):
    return [getattr(obj, attr_name) for obj in db.query(model_cls).all() if getattr(obj, attr_name)]

def build_index_and_save(name, items):
    vectors = model.encode(items, convert_to_numpy=True)
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, f"data/{name}_index.faiss")
    np.save(f"data/{name}_names.npy", items)
    print(f"[Saved] {name} 인덱스 완료 ({len(items)}개)")

def build_all_indexes():
    db = SessionLocal()
    try:
        stock_names = fetch_names_from_db(db, StockInfo, "stock_name")
        game_names = fetch_names_from_db(db, SteamDiscountedGames, "game_name")
        item_names = fetch_names_from_db(db, L2m, "item_name")
        festival_names = fetch_names_from_db(db, FestivalInfo, "festival_name")

        build_index_and_save("stock", stock_names)
        build_index_and_save("game", game_names)
        build_index_and_save("item", item_names)
        build_index_and_save("festival", festival_names)
    finally:
        db.close()

if __name__ == "__main__":
    build_all_indexes()
