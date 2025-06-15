import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def explain_match(user, trial):
    prompt = f"""
You are a clinical trial eligibility evaluator.

Patient Profile:
- Age: {user['age']}
- Gender: {user['gender']}
- BMI: {user['bmi']}
- Conditions: {', '.join(user['conditions'])}
- Smoker: {user['smoker']}
- Alcohol Use: {user['alcohol']}

Trial Title: {trial['title']}
Eligibility Criteria:
{trial['criteria_text']}

Your Task:
1. Decide if the patient qualifies → respond clearly as:
   QUALIFIES: Yes or No

2. Estimate a MATCH SCORE between 0–100% based on how many criteria the patient meets (e.g., age, gender, BMI, conditions, smoking, alcohol).

3. Structure your explanation in 3 parts:
── MET CRITERIA ──
- list clearly which criteria were satisfied

── UNMET OR DISQUALIFYING CRITERIA ──
- list reasons for disqualification or failed eligibility

── FINAL NOTES ──
- any additional guidance or edge cases

Respond only in this format.
"""

    try:
        res = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt.strip(), "stream": False},
            timeout=300
        )
        res.raise_for_status()
        return res.json().get("response", "").strip()
    except Exception as e:
        return f"⚠️ Ollama explanation failed: {str(e)}"
