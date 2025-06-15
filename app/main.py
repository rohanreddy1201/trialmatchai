import streamlit as st
from matcher import match_trials
from llm_explainer import explain_match

st.set_page_config(page_title="TrialMatchAI", layout="wide")
st.title("🧪 TrialMatchAI – Clinical Trial Eligibility Matcher")

ALL_CONDITIONS = [
    "cancer", "diabetes", "asthma", "depression", "hypertension",
    "arthritis", "stroke", "epilepsy", "obesity", "HIV", "COVID-19",
    "chronic pain", "heart disease", "Parkinson's", "Alzheimer's",
    "anxiety", "bipolar disorder", "schizophrenia", "glaucoma",
    "hepatitis", "psoriasis", "multiple sclerosis", "endometriosis",
    "infertility", "osteoporosis", "lymphoma", "melanoma", "IBS",
    "GERD", "insomnia"
]

with st.sidebar:
    st.header("User Profile")
    age = st.slider("Age", 18, 90, 35)
    gender = st.selectbox("Gender", ["male", "female"])
    bmi = st.slider("BMI", 10, 50, 22)
    conditions = st.multiselect("Conditions", ALL_CONDITIONS, default=["cancer"])
    smoker = st.selectbox("Smoker?", ["unspecified", "yes", "no"])
    alcohol = st.selectbox("Alcohol Use?", ["unspecified", "none", "light", "moderate", "heavy"])

if st.button("🔍 Find Matching Trials"):
    user = {
        "age": age,
        "gender": gender,
        "bmi": bmi,
        "conditions": conditions,
        "smoker": smoker,
        "alcohol": alcohol
    }

    with st.spinner("Matching..."):
        matches = match_trials(user, top_k=10)

    if not matches:
        st.warning("No matched trials found.")
    else:
        for i, trial in enumerate(matches):
            with st.expander(f"{i+1}. {trial.get('title', 'Unknown Title')}"):
                st.markdown(f"**🧾 NCT ID:** {trial.get('nct_id', 'N/A')}")
                st.markdown(f"**📋 Conditions:** {', '.join(trial.get('conditions', []))}")
                st.markdown(f"**🧍 Gender Eligibility:** {trial.get('gender', 'N/A')}")
                st.markdown(f"**🎯 Age Range:** {trial.get('min_age', 'N/A')} – {trial.get('max_age', 'N/A')}")
                st.markdown(f"**📅 Status:** {trial.get('overall_status', 'N/A')}")
                st.markdown(f"**🧪 Phase:** {trial.get('phase', 'N/A')}")
                st.markdown(f"**🏢 Sponsor:** {trial.get('sponsor', 'N/A')}")
                st.markdown(f"**👥 Enrollment:** {trial.get('enrollment', 'N/A')}")
                st.markdown(f"**🔗 [View Trial on ClinicalTrials.gov]({trial.get('url', '#')})**")
                st.divider()

                st.markdown(f"🧠 **Semantic Score:** `{trial.get('semantic_score')}`")
                st.markdown(f"🎯 **Condition Score:** `{trial.get('condition_score')}`")

                st.subheader("📜 Eligibility Criteria")
                st.write(trial.get("criteria_text", "No criteria provided."))

                with st.spinner("LLM reasoning..."):
                    explanation = explain_match(user, trial)

                # Extract match score line and isolate qualification
                lines = explanation.splitlines()
                status_line = next((line for line in lines if "qualifies" in line.lower()), "")
                match_line = next((line for line in lines if "match score" in line.lower()), "")
                if status_line: st.markdown(f"✅ **Eligibility:** `{status_line.strip()}`")
                if match_line: st.markdown(f"📊 **Match Score:** `{match_line.strip()}`")

                st.subheader("🧠 Match Evaluation")
                st.write(explanation)
