import os
import json
import datetime
import urllib3
import requests

from bs4 import BeautifulSoup
import streamlit as st
from typing import List, Literal, Dict, Any
from pydantic import BaseModel, Field
from openai import OpenAI

# Disable SSL warnings for passive reconnaissance scans
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 1. PAGE CONFIGURATION & THEME STYLING
# ==========================================
st.set_page_config(
    page_title="🌐 AI Web Security Configuration Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Command Center Sleek Dark Theme & Glossy CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    /* Global Dark Mode slate/zinc theme */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #090d16 !important;
        color: #e5e7eb;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #0d111a !important;
        border-right: 1px solid #1f2937 !important;
    }

    /* Typography Hierarchy */
    h1, h2, h3, h4, h5, h6 {
        color: #f9fafb !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Structured Card Layouts */
    .terminal-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        transition: border-color 0.2s ease;
    }
    
    .terminal-card:hover {
        border-color: #374151;
    }

    .kpi-card {
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }

    /* Status Badge Pills */
    .badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }

    .badge-critical { background-color: #3f1214; color: #f87171; border: 1px solid #7f1d1d; }
    .badge-high { background-color: #3b1a0e; color: #fb923c; border: 1px solid #9a3412; }
    .badge-medium { background-color: #362b0d; color: #facc15; border: 1px solid #854d0e; }
    .badge-low { background-color: #0e2a38; color: #38bdf8; border: 1px solid #0369a1; }
    .badge-informational { background-color: #1f2937; color: #9ca3af; border: 1px solid #374151; }

    /* Code Snippets & Monospace Components */
    .mono-text {
        font-family: 'JetBrains Mono', monospace;
    }

    .code-container {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        background-color: #030712;
        border: 1px solid #1f2937;
        border-radius: 6px;
        padding: 12px;
        color: #38bdf8;
        overflow-x: auto;
        white-space: pre-wrap;
    }

    /* Glossy Glassmorphism Finishing for Search Input Bar */
    div[data-testid="stTextInput"] > div > div {
        background: linear-gradient(135deg, rgba(31, 41, 55, 0.75) 0%, rgba(17, 24, 39, 0.6) 100%) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 0 1px 1px 0 rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stTextInput"] > div > div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.4), inset 0 1px 1px 0 rgba(255, 255, 255, 0.3) !important;
    }

    div[data-testid="stTextInput"] input {
        color: #f9fafb !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Custom Light Blue Launch Button */
    button[kind="primary"] {
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
        color: #090d16 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px 0 rgba(56, 189, 248, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
        height: 46px !important;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7dd3fc 0%, #0369a1 100%) !important;
        box-shadow: 0 6px 20px 0 rgba(56, 189, 248, 0.55) !important;
        color: #000000 !important;
        transform: translateY(-1px);
    }

    /* Custom Metrics & Controls */
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #f9fafb !important;
    }

    /* Main Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid #1f2937;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 20px;
        border-radius: 8px 8px 0px 0px;
        color: #9ca3af;
        font-weight: 600;
        font-size: 0.95rem;
        background-color: #0d111a;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #e5e7eb;
        background-color: #111827;
    }

    .stTabs [aria-selected="true"] {
        background-color: #111827 !important;
        color: #38bdf8 !important;
        border: 1px solid #1f2937 !important;
        border-bottom: 3px solid #38bdf8 !important;
    }

    /* Hide Default Header/Footer Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUDIT HISTORY PERSISTENCE LAYER
# ==========================================
HISTORY_FILE = "audit_history.json"

def load_audit_history() -> List[Dict[str, Any]]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_audit_history(history_list: List[Dict[str, Any]]):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=2)
    except Exception as e:
        st.error(f"Failed to persist audit history: {str(e)}")

# Initialize Session State for History
if "audit_history" not in st.session_state:
    st.session_state.audit_history = load_audit_history()

if "selected_history_id" not in st.session_state:
    st.session_state.selected_history_id = None

# ==========================================
# 3. PYDANTIC DATA MODELS
# ==========================================
class Finding(BaseModel):
    title: str = Field(description="Title of the misconfiguration or missing header")
    severity: Literal["Critical", "High", "Medium", "Low", "Informational"] = Field(description="Severity classification")
    description: str = Field(description="What is missing or misconfigured")
    security_impact: str = Field(description="Potential risk, e.g., Clickjacking, XSS, Session Hijacking")
    remediation: str = Field(description="Step-by-step remediation or server configuration snippet")

class AuditReport(BaseModel):
    summary: str = Field(description="Executive summary of the website's security posture")
    security_score: int = Field(description="Security rating from 0 (very insecure) to 100 (fully hardened)")
    findings: List[Finding] = Field(description="List of detected misconfigurations and risks")

# ==========================================
# 4. SIDEBAR & CONFIGURATION
# ==========================================
st.sidebar.markdown("### ⚙️ Auditor Settings")

# Safe Streamlit Secrets Key Retrieval
try:
    DEFAULT_GROQ_KEY = st.secrets.get("GROQ_API_KEY", "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")
except Exception:
    DEFAULT_GROQ_KEY = "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"

api_key_input = st.sidebar.text_input("Groq API Key", value=DEFAULT_GROQ_KEY, type="password", help="Enter your Groq API Key.")
model_choice = st.sidebar.selectbox(
    "LLM Model Engine",
    ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.6-27b"],
    index=0
)

# Configurable Timeout Control to Prevent 15s Timeout Errors
request_timeout_sec = st.sidebar.slider(
    "HTTP Request Timeout (Seconds)",
    min_value=10,
    max_value=60,
    value=30,
    step=5,
    help="Increase timeout limit for slow, CDN-protected, or distant target servers."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Safe Test Targets")

if "target_url" not in st.session_state:
    st.session_state.target_url = "https://example.com/"

col_chip1, col_chip2 = st.sidebar.columns(2)
if col_chip1.button("🌐 Example.com", use_container_width=True, help="Standard Baseline (Online & Active)"):
    st.session_state.target_url = "https://example.com/"
    st.rerun()

if col_chip2.button("📡 Httpbin API", use_container_width=True, help="Live HTTP Response Headers Target"):
    st.session_state.target_url = "https://httpbin.org/headers"
    st.rerun()

col_chip3, col_chip4 = st.sidebar.columns(2)
if col_chip3.button("⚡ TestPHP Demo", use_container_width=True, help="OWASP Vulnerable Demo Target (May be offline)"):
    st.session_state.target_url = "http://testphp.vulnweb.com/"
    st.rerun()

if col_chip4.button("🛡️ Juice Shop", use_container_width=True, help="OWASP Juice Shop Demo Target"):
    st.session_state.target_url = "https://juice-shop.herokuapp.com/"
    st.rerun()

st.sidebar.markdown("""
<div style="font-size: 0.75rem; color: #6b7280; margin-top: 15px;">
    <strong>Notice:</strong> Passive audits evaluate headers, HTTP/HTTPS flags, forms, and cookies without intrusive exploitation.
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. PASSIVE RECONNAISSANCE COLLECTOR WITH FALLBACK
# ==========================================
def collect_metadata(target_url: str, timeout_sec: int = 30) -> dict:
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "https://" + target_url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    session = requests.Session()
    session.max_redirects = 5

    try:
        # Full GET request with connection timeout 10s and read timeout = timeout_sec
        response = session.get(target_url, headers=headers, timeout=(10, timeout_sec), verify=False)
        final_url = response.url
        status_code = response.status_code
        resp_headers = dict(response.headers)
        
        cookies_data = []
        for c in response.cookies:
            cookies_data.append({
                "name": c.name,
                "secure_flag": c.secure,
                "httponly_flag": bool(c.has_nonstandard_attr('HttpOnly') or c._rest.get('HttpOnly'))
            })

        forms = []
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            for form in soup.find_all("form")[:5]:
                inputs = [i.get("name") or i.get("type") for i in form.find_all("input")]
                forms.append({
                    "action": form.get("action", ""),
                    "method": form.get("method", "GET").upper(),
                    "inputs": inputs
                })
        except Exception:
            pass

        return {
            "final_url": final_url,
            "status_code": status_code,
            "headers": resp_headers,
            "cookies": cookies_data,
            "forms_detected": forms,
            "is_https": final_url.startswith("https://")
        }

    except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
        # Fallback to lightweight HEAD request if full GET times out!
        try:
            head_resp = session.head(target_url, headers=headers, timeout=(10, 15), verify=False, allow_redirects=True)
            cookies_data = []
            for c in head_resp.cookies:
                cookies_data.append({
                    "name": c.name,
                    "secure_flag": c.secure,
                    "httponly_flag": bool(c.has_nonstandard_attr('HttpOnly') or c._rest.get('HttpOnly'))
                })
            return {
                "final_url": head_resp.url,
                "status_code": head_resp.status_code,
                "headers": dict(head_resp.headers),
                "cookies": cookies_data,
                "forms_detected": [],
                "is_https": head_resp.url.startswith("https://")
            }
        except Exception:
            raise requests.exceptions.Timeout(
                f"Target endpoint '{target_url}' failed to respond within {timeout_sec} seconds. "
                f"Try increasing the HTTP Request Timeout slider in the sidebar or verify that the website is online."
            )

# ==========================================
# 6. LLM EVALUATION & HISTORY LOGIC
# ==========================================
def run_llm_audit(collected_data: dict, model: str, api_key: str) -> AuditReport:
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

    system_prompt = (
        "You are an expert Web Application Security Auditor. Analyze the provided passive HTTP audit data "
        "and evaluate it against OWASP Secure Headers Project and security hardening standards.\n\n"
        "Examine:\n"
        "1. Missing defense headers (Content-Security-Policy, Strict-Transport-Security, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy).\n"
        "2. Insecure cookie flags (missing HttpOnly, missing Secure).\n"
        "3. HTTP vs HTTPS enforcement.\n"
        "4. Forms lacking CSRF protection tokens or using plain GET for sensitive actions.\n\n"
        "You MUST respond ONLY with a raw JSON object strictly adhering to this schema:\n"
        "{\n"
        '  "summary": "Executive summary of site security posture",\n'
        '  "security_score": <int 0-100>,\n'
        '  "findings": [\n'
        "    {\n"
        '      "title": "Finding Title",\n'
        '      "severity": "Critical" | "High" | "Medium" | "Low" | "Informational",\n'
        '      "description": "Clear description of the issue",\n'
        '      "security_impact": "Potential attack risk (e.g., Clickjacking, XSS)",\n'
        '      "remediation": "Configuration or code fix to resolve it"\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"Audit Target Data:\n```json\n{json.dumps(collected_data, indent=2)}\n```"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
        timeout=45
    )

    return AuditReport.model_validate_json(response.choices[0].message.content)

def record_audit_to_history(target_url: str, recon_data: dict, audit_report: AuditReport):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_id = f"audit_{int(datetime.datetime.now().timestamp())}_{os.urandom(2).hex()}"
    
    score = audit_report.security_score
    if score >= 90:
        grade = "Grade A (Hardened & Secure)"
        score_color = "#34d399"
    elif score >= 75:
        grade = "Grade B (Moderate Security Posture)"
        score_color = "#60a5fa"
    elif score >= 60:
        grade = "Grade C (Needs Improvement)"
        score_color = "#facc15"
    elif score >= 40:
        grade = "Grade D (Significant Vulnerabilities)"
        score_color = "#fb923c"
    else:
        grade = "Grade F (Critical Attention Required)"
        score_color = "#f87171"

    findings_list = [f.model_dump() for f in audit_report.findings]
    crit_count = sum(1 for f in audit_report.findings if f.severity == "Critical")
    high_count = sum(1 for f in audit_report.findings if f.severity == "High")
    med_count = sum(1 for f in audit_report.findings if f.severity == "Medium")
    low_count = sum(1 for f in audit_report.findings if f.severity == "Low")
    info_count = sum(1 for f in audit_report.findings if f.severity == "Informational")

    entry = {
        "id": entry_id,
        "timestamp": timestamp,
        "target_url": target_url,
        "final_url": recon_data.get("final_url", target_url),
        "status_code": recon_data.get("status_code", 200),
        "security_score": score,
        "grade": grade,
        "score_color": score_color,
        "summary": audit_report.summary,
        "total_findings": len(findings_list),
        "severity_counts": {
            "Critical": crit_count,
            "High": high_count,
            "Medium": med_count,
            "Low": low_count,
            "Informational": info_count
        },
        "recon_data": recon_data,
        "audit_report": {
            "summary": audit_report.summary,
            "security_score": score,
            "findings": findings_list
        }
    }

    if "audit_history" not in st.session_state:
        st.session_state.audit_history = load_audit_history()

    st.session_state.audit_history.insert(0, entry)
    save_audit_history(st.session_state.audit_history)

# ==========================================
# 7. RENDER FULL AUDIT REPORT COMPONENT
# ==========================================
def render_audit_report_display(report_data: dict, recon_data: dict, key_prefix: str = ""):
    score = report_data.get("security_score", 0)
    if score >= 90:
        grade = "Grade A (Hardened & Secure)"
        score_color = "#34d399"
    elif score >= 75:
        grade = "Grade B (Moderate Security Posture)"
        score_color = "#60a5fa"
    elif score >= 60:
        grade = "Grade C (Needs Improvement)"
        score_color = "#facc15"
    elif score >= 40:
        grade = "Grade D (Significant Vulnerabilities)"
        score_color = "#fb923c"
    else:
        grade = "Grade F (Critical Attention Required)"
        score_color = "#f87171"

    findings = report_data.get("findings", [])
    total_findings = len(findings)
    crit_count = sum(1 for f in findings if f.get("severity") == "Critical")
    high_count = sum(1 for f in findings if f.get("severity") == "High")
    med_count = sum(1 for f in findings if f.get("severity") == "Medium")
    low_count = sum(1 for f in findings if f.get("severity") == "Low")
    info_count = sum(1 for f in findings if f.get("severity") == "Informational")

    # Metrics Overview Banner
    col_score, col_m1, col_m2, col_m3 = st.columns([2.5, 1, 1, 1])
    with col_score:
        st.markdown(f"""
        <div style="background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 14px 18px;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #9ca3af; text-transform: uppercase;">
                SYSTEM SECURITY SCORE
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.7rem; color: {score_color}; margin-top: 2px;">
                {score} / 100
            </div>
            <div style="font-size: 0.85rem; color: #d1d5db; margin-top: 2px; font-weight: 500;">{grade}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(score / 100.0)

    with col_m1:
        st.metric("Total Findings", str(total_findings))
    with col_m2:
        st.metric("Critical / High", f"{crit_count + high_count}")
    with col_m3:
        st.metric("Medium / Low", f"{med_count + low_count}")

    # Executive Summary Box
    st.markdown(f"""
    <div style="background-color: #0f172a; border-left: 4px solid #38bdf8; border-top: 1px solid #1e293b; border-right: 1px solid #1e293b; border-bottom: 1px solid #1e293b; padding: 16px 20px; border-radius: 6px; margin: 18px 0;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #38bdf8; text-transform: uppercase; font-weight: 700; margin-bottom: 6px;">
            📋 Executive Audit Summary
        </div>
        <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.5;">
            {report_data.get('summary', 'No summary provided.')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sub-Tabs Inside Audit Display
    sub_tab1, sub_tab2, sub_tab3 = st.tabs([
        "🚨 Security Audit Findings",
        "📡 Reconnaissance Raw Data",
        "📥 Export & Report"
    ])

    # Sub-Tab 1: Findings & Remediation
    with sub_tab1:
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            sev_filter = st.selectbox(
                "Filter by Severity Level",
                ["All Severities", "Critical", "High", "Medium", "Low", "Informational"],
                key=f"{key_prefix}_sev_filter"
            )
        with f_col2:
            search_kw = st.text_input(
                "Search Findings Keyword",
                placeholder="🔍 Real-time search (e.g. CSP, Cookie, HSTS, XSS...)",
                key=f"{key_prefix}_kw_filter"
            )

        # Filter Findings Logic
        display_findings = []
        for flaw in findings:
            f_sev = flaw.get("severity", "Informational")
            if sev_filter != "All Severities" and f_sev.lower() != sev_filter.lower():
                continue
            if search_kw.strip():
                kw = search_kw.strip().lower()
                in_title = kw in flaw.get("title", "").lower()
                in_desc = kw in flaw.get("description", "").lower()
                in_impact = kw in flaw.get("security_impact", "").lower()
                in_remed = kw in flaw.get("remediation", "").lower()
                if not (in_title or in_desc or in_impact or in_remed):
                    continue
            display_findings.append(flaw)

        st.markdown("<br>", unsafe_allow_html=True)

        if not display_findings:
            st.info("ℹ️ No vulnerabilities match the current severity and keyword filter.")
        else:
            for flaw in display_findings:
                severity = flaw.get("severity", "Informational")
                badge_cls = f"badge-{severity.lower()}"
                st.markdown(f"""
                <div class="terminal-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-weight: 600; font-size: 1.05rem; color: #f9fafb;">{flaw.get('title', 'Untitled Finding')}</span>
                        <span class="badge {badge_cls}">[{severity.upper()}]</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #9ca3af; margin-bottom: 10px;">
                        <strong style="color: #d1d5db;">Root Cause / Risk Description:</strong> {flaw.get('description', '')}
                    </div>
                    <div style="font-size: 0.9rem; color: #9ca3af; margin-bottom: 12px;">
                        <strong style="color: #fb923c;">🎯 Security Impact:</strong> {flaw.get('security_impact', '')}
                    </div>
                    <div style="font-size: 0.75rem; color: #6b7280; font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">RECOMMENDED REMEDIATION & SNIPPET:</div>
                    <div class="code-container">{flaw.get('remediation', '')}</div>
                </div>
                """, unsafe_allow_html=True)

    # Sub-Tab 2: Reconnaissance Raw Data
    with sub_tab2:
        st.markdown("### 📡 Raw Endpoint Inspection Metadata")
        
        with st.expander("🌐 Target Connection Summary", expanded=True):
            st.json({
                "Final Endpoint URL": recon_data.get("final_url"),
                "HTTP Response Code": recon_data.get("status_code"),
                "HTTPS Enforcement": recon_data.get("is_https")
            })

        with st.expander("🔑 Observed HTTP Response Headers"):
            st.json(recon_data.get("headers", {}))

        with st.expander("🍪 Detected Cookies & Security Flag Status"):
            cookies = recon_data.get("cookies", [])
            if cookies:
                formatted_cookies = []
                for c in cookies:
                    formatted_cookies.append({
                        "Cookie Name": c.get("name"),
                        "Secure Flag": "✅ Present" if c.get("secure_flag") else "❌ Missing (Insecure HTTP transmission)",
                        "HttpOnly Flag": "✅ Present" if c.get("httponly_flag") else "❌ Missing (XSS Accessible)"
                    })
                st.table(formatted_cookies)
            else:
                st.info("No Set-Cookie response headers observed.")

        with st.expander("📝 Extracted HTML Form & Input Fields"):
            forms = recon_data.get("forms_detected", [])
            if forms:
                st.json(forms)
            else:
                st.info("No HTML form elements detected on the target URL.")

    # Sub-Tab 3: Export & Report Generation
    with sub_tab3:
        st.markdown("### 📥 Generate & Export Audit Documentation")
        st.caption("Export structured compliance reports for developer handoff, SIEM tools, or documentation.")

        json_export_str = json.dumps({
            "target_url": recon_data.get("final_url"),
            "audit_timestamp": str(datetime.datetime.now()),
            "security_score": score,
            "executive_summary": report_data.get("summary", ""),
            "findings": findings
        }, indent=2)

        md_report_str = f"""# 🛡️ AI Web Security Configuration Audit Report

**Target Endpoint:** `{recon_data.get("final_url")}`  
**Audit Timestamp:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}`  
**Security Score:** `{score}/100` ({grade})  

---

## 📋 Executive Summary
{report_data.get("summary", "")}

---

## 📊 Findings Breakdown
- **Total Issues Identified:** {total_findings}
- **Critical:** {crit_count}
- **High:** {high_count}
- **Medium:** {med_count}
- **Low:** {low_count}
- **Informational:** {info_count}

---

## 🚨 Detailed Vulnerability Findings & Remediation

"""
        for idx, flaw in enumerate(findings, 1):
            md_report_str += f"""### {idx}. [{flaw.get('severity', 'INFO').upper()}] {flaw.get('title', '')}
- **Description:** {flaw.get('description', '')}
- **Security Impact:** {flaw.get('security_impact', '')}
- **Remediation Snippet:**
```
{flaw.get('remediation', '')}
```

"""

        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            st.markdown("""
            <div class="terminal-card">
                <h4 style="margin-top:0; color:#f9fafb;">📄 JSON Audit Report</h4>
                <p style="font-size:0.85rem; color:#9ca3af;">Machine-readable structured output ideal for automated pipelines & SIEM tools.</p>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇️ Download Audit Report (.json)",
                data=json_export_str,
                file_name=f"security_audit_{recon_data.get('status_code', 200)}.json",
                mime="application/json",
                use_container_width=True,
                key=f"{key_prefix}_dl_json"
            )

        with exp_col2:
            st.markdown("""
            <div class="terminal-card">
                <h4 style="margin-top:0; color:#f9fafb;">📝 Markdown Audit Report</h4>
                <p style="font-size:0.85rem; color:#9ca3af;">Formatted report suitable for GitHub issues, pull requests, and security docs.</p>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="⬇️ Download Audit Report (.md)",
                data=md_report_str,
                file_name=f"security_audit_report.md",
                mime="text/markdown",
                use_container_width=True,
                key=f"{key_prefix}_dl_md"
            )

# ==========================================
# 8. APP HEADER & TOP-LEVEL NAVIGATION
# ==========================================
st.markdown("""
<div style="margin-bottom: 16px;">
    <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: #f9fafb;">🌐 AI Web Security Configuration Auditor</h1>
    <p style="margin-top: 6px; color: #38bdf8; font-size: 0.95rem; font-weight: 500;">
        Automated defensive inspection evaluating HTTP headers, cookie security, OWASP standards & audit history analytics.
    </p>
</div>
""", unsafe_allow_html=True)

# Main Application Top-Level Tabs
tab_dashboard, tab_auditor, tab_history = st.tabs([
    "📊 Executive Dashboard",
    "🛡️ Security Auditor",
    "📜 Search & Audit History"
])

# ==========================================
# TAB 1: EXECUTIVE DASHBOARD
# ==========================================
with tab_dashboard:
    history = st.session_state.audit_history
    
    st.markdown("### 📊 Executive Security Analytics & Portfolio Dashboard")
    st.caption("Comprehensive metrics and posture overview across all audited website targets.")

    if not history:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(17, 24, 39, 0.65) 100%); border: 1px dashed rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 40px 20px; text-align: center; margin: 20px 0;">
            <div style="font-size: 3rem; margin-bottom: 10px;">🛡️</div>
            <h3 style="color: #f9fafb; margin-bottom: 8px;">No Audit Data Available Yet</h3>
            <p style="color: #9ca3af; font-size: 0.95rem; max-width: 500px; margin: 0 auto 20px auto;">
                Launch your first security scan in the <strong>Security Auditor</strong> tab to populate executive metrics, threat breakdowns, and historical logs.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_scans = len(history)
        avg_score = round(sum(item["security_score"] for item in history) / total_scans, 1)
        total_vulns = sum(item["total_findings"] for item in history)
        
        total_crit = sum(item["severity_counts"].get("Critical", 0) for item in history)
        total_high = sum(item["severity_counts"].get("High", 0) for item in history)
        total_med = sum(item["severity_counts"].get("Medium", 0) for item in history)
        total_low = sum(item["severity_counts"].get("Low", 0) for item in history)
        total_info = sum(item["severity_counts"].get("Informational", 0) for item in history)

        # Top KPI Metrics Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-size: 0.75rem; color: #9ca3af; font-weight: 600; text-transform: uppercase;">Total Scans Executed</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #38bdf8; margin-top: 4px;">{total_scans}</div>
                <div style="font-size: 0.8rem; color: #6b7280; margin-top: 2px;">Audited targets logged</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi2:
            score_clr = "#34d399" if avg_score >= 80 else ("#facc15" if avg_score >= 60 else "#f87171")
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-size: 0.75rem; color: #9ca3af; font-weight: 600; text-transform: uppercase;">Average Security Score</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: {score_clr}; margin-top: 4px;">{avg_score} / 100</div>
                <div style="font-size: 0.8rem; color: #6b7280; margin-top: 2px;">Portfolio-wide hardening rating</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi3:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-size: 0.75rem; color: #9ca3af; font-weight: 600; text-transform: uppercase;">Total Vulnerabilities</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #fb923c; margin-top: 4px;">{total_vulns}</div>
                <div style="font-size: 0.8rem; color: #6b7280; margin-top: 2px;">Misconfigurations identified</div>
            </div>
            """, unsafe_allow_html=True)

        with kpi4:
            crit_ratio = round(((total_crit + total_high) / total_vulns * 100), 1) if total_vulns > 0 else 0
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-size: 0.75rem; color: #9ca3af; font-weight: 600; text-transform: uppercase;">Critical & High Risk Ratio</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #f87171; margin-top: 4px;">{crit_ratio}%</div>
                <div style="font-size: 0.8rem; color: #6b7280; margin-top: 2px;">High priority remediation ratio</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Vulnerability Severity Distribution & Grade Counts
        dash_col1, dash_col2 = st.columns([1.5, 1])

        with dash_col1:
            st.markdown("""
            <div class="terminal-card">
                <h4 style="margin-top:0; color:#f9fafb;">🔥 Cumulative Risk Severity Distribution</h4>
                <p style="font-size:0.85rem; color:#9ca3af;">Vulnerability findings categorized by severity across all audited targets.</p>
            </div>
            """, unsafe_allow_html=True)

            s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(5)
            with s_col1:
                st.markdown(f"""
                <div style="background-color: #3f1214; border: 1px solid #7f1d1d; border-radius: 6px; padding: 12px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #f87171; font-weight: 700; text-transform: uppercase;">CRITICAL</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #f87171; margin-top: 4px;">{total_crit}</div>
                </div>
                """, unsafe_allow_html=True)
            with s_col2:
                st.markdown(f"""
                <div style="background-color: #3b1a0e; border: 1px solid #9a3412; border-radius: 6px; padding: 12px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #fb923c; font-weight: 700; text-transform: uppercase;">HIGH</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #fb923c; margin-top: 4px;">{total_high}</div>
                </div>
                """, unsafe_allow_html=True)
            with s_col3:
                st.markdown(f"""
                <div style="background-color: #362b0d; border: 1px solid #854d0e; border-radius: 6px; padding: 12px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #facc15; font-weight: 700; text-transform: uppercase;">MEDIUM</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #facc15; margin-top: 4px;">{total_med}</div>
                </div>
                """, unsafe_allow_html=True)
            with s_col4:
                st.markdown(f"""
                <div style="background-color: #0e2a38; border: 1px solid #0369a1; border-radius: 6px; padding: 12px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #38bdf8; font-weight: 700; text-transform: uppercase;">LOW</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #38bdf8; margin-top: 4px;">{total_low}</div>
                </div>
                """, unsafe_allow_html=True)
            with s_col5:
                st.markdown(f"""
                <div style="background-color: #1f2937; border: 1px solid #374151; border-radius: 6px; padding: 12px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #9ca3af; font-weight: 700; text-transform: uppercase;">INFO</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #9ca3af; margin-top: 4px;">{total_info}</div>
                </div>
                """, unsafe_allow_html=True)

        with dash_col2:
            grade_counts = {"Grade A": 0, "Grade B": 0, "Grade C": 0, "Grade D": 0, "Grade F": 0}
            for item in history:
                g = item.get("grade", "")
                if "Grade A" in g: grade_counts["Grade A"] += 1
                elif "Grade B" in g: grade_counts["Grade B"] += 1
                elif "Grade C" in g: grade_counts["Grade C"] += 1
                elif "Grade D" in g: grade_counts["Grade D"] += 1
                else: grade_counts["Grade F"] += 1

            st.markdown("""
            <div class="terminal-card">
                <h4 style="margin-top:0; color:#f9fafb;">🏷️ Hardening Grade Breakdown</h4>
                <p style="font-size:0.85rem; color:#9ca3af;">Distribution of security ratings across audited endpoints.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="font-size: 0.85rem; color: #d1d5db; line-height: 1.8;">
                🟢 <strong>Grade A (Hardened):</strong> {grade_counts['Grade A']} target(s)<br>
                🔵 <strong>Grade B (Moderate):</strong> {grade_counts['Grade B']} target(s)<br>
                🟡 <strong>Grade C (Needs Work):</strong> {grade_counts['Grade C']} target(s)<br>
                🟠 <strong>Grade D (Vulnerable):</strong> {grade_counts['Grade D']} target(s)<br>
                🔴 <strong>Grade F (Critical):</strong> {grade_counts['Grade F']} target(s)
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Recent Scans Table Summary
        st.markdown("### 🕒 Recent Audits Overview")
        recent_items = history[:5]
        for item in recent_items:
            badge_color = item.get("score_color", "#38bdf8")
            st.markdown(f"""
            <div class="terminal-card" style="display: flex; justify-content: space-between; align-items: center; padding: 14px 18px;">
                <div>
                    <span style="font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 1rem; color: #f9fafb;">
                        {item['target_url']}
                    </span>
                    <div style="font-size: 0.8rem; color: #6b7280; margin-top: 2px;">
                        Audited on: {item['timestamp']} | Status: HTTP {item['status_code']}
                    </div>
                </div>
                <div style="text-align: right;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.1rem; color: {badge_color};">
                        {item['security_score']} / 100
                    </span>
                    <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 2px;">
                        {item['total_findings']} vulnerabilities
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# TAB 2: SECURITY AUDITOR (SCANNER & RESULTS)
# ==========================================
with tab_auditor:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(17, 24, 39, 0.65) 100%); backdrop-filter: blur(10px); border: 1px solid rgba(56, 189, 248, 0.25); border-left: 4px solid #38bdf8; padding: 18px 22px; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
        <h4 style="margin-top: 0; margin-bottom: 8px; color: #f9fafb; font-size: 1rem; font-weight: 600;">
            💡 Active Security Auditor
        </h4>
        <p style="margin: 0; color: #9ca3af; font-size: 0.9rem; line-height: 1.6;">
            Perform automated, non-intrusive passive security audits on target website endpoints. It captures server HTTP response headers, verifies <code>Secure</code> and <code>HttpOnly</code> cookie security flags, and analyzes HTML form inputs. Data is evaluated using Groq-accelerated LLMs against OWASP Secure Headers benchmarks.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Glossy Target URL Input Bar
    url_input = st.text_input(
        "Target Endpoint URL",
        value=st.session_state.target_url,
        help="Enter an HTTP/HTTPS URL endpoint for passive reconnaissance & security analysis.",
        key="target_input_field"
    )

    st.session_state.target_url = url_input

    # Launch Button
    scan_btn = st.button("Launch Security Audit", type="primary", use_container_width=True)

    # Execute Audit
    if scan_btn:
        if not url_input.strip():
            st.warning("⚠️ Target URL cannot be empty. Please specify a domain or IP.")
        elif not api_key_input.strip():
            st.error("🔑 Groq API Key is required. Please provide a valid key in the sidebar.")
        else:
            with st.spinner("🌐 Fetching endpoint headers & executing LLM threat evaluation..."):
                try:
                    # 1. Passive Reconnaissance with configurable timeout
                    data = collect_metadata(url_input, timeout_sec=request_timeout_sec)
                    # 2. LLM Security Audit
                    report_obj = run_llm_audit(data, model_choice, api_key_input)
                    # 3. Save to History
                    record_audit_to_history(url_input, data, report_obj)
                    # 4. Store active scan results
                    st.session_state.recon_data = data
                    st.session_state.audit_report = report_obj
                    st.success("✅ Security Audit Completed & Saved to History!")
                    st.rerun()
                except requests.exceptions.Timeout as e:
                    st.error(f"⏰ Target Request Timed Out: {str(e)}")
                    st.info("💡 **Troubleshooting Tip:** You can increase the **HTTP Request Timeout (Seconds)** slider in the sidebar to 45s or 60s if the target host is slow.")
                except requests.exceptions.RequestException as e:
                    st.error(f"🌐 Endpoint Connection Error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Audit Execution Failed: {str(e)}")

    # Render Active Scan Results
    if "audit_report" in st.session_state and st.session_state.audit_report is not None:
        st.markdown("---")
        st.markdown("### 🎯 Active Scan Results")
        
        rep_obj = st.session_state.audit_report
        rep_dict = rep_obj.model_dump() if hasattr(rep_obj, "model_dump") else rep_obj
        recon_d = st.session_state.recon_data
        
        render_audit_report_display(rep_dict, recon_d, key_prefix="active_scan")

# ==========================================
# TAB 3: SEARCH & AUDIT HISTORY
# ==========================================
with tab_history:
    st.markdown("### 📜 Search & Audit History Log")
    st.caption("Search, filter, and inspect detailed historical vulnerability reports.")

    history = st.session_state.audit_history

    if not history:
        st.info("ℹ️ No historical audit records found. Run a scan in the Security Auditor tab to log results.")
    else:
        # Check if a specific history item is selected for detailed inspection
        if st.session_state.selected_history_id:
            selected_item = next((item for item in history if item["id"] == st.session_state.selected_history_id), None)
            
            if selected_item:
                if st.button("⬅️ Back to Audit History List", key="back_to_history_btn"):
                    st.session_state.selected_history_id = None
                    st.rerun()

                st.markdown(f"""
                <div style="background: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px;">
                    <div style="font-size: 0.8rem; color: #38bdf8; font-weight: 700; text-transform: uppercase;">HISTORICAL AUDIT REPORT DETAILS</div>
                    <h3 style="margin: 4px 0; color: #f9fafb;">{selected_item['target_url']}</h3>
                    <div style="font-size: 0.85rem; color: #9ca3af;">Audited on: {selected_item['timestamp']} | Status Code: HTTP {selected_item['status_code']}</div>
                </div>
                """, unsafe_allow_html=True)

                render_audit_report_display(
                    selected_item["audit_report"],
                    selected_item["recon_data"],
                    key_prefix=f"hist_{selected_item['id']}"
                )
            else:
                st.session_state.selected_history_id = None
                st.rerun()
        else:
            # Search & Filter Controls
            h_col1, h_col2, h_col3 = st.columns([2, 1, 1])
            with h_col1:
                search_query = st.text_input(
                    "Search History by URL / Domain",
                    placeholder="🔍 Enter domain name or target keyword...",
                    key="history_search_input"
                )
            with h_col2:
                grade_filter = st.selectbox(
                    "Filter by Security Grade",
                    ["All Grades", "Grade A Hardened", "Grade B Moderate", "Grade C Needs Work", "Grade D Vulnerable", "Grade F Critical"],
                    key="history_grade_filter"
                )
            with h_col3:
                sort_order = st.selectbox(
                    "Sort Order",
                    ["Newest First", "Oldest First", "Highest Score First", "Lowest Score First"],
                    key="history_sort_order"
                )

            # Filtering Logic
            filtered_history = []
            for item in history:
                if search_query.strip():
                    q = search_query.strip().lower()
                    if q not in item["target_url"].lower() and q not in item["final_url"].lower():
                        continue
                
                g = item.get("grade", "")
                if grade_filter != "All Grades":
                    if "Grade A" in grade_filter and "Grade A" not in g: continue
                    if "Grade B" in grade_filter and "Grade B" not in g: continue
                    if "Grade C" in grade_filter and "Grade C" not in g: continue
                    if "Grade D" in grade_filter and "Grade D" not in g: continue
                    if "Grade F" in grade_filter and "Grade F" not in g: continue

                filtered_history.append(item)

            # Sorting Logic
            if sort_order == "Oldest First":
                filtered_history.reverse()
            elif sort_order == "Highest Score First":
                filtered_history.sort(key=lambda x: x["security_score"], reverse=True)
            elif sort_order == "Lowest Score First":
                filtered_history.sort(key=lambda x: x["security_score"])

            st.markdown("<br>", unsafe_allow_html=True)

            # Manage History Clear Button
            top_h1, top_h2 = st.columns([3, 1])
            with top_h1:
                st.caption(f"Showing {len(filtered_history)} of {len(history)} logged audit records.")
            with top_h2:
                if st.button("🗑️ Clear Search History", use_container_width=True):
                    st.session_state.audit_history = []
                    save_audit_history([])
                    st.success("Audit history cleared!")
                    st.rerun()

            # Render History Cards
            if not filtered_history:
                st.info("ℹ️ No audit records match your search query and grade filter.")
            else:
                for item in filtered_history:
                    item_id = item["id"]
                    badge_color = item.get("score_color", "#38bdf8")
                    sev_counts = item.get("severity_counts", {})
                    
                    st.markdown(f"""
                    <div class="terminal-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.05rem; color: #f9fafb;">
                                    {item['target_url']}
                                </span>
                                <span style="font-size: 0.75rem; color: #9ca3af; margin-left: 10px; font-family: 'JetBrains Mono', monospace;">
                                    [HTTP {item['status_code']}]
                                </span>
                            </div>
                            <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.2rem; color: {badge_color};">
                                SCORE: {item['security_score']}/100
                            </span>
                        </div>
                        <div style="font-size: 0.8rem; color: #6b7280; margin-top: 4px; margin-bottom: 10px;">
                            📅 Timestamp: {item['timestamp']} | {item['grade']}
                        </div>
                        <div style="font-size: 0.85rem; color: #d1d5db; margin-bottom: 12px; line-height: 1.4;">
                            <strong>Summary:</strong> {item.get('summary', '')[:220]}...
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
                            <span class="badge badge-critical">Critical: {sev_counts.get('Critical', 0)}</span>
                            <span class="badge badge-high">High: {sev_counts.get('High', 0)}</span>
                            <span class="badge badge-medium">Medium: {sev_counts.get('Medium', 0)}</span>
                            <span class="badge badge-low">Low: {sev_counts.get('Low', 0)}</span>
                            <span class="badge badge-informational">Info: {sev_counts.get('Informational', 0)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_c1, btn_c2 = st.columns([3, 1])
                    with btn_c1:
                        if st.button(f"🔍 View Full Audit Details", key=f"view_btn_{item_id}", use_container_width=True):
                            st.session_state.selected_history_id = item_id
                            st.rerun()
                    with btn_c2:
                        if st.button(f"🗑️ Delete", key=f"del_btn_{item_id}", use_container_width=True):
                            st.session_state.audit_history = [i for i in st.session_state.audit_history if i["id"] != item_id]
                            save_audit_history(st.session_state.audit_history)
                            st.rerun()
