from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

# 인덱스 캐싱
cache = {}

def load_index(name):
    if name in cache:
        return cache[name]
    index = faiss.read_index(f"data/{name}_index.faiss")
    names = np.load(f"data/{name}_names.npy", allow_pickle=True)
    cache[name] = (index, names)
    return index, names

def vector_search(name, query, top_k=1):
    index, names = load_index(name)
    vec = model.encode([query])
    D, I = index.search(vec, top_k)
    return [(names[i], D[0][idx]) for idx, i in enumerate(I[0])]
