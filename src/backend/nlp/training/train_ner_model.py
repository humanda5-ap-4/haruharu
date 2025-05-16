import json
import torch
from transformers import BertTokenizerFast, BertForTokenClassification
from transformers import TrainingArguments, Trainer, DataCollatorForTokenClassification
from datasets import Dataset
import os
import shutil
import re

# 캐시 삭제 (선택사항)
#shutil.rmtree(os.path.expanduser("~/.cache/huggingface"), ignore_errors=True)

# 설정
DATA_PATH = "dataset/final_ie_dataset_word.json"
MODEL_NAME = "kykim/bert-kor-base"
OUTPUT_DIR = "training/model/ner_model_kykim"

def recover_words(tokens, tags):
    words = []
    labels = []
    buffer = ""
    buffer_label = None

    for token, tag in zip(tokens, tags):
        if token.startswith("##"):
            buffer += token[2:]
        else:
            if buffer:
                words.append(buffer)
                labels.append(buffer_label if buffer_label else "O")
            buffer = token
            buffer_label = tag if tag.startswith("B-") else tag
    if buffer:
        words.append(buffer)
        labels.append(buffer_label if buffer_label else "O")
    return words, labels

# 변환 실행
with open("dataset/final_ie_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

new_data = []
for item in data:
    words, labels = recover_words(item["tokens"], item["tags"])
    new_data.append({
        "tokens": words,
        "tags": labels,
        "intent": item["intent"]
    })

# 저장
with open("dataset/final_ie_dataset_word.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)



# 1. 데이터 로드
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. 라벨 설정
unique_labels = sorted(set(tag for item in data for tag in item["tags"]))
label2id = {label: i for i, label in enumerate(unique_labels)}
id2label = {i: label for label, i in label2id.items()}

# 3. 모델, 토크나이저 로드
tokenizer = BertTokenizerFast.from_pretrained(MODEL_NAME)
model = BertForTokenClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(label2id),
    id2label=id2label,
    label2id=label2id
)

# 4. 전처리 함수
def preprocess(example):
    encoding = tokenizer(
        example["tokens"],
        is_split_into_words=True,
        truncation=True,
        padding="max_length",
        max_length=64
    )
    word_ids = encoding.word_ids()
    labels = []
    previous_word_idx = None
    for word_idx in word_ids:
        if word_idx is None:
            labels.append(-100)
        elif word_idx != previous_word_idx:
            labels.append(label2id[example["tags"][word_idx]])
        else:
            tag = example["tags"][word_idx]
            tag = tag.replace("B-", "I-") if tag.startswith("B-") else tag
            labels.append(label2id[tag])
        previous_word_idx = word_idx
    encoding["labels"] = labels
    return encoding

# 5. 데이터셋 준비
dataset = Dataset.from_list(data)
dataset = dataset.map(preprocess)

# 6. 학습 설정
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=8,
    num_train_epochs=3,
    logging_dir="./logs",
    report_to="none",
    save_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=DataCollatorForTokenClassification(tokenizer),
    tokenizer=tokenizer,
)

# 7. 학습 실행
trainer.train()

# 8. 저장
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

# 9. 추론 함수
def predict_ner_tags(text):
    encoded = tokenizer(text, return_tensors="pt", return_offsets_mapping=True, truncation=True)
    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=2)[0].tolist()
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    labels = [model.config.id2label[i] for i in predictions]

    result = []
    for token, label in zip(tokens, labels):
        if token not in tokenizer.all_special_tokens:
            result.append((token, label))
    return result

# 10. 테스트
if __name__ == "__main__":
    print("✅ 토크나이저 타입:", type(tokenizer))
    print("✅ tokenizer.tokenize:", tokenizer.tokenize("서울에 있는 축제 알려줘"))

    results = predict_ner_tags("서울에 있는 축제 알려줘")
    print("✅ NER 결과:")
    for token, label in results:
        print(f"{token}\t{label}")
