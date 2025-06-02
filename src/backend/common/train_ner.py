def train():
    import json
    import pathlib
    from datasets import Dataset
    from transformers import (
        AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer,
        DataCollatorForTokenClassification
    )
    from seqeval.metrics import accuracy_score, precision_score, recall_score, f1_score

    # 경로 설정
    BASE_DIR = pathlib.Path(__file__).resolve().parents[1]   # backend/
    DATA_DIR = BASE_DIR / "data"
    NLU_DIR = BASE_DIR / "nlu"
    LOG_DIR = BASE_DIR / "logs"
    NER_PATH = DATA_DIR / "ner_dataset.json"
    OUTPUT_DIR = NLU_DIR / "ner_model"

    # 모델 이름
    MODEL_NAME = "dslim/bert-base-NER"

    # ✅ 데이터 로드
    with open(NER_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # BIO 태그 적용된 라벨 리스트 생성
    base_labels = {label for item in raw_data for _, _, label in item["labels"]}
    bio_labels = set()
    for label in base_labels:
        bio_labels.add(f"B-{label}")
        bio_labels.add(f"I-{label}")
    bio_labels.add("O")

    label_list = sorted(bio_labels)
    label_to_id = {label: i for i, label in enumerate(label_list)}
    id_to_label = {i: label for label, i in label_to_id.items()}

    # 토크나이저
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # 토크나이징 + BIO 라벨 정렬
    def tokenize_and_align_labels(example):
        tokenized_inputs = tokenizer(
            example["text"],
            truncation=True,
            padding="max_length",
            max_length=128,
            return_offsets_mapping=True
        )

        labels = ["O"] * len(tokenized_inputs["input_ids"])
        offsets = tokenized_inputs["offset_mapping"]
        entities = json.loads(example["entities"])

        for start, end, label in entities:
            for idx, (offset_start, offset_end) in enumerate(offsets):
                if offset_start == offset_end == 0:
                    continue
                if offset_start >= start and offset_end <= end:
                    if labels[idx] == "O":
                        labels[idx] = f"B-{label}"
                    elif labels[idx].startswith("B-"):
                        labels[idx] = f"I-{label}"
                    elif labels[idx].startswith("I-"):
                        continue

        # BIO 태그를 ID로 변환
        label_ids = [label_to_id.get(l, -100) for l in labels]

        tokenized_inputs["labels"] = label_ids
        tokenized_inputs.pop("offset_mapping")
        return tokenized_inputs

    # HuggingFace Dataset 생성
    dataset = Dataset.from_list([
        {"text": item["text"], "entities": json.dumps(item["labels"])} for item in raw_data
    ])

    dataset = dataset.map(tokenize_and_align_labels)
    split = dataset.train_test_split(test_size=0.2)

    # 모델 초기화
    model = AutoModelForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(label_list),
        id2label=id_to_label,
        label2id=label_to_id,
        ignore_mismatched_sizes=True
    )

    # 학습 인자
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=2,
        logging_dir=str(LOG_DIR),
        logging_steps=10,
        lr_scheduler_type="constant"
    )

    # 평가 메트릭
    def compute_metrics(p):
        predictions, labels = p
        predictions = predictions.argmax(-1)

        true_labels = []
        true_predictions = []

        for pred, label in zip(predictions, labels):
            temp_pred = []
            temp_label = []
            for p_i, l_i in zip(pred, label):
                if l_i != -100:
                    temp_pred.append(id_to_label[p_i])
                    temp_label.append(id_to_label[l_i])
            true_predictions.append(temp_pred)
            true_labels.append(temp_label)

        return {
            "accuracy": accuracy_score(true_labels, true_predictions),
            "precision": precision_score(true_labels, true_predictions),
            "recall": recall_score(true_labels, true_predictions),
            "f1": f1_score(true_labels, true_predictions),
        }

    # 학습 시작
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=split["train"],
        eval_dataset=split["test"],
        tokenizer=tokenizer,
        data_collator=DataCollatorForTokenClassification(tokenizer),
        compute_metrics=compute_metrics
    )

    trainer.train()
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
