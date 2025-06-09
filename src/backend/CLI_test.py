import argparse
from common.nlu_engine import NLUEngine
from common.train_util import preprocess_data, train_intent_model
#from intents import INTENT_HANDLER  # 여기에 각 intent 핸들러 등록되어 있어야 함
#from intents import common  # fallback 핸들러
from intents.stock import handle as handle_stock_intent
from intents.festival import handle as handle_festival
from intents.steam import handle as handle_steam_intent
from intents.l2m import handle as handle_lineage2_intent
from intents.common import handle as handle_common

INTENT_HANDLER = {
    "stock": handle_stock_intent,
    "festival": handle_festival,
    "steam": handle_steam_intent,
    "lineage2": handle_lineage2_intent,
    "common": handle_common,  # fallback 핸들러
}
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preprocess", action="store_true")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--test", type=str)
    parser.add_argument("--ask", type=str)
    parser.add_argument("--train_ner", action="store_true")
    args = parser.parse_args()

    if args.preprocess:
        preprocess_data()

    elif args.train:
        train_intent_model()

    elif args.train_ner:
        from common import train_ner
        train_ner.train()  # train_ner.py에 train() 함수 만들기

    elif args.test:
        engine = NLUEngine()
        print("[INTENT]", engine.classify_intent(args.test))
        print("[ENTITY]", [f"{e.type}:{e.value}" for e in engine.extract_entities(args.test)])
        entities = engine.extract_entities("세동 주가 알려줘")
        print("✅ 엔티티 디버깅:", [(e.start, e.end, e.type, e.value) for e in entities])

    elif args.ask:
        engine = NLUEngine()
        intent = engine.classify_intent(args.ask)
        entities = engine.extract_entities(args.ask)
        handler = INTENT_HANDLER.get(intent, handle_lineage2_intent)
        response = handler(args.ask, entities)
        print("[BOT]", response)

    


if __name__ == "__main__":
    main()
