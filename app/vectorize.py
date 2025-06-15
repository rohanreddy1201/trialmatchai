# app/vectorize.py
import json, os, pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DATA_PATH = "data/raw_trials.json"
INDEX_PATH = "data/embedded_trials.pkl"

def load_trials():
    with open(DATA_PATH, "r") as f:
        trials = json.load(f)
    return [t for t in trials if t.get("criteria_text")]

def embed_trials(trials, model):
    texts = [t["criteria_text"] for t in trials]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings

def build_faiss_index(vectors):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index

def save(index, trials, vectors):
    with open(INDEX_PATH, "wb") as f:
        pickle.dump({"index": index, "trials": trials, "vectors": vectors}, f)

def main():
    os.makedirs("data", exist_ok=True)
    trials = load_trials()
    model = SentenceTransformer(MODEL_NAME)
    vectors = embed_trials(trials, model)
    index = build_faiss_index(vectors)
    save(index, trials, vectors)
    print(f"✅ Embedded {len(trials)} trials. FAISS index saved to {INDEX_PATH}")

if __name__ == "__main__":
    main()
