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
# මෙතන තියෙන "your_secret_password" වෙනුවට ඔයාගේ පාස්වර්ඩ් එක දාන්න!
# ----------------------------------------------------
ADMIN_PASSWORD = "your_secret_password" 

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
            
        with col2:
            maths_marks = st.number_input("ගණිතය ලකුණු:", min_value=0, max_value=100, value=0)
            health_marks = st.number_input("සෞඛ්‍යය ලකුණු:", min_value=0, max_value=100, value=0)
            sinhala_marks = st.number_input("සිංහල ලකුණු:", min_value=0, max_value=100, value=0)
            
        submitted = st.form_submit_button("දත්ත සුරකින්න (Save)")
        
        if submitted:
            if index_no and name:
                new_record = {
                    "index_no": index_no,
                    "name": name,
                    "grade": grade,
                    "maths": maths_marks,
                    "health": health_marks,
                    "sinhala": sinhala_marks,
                    "is_locked": False # Default unlocked
                }
                data.append(new_record)
                save_data(data)
                st.success(f"{name} ගේ දත්ත සාර්ථකව සුරකින ලදී!")
            else:
                st.error("කරුණාකර ඇතුළත් වීමේ අංකය සහ නම ඇතුළත් කරන්න.")

# ----------------------------------------------------
# TAB 2: DATA VIEW & LOCK SYSTEM
# ----------------------------------------------------
with tab2:
    st.header("ඇතුළත් කළ දත්ත නිරීක්ෂණය")
    
    if len(data) > 0:
        df = pd.DataFrame(data)
        
        # Display Columns mapping
        df_display = df.rename(columns={
            "index_no": "අංකය",
            "name": "නම",
            "grade": "ශ්‍රේණිය",
            "maths": "ගණිතය",
            "health": "සෞඛ්‍යය",
            "sinhala": "සිංහල",
            "is_locked": "Locked Status"
        })
        
        st.dataframe(df_display, use_container_width=True)
        
        st.divider()
        st.subheader("🔒 දත්ත Lock කිරීම (ගුරුවරුන් සඳහා)")
        st.info("දත්ත සියල්ල නිවැරදි නම්, අදාළ ශිෂ්‍යයාගේ දත්ත වෙනස් කළ නොහැකි ලෙස Lock කළ හැක.")
        
        unlocked_students = [item["name"] for item in data if not item.get("is_locked", False)]
        
        if unlocked_students:
            student_to_lock = st.selectbox("Lock කිරීමට ශිෂ්‍යයා තෝරන්න:", unlocked_students)
            if st.button("තෝරාගත් ශිෂ්‍යයාගේ දත්ත Lock කරන්න"):
                for item in data:
                    if item["name"] == student_to_lock:
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
        locked_students = [item["name"] for item in data if item.get("is_locked", False)]
        
        if locked_students:
            student_to_unlock = st.selectbox("Unlock කිරීමට ශිෂ්‍යයා තෝරන්න:", locked_students)
            if st.button("Unlock කරන්න"):
                for item in data:
                    if item["name"] == student_to_unlock:
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
