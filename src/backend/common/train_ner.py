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

    MODEL_NAME = "dslim/bert-base-NER"

    # ✅ 데이터 로드
    with open(NER_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # BIO 태그 리스트 추출
    base_labels = {label for item in raw_data for label in item["ner_tags"]}
    label_list = sorted(base_labels)
    label_to_id = {label: i for i, label in enumerate(label_list)}
    id_to_label = {i: label for label, i in label_to_id.items()}

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # label_all_tokens 플래그 (subword에도 라벨 적용 여부)
    label_all_tokens = True

    def tokenize_and_align_labels(example):
        tokenized_inputs = tokenizer(
            example["tokens"],
            is_split_into_words=True,
            truncation=True,
            padding="max_length",
            max_length=128,
            return_offsets_mapping=False
        )

        word_ids = tokenized_inputs.word_ids()
        aligned_labels = []
        previous_word_idx = None

        for word_idx in word_ids:
            if word_idx is None:
                aligned_labels.append(-100)
            elif word_idx != previous_word_idx:
                aligned_labels.append(label_to_id.get(example["ner_tags"][word_idx], -100))
            else:
                aligned_labels.append(label_to_id.get(example["ner_tags"][word_idx], -100) if label_all_tokens else -100)
            previous_word_idx = word_idx

        tokenized_inputs["labels"] = aligned_labels
        return tokenized_inputs

    # HuggingFace Dataset 생성
    dataset = Dataset.from_list(raw_data)
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

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        #evaluation_strategy="epoch",
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
