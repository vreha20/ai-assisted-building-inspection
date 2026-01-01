import streamlit as st
import pandas as pd

# -----------------------------
# Dummy Inspection Data
# -----------------------------
data = [
    {"FINDING_ID": 1, "NOTE_TEXT": "Crack found in main beam near entrance"},
    {"FINDING_ID": 2, "NOTE_TEXT": "Water leakage and dampness on ceiling"},
    {"FINDING_ID": 3, "NOTE_TEXT": "Exposed electrical wiring near panel"},
    {"FINDING_ID": 4, "NOTE_TEXT": "Fire extinguisher missing on floor 2"},
    {"FINDING_ID": 5, "NOTE_TEXT": "Minor paint damage observed"}
]

df = pd.DataFrame(data)

# -----------------------------
# AI Classification Logic
# -----------------------------
KEYWORDS = {
    "Structural": ["crack", "beam", "pillar", "foundation"],
    "Water Damage": ["leak", "damp", "moisture", "water"],
    "Electrical": ["wire", "electrical", "short circuit", "panel"],
    "Fire Hazard": ["fire", "smoke", "flammable", "extinguisher"]
}

RISK_SCORE = {
    "Structural": 9,
    "Fire Hazard": 8,
    "Electrical": 7,
    "Water Damage": 6,
    "General": 3
}

def classify_issue(note):
    note_lower = note.lower()
    for issue_type, keywords in KEYWORDS.items():
        if any(k.lower() in note_lower for k in keywords):
            return issue_type, RISK_SCORE[issue_type]
    return "General", RISK_SCORE["General"]

df[['Issue Type', 'Risk Score']] = df['NOTE_TEXT'].apply(lambda x: pd.Series(classify_issue(x)))

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="AI-Assisted Inspection", page_icon="🏠", layout="wide")
st.title("🏠 AI-Assisted Inspection Dashboard")
st.caption("Automated rule-based issue classification and risk scoring")

# High Risk Only Filter
high_risk_only = st.checkbox("Show High Risk Only (8-10)")
if high_risk_only:
    df_display = df[df['Risk Score'] >= 8]
else:
    df_display = df

# -----------------------------
# Color Highlighting
# -----------------------------
def highlight_risk(row):
    if row['Risk Score'] >= 8:
        return ['background-color: #ff9999']*len(row)
    elif row['Risk Score'] >= 6:
        return ['background-color: #fff0b3']*len(row)
    else:
        return ['background-color: #ccffcc']*len(row)

st.subheader("📋 Inspection Findings (Risk Highlighted)")
st.dataframe(df_display.style.apply(highlight_risk, axis=1))

# Risk Legend
st.markdown("""
🧭 **Risk Legend**
- 🔴 High Risk (8–10) – Immediate attention required
- 🟠 Medium Risk (6–7) – Needs inspection
- 🟢 Low Risk (≤5) – Monitor only
""")

# Risk Overview Chart
st.subheader("📊 Risk Overview")
risk_counts = df_display['Risk Score'].apply(lambda x: "High (8–10)" if x>=8 else "Medium (6–7)" if x>=6 else "Low (≤5)")
risk_summary = risk_counts.value_counts().reindex(["High (8–10)", "Medium (6–7)", "Low (≤5)"]).fillna(0)
st.bar_chart(risk_summary)

# AI-style Summary
st.subheader("🤖 Inspection Summary")
summary_text = (
    f"Total Findings: {len(df_display)}\n\n"
    f"High Risk: {risk_summary['High (8–10)']} – Immediate attention required\n"
    f"Medium Risk: {risk_summary['Medium (6–7)']} – Needs inspection\n"
    f"Low Risk: {risk_summary['Low (≤5)']} – Monitor only\n\n"
    "Recommendation: Prioritize high-risk issues first and schedule inspections for medium-risk items."
)
st.text_area("Summary", summary_text, height=140)

# Download CSV
st.download_button(
    label="⬇️ Download Inspection Report",
    data=df_display.to_csv(index=False).encode('utf-8'),
    file_name='inspection_report.csv',
    mime='text/csv'
)
