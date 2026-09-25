import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import google.generativeai as genai
from PIL import Image

# Page Setup
st.set_page_config(
    page_title="සිරි සුමන පිරිවෙන් ලකුණු පද්ධතිය",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Admin Password & API Configuration
ADMIN_PASSWORD = "sirisumana123"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=GEMINI_API_KEY)

# Permanent Data Files
DATA_FILE = "student_marks.json"
ROSTER_FILE = "student_roster.json"

# Helper Functions for Marks Data Persistence
def load_marks_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                if "Year" not in df.columns:
                    df["Year"] = "2026"
                return df
        except Exception:
            pass
    return pd.DataFrame(columns=["Student ID", "Grade", "Year", "Term", "Subject", "Marks", "Status"])

def save_marks_data(df):
    data = df.to_dict(orient="records")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Helper Functions for Roster Persistence
def load_roster_data():
    if os.path.exists(ROSTER_FILE):
        try:
            with open(ROSTER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_roster_data(roster):
    with open(ROSTER_FILE, "w", encoding="utf-8") as f:
        json.dump(roster, f, ensure_ascii=False, indent=4)

# Always load persistent data
st.session_state.student_data = load_marks_data()
st.session_state.roster_data = load_roster_data()

# Header
st.title("🏫 මහා/දෙනු/ ශ්‍රී සුමන ද්විභාෂා පිරිවෙන")
st.caption("ශිෂ්‍ය සාධන හා ලේඛන කළමනාකරණ පද්ධතිය - විභාග අංශය")
st.divider()

# Sidebar Authentication & UI Zoom Control
st.sidebar.title("🔑 පද්ධති ප්‍රවේශය (Login)")
role = st.sidebar.radio("ඔබගේ කාර්යභාරය තෝරන්න:", ["පන්තිභාර ගුරු (Teacher)", "විදුහල්පති/Admin (Principal)"])

admin_access = False
if role == "විදුහල්පති/Admin (Principal)":
    password = st.sidebar.text_input("Admin මුරපදය (Password):", type="password")
    if password == ADMIN_PASSWORD:
        admin_access = True
        st.sidebar.success("Admin විදියට සාර්ථකව Log වුණා!")
    elif password:
        st.sidebar.error("වැරදි මුරපදයකි!")

st.sidebar.divider()

# App UI Zoom Control Settings
st.sidebar.subheader("🔍 App Zoom & අකුරු ප්‍රමාණය")
zoom_level = st.sidebar.select_slider(
    "පද්ධතියේ Font Size එක තෝරන්න:",
    options=["සාමාන්‍ය (Normal)", "විශාල (Large)", "ඉතා විශාල (Extra Large)"],
    value="සාමාන්‍ය (Normal)"
)

if zoom_level == "විශාල (Large)":
    st.markdown("""
        <style>
            html, body, [class*="css"] { font-size: 18px !important; }
            input { font-size: 18px !important; height: 45px !important; }
            .stSelectbox, .stNumberInput { font-size: 18px !important; }
        </style>
    """, unsafe_allow_html=True)
elif zoom_level == "ඉතා විශාල (Extra Large)":
    st.markdown("""
        <style>
            html, body, [class*="css"] { font-size: 21px !important; }
            input { font-size: 21px !important; height: 50px !important; }
            .stSelectbox, .stNumberInput { font-size: 21px !important; }
        </style>
    """, unsafe_allow_html=True)

# TAB NAVIGATION
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 ශිෂ්‍ය නාම ලේඛනය",
    "📝 ලකුණු ඇතුළත් කිරීම", 
    "📄 විෂයානුබද්ධ විශ්ලේෂණය (නිල වාර්තාව)", 
    "👤 ශිෂ්‍යානුබද්ධ විශ්ලේෂණය", 
    "🏫 සමස්ත පන්ති විශ්ලේෂණය", 
    "⚙️ දත්ත පාලනය"
])

# Grade List including Foundation Grade & English Medium
GRADES = [
    "මූලික ශ්‍රේණිය", "1 ශ්‍රේණිය", "2 ශ්‍රේණිය", "3 ශ්‍රේණිය", "4 ශ්‍රේණිය", "5 ශ්‍රේණිය",
    "English Medium 1", "English Medium 2", "English Medium 3", "English Medium 4", "English Medium 5"
]

# Years List
YEARS = ["2025", "2026", "2027", "2028", "2029", "2030"]

# List of all 10 subjects
SUBJECTS = [
    "ත්‍රිපිටක ධර්මය (Tripitaka)",
    "සිංහල (Sinhala)",
    "පාලි (Pali)",
    "සංස්ක්‍රත (Sanskrit)",
    "ගණිතය (Maths)",
    "ඉංග්‍රීසි (English)",
    "ඉතිහාසය (History)",
    "සමාජ විද්‍යාව (Social Sci.)",
    "සෞඛ්‍ය විද්‍යාව (Health Sci.)",
    "භූගෝල විද්‍යාව (Geog. Phy.)"
]

# Helper Function for Grading
def get_grade(marks):
    if marks >= 75: return "A"
    elif marks >= 65: return "B"
    elif marks >= 50: return "C"
    elif marks >= 35: return "S"
    else: return "F"

# ----------------------------------------------------
# TAB 0: STUDENT ROSTER MANAGEMENT
# ----------------------------------------------------
with tab0:
    st.header("📋 පන්ති අනුව ශිෂ්‍ය නාම ලේඛනය ලියාපදිංචිය")
    st.info("මෙහි පන්තියට අදාළ ශිෂ්‍ය විභාග අංක ලියාපදිංචි කර තැබිය හැක.")
    
    col_r_meta1, col_r_meta2 = st.columns(2)
    with col_r_meta1:
        r_grade = st.selectbox("ශ්‍රේණිය / පන්තිය තෝරන්න:", GRADES, key="r_grade")
    with col_r_meta2:
        r_year = st.selectbox("වර්ෂය තෝරන්න:", YEARS, index=1, key="r_year")
    
    reg_id = st.text_input("ඇතුළත් වීමේ අංකය / විභාග අංකය (උදා: 3000):")
        
    if st.button("➕ ශිෂ්‍ය අංකය පන්තියට Save කරන්න", type="primary"):
        if reg_id:
            if r_grade not in st.session_state.roster_data:
                st.session_state.roster_data[r_grade] = []
            if reg_id not in st.session_state.roster_data[r_grade]:
                st.session_state.roster_data[r_grade].append(reg_id)
                save_roster_data(st.session_state.roster_data)
                st.success(f"විභාග අංක {reg_id} ශිෂ්‍යයා {r_grade} පන්තියට සාර්ථකව සේව් විය!")
                st.rerun()
            else:
                st.warning("මෙම විභාග අංකය දැනටමත් ඇතුළත් කර ඇත.")
        else:
            st.warning("කරුණාකර විභාග අංකය ඇතුළත් කරන්න.")
            
    st.divider()
    st.subheader(f"📌 {r_grade} දැනට ලියාපදිංචි සිසුන්ගේ අංක")
    if r_grade in st.session_state.roster_data and st.session_state.roster_data[r_grade]:
        roster_df = pd.DataFrame(st.session_state.roster_data[r_grade], columns=["විභාග අංකය"])
        st.dataframe(roster_df, use_container_width=True)
    else:
        st.write("මෙම පන්තියට තවමත් සිසුන් ලියාපදිංචි කර නැත.")

# ----------------------------------------------------
# TAB 1: DATA ENTRY (MANUAL / PHOTO / PDF)
# ----------------------------------------------------
with tab1:
    st.header("ශිෂ්‍ය ලකුණු ඇතුළත් කිරීම")
    
    entry_method = st.radio(
        "ඇතුළත් කිරීමේ ක්‍රමය තෝරන්න:", 
        [
            "📸 Photo එකක් upload කර Scan කිරීම (AI Scan)", 
            "📄 PDF File එකක් upload කර Scan කිරීම (PDF Scan)",
            "✍️ අතින් එකින් එක ටයිප් කිරීම (Manual Entry)"
        ], 
        horizontal=True
    )
    st.divider()

    # METHOD 1: PHOTO AI SCAN
    if "Photo" in entry_method:
        st.subheader("📸 ඡායාරූපයක් (Photo Image) මඟින් ලකුණු ලබා ගැනීම")
        uploaded_img = st.file_uploader("ලකුණු පත්‍රිකාවේ Image එක Upload කරන්න (JPG/PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_img:
            img = Image.open(uploaded_img)
            with st.expander("🔍 ඡායාරූපය Zoom කර බලන්න", expanded=True):
                img_width = st.slider("Zoom Level:", min_value=300, max_value=1500, value=700, step=50, key="img_zoom")
                st.image(img, caption="Upload කරන ලද Image එක", width=img_width)

        col_scan1, col_scan2, col_scan3 = st.columns(3)
        with col_scan1:
            scan_grade = st.selectbox("ශ්‍රේණිය / පන්තිය:", GRADES, key="img_scan_grade")
        with col_scan2:
            scan_year = st.selectbox("වර්ෂය:", YEARS, index=1, key="img_scan_year")
        with col_scan3:
            scan_term = st.selectbox("වාරය:", ["1 වන වාරය", "2 වන වාරය", "3 වන වාරය"], key="img_scan_term")

        if uploaded_img and st.button("🔍 Photo එක Scan කර දත්ත ලබා ගන්න", type="primary", key="btn_img_scan"):
            if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
                st.error("කරුණාකර API Key එක සකසන්න.")
            else:
                try:
                    with st.spinner("AI මඟින් Photo එක පරීක්ෂා කරමින් පවතී..."):
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt_text = (
                            "Extract student marks into a JSON list. "
                            "Format: [{\"Student ID\": \"3017\", \"Marks\": {\"ත්‍රිපිටක ධර්මය (Tripitaka)\": 48, \"සිංහල (Sinhala)\": 62, \"පාලි (Pali)\": 60, \"සංස්ක්‍රත (Sanskrit)\": 55, \"ගණිතය (Maths)\": 59, \"ඉංග්‍රීසි (English)\": 31, \"ඉතිහාසය (History)\": 0, \"සමාජ විද්‍යාව (Social Sci.)\": 0, \"සෞඛ්‍ය විද්‍යාව (Health Sci.)\": 0, \"භූගෝල විද්‍යාව (Geog. Phy.)\": 0}}] "
                            "Return only pure JSON without markdown blocks."
                        )
                        response = model.generate_content([img, prompt_text])
                        raw_json = response.text.strip().replace("```json", "").replace("```", "").strip()
                        extracted_students = json.loads(raw_json)
                        
                        new_rows = []
                        for st_data in extracted_students:
                            s_id = str(st_data.get("Student ID", ""))
                            s_marks = st_data.get("Marks", {})
                            for sub, mark in s_marks.items():
                                if sub in SUBJECTS:
                                    new_rows.append({
                                        "Student ID": s_id, "Grade": scan_grade, "Year": scan_year,
                                        "Term": scan_term, "Subject": sub,
                                        "Marks": int(mark) if str(mark).isdigit() else 0, "Status": "Locked"
                                    })
                        if new_rows:
                            extracted_df = pd.DataFrame(new_rows)
                            st.session_state.student_data = pd.concat([st.session_state.student_data, extracted_df], ignore_index=True)
                            save_marks_data(st.session_state.student_data)
                            st.success("✅ Photo එකෙන් දත්ත සාර්ථකව ඇතුළත් කරගන්නා ලදී!")
                            st.dataframe(extracted_df, use_container_width=True)
                except Exception as e:
                    st.error(f"දෝෂයක් සිදු විය: {str(e)}")

    # METHOD 2: PDF AI SCAN
    elif "PDF" in entry_method:
        st.subheader("📄 PDF File එකක් මඟින් ලකුණු ලබා ගැනීම")
        uploaded_pdf = st.file_uploader("ලකුණු පත්‍රිකාවේ PDF File එක Upload කරන්න", type=["pdf"])

        col_pdf1, col_pdf2, col_pdf3 = st.columns(3)
        with col_pdf1:
            pdf_grade = st.selectbox("ශ්‍රේණිය / පන්තිය:", GRADES, key="pdf_scan_grade")
        with col_pdf2:
            pdf_year = st.selectbox("වර්ෂය:", YEARS, index=1, key="pdf_scan_year")
        with col_pdf3:
            pdf_term = st.selectbox("වාරය:", ["1 වන වාරය", "2 වන වාරය", "3 වන වාරය"], key="pdf_scan_term")

        if uploaded_pdf and st.button("📄 PDF එක Scan කර දත්ත ලබා ගන්න", type="primary", key="btn_pdf_scan"):
            if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
                st.error("කරුණාකර API Key එක සකසන්න.")
            else:
                try:
                    with st.spinner("AI මඟින් PDF එක පරීක්ෂා කරමින් පවතී..."):
                        temp_pdf_path = "temp_uploaded.pdf"
                        with open(temp_pdf_path, "wb") as f:
                            f.write(uploaded_pdf.getbuffer())
                        
                        pdf_file_ref = genai.upload_file(temp_pdf_path, mime_type="application/pdf")
                        
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        prompt_text = (
                            "Extract student marks into a JSON list from this PDF. "
                            "Format: [{\"Student ID\": \"3017\", \"Marks\": {\"ත්‍රිපිටක ධර්මය (Tripitaka)\": 48, \"සිංහල (Sinhala)\": 62, \"පාලි (Pali)\": 60, \"සංස්ක්‍රත (Sanskrit)\": 55, \"ගණිතය (Maths)\": 59, \"ඉංග්‍රීසි (English)\": 31, \"ඉතිහාසය (History)\": 0, \"සමාජ විද්‍යාව (Social Sci.)\": 0, \"සෞඛ්‍ය විද්‍යාව (Health Sci.)\": 0, \"භූගෝල විද්‍යාව (Geog. Phy.)\": 0}}] "
                            "Return only pure JSON without markdown blocks."
                        )
                        
                        response = model.generate_content([pdf_file_ref, prompt_text])
                        
                        if os.path.exists(temp_pdf_path):
                            os.remove(temp_pdf_path)

                        raw_json = response.text.strip().replace("```json", "").replace("
