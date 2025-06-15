# app/trial_ingest.py
import requests, time, json, os

CONDITIONS = [
    "cancer", "diabetes", "asthma", "depression", "hypertension",
    "arthritis", "stroke", "epilepsy", "obesity", "HIV", "COVID-19",
    "chronic pain", "heart disease", "Parkinson's", "Alzheimer's",
    "anxiety", "bipolar disorder", "schizophrenia", "glaucoma",
    "hepatitis", "psoriasis", "multiple sclerosis", "endometriosis",
    "infertility", "osteoporosis", "lymphoma", "melanoma", "IBS",
    "GERD", "insomnia"
]
OUTFILE = "data/raw_trials.json"
MAX_TRIALS = 500
PAGE_SIZE = 100
EXCLUDED_STATUSES = {"COMPLETED", "WITHDRAWN", "TERMINATED", "SUSPENDED", "NO LONGER AVAILABLE"}

def fetch_trials(term):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    params = {"query.term": term, "pageSize": PAGE_SIZE}
    trials = []
    seen = set()
    page = 1

    while True:
        print(f"  🔄 Fetching page {page} with params {params}")
        r = requests.get(base_url, params=params)
        if r.status_code != 200:
            print(f"  ❌ Error {r.status_code} → skipping")
            break

        data = r.json()
        studies = data.get("studies", [])
        print(f"  🔽 Received {len(studies)} studies on page {page}")

        count_before = len(trials)
        for s in studies:
            sec = s.get("protocolSection", {})
            design = sec.get("designModule", {})
            status = sec.get("statusModule", {}).get("overallStatus", "").upper()
            if design.get("studyType") != "INTERVENTIONAL" or status in EXCLUDED_STATUSES:
                continue

            elig = sec.get("eligibilityModule", {})
            idm = sec.get("identificationModule", {})
            phase = design.get("phaseList", ["N/A"])
            sponsor = sec.get("sponsorsModule", {}).get("leadSponsor", {}).get("agencyName")
            enroll = sec.get("enrollmentModule", {}).get("enrollmentCount")
            url = f"https://clinicaltrials.gov/ct2/show/{idm.get('nctId')}"

            nct_id = idm.get("nctId")
            if not nct_id or nct_id in seen:
                continue
            seen.add(nct_id)

            trials.append({
                "nct_id": nct_id,
                "title": idm.get("briefTitle"),
                "conditions": sec.get("conditionsModule", {}).get("conditions", []),
                "min_age": elig.get("minimumAge"),
                "max_age": elig.get("maximumAge"),
                "gender": elig.get("gender"),
                "criteria_text": elig.get("eligibilityCriteria", ""),
                "overall_status": status,
                "phase": phase[0] if isinstance(phase, list) else phase,
                "sponsor": sponsor,
                "enrollment": enroll,
                "url": url
            })

        added = len(trials) - count_before
        print(f"   • {added} trials added on page {page} (total: {len(trials)})")

        if len(trials) >= MAX_TRIALS:
            break

        token = data.get("nextPageToken")
        if not token:
            break

        params["pageToken"] = token
        page += 1
        time.sleep(0.25)

    return trials

def run():
    os.makedirs("data", exist_ok=True)
    all_trials = []
    for cond in CONDITIONS:
        print(f"\n🔍 Searching for trials matching: '{cond}'...")
        trials = fetch_trials(cond)
        print(f"🎯 Done: {len(trials)} total trials collected for '{cond}'")
        all_trials.extend(trials)

    with open(OUTFILE, "w") as f:
        json.dump(all_trials, f, indent=2)
    print(f"\n✅ Final save: {len(all_trials)} trials → {OUTFILE}")

if __name__ == "__main__":
    run()
