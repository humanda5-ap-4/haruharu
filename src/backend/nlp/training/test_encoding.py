# train_ner_model.py

import json
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import TrainingArguments, Trainer, DataCollatorForTokenClassification
from datasets import Dataset

# 경로 및 모델 설정
DATA_PATH = "dataset/final_ie_dataset.json"
MODEL_NAME = "beomi/KcELECTRA-base"  # SNS 특화 모델

# 1. 데이터 로드
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. 라벨 리스트 구성
unique_labels = set(tag for item in data for tag in item["tags"])
label_list = sorted(unique_labels)
label2id = {label: i for i, label in enumerate(label_list)}
id2label = {i: label for label, i in label2id.items()}

# 3. 토크나이저, 모델 불러오기
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(label_list),
    id2label=id2label,
    label2id=label2id
)

# 4. 전처리 함수
def preprocess(example):
    tokens = example["tokens"]
    tags = example["tags"]

    encoding = tokenizer(
        tokens,
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
            labels.append(label2id[tags[word_idx]])
        else:
            # 중간 토큰은 I-로 바꿔줄 수 있음
            label = tags[word_idx]
            if label.startswith("B-"):
                label = label.replace("B-", "I-")
            labels.append(label2id[label])
        previous_word_idx = word_idx

    encoding["labels"] = labels
    return encoding

# 5. 데이터셋 준비
dataset = Dataset.from_list(data)
dataset = dataset.map(preprocess)

# 6. 학습 설정
training_args = TrainingArguments(
    output_dir="./ner_model",
    per_device_train_batch_size=8,
    num_train_epochs=3,
    logging_dir="./logs",
    report_to="none"
)

data_collator = DataCollatorForTokenClassification(tokenizer)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

# 7. 학습 실행
trainer.train()

# 8. 추론 함수
def predict_ner_tags(text):
    encoded = tokenizer(text, return_tensors="pt", return_offsets_mapping=True, truncation=True)
    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=2)[0].tolist()

    decoded_text = tokenizer.decode(input_ids[0], skip_special_tokens=True)
    print("✅ 디코딩된 문장:", decoded_text)  # 한글 확인용

    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    labels = [model.config.id2label[i] for i in predictions]

    result = []
    for token, label in zip(tokens, labels):
        if token not in tokenizer.all_special_tokens:
            result.append((token, label))

    return result


# 9. 테스트 출력
text = "서울에 있는 축제 알려줘"
result = predict_ner_tags(text)

# 토큰만 보기
result = predict_ner_tags("서울에 있는 축제 알려줘")
print("✅ 토큰 + 태그 결과:", result)
