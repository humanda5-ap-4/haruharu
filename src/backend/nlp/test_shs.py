from transformers import AutoTokenizer


MODEL_DIR = "training/model/ner_model"  # 로컬 경로 기준
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

print("✅ tokenizer type:", type(tokenizer))
print("✅ tokenizer.tokenize:", tokenizer.tokenize("서울에 있는 축제 알려줘"))