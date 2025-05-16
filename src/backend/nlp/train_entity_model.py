"""
✅ entity 추출(=NER)에 적합한 방법은?
방법	적합도	설명
✅ KoBERT, KoELECTRA NER Fine-tuning	⭐ 최고	HuggingFace에서 BERTForTokenClassification 사용
✅ spaCy (한국어 모델 추가 필요)	중간	정규식 + POS 기반 추출
✅ 정규식 + 키워드 사전	빠르고 쉬움	지금 당장 쓸 수 있음
❌ SBERT	부적합	의미 파악은 좋지만 "어떤 단어가 엔터티인가"는 판단 못함


"""