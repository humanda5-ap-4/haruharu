import argparse
from common.nlu_engine import NLUEngine
from common.train_util import preprocess_data, train_intent_model
from intents import INTENT_HANDLER  # 여기에 각 intent 핸들러 등록되어 있어야 함
from intents import common  # fallback 핸들러

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preprocess", action="store_true")
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--test", type=str)
    parser.add_argument("--ask", type=str)
    args = parser.parse_args()

    if args.preprocess:
        preprocess_data()

    if args.train:
        train_intent_model()

    if args.test:
        print("[INTENT]", NLUEngine.classify_intent(args.test))
        print("[ENTITY]", [f"{e.type}:{e.value}" for e in NLUEngine.extract_entities(args.test)])

    if args.ask:
        intent = NLUEngine.classify_intent(args.ask)
        entities = NLUEngine.extract_entities(args.ask)

        # 🎯 intent에 맞는 핸들러 가져오기
        handler = INTENT_HANDLER.get(intent, common.handle)

        # 🔁 해당 핸들러로 응답 생성
        response = handler(args.ask, entities)
        print("[BOT]", response)

if __name__ == "__main__":
    main()
