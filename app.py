import streamlit as st
import os
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import google.generativeai as genai
from PyPDF2 import PdfReader
from io import BytesIO

# Set page configuration with standard title and icon
st.set_page_config(
    page_title="GuardianAudit | Simple AI Document & Rules Checker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States for simple checkbox tracking & chat
if "mitigated_gaps" not in st.session_state:
    st.session_state["mitigated_gaps"] = {}
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ---------------------------------------------------------
# PREMIUM CSS STYLING ENGINE
# ---------------------------------------------------------
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #090b11;
        color: #e2e8f0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Header blur effect */
    [data-testid="stHeader"] {
        background-color: rgba(9, 11, 17, 0.8) !important;
        backdrop-filter: blur(12px);
    }
    
    /* Sidebar custom styling */
    [data-testid="stSidebar"] {
        background-color: #0f121d !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Dynamic Dashboard Card */
    .dashboard-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .dashboard-card:hover {
        border-color: rgba(16, 185, 129, 0.3);
        transform: translateY(-2px);
    }
    
    /* Key Metric Blocks */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        line-height: 1;
        background: linear-gradient(45deg, #10b981, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }
    
    /* Finding Cards */
    .finding-card {
        background: rgba(255, 255, 255, 0.015);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Custom colored borders for severities */
    .border-critical { border-left: 5px solid #ef4444; }
    .border-high { border-left: 5px solid #f97316; }
    .border-medium { border-left: 5px solid #f59e0b; }
    .border-low { border-left: 5px solid #3b82f6; }
    .border-compliant { border-left: 5px solid #10b981; }
    
    /* Modern Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 8px;
    }
    .badge-critical { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-high { background-color: rgba(249, 115, 22, 0.15); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); }
    .badge-medium { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-low { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-compliant { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    
    .badge-non-compliant { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-partially-compliant { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    
    /* Styled code containers */
    code {
        color: #f43f5e !important;
        background-color: rgba(244, 63, 94, 0.05) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    
    /* Premium landing header */
    .hero-container {
        padding: 40px;
        border-radius: 24px;
        background: radial-gradient(circle at top right, rgba(16, 185, 129, 0.08), transparent 60%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 30px;
        text-align: left;
    }
    
    .hero-title {
        font-size: 3rem;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    /* Chat bubbles modifications */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #3b82f6 !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #10b981 !important;
    }
    
    /* Hide default Streamlit elements if needed */
    footer {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# UTILITY CLASSES & DATA STRUCTS
# ---------------------------------------------------------
class PresetStandards:
    """Pre-configured simple standard rules lists."""
    @staticmethod
    def get_presets():
        return {
            "SOC 2 Security Standard (Safety & Trust)": [
                "Individual user accounts must have strict safety permissions, so employees only access files they need to do their jobs.",
                "Production and database systems must require Multi-Factor Authentication (MFA, like a phone prompt code) to log in.",
                "All customer databases and files must be securely encrypted when stored and encrypted when sent over the internet.",
                "Automatic security checks must scan for computer bugs at least monthly, and dangerous bugs must be fixed within 14 days.",
                "Backup copies of databases must run automatically every day, be stored in a separate location, and be checked once a year.",
                "There must be a clear plan to handle security issues and hacks, including telling affected customers within 72 hours of finding a breach."
            ],
            "ISO 27001 standard (Global Safety Rules)": [
                "There must be an official company security rulebook approved by managers, updated every year, and read by all employees.",
                "Background checks must be run on all new hires before they start, and they must sign basic non-disclosure rules.",
                "All company devices, software, and databases must be listed in a clear inventory list with assigned owners.",
                "Access permissions for computers and systems must be reviewed at least every 6 months to make sure old employees don't have access.",
                "Office entries and server areas must be locked, requiring badges or keys, with cameras and visitor logs.",
                "How computers are managed, changed, and configured must be clearly written down so anyone can follow the steps."
            ],
            "HIPAA Rules (Health Data Privacy)": [
                "Every employee accessing private patient health records must have their own unique username and password.",
                "Workstations and computers displaying patient health records must log out automatically when left unattended.",
                "All patient health files must be encrypted before sending them over the public internet.",
                "Databases storing health records must log every user who views, edits, or deletes a file.",
                "There must be a clear data recovery plan, including daily backups, to restore health records in case of an emergency."
            ],
            "GDPR Rules (European Privacy Rules)": [
                "The business must have a clear reason to collect customer data, get explicit permission first, and let customers opt out easily.",
                "Customers must be shown a simple privacy notice explaining what data is saved, how long it is kept, and who sees it.",
                "Customers must have the right to request that all of their personal data be deleted immediately ('right to be forgotten').",
                "The business must only collect the minimum amount of customer information needed to perform their services.",
                "If customer data is leaked or hacked, the business must notify privacy authorities within 72 hours of finding out."
            ]
        }


class PDFProcessor:
    """Helper to safely extract text from PDF files."""
    @staticmethod
    def extract_text(uploaded_file) -> str:
        try:
            pdf_data = uploaded_file.read()
            pdf_file = BytesIO(pdf_data)
            reader = PdfReader(pdf_file)
            
            text_chunks = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
            
            cleaned_text = "\n\n".join(text_chunks)
            # Basic sanitization of invalid unicode structures
            cleaned_text = cleaned_text.replace('\u0000', '')
            return cleaned_text.strip()
        except Exception as e:
            st.error(f"Error parsing PDF: {str(e)}")
            return ""


# ---------------------------------------------------------
# GEMINI AUDIT ENGINE
# ---------------------------------------------------------
class AuditEngine:
    """Core LLM Interface handling prompts, schemas, and Gemini calls."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)

    def audit_document(self, doc_text: str, requirements: list, model_name: str = "gemini-1.5-flash") -> dict:
        """Runs the surgical audit prompt against Gemini and returns verified structured JSON output."""
        
        system_instruction = (
            "You are a friendly, highly qualified Security Compliance Auditor and Rules Checker. "
            "Your task is to review a company's business document or policy file and compare it against "
            "a set of specific rules or safety requirements.\n\n"
            "Look for direct or implied contradictions, missing items, or partial alignments. "
            "For each requirement, provide a clear finding in a simple, non-jargony, readable JSON structure."
        )
        
        prompt = f"""
OPERATIONAL DOCUMENT TEXT:
\"\"\"
{doc_text}
\"\"\"

COMPLIANCE REQUIREMENTS TO AUDIT AGAINST:
{json.dumps(requirements, indent=2)}

INSTRUCTIONS:
Conduct an audit. For EACH of the rules listed above, construct a finding containing:
1. `requirement`: The text of the rule checked.
2. `status`: One of "Compliant" (fully addressed with evidence), "Partially Compliant" (addressed but missing core components/details), or "Non-Compliant" (not addressed, missing entirely, or directly violated).
3. `severity`: The risk severity if this rule is missing. One of "Critical", "High", "Medium", "Low", or "None" (if fully Compliant).
4. `evidence`: The direct quote or referenced section from the document. If the rule is missing, explain the exact lack of text.
5. `gap_details`: Detail the specific delta or missing control in simple, everyday language. What makes it not compliant?
6. `recommendation`: A highly specific, concrete, step-by-step action plan to achieve complete safety.

Also calculate:
- `compliance_score`: A percentage (0-100) representing overall safety score based on statuses:
  - Compliant = 100%
  - Partially Compliant = 50%
  - Non-Compliant = 0%
  Average the scores across all rules.
- `executive_summary`: A concise, high-level summary of the safety check results in very friendly, plain English.

Your response must be a single, valid JSON object following this EXACT schema structure:
{{
  "compliance_score": 75,
  "executive_summary": "Simple overview of the results in plain English...",
  "findings": [
    {{
      "requirement": "Rule text...",
      "status": "Non-Compliant",
      "severity": "High",
      "evidence": "No mention of monthly scans is present in the document.",
      "gap_details": "The document describes manual checks but does not set up a regular monthly schedule.",
      "recommendation": "Add a line to Section 4.2 of your policy stating that automatic security scans are set up to run every single month."
    }}
  ]
}}
"""

        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.1,
                },
                system_instruction=system_instruction
            )
            
            response = model.generate_content(prompt)
            result_json = json.loads(response.text)
            return result_json
            
        except json.JSONDecodeError as je:
            st.error("AI returned invalid data format. Attempting recovery...")
            return {
                "compliance_score": 0,
                "executive_summary": "Failed to parse the response. Please try scanning again.",
                "findings": []
            }
        except Exception as e:
            st.error(f"AI Engine Error: {str(e)}")
            return None


# ---------------------------------------------------------
# COMPLIANCE REPORT GENERATOR
# ---------------------------------------------------------
class ComplianceReporter:
    """Handles report compilation, metrics math, and file exports."""
    @staticmethod
    def generate_markdown_report(data: dict, mitigated_dict: dict = None) -> str:
        """Compiles the JSON audit payload into a clean, easy-to-read markdown report."""
        findings = data.get("findings", [])
        
        # Calculate dynamic values based on active checkmarks
        individual_scores = []
        for idx, f in enumerate(findings):
            status = f.get("status", "Non-Compliant")
            is_mitigated = mitigated_dict.get(idx, False) if mitigated_dict else False
            
            if status == "Compliant" or is_mitigated:
                individual_scores.append(100)
            elif status == "Partially Compliant":
                individual_scores.append(50)
            else:
                individual_scores.append(0)
        
        score = int(sum(individual_scores) / len(individual_scores)) if len(individual_scores) > 0 else 0
        summary = data.get("executive_summary", "")
        
        md = []
        md.append(f"# Business Safety & Rules Checker Report")
        md.append(f"**Overall Safety Score (With Your Fixes): `{score}%`**")
        md.append(f"")
        md.append(f"## 1. Summary of Results")
        md.append(summary)
        md.append(f"")
        md.append(f"## 2. Quick Scorecard & Fix Checklist")
        md.append(f"| # | Status | Danger Level | Your Checklist Status | Safety Rule Checked |")
        md.append(f"|---|--------|--------------|-----------------------|---------------------|")
        
        status_map = {"Compliant": "Safe", "Partially Compliant": "Needs Work", "Non-Compliant": "Failed/Missing"}
        sev_map = {"Critical": "🚨 Critical", "High": "🟠 High", "Medium": "🟡 Medium", "Low": "🔵 Low", "None": "🟢 Safe"}
        
        for i, f in enumerate(findings, 1):
            is_mitigated = mitigated_dict.get(i-1, False) if mitigated_dict else False
            orig_status = status_map.get(f.get('status'), f.get('status'))
            display_sev = sev_map.get(f.get('severity'), f.get('severity'))
            
            fix_state = "🛠️ Fixed (Recalculated)" if is_mitigated else "🔴 Open Problem" if f.get('status') != 'Compliant' else "✔️ Passes"
            md.append(f"| {i} | {orig_status} | {display_sev} | {fix_state} | {f.get('requirement')[:60]}... |")
            
        md.append(f"")
        md.append(f"## 3. Detailed Explanations & Step-by-Step Fixes")
        
        for i, f in enumerate(findings, 1):
            is_mitigated = mitigated_dict.get(i-1, False) if mitigated_dict else False
            orig_status = status_map.get(f.get('status'), f.get('status'))
            display_sev = sev_map.get(f.get('severity'), f.get('severity'))
            
            md.append(f"### Rule {i:02d}: {f.get('requirement')[:100]}")
            md.append(f"- **Current Status**: {orig_status}  ")
            md.append(f"- **Danger Level**: {display_sev}  ")
            md.append(f"- **Your Checklist Status**: {'🛠️ Fixed by You (Score Recalculated)' if is_mitigated else '🔴 Needs attention'}  ")
            md.append(f"")
            md.append(f"#### What we found in your file:")
            md.append(f"> {f.get('evidence')}")
            md.append(f"")
            md.append(f"#### What is missing or wrong:")
            md.append(f"{f.get('gap_details')}")
            md.append(f"")
            md.append(f"#### 💡 How to fix it:")
            md.append(f"**Step-by-step**: {f.get('recommendation')}")
            md.append(f"---")
            md.append(f"")
            
        return "\n".join(md)

    @staticmethod
    def generate_csv_report(data: dict, mitigated_dict: dict = None) -> bytes:
        """Converts findings into a simple CSV structure for Excel."""
        findings = data.get("findings", [])
        rows = []
        
        status_map = {"Compliant": "Safe", "Partially Compliant": "Needs Work", "Non-Compliant": "Failed/Missing"}
        sev_map = {"Critical": "Critical Risk", "High": "High Risk", "Medium": "Medium Risk", "Low": "Low Risk", "None": "No Risk"}
        
        for idx, f in enumerate(findings):
            is_mitigated = mitigated_dict.get(idx, False) if mitigated_dict else False
            status = f.get("status", "Non-Compliant")
            
            row = {
                "Safety Rule": f.get("requirement", ""),
                "Original Status": status_map.get(status, status),
                "Checklist Status": "Fixed by User" if is_mitigated else "Safe" if status == "Compliant" else "Needs Attention",
                "Danger Level": sev_map.get(f.get("severity"), f.get("severity")),
                "What we found in your document": f.get("evidence", ""),
                "What is missing": f.get("gap_details", ""),
                "How to fix it": f.get("recommendation", "")
            }
            rows.append(row)
            
        df = pd.DataFrame(rows)
        cols = ["Safety Rule", "Original Status", "Checklist Status", "Danger Level", "What we found in your document", "What is missing", "How to fix it"]
        df = df[cols]
        return df.to_csv(index=False).encode('utf-8')


# ---------------------------------------------------------
# DEMO MOCK SAMPLE DATA GENERATOR
# ---------------------------------------------------------
DEMO_POLICY_TEXT = """
ACME CORP DRAFT SECURITY & DATA OPERATION PROCEDURE
Version 0.4 (October 2025)

1. General Overview
Acme Corp operates a cloud platform connecting users with local retail listings. We care about data safety, but value operational speed above unnecessary processes.

2. Access Governance & Accounts
To ensure work doesn't halt when developers are on vacation, we utilize shared master database passwords which are stored securely on a whiteboard in our locked main engineering room. New engineers are verbally told the passwords. When engineers leave, we change the passwords within a month if they had access to customer records. MFA is strongly encouraged for email, but is optional for AWS server consoles to prevent session timeout disruptions.

3. Encryption & Information Storage
All databases reside in AWS. We rely on AWS's physical infrastructure for security. Because our main office in Stanford is gated, we do not require device-level encryption on developer laptops. Customer names and email lists are kept in plain text in PostgreSQL databases to make it fast for marketing tools to pull newsletters. 

4. Vulnerability Operations
Our lead developer manually checks dependencies and reads security newsletters every few months. If we hear of a zero-day exploit, we try to deploy patches during the next scheduled quarterly release.

5. System Recovery & Backups
To save AWS storage costs, we don't do daily automated backups of our SQL databases. The engineering lead takes a manual database snapshot on their laptop before any major system release (usually once every 4 months). These snapshots are stored in their local downloads folder.

6. Incident Responses
In the event that our logs show database intrusion, the engineering lead will reboot the server instances. We do not have a written incident report template, as we believe a quick Zoom call is faster. We only tell customers about hacks if a major credit card portal notifies us that cards are leaking.
"""


# ---------------------------------------------------------
# STREAMLIT UI CONTROLLER & ROUTER
# ---------------------------------------------------------
def main():
    # Application Title Bar
    st.markdown(
        """
        <div class='hero-container'>
            <div style='font-size: 0.85rem; font-weight: 800; color: #10b981; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;'>
                🛡️ Smart Safety & Rules Checker
            </div>
            <h1 class='hero-title'>GuardianAudit AI</h1>
            <p style='color: #94a3b8; font-size: 1.1rem; max-width: 800px; margin: 0;'>
                Instantly check your business documents or policies to find missing rules and safety gaps. Fix issues step-by-step and write better rules with our friendly AI assistant.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ---------------------------------------------------------
    # SIDEBAR PANEL - CONFIG & KEYS
    # ---------------------------------------------------------
    st.sidebar.image("https://img.icons8.com/nolan/96/shield.png", width=60)
    st.sidebar.markdown("### ⚙️ Settings")
    
    # API Key retrieval (Env Variable first, then user input)
    env_key = os.environ.get("GEMINI_API_KEY", "")
    api_key_placeholder = "Pre-configured from Server" if env_key else "Paste Gemini API Key..."
    
    api_key = st.sidebar.text_input(
        "Google AI Studio API Key",
        value=env_key,
        type="password",
        placeholder=api_key_placeholder,
        help="Get a free key from Google AI Studio or search 'Google AI Studio key'"
    )
    
    final_api_key = api_key if api_key else env_key
    
    if not final_api_key:
        st.sidebar.warning("⚠️ API Key is missing. Please paste one above to start running scans.")
        
    model_choice = st.sidebar.selectbox(
        "🧠 AI Scan Speed / Detail Level",
        options=["gemini-1.5-flash", "gemini-1.5-pro"],
        format_func=lambda x: "⚡ Fast Engine (Recommended)" if x == "gemini-1.5-flash" else "🧠 Deep Scan Engine (Detailed)",
        index=0,
        help="The Fast Engine is incredibly fast and perfect for quick checks. The Deep Scan Engine is recommended for huge documents."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Choose Rules to Check Against")
    
    audit_mode = st.sidebar.radio(
        "How would you like to check it?",
        options=[
            "Standard Safety Rules (SOC2, GDPR, HIPAA, etc.)",
            "Write My Own Custom Rules Checklist",
            "Compare Against Another PDF Document"
        ]
    )
    
    preset_dict = PresetStandards.get_presets()
    selected_preset = None
    custom_rules_list = []
    reference_pdf_text = ""
    
    if "Standard Safety Rules" in audit_mode:
        selected_preset = st.sidebar.selectbox(
            "Select Rules Framework",
            options=list(preset_dict.keys())
        )
        audit_requirements = preset_dict[selected_preset]
        
    elif "Write My Own" in audit_mode:
        st.sidebar.info("Type or paste your rules here (one rule per line).")
        custom_input = st.sidebar.text_area(
            "My Custom Rules List",
            value="All system administrators must use a security password manager.\nDatabase backups must run automatically every single day.\nAll database screens must use a secure encrypted connection.",
            height=150
        )
        audit_requirements = [r.strip() for r in custom_input.split("\n") if r.strip()]
        
    else: # Dual-PDF mode
        st.sidebar.info("Upload the PDF document containing the reference rules you want to check against.")
        ref_file = st.sidebar.file_uploader("Upload Reference Rules PDF", type=["pdf"], key="ref_pdf_uploader")
        
        if ref_file:
            with st.spinner("Extracting reference standard..."):
                reference_pdf_text = PDFProcessor.extract_text(ref_file)
            st.sidebar.success("✅ Reference standard loaded!")
        
        audit_requirements = []
        
    st.sidebar.markdown("---")
    st.sidebar.markdown("💡 **Test It Instantly!**")
    load_demo = st.sidebar.button("✨ Load Sample Document", help="Click to immediately load a sample draft policy containing intentional security gaps to test the checker instantly.")
    
    # ---------------------------------------------------------
    # MAIN WORKSPACE
    # ---------------------------------------------------------
    col_input, col_meta = st.columns([2, 1])
    
    with col_input:
        st.markdown("### 📥 Upload Your Document (PDF)")
        uploaded_doc = st.file_uploader(
            "Upload the file you want to check (like a security policy, user guide, or business contract PDF)",
            type=["pdf"],
            key="doc_pdf_uploader"
        )
        
    with col_meta:
        st.markdown("### ⚡ Quick Actions")
        if load_demo:
            st.session_state["doc_text"] = DEMO_POLICY_TEXT
            st.session_state["doc_name"] = "Demo_Company_Draft_Policy.txt"
            st.session_state["mitigated_gaps"] = {}
            st.session_state["chat_history"] = []
            st.toast("Loaded Sample Draft Policy!", icon="✨")
            
        if uploaded_doc:
            with st.spinner("Reading text from your PDF..."):
                st.session_state["doc_text"] = PDFProcessor.extract_text(uploaded_doc)
                st.session_state["doc_name"] = uploaded_doc.name
                st.session_state["mitigated_gaps"] = {}
                st.session_state["chat_history"] = []
            st.toast("Successfully read PDF!", icon="📄")

        has_doc = "doc_text" in st.session_state and st.session_state["doc_text"]
        
        if has_doc:
            st.success(f"📂 Active Document: **{st.session_state.get('doc_name', 'Custom Text')}** ({len(st.session_state['doc_text'])} characters)")
        else:
            st.info("No document loaded yet. Please upload a PDF or click 'Load Sample Document' in the sidebar.")
            
        run_audit_btn = st.button(
            "🛡️ START THE SAFETY SCAN",
            use_container_width=True,
            type="primary",
            disabled=not has_doc
        )

    # ---------------------------------------------------------
    # SCAN EXECUTION HANDLER
    # ---------------------------------------------------------
    if run_audit_btn:
        if not final_api_key:
            st.error("❌ Unable to run scan. Please paste a valid Gemini API Key in the left Settings panel.")
        else:
            st.session_state["mitigated_gaps"] = {}
            st.session_state["chat_history"] = []
            
            if "Compare Against" in audit_mode:
                if not reference_pdf_text:
                    st.error("❌ Compare mode selected, but no Reference Rules PDF was uploaded.")
                    return
                with st.spinner("Extracting safety requirements from your reference PDF..."):
                    extractor_engine = AuditEngine(final_api_key)
                    extraction_prompt = f"""
                    You are a Security Assessor. Analyze this reference guidelines document and extract up to 6 core, clear, actionable safety rules or instructions. Return them as a flat JSON array of strings in friendly, plain language.
                    
                    TEXT:
                    {reference_pdf_text[:12000]}
                    
                    OUTPUT SCHEMA:
                    [
                      "Rule 1...",
                      "Rule 2..."
                    ]
                    """
                    try:
                        model = genai.GenerativeModel(
                            model_choice,
                            generation_config={"response_mime_type": "application/json", "temperature": 0.1}
                        )
                        response = model.generate_content(extraction_prompt)
                        dynamic_requirements = json.loads(response.text)
                        if isinstance(dynamic_requirements, list) and len(dynamic_requirements) > 0:
                            audit_requirements = dynamic_requirements
                            st.info(f"📋 Found {len(audit_requirements)} rules in reference document.")
                        else:
                            st.warning("Could not extract rules. Using pre-set SOC2 rules list instead.")
                            audit_requirements = preset_dict["SOC 2 Security Standard (Safety & Trust)"]
                    except Exception as e:
                        st.error(f"Error reading rules: {str(e)}")
                        audit_requirements = preset_dict["SOC 2 Security Standard (Safety & Trust)"]
            
            with st.spinner("⚡ AI checking your document for safety gaps and comparing clauses..."):
                auditor = AuditEngine(final_api_key)
                audit_result = auditor.audit_document(
                    doc_text=st.session_state["doc_text"],
                    requirements=audit_requirements,
                    model_name=model_choice
                )
                
                if audit_result:
                    st.session_state["audit_result"] = audit_result
                    st.success("🎉 Safety check completed successfully!")
                    st.balloons()
                else:
                    st.error("The AI engine ran into an error. Please verify your API key and try again.")

    # ---------------------------------------------------------
    # RENDERING THE EXECUTIVE ANALYTICS DASHBOARD
    # ---------------------------------------------------------
    if "audit_result" in st.session_state and st.session_state["audit_result"]:
        report_data = st.session_state["audit_result"]
        findings = report_data.get("findings", [])
        
        # Calculate dynamic safety score based on user's fix checkboxes
        individual_scores = []
        mitigated_dict = st.session_state.get("mitigated_gaps", {})
        
        for idx, f in enumerate(findings):
            status = f.get("status", "Non-Compliant")
            is_mitigated = mitigated_dict.get(idx, False)
            
            if status == "Compliant" or is_mitigated:
                individual_scores.append(100)
            elif status == "Partially Compliant":
                individual_scores.append(50)
            else:
                individual_scores.append(0)
                
        score = int(sum(individual_scores) / len(individual_scores)) if len(individual_scores) > 0 else report_data.get("compliance_score", 0)
        executive_summary = report_data.get("executive_summary", "")
        
        # Calculate Danger Level aggregations for open gaps only
        sev_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "None": 0}
        status_counts = {"Compliant": 0, "Partially Compliant": 0, "Non-Compliant": 0}
        
        for idx, f in enumerate(findings):
            status = f.get("status", "Non-Compliant")
            is_mitigated = mitigated_dict.get(idx, False)
            
            if is_mitigated:
                status_counts["Compliant"] += 1
                sev_counts["None"] += 1
            else:
                sev = f.get("severity", "None")
                sev_counts[sev] = sev_counts.get(sev, 0) + 1
                status_counts[status] = status_counts.get(status, 0) + 1
            
        critical_count = sev_counts.get("Critical", 0)
        high_count = sev_counts.get("High", 0)
        total_gaps = len(findings) - status_counts.get("Compliant", 0)
        
        # Mapping to friendly terms
        status_map = {"Compliant": "Safe (Passes)", "Partially Compliant": "Needs Work", "Non-Compliant": "Failed / Missing"}
        sev_map = {"Critical": "🚨 Critical Danger", "High": "🟠 High Danger", "Medium": "🟡 Medium Danger", "Low": "🔵 Low Danger", "None": "🟢 Safe"}
        
        st.markdown("---")
        
        # Tabbed Layout in simple terms
        tab_dashboard, tab_findings, tab_chat, tab_raw_docs, tab_exports = st.tabs([
            "📊 Summary Dashboard",
            "🛡️ Safety Gaps Found",
            "💬 Ask the AI Assistant",
            "📄 View Document Text",
            "📥 Download Reports"
        ])
        
        # 1. TAB: DASHBOARD
        with tab_dashboard:
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            
            with col_kpi1:
                st.markdown(
                    f"""
                    <div class='dashboard-card'>
                        <div class='metric-value'>{score}%</div>
                        <div class='metric-label'>Overall Safety Score</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_kpi2:
                st.markdown(
                    f"""
                    <div class='dashboard-card'>
                        <div class='metric-value' style='background: linear-gradient(45deg, #ef4444, #f97316); -webkit-text-fill-color: transparent;'>{critical_count + high_count}</div>
                        <div class='metric-label'>🚨 Dangerous Gaps Remaining</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_kpi3:
                st.markdown(
                    f"""
                    <div class='dashboard-card'>
                        <div class='metric-value' style='background: linear-gradient(45deg, #f59e0b, #60a5fa); -webkit-text-fill-color: transparent;'>{total_gaps}</div>
                        <div class='metric-label'>⚠️ Total Problems Left</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            # Charts Section
            col_chart1, col_chart2 = st.columns([1, 1])
            
            with col_chart1:
                # Radial Safety Gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Safety Meter Score", 'font': {'size': 20, 'family': 'Outfit'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                        'bar': {'color': "#10b981" if score >= 80 else "#f59e0b" if score >= 50 else "#ef4444"},
                        'bgcolor': "rgba(255,255,255,0.03)",
                        'borderwidth': 1,
                        'bordercolor': "rgba(255,255,255,0.1)",
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.08)'},
                            {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.08)'},
                            {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.08)'}
                        ]
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#e2e8f0"},
                    height=280,
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col_chart2:
                # Gaps Danger Level Pie Chart
                sev_filtered = {sev_map.get(k, k): v for k, v in sev_counts.items() if k != "None" and v > 0}
                if len(sev_filtered) == 0:
                    sev_filtered = {"Fully Secure (No Gaps)": 1}
                    color_seq = ["#10b981"]
                else:
                    color_seq = []
                    colors_mapping = {"🚨 Critical Danger": "#ef4444", "🟠 High Danger": "#f97316", "🟡 Medium Danger": "#f59e0b", "🔵 Low Danger": "#3b82f6"}
                    for k in sev_filtered.keys():
                        color_seq.append(colors_mapping.get(k, "#64748b"))
                
                fig_donut = px.pie(
                    names=list(sev_filtered.keys()),
                    values=list(sev_filtered.values()),
                    hole=0.5,
                    title="Gaps by Danger Level",
                    color_discrete_sequence=color_seq
                )
                fig_donut.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': "#e2e8f0", 'family': 'Plus Jakarta Sans'},
                    height=280,
                    margin=dict(l=20, r=20, t=50, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
                st.plotly_chart(fig_donut, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Executive Summary card
            st.markdown(
                f"""
                <div class='dashboard-card'>
                    <h3 style='margin-top:0; color:#10b981;'>🕵️ Friendly Overview & Analysis</h3>
                    <p style='color: #cbd5e1; line-height: 1.6; font-size: 1rem; margin:0;'>
                        {executive_summary}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # 2. TAB: DETAILED FINDINGS
        with tab_findings:
            st.markdown("### 🔍 Step-by-Step Breakdown & Fixes")
            st.caption("Review individual items, check off what you've fixed, and see your Safety score increase dynamically above!")
            
            # Interactive Filter Bar
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_status = st.multiselect(
                    "Filter by Status",
                    options=["Compliant", "Partially Compliant", "Non-Compliant"],
                    format_func=lambda x: status_map.get(x),
                    default=["Compliant", "Partially Compliant", "Non-Compliant"]
                )
            with col_f2:
                filter_sev = st.multiselect(
                    "Filter by Danger Level",
                    options=["Critical", "High", "Medium", "Low", "None"],
                    format_func=lambda x: sev_map.get(x),
                    default=["Critical", "High", "Medium", "Low", "None"]
                )
                
            # Render Findings List
            matching_findings = 0
            for i, f in enumerate(findings, 1):
                status = f.get("status", "Non-Compliant")
                sev = f.get("severity", "None")
                
                # Apply filter
                if status not in filter_status or sev not in filter_sev:
                    continue
                
                matching_findings += 1
                
                is_gap = status != "Compliant"
                is_mitigated = st.session_state["mitigated_gaps"].get(i-1, False)
                
                # Dynamic rendering based on fixes checkbox
                display_status = "Safe (Fixed)" if is_mitigated else status_map.get(status, status)
                display_sev = "Safe" if is_mitigated else sev_map.get(sev, sev)
                border_cls = "border-compliant" if (status == "Compliant" or is_mitigated) else f"border-{sev.lower()}"
                badge_sev_cls = "badge-compliant" if is_mitigated else f"badge-{sev.lower()}"
                badge_status_cls = "badge-compliant" if is_mitigated else f"badge-{status.lower().replace(' ', '-')}"
                
                st.markdown(
                    f"""
                    <div class='finding-card {border_cls}' style='margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                            <div>
                                <span class='badge {badge_status_cls}'>{display_status}</span>
                                <span class='badge {badge_sev_cls}'>{display_sev}</span>
                            </div>
                            <span style='color: #64748b; font-size: 0.85rem; font-weight: 600;'>Rule #{i:02d}</span>
                        </div>
                        <h4 style='margin: 0 0 10px 0; color: #f1f5f9;'>{f.get('requirement')}</h4>
                        <div style='margin-bottom: 12px;'>
                            <strong style='color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing:0.02em;'>What we found in your file:</strong>
                            <p style='color: #cbd5e1; font-style: italic; background: rgba(0,0,0,0.2); padding: 10px 14px; border-radius: 6px; border-left: 2px solid rgba(255,255,255,0.1); margin: 6px 0 0 0; font-size: 0.9rem;'>
                                "{f.get('evidence')}"
                            </p>
                        </div>
                        <div style='margin-bottom: 12px;'>
                            <strong style='color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing:0.02em;'>What is missing or wrong:</strong>
                            <p style='color: #cbd5e1; margin: 4px 0 0 0; font-size: 0.92rem;'>{f.get('gap_details')}</p>
                        </div>
                        <div style='background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.15); padding: 12px 16px; border-radius: 8px;'>
                            <strong style='color: #34d399; font-size: 0.85rem; text-transform: uppercase; letter-spacing:0.02em;'>💡 How to fix this:</strong>
                            <p style='color: #e2e8f0; margin: 4px 0 0 0; font-weight: 500; font-size: 0.92rem;'>{f.get('recommendation')}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Checkbox container integration
                if is_gap:
                    st.markdown("<div style='background: rgba(255,255,255,0.01); border-left: 5px solid #64748b; border-right: 1px solid rgba(255,255,255,0.04); border-bottom: 1px solid rgba(255,255,255,0.04); border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; padding: 12px 20px; margin-bottom: 16px;'>", unsafe_allow_html=True)
                    cb_key = f"mitigate_{i}_{f.get('requirement')[:15].replace(' ', '_')}"
                    
                    is_mitigated_val = st.checkbox(
                        "🛠️ I have fixed this problem (recalculate score)",
                        key=cb_key,
                        value=st.session_state["mitigated_gaps"].get(i-1, False)
                    )
                    st.session_state["mitigated_gaps"][i-1] = is_mitigated_val
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
                
            if matching_findings == 0:
                st.info("No rules match the selected status and danger filters.")
                
        # 3. TAB: AI CHATBOT
        with tab_chat:
            st.markdown("### 💬 Ask the AI Assistant")
            st.caption("Ask questions about your results. You can ask: 'Draft a simple backup guide for our employees' or 'Explain why database passwords shouldn't be on a whiteboard'.")
            
            for msg in st.session_state["chat_history"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            if user_query := st.chat_input("e.g. 'Help me write a security rule for passwords'", key="auditor_chat_input"):
                with st.chat_message("user"):
                    st.markdown(user_query)
                st.session_state["chat_history"].append({"role": "user", "content": user_query})
                
                with st.chat_message("assistant"):
                    with st.spinner("AI Helper drafting response..."):
                        chat_prompt = f"""
                        You are a friendly Security Assessor and Assistant.
                        You have completed a safety check on this Document:
                        
                        DOCUMENT TEXT:
                        \"\"\"
                        {st.session_state.get("doc_text", "")}
                        \"\"\"
                        
                        CHECK RESULTS:
                        {json.dumps(report_data, indent=2)}
                        
                        Here is our conversation history:
                        {json.dumps(st.session_state["chat_history"][:-1], indent=2)}
                        
                        USER QUESTION:
                        {user_query}
                        
                        Write a very clear, encouraging, and helpful response in simple, non-technical plain English.
                        If they ask for guidelines or draft rules, write them clearly in standard markdown blocks so they can easily copy them.
                        """
                        try:
                            model = genai.GenerativeModel(model_choice)
                            response = model.generate_content(chat_prompt)
                            response_text = response.text
                            st.markdown(response_text)
                            st.session_state["chat_history"].append({"role": "assistant", "content": response_text})
                        except Exception as e:
                            st.error(f"Failed to generate response: {str(e)}")
                            
            if len(st.session_state["chat_history"]) > 0:
                st.markdown("---")
                if st.button("🗑️ Clear Chat Log"):
                    st.session_state["chat_history"] = []
                    st.rerun()
                
        # 4. TAB: RAW TEXT
        with tab_raw_docs:
            st.markdown("### 📄 View Document Text")
            st.info("This is the exact plain text extracted from your PDF that the AI read.")
            
            st.text_area(
                "Document Text",
                value=st.session_state.get("doc_text", ""),
                height=400,
                disabled=True
            )
            
        # 5. TAB: DOWNLOADS
        with tab_exports:
            st.markdown("### 📥 Download Reports")
            st.write("Download your safety results and checklist progress to view or open in Excel.")
            
            md_report = ComplianceReporter.generate_markdown_report(report_data, mitigated_dict)
            csv_data = ComplianceReporter.generate_csv_report(report_data, mitigated_dict)
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                st.markdown(
                    """
                    <div class='dashboard-card'>
                        <h4 style='margin-top:0; color: #3b82f6;'>📝 Written Summary Report</h4>
                        <p style='color: #94a3b8; font-size: 0.9rem;'>
                            A professionally structured written guide containing the scorecard, checklist updates, gaps found, and step-by-step fix guides.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.download_button(
                    label="📥 Download Written Report (.md)",
                    data=md_report,
                    file_name=f"Safety_Report_{st.session_state.get('doc_name', 'Policy')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
            with col_exp2:
                st.markdown(
                    """
                    <div class='dashboard-card'>
                        <h4 style='margin-top:0; color: #10b981;'>📊 Spreadsheet Excel Export</h4>
                        <p style='color: #94a3b8; font-size: 0.9rem;'>
                            A clean grid spreadsheet containing safety rules, status, danger level, gaps, and fix instructions. Perfect to open in Microsoft Excel or Google Sheets.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.download_button(
                    label="📥 Download Spreadsheet (.csv)",
                    data=csv_data,
                    file_name=f"Safety_Gaps_Spreadsheet_{st.session_state.get('doc_name', 'Policy')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            st.markdown("---")
            st.markdown("### ⚙️ Developer JSON Data Payload")
            with st.expander("View Raw Audit JSON Payload"):
                st.json(report_data)

    # ---------------------------------------------------------
    # WELCOME / FALLBACK DISPLAY STATE (Dashboard Mockup/Intro)
    # ---------------------------------------------------------
    else:
        st.markdown("---")
        st.markdown("### 🛠️ How to Get Started")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                """
                <div class='dashboard-card' style='height: 250px;'>
                    <h4 style='color:#10b981; margin-top:0;'>🔑 1. Setup API Key</h4>
                    <p style='color: #94a3b8; font-size: 0.92rem; line-height: 1.5;'>
                        Paste your <b>Google AI Studio API Key</b> in the left sidebar Settings panel. 
                        This keys the AI Engine so it can scan your documents.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown(
                """
                <div class='dashboard-card' style='height: 250px;'>
                    <h4 style='color:#3b82f6; margin-top:0;'>📂 2. Select Rules & File</h4>
                    <p style='color: #94a3b8; font-size: 0.92rem; line-height: 1.5;'>
                        Upload the PDF document you want to check (or click <b>"✨ Load Sample Document"</b> in the sidebar). Choose a rules checklist to check against.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                """
                <div class='dashboard-card' style='height: 250px;'>
                    <h4 style='color:#f59e0b; margin-top:0;'>⚡ 3. Start the Scan</h4>
                    <p style='color: #94a3b8; font-size: 0.92rem; line-height: 1.5;'>
                        Click the red <b>"🛡️ Start the Safety Scan"</b> button. The AI will inspect every clause, find missing rules, and show your safety score instantly!
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
