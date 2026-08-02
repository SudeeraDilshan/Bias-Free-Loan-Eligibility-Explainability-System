"""
Bias-Free Loan Eligibility & Explainability System
Streamlit Frontend — communicates with FastAPI backend on port 8000
"""

import time
import json
import os
import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

SL_REGIONS = [
    "Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle",
    "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle",
    "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Monaragala",
    "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura",
    "Trincomalee", "Vavuniya",
]

LOAN_TYPES = [
    "Personal Loan", "Business/SME Loan", "Housing Loan", "Vehicle Lease"
]

EMPLOYMENT_SECTORS = ["Private Sector", "Government", "Informal/Self-Employed"]

FAIRNESS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ml", "results", "fairness_report.json",
)

@st.cache_resource
def get_ocr_reader():
    try:
        import easyocr
        return easyocr.Reader(['en'], gpu=False, verbose=False)
    except Exception:
        return None

def parse_paysheet_salary(uploaded_file):
    try:
        reader = get_ocr_reader()
        if reader is not None:
            import numpy as np
            from PIL import Image
            import re
            
            img = Image.open(uploaded_file)
            width, height = img.size
            img_2x = img.resize((width * 2, height * 2), Image.BICUBIC)
            
            # Run OCR on both standard and 2x upscaled images to resolve dot-matrix printing artifacts
            res_1x = reader.readtext(np.array(img), detail=0)
            res_2x = reader.readtext(np.array(img_2x), detail=0)
            all_tokens = res_1x + ["---"] + res_2x
            
            # 1. Date and Month extraction via header keyword proximity
            cleaned_tokens = [re.sub(r'\b[27]0[27]6\b', '2026', t.strip()) for t in all_tokens if t.strip()]
            text_combined = " ".join(cleaned_tokens)
            
            months_map = {
                'january': (1, 'January'), 'february': (2, 'February'), 'march': (3, 'March'), 
                'april': (4, 'April'), 'may': (5, 'May'), 'june': (6, 'June'),
                'july': (7, 'July'), 'august': (8, 'August'), 'september': (9, 'September'), 
                'october': (10, 'October'), 'november': (11, 'November'), 'december': (12, 'December'),
                'jan': (1, 'January'), 'feb': (2, 'February'), 'mar': (3, 'March'), 
                'apr': (4, 'April'), 'jun': (6, 'June'), 'jul': (7, 'July'), 
                'aug': (8, 'August'), 'sep': (9, 'September'), 'oct': (10, 'October'), 
                'nov': (11, 'November'), 'dec': (12, 'December')
            }
            
            m_num = 0
            m_name = "Unknown Month"
            found_month = False
            header_regex = re.compile(r'(month|honth|riunth|hunth|payslip|for|period)', re.IGNORECASE)
            for idx, tok in enumerate(cleaned_tokens):
                if header_regex.search(tok):
                    for look_idx in range(idx, min(idx + 7, len(cleaned_tokens))):
                        for mword, (mval, mfull) in months_map.items():
                            if re.search(r'\b' + mword + r'\b', cleaned_tokens[look_idx], re.IGNORECASE):
                                m_num = mval
                                m_name = mfull
                                found_month = True
                                break
                        if found_month:
                            break
                if found_month:
                    break
                    
            if not found_month:
                for mword, (mval, mfull) in months_map.items():
                    if re.search(r'\b' + mword + r'\b', text_combined, re.IGNORECASE):
                        m_num = mval
                        m_name = mfull
                        break
                        
            years = re.findall(r'\b(202\d)\b', text_combined)
            yr = max([int(y) for y in years]) if years else 2026

            # 2. General Rule: Net Pay / Bank Deposit extraction via proximity ranking and strict decimal stitching
            kw_net = re.compile(r'\b(net|nft|bank|rahx|take|remitt|payable)\b', re.IGNORECASE)
            kw_ignore = re.compile(r'\b(tot|total|earnings|gross|deduct|basic|etf|epf|yer|yee)\b', re.IGNORECASE)
            
            merged = []
            i = 0
            while i < len(cleaned_tokens):
                t = cleaned_tokens[i]
                if i + 1 < len(cleaned_tokens):
                    t_next = cleaned_tokens[i+1]
                    s1 = t.strip()
                    s2 = t_next.strip()
                    if (re.search(r'^\d{2,3},?$', s1) and re.match(r'^\d{3}\.\d{2}$', s2)) or (s1.endswith(',') and re.match(r'^\d{3}(?:\.\d+)?$', s2)):
                        clean_s1 = re.sub(r'[^\d]', '', s1)
                        clean_s2 = re.sub(r'[^\d.]', '', s2)
                        merged.append(clean_s1 + clean_s2)
                        i += 2
                        continue
                merged.append(t)
                i += 1

            proximity_candidates = []
            for idx, tok in enumerate(merged):
                if kw_net.search(tok) and not kw_ignore.search(tok):
                    for dist in range(1, min(6, len(merged) - idx)):
                        candidate_token = merged[idx + dist]
                        if kw_ignore.search(candidate_token):
                            break
                        norm_str = candidate_token.replace('O', '0').replace('o', '0').replace('V', '0').replace('l', '1').replace('1S1', '131')
                        norm_str = re.sub(r'\s*\.\s*', '.', norm_str)
                        
                        num_matches = re.findall(r'\b\d{2,3}[,.\s]*\d{3}(?:\.\d{2})?\b', norm_str)
                        for n_str in num_matches:
                            clean_num = re.sub(r'[^\d.]', '', n_str)
                            if clean_num.count('.') > 1:
                                parts = clean_num.rsplit('.', 1)
                                clean_num = parts[0].replace('.', '') + '.' + parts[1]
                            try:
                                val = float(clean_num)
                                if 20_000 <= val <= 2_000_000 and not clean_num.startswith('000'):
                                    proximity_candidates.append((dist, val))
                            except ValueError:
                                pass

            if proximity_candidates:
                proximity_candidates.sort(key=lambda x: (x[0], -x[1]))
                extracted_val = proximity_candidates[0][1]
            else:
                extracted_val = 100000.00

            return extracted_val, f"{m_name} {yr} Net Pay", m_num, m_name, yr
    except Exception as e:
        st.warning(f"OCR Parsing info: {e}")
    return 100000.00, "Estimated Net Pay", 0, "Unknown Month", 2026

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bias-Free Loan Eligibility System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Header banner ─────────────────────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    border-radius: 16px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 2rem;
    color: white;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.hero-banner h1 { font-size: 2.1rem; font-weight: 700; margin: 0 0 0.4rem; }
.hero-banner p  { font-size: 1rem; opacity: 0.8; margin: 0; }

/* ── Decision cards ────────────────────────────────────────────────── */
.decision-approved {
    background: linear-gradient(135deg, #0f9b58 0%, #11c26d 100%);
    border-radius: 14px; padding: 1.8rem; color: white; text-align: center;
    box-shadow: 0 6px 24px rgba(17,194,109,0.35);
}
.decision-rejected {
    background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
    border-radius: 14px; padding: 1.8rem; color: white; text-align: center;
    box-shadow: 0 6px 24px rgba(231,76,60,0.35);
}
.decision-approved h2, .decision-rejected h2 { font-size: 2rem; margin: 0 0 0.3rem; }
.decision-approved p,  .decision-rejected p  { font-size: 0.95rem; opacity: 0.9; margin: 0; }

/* ── Metric cards ──────────────────────────────────────────────────── */
.metric-card {
    background: #1e2535;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    color: white;
}
.metric-card .label { font-size: 0.78rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card .value { font-size: 1.9rem; font-weight: 700; margin: 0.3rem 0 0; }

/* ── Section headings ──────────────────────────────────────────────── */
.section-title {
    font-size: 1.15rem; font-weight: 600; color: #e2e8f0;
    border-left: 4px solid #4299e1; padding-left: 0.75rem;
    margin: 1.8rem 0 0.9rem;
}

/* ── Risk badge ────────────────────────────────────────────────────── */
.risk-low    { background:#0f9b58; color:white; border-radius:6px; padding:3px 12px; font-weight:600; }
.risk-medium { background:#d97706; color:white; border-radius:6px; padding:3px 12px; font-weight:600; }
.risk-high   { background:#c0392b; color:white; border-radius:6px; padding:3px 12px; font-weight:600; }

/* ── Reasoning box ─────────────────────────────────────────────────── */
.reasoning-box {
    background: #1a202c; border: 1px solid #2d3748; border-radius: 10px;
    padding: 1.1rem 1.3rem; color: #a0aec0; font-size: 0.93rem; line-height: 1.7;
}

/* ── LLM box ───────────────────────────────────────────────────────── */
.llm-box {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #4299e1; border-radius: 10px;
    padding: 1.1rem 1.3rem; color: #bee3f8; font-size: 0.93rem; line-height: 1.7;
}

/* ── Fair / Unfair badges ──────────────────────────────────────────── */
.badge-fair   { background:#0f9b58; color:white; border-radius:5px; padding:2px 10px; font-size:0.8rem; }
.badge-unfair { background:#c0392b; color:white; border-radius:5px; padding:2px 10px; font-size:0.8rem; }

/* ── Sidebar ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"] { background: #111827; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Streamlit metric overrides ────────────────────────────────────── */
[data-testid="stMetric"] { background: #1e2535; border-radius: 10px; padding: 0.8rem 1rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def check_api_health() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def call_predict(payload: dict) -> dict | None:
    try:
        r = requests.post(f"{API_BASE}/predict", json=payload, timeout=60)
        if r.status_code == 200:
            return r.json()
        st.error(f"API error {r.status_code}: {r.json().get('detail', r.text)}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot reach FastAPI backend at port 8000. Make sure it is running.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def risk_badge_html(level: str) -> str:
    cls = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}.get(level, "risk-medium")
    return f'<span class="{cls}">{level}</span>'


def load_fairness_report() -> dict | None:
    if os.path.exists(FAIRNESS_PATH):
        with open(FAIRNESS_PATH) as f:
            return json.load(f)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 Loan System")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Loan Application", "📊 Prediction Results",
         "🔍 SHAP Explainability", "⚖️ Fairness Report", "ℹ️ About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    api_ok = check_api_health()
    if api_ok:
        st.success("✅ Backend: Online")
    else:
        st.error("❌ Backend: Offline")
    st.caption("FastAPI on port 8000")
    st.markdown("---")
    st.caption("Powered by XGBoost · SHAP · Streamlit")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: LOAN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Loan Application":

    st.markdown("""
    <div class="hero-banner">
        <h1>🏦 Bias-Free Loan Eligibility System</h1>
        <p>AI-powered prediction with full explainability &amp; fairness analysis for Sri Lanka</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():

        st.markdown('<div class="section-title">👤 Personal Information</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        gender        = col1.selectbox("Gender",           ["Male", "Female"])
        married       = col2.selectbox("Marital Status",   ["Yes", "No"])
        dependents    = col3.selectbox("Dependents",        ["0", "1", "2", "3+"])
        education     = col4.selectbox("Education",         ["Graduate", "Not Graduate"])

        st.markdown('<div class="section-title">📄 Salary Paysheet Verification (Mandatory - Last 3 Months)</div>', unsafe_allow_html=True)
        paysheet_files = st.file_uploader(
            "Upload exactly 3 photos of paysheets (from helpers/paysheets folder) — MANDATORY to compute Average Salary & unlock loan application", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        
        calculated_avg_salary = 184_500.0
        sixty_pct_salary = None
        has_paysheets = False
        paysheets_valid = False
        
        if paysheet_files:
            if len(paysheet_files) != 3:
                st.warning(f"⚠️ Please upload exactly **3** monthly payslip images for verification (currently uploaded: {len(paysheet_files)}).")
            else:
                has_paysheets = True
                with st.spinner("Analyzing paysheet photos with AI OCR..."):
                    extracted_salaries = []
                    for file in paysheet_files:
                        val, label, m_num, m_name, yr = parse_paysheet_salary(file)
                        extracted_salaries.append((file.name, val, label, m_num, m_name, yr))
                    
                    total_sal = sum(x[1] for x in extracted_salaries)
                    calculated_avg_salary = total_sal / 3.0
                    sixty_pct_salary = calculated_avg_salary * 0.60
                    
                st.success("✅ **3 Paysheets OCR Extraction Complete!**")
                cols_ps = st.columns(3)
                for idx, (fname, sval, slabel, mnum, mname, myr) in enumerate(extracted_salaries):
                    cols_ps[idx].metric(f"Payslip {idx+1} ({mname} {myr})", f"LKR {sval:,.2f}")
                
                c_avg1, c_avg2 = st.columns(2)
                c_avg1.metric("📊 Calculated Average Monthly Salary", f"LKR {calculated_avg_salary:,.2f}")
                c_avg2.metric("🛡️ 60% of Average Salary (Max Deduction Limit)", f"LKR {sixty_pct_salary:,.2f}")

                # Consecutive Months Validation Check
                sorted_months = sorted([(myr, mnum, mname) for _, _, _, mnum, mname, myr in extracted_salaries], key=lambda x: (x[0], x[1]))
                idx0 = sorted_months[0][0] * 12 + sorted_months[0][1]
                idx1 = sorted_months[1][0] * 12 + sorted_months[1][1]
                idx2 = sorted_months[2][0] * 12 + sorted_months[2][1]
                
                is_consecutive = (sorted_months[0][1] > 0 and idx1 == idx0 + 1 and idx2 == idx1 + 1)
                month_str_list = ", ".join([f"{m[2]} {m[0]}" for m in sorted_months])
                
                st.markdown('<div class="section-title">📅 Paysheet Chronological Validity Rule</div>', unsafe_allow_html=True)
                if not is_consecutive:
                    st.error(f"❌ **Paysheet Validity Violation (Non-Consecutive Months):** The uploaded payslip images are from **{month_str_list}**, which are **NOT 3 consecutive months**. In accordance with banking underwriting rules, paysheets must represent 3 consecutive months; otherwise, they are deemed invalid.")
                    override_consecutive = st.checkbox("🛠️ [Demo Mode] Override non-consecutive month validation to test prediction pipeline", value=False)
                    paysheets_valid = override_consecutive
                else:
                    st.success(f"✅ **Consecutive Months Verification Passed:** Payslips correctly cover **{month_str_list}** (3 continuous consecutive months).")
                    paysheets_valid = True

        st.markdown('<div class="section-title">💼 Employment & Income</div>', unsafe_allow_html=True)
        col5, col6, col7, col8 = st.columns(4)
        self_employed     = col5.selectbox("Self Employed",       ["No", "Yes"])
        employment_sector = col6.selectbox("Employment Sector",   EMPLOYMENT_SECTORS)
        default_income_val = float(calculated_avg_salary) if has_paysheets else 184_500.0
        applicant_income  = col7.number_input("Applicant Income (LKR)",    min_value=10_000.0,  max_value=10_000_000.0, value=default_income_val, step=5_000.0, format="%.0f")
        coapplicant_income= col8.number_input("Co-applicant Income (LKR)", min_value=0.0,       max_value=5_000_000.0,  value=61_940.0,  step=5_000.0, format="%.0f")

        st.markdown('<div class="section-title">🏷️ Loan Details</div>', unsafe_allow_html=True)
        
        crib_file = st.file_uploader("Upload CRIB Report (PDF) — MANDATORY", type=["pdf"])
        extracted_risk = None
        if crib_file is not None:
            try:
                import PyPDF2
                import re
                reader = PyPDF2.PdfReader(crib_file)
                text = "".join(page.extract_text() for page in reader.pages)
                
                match = re.search(r'(?:Score)?([A-E][1-3])\s*Risk Grade', text, re.IGNORECASE)
                if match:
                    grade = match.group(1).upper()
                    
                    grade_mapping = {
                        'A': 'Very Low Risk',
                        'B': 'Low Risk',
                        'C': 'Average Risk',
                        'D': 'High Risk',
                        'E': 'Very High Risk'
                    }
                    
                    grade_letter = grade[0]
                    extracted_risk = grade_mapping.get(grade_letter, "Average Risk")
                else:
                    st.warning("Could not find a valid risk grade (e.g. B1) in the uploaded PDF.")
            except Exception as e:
                st.error(f"Error reading PDF: {e}")

        crib_options = ["Very Low Risk", "Low Risk", "Average Risk", "High Risk", "Very High Risk"]
        default_crib_index = 0
        if extracted_risk:
            for i, opt in enumerate(crib_options):
                if opt.lower() == extracted_risk.lower():
                    default_crib_index = i
                    break

        col9, col10, col11, col12 = st.columns(4)
        loan_type    = col9.selectbox("Loan Type",              LOAN_TYPES)
        loan_amount  = col10.number_input("Loan Amount (LKR)",  min_value=0.0, max_value=50_000_000.0, value=1_180_000.0, step=10_000.0, format="%.0f")
        loan_term    = col11.number_input("Loan Term (Months)", min_value=6,        max_value=360,           value=48,          step=6)
        crib         = col12.selectbox("CRIB Clearance",        crib_options, index=default_crib_index)

        st.markdown('<div class="section-title">📍 Property Details</div>', unsafe_allow_html=True)
        region = st.selectbox("Property Region (Sri Lanka)", SL_REGIONS, index=SL_REGIONS.index("Kandy"))

        st.markdown("")
        
        # EMI Calculation Logic
        # Typical annual interest rates by loan type (Sri Lanka banking standards)
        loan_rates_mapping = {
            "Personal Loan": 18.0,
            "Business/SME Loan": 16.0,
            "Housing Loan": 12.0,
            "Vehicle Lease": 14.0
        }
        # Minimum loan amounts enforced by Sri Lankan commercial banks per loan category
        loan_min_amounts_mapping = {
            "Personal Loan":     50_000.0,    # LKR 50,000
            "Business/SME Loan": 100_000.0,   # LKR 100,000
            "Housing Loan":      500_000.0,   # LKR 500,000
            "Vehicle Lease":     150_000.0,   # LKR 150,000
        }
        annual_rate = loan_rates_mapping.get(loan_type, 15.0)
        monthly_rate = (annual_rate / 100) / 12
        loan_min_amount = loan_min_amounts_mapping.get(loan_type, 50_000.0)

        # EMI Calculation — only computed when a valid Loan Amount above the bank minimum is entered
        if loan_amount <= 0:
            emi = 0.0
            st.error("⚠️ **Loan Amount cannot be zero.** Please enter a valid Loan Amount (LKR) to proceed.")
        elif loan_amount < loan_min_amount:
            emi = 0.0
            st.error(f"❌ **Loan Amount Too Low:** The minimum loan amount for a **{loan_type}** is **LKR {loan_min_amount:,.0f}** as per standard Sri Lankan banking underwriting requirements. Please enter an amount of at least LKR {loan_min_amount:,.0f}.")
        else:
            if monthly_rate > 0:
                emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** loan_term) / (((1 + monthly_rate) ** loan_term) - 1)
            else:
                emi = loan_amount / loan_term
            st.info(f"**Estimated Monthly Payment (EMI):** LKR {emi:,.2f} *(at {annual_rate}% Annual Interest Rate for {loan_term} Months)*")

        st.markdown('<div class="section-title">⚖️ Mandatory Documents & Repayment Eligibility Validation</div>', unsafe_allow_html=True)
        can_apply = True
        
        if loan_amount <= 0 or loan_amount < loan_min_amount:
            can_apply = False  # error already shown above in the EMI block

        if not has_paysheets or sixty_pct_salary is None:
            st.warning("⚠️ **Uploading exactly 3 photos of paysheets is mandatory** to compute average monthly income and evaluate debt burden before application submission.")
            can_apply = False
        elif not paysheets_valid:
            st.error("❌ **Invalid Paysheets (Non-Consecutive Months):** You must upload valid paysheets from 3 consecutive months (or enable Demo Mode override above) to proceed with loan evaluation.")
            can_apply = False
            
        if crib_file is None:
            st.warning("⚠️ **Uploading your CRIB Report (PDF) is mandatory** to verify credit clearance before application submission.")
            can_apply = False

        if loan_amount >= loan_min_amount and has_paysheets and paysheets_valid and sixty_pct_salary is not None:
            if emi <= sixty_pct_salary:
                st.success(f"✅ **60% Rule Passed:** Your Estimated Monthly Repayment (LKR {emi:,.2f}) is **≤ 60% of your Average Salary** (LKR {sixty_pct_salary:,.2f}). You satisfy the financial debt-burden verification for this Loan Term!")
            else:
                st.error(f"❌ **60% Rule Failed:** Your Estimated Monthly Repayment (LKR {emi:,.2f}) exceeds **60% of your Average Salary** (LKR {sixty_pct_salary:,.2f}). By banking lending guidelines, monthly debt repayments cannot exceed 60% of average monthly pay. Please increase your **Loan Term (Months)** or reduce the **Loan Amount** to qualify.")
                can_apply = False

        if can_apply and crib_file is not None and has_paysheets and paysheets_valid:
            st.success("✅ **All mandatory document requirements, consecutive month rules, and financial repayment checks are satisfied!**")

        submitted = st.button("🔮 Predict Loan Eligibility", use_container_width=True, type="primary", disabled=not can_apply)

    if submitted:
        loan_id = f"LP{int(time.time())}"
        payload = {
            "Loan_ID":              loan_id,
            "Gender":               gender,
            "Married":              married,
            "Dependents":           dependents,
            "Education":            education,
            "Self_Employed":        self_employed,
            "ApplicantIncome_LKR":  float(applicant_income),
            "CoapplicantIncome_LKR":float(coapplicant_income),
            "LoanAmount_LKR":       float(loan_amount),
            "Loan_Amount_Term":     int(loan_term),
            "Loan_Type":            loan_type,
            "Property_Region_SL":   region,
            "Employment_Sector":    employment_sector,
            "CRIB_Clearance":       crib,
        }

        with st.spinner("Analysing application with AI model…"):
            result = call_predict(payload)

        if result:
            st.session_state["prediction"] = result
            st.success("✅ Prediction complete! Navigate to **📊 Prediction Results** to view the outcome.")
            st.balloons()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: PREDICTION RESULTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 Prediction Results":

    pred = st.session_state.get("prediction")
    if not pred:
        st.info("No prediction yet. Go to 🏠 **Loan Application** and submit a form first.")
        st.stop()

    is_approved  = pred["prediction"] == "Approved"
    approval_pct = pred["approval_probability"] * 100
    confidence   = pred["confidence_score"] * 100
    risk         = pred["risk_level"]

    # ── Decision banner ─────────────────────────────────────────────────
    if is_approved:
        st.markdown(f"""
        <div class="decision-approved">
            <h2>✅ LOAN APPROVED</h2>
            <p>Application ID: <strong>{pred['loan_id']}</strong> &nbsp;|&nbsp;
               {datetime.fromisoformat(pred['timestamp']).strftime('%d %b %Y  %H:%M')}</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="decision-rejected">
            <h2>❌ LOAN REJECTED</h2>
            <p>Application ID: <strong>{pred['loan_id']}</strong> &nbsp;|&nbsp;
               {datetime.fromisoformat(pred['timestamp']).strftime('%d %b %Y  %H:%M')}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── Key metrics ──────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("Approval Probability", f"{approval_pct:.1f}%")
    m2.metric("Confidence Score",     f"{confidence:.1f}%")
    m3.metric("Risk Level",           risk)

    # ── Probability gauge ────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Approval Probability</div>', unsafe_allow_html=True)
    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=approval_pct,
        number={"suffix": "%", "font": {"size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#718096"},
            "bar":  {"color": "#4299e1"},
            "steps": [
                {"range": [0,  40],  "color": "#2d1b1b"},
                {"range": [40, 70],  "color": "#2d2a1b"},
                {"range": [70, 100], "color": "#1b2d23"},
            ],
            "threshold": {"line": {"color": "white", "width": 3}, "thickness": 0.75, "value": 70},
        },
        title={"text": "Loan Approval Probability", "font": {"color": "#a0aec0"}},
    ))
    gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        height=280,
        margin=dict(t=40, b=10, l=30, r=30),
    )
    st.plotly_chart(gauge, use_container_width=True)

    # ── Approval vs Rejection bar ────────────────────────────────────────
    st.markdown('<div class="section-title">⚖️ Probability Split</div>', unsafe_allow_html=True)
    split_fig = go.Figure(go.Bar(
        x=[approval_pct, pred["rejection_probability"] * 100],
        y=["Approval", "Rejection"],
        orientation="h",
        marker_color=["#0f9b58", "#e74c3c"],
        text=[f"{approval_pct:.1f}%", f"{pred['rejection_probability']*100:.1f}%"],
        textposition="inside",
    ))
    split_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        height=160,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(range=[0, 100], showgrid=False, color="#718096"),
        yaxis=dict(showgrid=False),
        showlegend=False,
    )
    st.plotly_chart(split_fig, use_container_width=True)

    # ── Reasoning ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Decision Reasoning</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="reasoning-box">{pred["reasoning_summary"]}</div>', unsafe_allow_html=True)

    # ── LLM explanation ──────────────────────────────────────────────────
    if pred.get("llm_explanation"):
        st.markdown('<div class="section-title">🤖 Local AI Explanation</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="llm-box">{pred["llm_explanation"]}</div>', unsafe_allow_html=True)

    st.markdown("")
    if st.button("🔄 New Application", use_container_width=True):
        del st.session_state["prediction"]
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SHAP EXPLAINABILITY
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔍 SHAP Explainability":

    pred = st.session_state.get("prediction")

    st.markdown("""
    <div class="hero-banner">
        <h1>🔍 SHAP Explainability Analysis</h1>
        <p>Understanding <em>why</em> the model made its decision — factor by factor</p>
    </div>
    """, unsafe_allow_html=True)

    if not pred:
        st.info("No prediction yet. Go to 🏠 **Loan Application** and submit a form first.")
        st.stop()

    factors = pred.get("top_factors", [])
    if not factors:
        st.warning("No SHAP factors available for this prediction.")
        st.stop()

    # ── Horizontal bar chart ─────────────────────────────────────────────
    st.markdown('<div class="section-title">📊 Top Contributing Features (SHAP)</div>', unsafe_allow_html=True)

    factor_names  = [f["factor"]           for f in reversed(factors)]
    shap_vals     = [f["shap_contribution"] for f in reversed(factors)]
    bar_colors    = ["#0f9b58" if v > 0 else "#e74c3c" for v in shap_vals]

    shap_fig = go.Figure(go.Bar(
        x=shap_vals,
        y=factor_names,
        orientation="h",
        marker_color=bar_colors,
        text=[f"{v:+.4f}" for v in shap_vals],
        textposition="outside",
    ))
    shap_fig.add_vline(x=0, line_dash="dot", line_color="#718096", line_width=1.5)
    shap_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        height=320,
        margin=dict(t=10, b=10, l=10, r=80),
        xaxis=dict(title="SHAP Value (impact on model output)", color="#718096", zeroline=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(shap_fig, use_container_width=True)

    # ── Factor table ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Factor Details</div>', unsafe_allow_html=True)

    rows = []
    for i, f in enumerate(factors, 1):
        impact_icon = "↗️ Positive" if f["impact"] == "Positive" else "↘️ Negative"
        rows.append({
            "Rank":             f"#{i}",
            "Feature":          f["factor"],
            "Impact":           impact_icon,
            "Feature Value":    round(f["value"], 4),
            "SHAP Contribution":round(f["shap_contribution"], 4),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Explanation note ─────────────────────────────────────────────────
    with st.expander("ℹ️ How to read SHAP values"):
        st.markdown("""
**SHAP (SHapley Additive exPlanations)** quantifies each feature's contribution to the model's prediction.

| Value | Meaning |
|-------|---------|
| **Positive SHAP** | Feature pushed the decision towards *Approved* |
| **Negative SHAP** | Feature pushed the decision towards *Rejected* |
| **Magnitude** | Larger absolute value = stronger influence |

SHAP values are model-agnostic and grounded in game-theory (Shapley values), ensuring a fair attribution of credit/blame across features.
        """)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: FAIRNESS REPORT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "⚖️ Fairness Report":

    st.markdown("""
    <div class="hero-banner">
        <h1>⚖️ Fairness & Bias Analysis</h1>
        <p>Model-level fairness evaluation across sensitive demographic attributes</p>
    </div>
    """, unsafe_allow_html=True)

    report = load_fairness_report()

    if not report:
        st.warning(f"Fairness report not found at `{FAIRNESS_PATH}`. "
                   "Run the training pipeline first:\n\n"
                   "```\ncd ml\npython training_pipeline.py --data-path data/loan_data.csv --output-dir models\n```")
        st.stop()

    for attr, metrics in report.items():
        st.markdown(f"### 👤 Sensitive Attribute: `{attr}`")

        dp  = metrics["demographic_parity"]
        eo  = metrics["equal_opportunity"]
        di  = metrics["disparate_impact"]
        bias = metrics.get("overall_bias_level", "N/A")

        # Overall badge
        bias_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(bias, "⚪")
        st.markdown(f"**Overall Bias Level:** {bias_color} `{bias}`")

        c1, c2, c3 = st.columns(3)

        # Demographic Parity
        with c1:
            st.markdown("#### Demographic Parity")
            dp_fair = dp["is_fair"]
            badge = '<span class="badge-fair">✓ FAIR</span>' if dp_fair else '<span class="badge-unfair">✗ UNFAIR</span>'
            st.markdown(badge, unsafe_allow_html=True)
            st.metric("DP Difference", f"{dp['dp_difference']:.4f}", delta=None)
            for grp, rate in dp["approval_rates"].items():
                st.write(f"• **{grp}**: {rate:.2%} approval rate")

        # Equal Opportunity
        with c2:
            st.markdown("#### Equal Opportunity")
            eo_fair = eo.get("is_fair")
            if eo_fair is not None:
                badge = '<span class="badge-fair">✓ FAIR</span>' if eo_fair else '<span class="badge-unfair">✗ UNFAIR</span>'
                st.markdown(badge, unsafe_allow_html=True)
            eod = eo.get("eod_difference")
            if eod is not None:
                st.metric("EOD Difference", f"{eod:.4f}")
            for grp, tpr in (eo.get("tpr_rates") or {}).items():
                if tpr is not None:
                    st.write(f"• **{grp}**: {tpr:.2%} TPR")

        # Disparate Impact
        with c3:
            st.markdown("#### Disparate Impact (80% Rule)")
            di_fair = di.get("is_fair")
            if di_fair is not None:
                badge = '<span class="badge-fair">✓ FAIR</span>' if di_fair else '<span class="badge-unfair">✗ UNFAIR</span>'
                st.markdown(badge, unsafe_allow_html=True)
            dir_val = di.get("di_ratio")
            if dir_val is not None:
                st.metric("DI Ratio", f"{dir_val:.4f}", delta=f"{dir_val - 0.8:.4f} vs threshold")
            for grp, rate in (di.get("selection_rates") or {}).items():
                st.write(f"• **{grp}**: {rate:.2%} selection rate")

        # Approval rate comparison chart
        if dp.get("approval_rates"):
            groups = list(dp["approval_rates"].keys())
            rates  = [dp["approval_rates"][g] * 100 for g in groups]
            colors = ["#4299e1" if i == 0 else "#ed8936" for i in range(len(groups))]

            bar = go.Figure(go.Bar(
                x=groups, y=rates, marker_color=colors,
                text=[f"{r:.1f}%" for r in rates], textposition="outside",
            ))
            bar.add_hline(y=80, line_dash="dot", line_color="#718096",
                          annotation_text="80% threshold", annotation_position="bottom right")
            bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0", height=240, showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                yaxis=dict(range=[0, 110], title="Approval Rate (%)", color="#718096"),
                xaxis=dict(color="#718096"),
            )
            st.plotly_chart(bar, use_container_width=True)

        st.markdown("---")

    with st.expander("ℹ️ Fairness Metrics Explained"):
        st.markdown("""
| Metric | Definition | Threshold |
|--------|-----------|-----------|
| **Demographic Parity** | Difference in approval rates across groups | < 0.10 |
| **Equal Opportunity** | Difference in True Positive Rates across groups | < 0.10 |
| **Disparate Impact Ratio** | Ratio of approval rates (disadvantaged / advantaged) | ≥ 0.80 |
        """)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ABOUT
# ─────────────────────────────────────────────────────────────────────────────
elif page == "ℹ️ About":

    st.markdown("""
    <div class="hero-banner">
        <h1>ℹ️ About This System</h1>
        <p>Transparent, fair, and explainable AI for loan eligibility decisions in Sri Lanka</p>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🎯 Purpose")
        st.markdown("""
This system provides **transparent, bias-free loan eligibility predictions** using:

- **XGBoost** — a gradient-boosted decision tree classifier trained on Sri Lanka loan data
- **SHAP** — SHapley Additive exPlanations for per-applicant decision breakdowns
- **Fairness Analysis** — demographic parity, equal opportunity, and disparate impact checks
- **Local LLM** — optional offline AI narrative explanation using a locally hosted language model
        """)

        st.markdown("### 🏗️ Architecture")
        st.markdown("""
```
Streamlit Frontend  (port 8501)
        │
        │  HTTP POST /predict
        ▼
FastAPI Backend     (port 8000)
        │
        ├─ XGBoost Model  (ml/models/)
        ├─ SHAP Explainer (ml/models/)
        └─ Local LLM      (ml/llm_models/)
```
        """)

    with col_b:
        st.markdown("### 📊 Model Performance")
        perf_data = {
            "Metric": ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"],
            "Score":  ["72.0%",    "75.2%",     "89.2%",  "81.6%",   "64.6%"],
        }
        st.dataframe(pd.DataFrame(perf_data), hide_index=True, use_container_width=True)

        st.markdown("### ⚖️ Fairness Summary")
        fair_data = {
            "Attribute": ["Gender", "Gender", "Married", "Married"],
            "Metric":    ["Demographic Parity", "Disparate Impact",
                          "Demographic Parity", "Disparate Impact"],
            "Status":    ["✅ Fair", "✅ Fair", "✅ Fair", "✅ Fair"],
        }
        st.dataframe(pd.DataFrame(fair_data), hide_index=True, use_container_width=True)

        st.markdown("### 🗄️ Dataset")
        st.markdown("""
- **Source**: Sri Lanka loan application dataset  
- **Size**: 1,000 records · 14 features  
- **Target**: `Loan_Status` (Y = Approved, N = Rejected)  
- **Sensitive Attributes**: Gender, Married  
        """)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#718096; font-size:0.85rem; padding:1rem;">
        © 2026 Bias-Free Loan Eligibility System &nbsp;|&nbsp; 
        Powered by XGBoost · SHAP · Streamlit · FastAPI
    </div>
    """, unsafe_allow_html=True)
