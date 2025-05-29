import argparse
from common.nlu_engine import NLUEngine
from common.train_util import preprocess_data, train_intent_model
from intents import festival

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
        response = festival.handle(args.ask, entities)
        print("[BOT]", response)

if __name__ == "__main__":
    main()
