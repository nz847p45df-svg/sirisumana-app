import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(
    page_title="සිරි සුමන පිරිවෙන් ලකුණු පද්ධතිය",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Admin Password
ADMIN_PASSWORD = "sirisumana123"

# Session State Initialization
if "student_data" not in st.session_state:
    st.session_state.student_data = pd.DataFrame(columns=[
        "Student ID", "Name", "Grade", "Term", "Subject", "Marks", "Status"
    ])

# Header
st.title("🏫 මහා/දෙනු/ ශ්‍රී සුමන ද්විභාෂා ප්‍රාථමික පිරිවෙන")
st.caption("ශිෂ්‍ය සාධන හා ලේඛන කළමනාකරණ පද්ධතිය")
st.divider()

# Sidebar Authentication
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

# TAB NAVIGATION
tab1, tab2, tab3 = st.tabs(["📝 ලකුණු ඇතුළත් කිරීම", "📊 වාර විශ්ලේෂණය", "⚙️ දත්ත පාලනය (Manage Data)"])

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
# TAB 1: DATA ENTRY & LOCKING
# ----------------------------------------------------
with tab1:
    st.header("ශිෂ්‍ය ලකුණු ඇතුළත් කිරීම")
    
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("ශ්‍රේණිය:", ["1 ශ්‍රේණිය", "2 ශ්‍රේණිය", "3 ශ්‍රේණිය", "4 ශ්‍රේණිය", "5 ශ්‍රේණිය"])
        term = st.selectbox("වාරය:", ["1 වන වාරය", "2 වන වාරය", "3 වන වාරය"])
        student_id = st.text_input("ඇතුළත් වීමේ අංකය (Index No):")
        student_name = st.text_input("ශිෂ්‍යයාගේ නම:")

    with col2:
        st.subheader("විෂයයන් 10 සහ ලකුණු")
        marks_dict = {}
        for sub in SUBJECTS:
            marks_dict[sub] = st.number_input(f"{sub} ලකුණු:", min_value=0, max_value=100, value=0, step=1)

    # Checking if data for this student/term is already locked
    is_locked = False
    if not st.session_state.student_data.empty:
        check_df = st.session_state.student_data[
            (st.session_state.student_data["Student ID"] == student_id) & 
            (st.session_state.student_data["Term"] == term) &
            (st.session_state.student_data["Status"] == "Locked")
        ]
        if not check_df.empty:
            is_locked = True

    st.divider()

    if is_locked and not admin_access:
        st.error("⛔ මෙම ශිෂ්‍යයාගේ මෙම වාරයේ ලකුණු දැනටමත් Lock කර ඇත. වෙනස් කිරීමට Admin අමතන්න.")
    else:
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("💾 තාවකාලිකව සුරකින්න (Save Draft)", use_container_width=True):
                if student_id and student_name:
                    st.session_state.student_data = st.session_state.student_data[
                        ~((st.session_state.student_data["Student ID"] == student_id) & 
                          (st.session_state.student_data["Term"] == term))
                    ]
                    new_rows = []
                    for sub, mark in marks_dict.items():
                        new_rows.append({
                            "Student ID": student_id, "Name": student_name,
                            "Grade": grade, "Term": term, "Subject": sub,
                            "Marks": mark, "Status": "Draft"
                        })
                    st.session_state.student_data = pd.concat([st.session_state.student_data, pd.DataFrame(new_rows)], ignore_index=True)
                    st.success("ලකුණු තාවකාලිකව සුරකින ලදී (Draft Mode)!")
                else:
                    st.warning("කරුණාකර ශිෂ්‍ය අංකය සහ නම ඇතුළත් කරන්න.")

        with btn_col2:
            if st.button("🔒 සම්පූර්ණයෙන් යවා Lock කරන්න (Final Submit)", type="primary", use_container_width=True):
                if student_id and student_name:
                    st.session_state.student_data = st.session_state.student_data[
                        ~((st.session_state.student_data["Student ID"] == student_id) & 
                          (st.session_state.student_data["Term"] == term))
                    ]
                    new_rows = []
                    for sub, mark in marks_dict.items():
                        new_rows.append({
                            "Student ID": student_id, "Name": student_name,
                            "Grade": grade, "Term": term, "Subject": sub,
                            "Marks": mark, "Status": "Locked"
                        })
                    st.session_state.student_data = pd.concat([st.session_state.student_data, pd.DataFrame(new_rows)], ignore_index=True)
                    st.success("ලකුණු සාර්ථකව පද්ධතියට එක් කර Lock කරන ලදී!")
                else:
                    st.warning("කරුණාකර ශිෂ්‍ය අංකය සහ නම ඇතුළත් කරන්න.")

# ----------------------------------------------------
# TAB 2: ANALYSIS & REPORTS
# ----------------------------------------------------
with tab2:
    st.header("📊 ශිෂ්‍ය වාර ප්‍රගති විශ්ලේෂණය")
    if st.session_state.student_data.empty:
        st.info("විශ්ලේෂණය සඳහා කිසිදු දත්තයක් ඇතුළත් කර නොමැත.")
    else:
        student_list = st.session_state.student_data["Student ID"].unique()
        selected_student = st.selectbox("විශ්ලේෂණය සඳහා ශිෂ්‍ය අංකය තෝරන්න:", student_list)
        
        student_df = st.session_state.student_data[st.session_state.student_data["Student ID"] == selected_student]
        s_name = student_df["Name"].iloc[0]
        st.subheader(f"ශිෂ්‍යයා: {s_name} ({selected_student})")
        
        # Plotly Comparison Chart
        fig = px.bar(student_df, x="Subject", y="Marks", color="Term", barmode="group",
                     title="වාර 3 හි විෂයයන් අනුව ලකුණු සංසන්දනය", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary Table
        pivot_df = student_df.pivot(index="Subject", columns="Term", values="Marks").fillna(0)
        st.write("### වාර ලකුණු සාරාංශය")
        st.dataframe(pivot_df, use_container_width=True)
        
        # Report Download
        csv = student_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 මෙම වාර්තාව Download කරගන්න (CSV Report)", data=csv, file_name=f"{selected_student}_report.csv", mime="text/csv")

# ----------------------------------------------------
# TAB 3: DATA MANAGEMENT & CLEAR BUTTON
# ----------------------------------------------------
with tab3:
    st.header("⚙️ දත්ත පාලන මධ්‍යස්ථානය")
    st.dataframe(st.session_state.student_data, use_container_width=True)
    
    st.divider()
    st.subheader("🧹 දත්ත ඉවත් කිරීම (Reset Data)")
    
    col_del1, col_del2 = st.columns(2)
    with col_del1:
        # Clear Data Button
        if st.button("🗑️ පරීක්ෂණ දත්ත සියල්ල ඉවත් කරන්න (Clear All Data)", type="secondary", use_container_width=True):
            st.session_state.student_data = pd.DataFrame(columns=[
                "Student ID", "Name", "Grade", "Term", "Subject", "Marks", "Status"
            ])
            st.success("සියලු දත්ත සාර්ථකව පද්ධතියෙන් ඉවත් කරන ලදී!")
            st.rerun()

    with col_del2:
        if admin_access:
            if st.button("🔓 සියලුම Locked Data Unlock කරන්න (Admin Only)", use_container_width=True):
                st.session_state.student_data["Status"] = "Draft"
                st.success("සියලුම දත්ත Unlock කරන ලදී!")
                st.rerun()
