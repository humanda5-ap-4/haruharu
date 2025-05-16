import json
import re

from transformers import AutoTokenizer

ENTITY_PATH = "dataset/entity_dataset.json"
INTENT_PATH = "dataset/intent_dataset.json"
OUTPUT_PATH = "dataset/final_ie_dataset.json"

tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")


with open(ENTITY_PATH, "r", encoding="utf-8") as f:
    entity_dict = json.load(f)

with open(INTENT_PATH, "r", encoding="utf-8") as f:
    intent_data = json.load(f)

def tag_tokens(text, entity_dict):
    tokens = tokenizer.tokenize(text)
    tags = ["O"] * len(tokens)
    
    for entity_type, entity_list in entity_dict.items():
        for entity in entity_list:
            pattern = re.escape(entity)
            match = re.search(pattern, text)
            if match:
                entity_tokens = tokenizer.tokenize(entity)
                for i in range(len(tokens) - len(entity_tokens) + 1):
                    if tokens[i:i+len(entity_tokens)] == entity_tokens:
                        tags[i] = f"B-{entity_type}"
                        for j in range(1, len(entity_tokens)):
                            tags[i+j] = f"I-{entity_type}"
                        break
    return tokens, tags

output_data = []
for item in intent_data:
    text = item["text"]
    intent = item["intent"]
    tokens, tags = tag_tokens(text, entity_dict)
    output_data.append({
        "tokens": tokens,
        "tags": tags,
        "intent": intent
    })

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)