import os
import json
import datetime
import urllib3
import requests
from bs4 import BeautifulSoup
import streamlit as st
from typing import List, Literal
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

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #1f2937;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        border-radius: 6px 6px 0px 0px;
        color: #9ca3af;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #111827 !important;
        color: #38bdf8 !important;
        border: 1px solid #1f2937 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }

    /* Hide Default Header/Footer Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PYDANTIC DATA MODELS
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
# 3. SIDEBAR & CONFIGURATION
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

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Safe Test Targets")

# Session State for Target URL
if "target_url" not in st.session_state:
    st.session_state.target_url = "http://testphp.vulnweb.com/"

col_chip1, col_chip2 = st.sidebar.columns(2)
if col_chip1.button("⚡ TestPHP Demo", use_container_width=True, help="OWASP Vulnerable Demo Target"):
    st.session_state.target_url = "http://testphp.vulnweb.com/"
    st.rerun()

if col_chip2.button("🌐 Example.com", use_container_width=True, help="Standard Hardened Baseline"):
    st.session_state.target_url = "https://example.com/"
    st.rerun()

st.sidebar.markdown("""
<div style="font-size: 0.75rem; color: #6b7280; margin-top: 15px;">
    <strong>Notice:</strong> Passive audits evaluate headers, HTTP/HTTPS flags, forms, and cookies without intrusive exploitation.
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. PASSIVE RECONNAISSANCE COLLECTOR
# ==========================================
def collect_metadata(target_url: str) -> dict:
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "https://" + target_url

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SecurityAuditor/1.0"}
    response = requests.get(target_url, headers=headers, timeout=15, verify=False)
    
    # 1. Response Headers
    resp_headers = dict(response.headers)
    
    # 2. Cookie Flag Inspection
    cookies_data = []
    for c in response.cookies:
        cookies_data.append({
            "name": c.name,
            "secure_flag": c.secure,
            "httponly_flag": bool(c.has_nonstandard_attr('HttpOnly') or c._rest.get('HttpOnly'))
        })

    # 3. HTML Form Analysis
    soup = BeautifulSoup(response.text, "html.parser")
    forms = []
    for form in soup.find_all("form")[:5]:
        inputs = [i.get("name") or i.get("type") for i in form.find_all("input")]
        forms.append({
            "action": form.get("action", ""),
            "method": form.get("method", "GET").upper(),
            "inputs": inputs
        })

    return {
        "final_url": response.url,
        "status_code": response.status_code,
        "headers": resp_headers,
        "cookies": cookies_data,
        "forms_detected": forms,
        "is_https": response.url.startswith("https://")
    }

# ==========================================
# 5. LLM EVALUATION LOGIC
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
        timeout=15
    )

    return AuditReport.model_validate_json(response.choices[0].message.content)

# ==========================================
# 6. APP HEADER & EXPLANATION
# ==========================================
st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="margin: 0; font-size: 2.1rem; font-weight: 700; color: #f9fafb;">🌐 AI Web Security Configuration Auditor</h1>
    <p style="margin-top: 6px; color: #38bdf8; font-size: 0.95rem; font-weight: 500;">
        Automated defensive inspection evaluating HTTP headers, cookie security, and OWASP configuration standards.
    </p>
</div>

<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(17, 24, 39, 0.65) 100%); backdrop-filter: blur(10px); border: 1px solid rgba(56, 189, 248, 0.25); border-left: 4px solid #38bdf8; padding: 18px 22px; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);">
    <h4 style="margin-top: 0; margin-bottom: 8px; color: #f9fafb; font-size: 1rem; font-weight: 600;">
        💡 About This Auditor
    </h4>
    <p style="margin: 0; color: #9ca3af; font-size: 0.9rem; line-height: 1.6;">
        This application performs automated, non-intrusive passive security audits on target website endpoints. It captures server HTTP response headers, verifies <code>Secure</code> and <code>HttpOnly</code> cookie security flags, and analyzes HTML form inputs. Collected data is evaluated using Groq-accelerated Large Language Models against OWASP Secure Headers benchmarks to deliver instant security scores and actionable remediation snippets.
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

# Update session state if typed manually
st.session_state.target_url = url_input

# Light Blue Launch Button (No Rocket Emoji)
scan_btn = st.button("Launch Security Audit", type="primary", use_container_width=True)

# Handle Scan Execution
if scan_btn:
    if not url_input.strip():
        st.warning("⚠️ Target URL cannot be empty. Please specify a domain or IP.")
    elif not api_key_input.strip():
        st.error("🔑 Groq API Key is required. Please provide a valid key in the sidebar.")
    else:
        with st.spinner("🌐 Fetching endpoint headers & executing LLM threat evaluation..."):
            try:
                # 1. Passive Reconnaissance
                data = collect_metadata(url_input)
                # 2. LLM Security Audit
                report_obj = run_llm_audit(data, model_choice, api_key_input)
                # 3. Store Results in Session State
                st.session_state.recon_data = data
                st.session_state.audit_report = report_obj
                st.rerun()
            except requests.exceptions.Timeout:
                st.error("⏰ Target Request Timed Out: Endpoint failed to respond within 15 seconds.")
            except requests.exceptions.RequestException as e:
                st.error(f"🌐 Endpoint Connection Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Audit Execution Failed: {str(e)}")

# ==========================================
# 7. INTERACTIVE AUDIT DASHBOARD
# ==========================================
if "audit_report" in st.session_state and st.session_state.audit_report is not None:
    report: AuditReport = st.session_state.audit_report
    recon_data: dict = st.session_state.recon_data

    st.markdown("---")

    # Security Score Grade Calculation
    score = report.security_score
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

    total_findings = len(report.findings)
    crit_count = sum(1 for f in report.findings if f.severity == "Critical")
    high_count = sum(1 for f in report.findings if f.severity == "High")
    med_count = sum(1 for f in report.findings if f.severity == "Medium")
    low_count = sum(1 for f in report.findings if f.severity == "Low")
    info_count = sum(1 for f in report.findings if f.severity == "Informational")

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
        st.metric("Critical / High", f"{crit_count + high_count}", delta_color="inverse")
    with col_m3:
        st.metric("Medium / Low", f"{med_count + low_count}")

    # Executive Summary Box
    st.markdown(f"""
    <div style="background-color: #0f172a; border-left: 4px solid #38bdf8; border-top: 1px solid #1e293b; border-right: 1px solid #1e293b; border-bottom: 1px solid #1e293b; padding: 16px 20px; border-radius: 6px; margin: 18px 0;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #38bdf8; text-transform: uppercase; font-weight: 700; margin-bottom: 6px;">
            📋 Executive Audit Summary
        </div>
        <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.5;">
            {report.summary}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3-Tab Interactive Results Display
    tab1, tab2, tab3 = st.tabs([
        "🚨 Security Audit Findings",
        "📡 Reconnaissance Raw Data",
        "📥 Export & Report"
    ])

    # ==========================================
    # TAB 1: FINDINGS & REMEDIATION
    # ==========================================
    with tab1:
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            sev_filter = st.selectbox(
                "Filter by Severity Level",
                ["All Severities", "Critical", "High", "Medium", "Low", "Informational"],
                key="severity_filter_select"
            )
        with f_col2:
            search_kw = st.text_input(
                "Search Findings Keyword",
                placeholder="🔍 Real-time search (e.g. CSP, Cookie, HSTS, XSS...)",
                key="search_kw_select"
            )

        # Filter Findings Logic
        display_findings = []
        for flaw in report.findings:
            if sev_filter != "All Severities" and flaw.severity.lower() != sev_filter.lower():
                continue
            if search_kw.strip():
                kw = search_kw.strip().lower()
                in_title = kw in flaw.title.lower()
                in_desc = kw in flaw.description.lower()
                in_impact = kw in flaw.security_impact.lower()
                in_remed = kw in flaw.remediation.lower()
                if not (in_title or in_desc or in_impact or in_remed):
                    continue
            display_findings.append(flaw)

        st.markdown("<br>", unsafe_allow_html=True)

        if not display_findings:
            st.info("ℹ️ No vulnerabilities match the current severity and keyword filter.")
        else:
            for flaw in display_findings:
                badge_cls = f"badge-{flaw.severity.lower()}"
                st.markdown(f"""
                <div class="terminal-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-weight: 600; font-size: 1.05rem; color: #f9fafb;">{flaw.title}</span>
                        <span class="badge {badge_cls}">[{flaw.severity.upper()}]</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #9ca3af; margin-bottom: 10px;">
                        <strong style="color: #d1d5db;">Root Cause / Risk Description:</strong> {flaw.description}
                    </div>
                    <div style="font-size: 0.9rem; color: #9ca3af; margin-bottom: 12px;">
                        <strong style="color: #fb923c;">🎯 Security Impact:</strong> {flaw.security_impact}
                    </div>
                    <div style="font-size: 0.75rem; color: #6b7280; font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">RECOMMENDED REMEDIATION & SNIPPET:</div>
                    <div class="code-container">{flaw.remediation}</div>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # TAB 2: RECONNAISSANCE RAW DATA
    # ==========================================
    with tab2:
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

    # ==========================================
    # TAB 3: EXPORT & REPORT GENERATION
    # ==========================================
    with tab3:
        st.markdown("### 📥 Generate & Export Audit Documentation")
        st.caption("Export structured compliance reports for developer handoff, SIEM tools, or documentation.")

        # JSON Export Data
        json_export_str = json.dumps({
            "target_url": recon_data.get("final_url"),
            "audit_timestamp": str(datetime.datetime.now()),
            "security_score": report.security_score,
            "executive_summary": report.summary,
            "findings": [f.model_dump() for f in report.findings]
        }, indent=2)

        # Markdown Export Document
        md_report_str = f"""# 🛡️ AI Web Security Configuration Audit Report

**Target Endpoint:** `{recon_data.get("final_url")}`  
**Audit Timestamp:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}`  
**Security Score:** `{report.security_score}/100` ({grade})  

---

## 📋 Executive Summary
{report.summary}

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
        for idx, flaw in enumerate(report.findings, 1):
            md_report_str += f"""### {idx}. [{flaw.severity.upper()}] {flaw.title}
- **Description:** {flaw.description}
- **Security Impact:** {flaw.security_impact}
- **Remediation Snippet:**
```
{flaw.remediation}
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
                file_name=f"security_audit_{recon_data.get('status_code')}.json",
                mime="application/json",
                use_container_width=True
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
                use_container_width=True
            )