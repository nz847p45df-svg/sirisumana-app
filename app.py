import streamlit as st
import pandas as pd
import json
import os

# Page Config
st.set_page_config(page_title="ශ්‍රී සුමන ප්‍රාථමික පිරිවෙන - ලේඛන පද්ධතිය", layout="wide")

# File Path
DATA_FILE = "student_data.json"

# Helper Functions to Load and Save Data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Load existing data
data = load_data()

# ----------------------------------------------------
# 🔑 ADMIN PASSWORD SETTING
# ----------------------------------------------------
ADMIN_PASSWORD = "sirisumana123" 

# Header
st.title("🏫 මහා/දෙනු/ ශ්‍රී සුමන ද්විභාෂා ප්‍රාථමික පිරිවෙන")
st.subheader("ශිෂ්‍ය සාධන හා ලේඛන කළමනාකරණ පද්ධතිය")

# Sidebar - Role Selection
st.sidebar.header("🔑 පද්ධති ප්‍රවේශය (Login)")
role = st.sidebar.radio("ඔබගේ කාර්යභාරය තෝරන්න:", ["ගුරුභවතා (Teacher)", "විදුහල්පති/Admin (Principal)"])

is_admin = False

if role == "විදුහල්පති/Admin (Principal)":
    entered_password = st.sidebar.text_input("Admin මුරපදය (Password):", type="password")
    if entered_password == ADMIN_PASSWORD:
        is_admin = True
        st.sidebar.success("Admin විදියට සාර්ථකව Log වුණා!")
    elif entered_password != "":
        st.sidebar.error("මුරපදය වැරදියි!")

# Tab Layout
tab1, tab2, tab3 = st.tabs(["📝 දත්ත ඇතුළත් කිරීම", "📊 දත්ත නිරීක්ෂණය / සංස්කරණය", "⚙️ Admin පාලක පුවරුව"])

# List of all 10 subjects
SUBJECTS = [
    "ත්‍රිපිටක ධර්මය (Tripitaka)",
    "සිංහල (Sinhala)",
    "පාලි (Pali)",
    "සංස්കൃත (Sanskrit)",
    "ගණිතය (Maths)",
    "ඉංග්‍රීසි (English)",
    "ඉතිහාසය (History)",
    "සමාජ විද්‍යාව (Social Sci.)",
    "සෞඛ්‍ය විද්‍යාව (Health Sci.)",
    "භූගෝල විද්‍යාව (Geog. Phy.)"
]

# ----------------------------------------------------
# TAB 1: DATA ENTRY
# ----------------------------------------------------
with tab1:
    st.header("නව ශිෂ්‍ය දත්ත ඇතුළත් කිරීම")
    
    with st.form("student_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            index_no = st.text_input("ඇතුළත් වීමේ අංකය / විභාග අංකය:")
            name = st.text_input("ශිෂ්‍යයාගේ නම:")
            grade = st.selectbox("ශ්‍රේණිය:", ["1 ශ්‍රේණිය", "2 ශ්‍රේණිය", "3 ශ්‍රේණිය", "4 ශ්‍රේණිය", "5 ශ්‍රේණිය"])
            term = st.selectbox("වාරය:", ["1 වන වාරය", "2 වන වාරය", "3 වන වාරය"])
            
        with col2:
            st.subheader("විෂයයන් 10 සහ ලකුණු")
            marks_dict = {}
            for sub in SUBJECTS:
                marks_dict[sub] = st.number_input(f"{sub}:", min_value=0, max_value=100, value=0, step=1)
            
        submitted = st.form_submit_button("දත්ත සුරකින්න (Save)")
        
        if submitted:
            if index_no and name:
                new_record = {
                    "index_no": index_no,
                    "name": name,
                    "grade": grade,
                    "term": term,
                    "marks": marks_dict,
                    "is_locked": False # Default unlocked
                }
                data.append(new_record)
                save_data(data)
                st.success(f"{name} ගේ {term} ලකුණු සාර්ථකව සුරකින ලදී!")
            else:
                st.error("කරුණාකර ඇතුළත් වීමේ අංකය සහ නම ඇතුළත් කරන්න.")

# ----------------------------------------------------
# TAB 2: DATA VIEW & LOCK SYSTEM
# ----------------------------------------------------
with tab2:
    st.header("ඇතුළත් කළ දත්ත නිරීක්ෂණය")
    
    if len(data) > 0:
        flattened_data = []
        for item in data:
            row = {
                "අංකය": item["index_no"],
                "නම": item["name"],
                "ශ්‍රේණිය": item["grade"],
                "වාරය": item.get("term", "-"),
                "Locked Status": "🔒 Locked" if item.get("is_locked", False) else "🔓 Unlocked"
            }
            # Add subject marks
            if "marks" in item:
                for sub_name, mark in item["marks"].items():
                    row[sub_name] = mark
            flattened_data.append(row)

        df_display = pd.DataFrame(flattened_data)
        st.dataframe(df_display, use_container_width=True)
        
        st.divider()
        st.subheader("🔒 දත්ත Lock කිරීම (ගුරුවරුන් සඳහා)")
        st.info("දත්ත සියල්ල නිවැරදි නම්, අදාළ ශිෂ්‍යයාගේ දත්ත වෙනස් කළ නොහැකි ලෙස Lock කළ හැක.")
        
        unlocked_students = [f"{item['name']} ({item.get('term', '')})" for item in data if not item.get("is_locked", False)]
        
        if unlocked_students:
            student_to_lock = st.selectbox("Lock කිරීමට ශිෂ්‍යයා තෝරන්න:", unlocked_students)
            if st.button("තෝරාගත් ශිෂ්‍යයාගේ දත්ත Lock කරන්න"):
                for item in data:
                    if f"{item['name']} ({item.get('term', '')})" == student_to_lock:
                        item["is_locked"] = True
                        break
                save_data(data)
                st.success(f"{student_to_lock} ගේ දත්ත සාර්ථකව Lock කරන ලදී!")
                st.rerun()
        else:
            st.write("සියලුම ශිෂ්‍යයින්ගේ දත්ත දැනටමත් Lock කර ඇත.")
            
    else:
        st.warning("තවමත් කිසිදු දත්තයක් ඇතුළත් කර නොමැත.")

# ----------------------------------------------------
# TAB 3: ADMIN CONTROLS (UNLOCK & CLEAR ALL)
# ----------------------------------------------------
with tab3:
    st.header("⚙️ Admin පාලන කොටස")
    
    if is_admin:
        st.success("ඔබ Admin ලෙස ප්‍රවේශ වී ඇත. පහත විශේෂ බලතල භාවිතා කළ හැක.")
        
        # Feature 1: Unlock Data
        st.subheader("🔓 Lock කළ දත්ත නැවත Unlock කිරීම")
        locked_students = [f"{item['name']} ({item.get('term', '')})" for item in data if item.get("is_locked", False)]
        
        if locked_students:
            student_to_unlock = st.selectbox("Unlock කිරීමට ශිෂ්‍යයා තෝරන්න:", locked_students)
            if st.button("Unlock කරන්න"):
                for item in data:
                    if f"{item['name']} ({item.get('term', '')})" == student_to_unlock:
                        item["is_locked"] = False
                        break
                save_data(data)
                st.success(f"{student_to_unlock} ගේ දත්ත නැවත Unlock කරන ලදී!")
                st.rerun()
        else:
            st.info("දැනට Lock කළ දත්ත කිසිවක් නැත.")
            
        st.divider()
        
        # Feature 2: Clear All Testing Data
        st.subheader("🗑️ පරීක්ෂණ දත්ත සම්පූර්ණයෙන්ම ඉවත් කිරීම (Reset System)")
        st.warning("අවධානයයි: මෙය මගින් පද්ධතියේ ඇති සියලුම ටෙස්ට් දත්ත මකා දැමෙනු ඇත!")
        
        if st.button("සියලුම දත්ත මකා දමන්න (Clear All Data)"):
            save_data([])
            st.success("සියලුම දත්ත සාර්ථකව මකා දැමීය!")
            st.rerun()
            
    else:
        st.error("මෙම කොටස භාවිතා කිරීමට Admin මුරපදය (Password) ඇතුළත් කර Log වෙන්න.")
