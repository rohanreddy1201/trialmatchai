# app/matcher.py
import pickle, re
import numpy as np
from sentence_transformers import SentenceTransformer
from difflib import SequenceMatcher
import faiss

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_PATH = "data/embedded_trials.pkl"

def load_index():
    with open(INDEX_PATH, "rb") as f:
        obj = pickle.load(f)
    return obj["index"], obj["trials"], obj["vectors"]

def age_to_num(age_str):
    if not age_str or age_str == "N/A": return None
    try: return int(age_str.split()[0])
    except: return None

def split_criteria(criteria_text):
    text = criteria_text.lower()
    inc_match = re.search(r"inclusion criteria:?([\s\S]*?)(exclusion criteria|$)", text)
    exc_match = re.search(r"exclusion criteria:?([\s\S]*)", text)
    return (inc_match.group(1).strip() if inc_match else ""), (exc_match.group(1).strip() if exc_match else "")

def fuzzy_match(phrase, text, threshold=0.8):
    return any(SequenceMatcher(None, phrase, t).ratio() > threshold for t in text.split())

def compute_condition_score(user_conds, inclusion_text):
    return sum(1 for cond in user_conds if fuzzy_match(cond, inclusion_text))

def match_trials(user_profile, top_k=10):
    index, trials, vectors = load_index()
    model = SentenceTransformer(MODEL_NAME)

    query_text = f"Clinical trials for: {', '.join(user_profile['conditions'])}"
    query_vec = model.encode([query_text])[0]
    D, I = index.search(np.array([query_vec]), 100)

    user_conds = [c.lower() for c in user_profile["conditions"]]
    scored_trials = []
    seen = set()

    for idx, dist in zip(I[0], D[0]):
        trial = trials[idx]
        if trial["nct_id"] in seen:
            continue
        seen.add(trial["nct_id"])

        inclusion, exclusion = split_criteria(trial["criteria_text"])

        if any(fuzzy_match(cond, exclusion) for cond in user_conds):
            continue

        cond_score = compute_condition_score(user_conds, inclusion)
        if cond_score == 0:
            continue  # ❌ Skip trials not matching any condition

        trial["condition_score"] = cond_score
        trial["semantic_score"] = round(1 / (1 + dist), 4)
        scored_trials.append(trial)

    scored_trials.sort(key=lambda t: (t["condition_score"], t["semantic_score"]), reverse=True)
    return scored_trials[:top_k]
