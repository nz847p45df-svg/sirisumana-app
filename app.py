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
st.caption("ශිෂ්‍ය සාධන හා ලේඛන කළමනාකරණ පද්ධතිය - විභාග අංශය")
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 ලකුණු ඇතුළත් කිරීම", 
    "📄 විෂයානුබද්ධ විශ්ලේෂණය (නිල වාර්තාව)", 
    "👤 ශිෂ්‍යානුබද්ධ විශ්ලේෂණය", 
    "🏫 සමස්ත පන්ති විශ්ලේෂණය", 
    "⚙️ දත්ත පාලනය"
])

# Grade List including English Medium
GRADES = [
    "1 ශ්‍රේණිය", "2 ශ්‍රේණිය", "3 ශ්‍රේණිය", "4 ශ්‍රේණිය", "5 ශ්‍රේණිය",
    "English Medium 1", "English Medium 2", "English Medium 3", "English Medium 4", "English Medium 5"
]

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
# TAB 1: DATA ENTRY & LOCKING
# ----------------------------------------------------
with tab1:
    st.header("ශිෂ්‍ය ලකුණු ඇතුළත් කිරීම")
    
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("ශ්‍රේණිය / පන්තිය තෝරන්න:", GRADES)
        term = st.selectbox("වාරය තෝරන්න:", ["1 වන වාරය", "2 වන වාරය", "3 වන වාරය"])
        student_id = st.text_input("ඇතුළත් වීමේ අංකය / විභාග අංකය (Index No):")
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
# TAB 2: SUBJECT-WISE OFFICIAL PRINT FORM
# ----------------------------------------------------
with tab2:
    st.header("📄 මූලික පිරිවෙණ මධ්‍යවාර පරීක්ෂණය - ප්‍රතිඵල විශ්ලේෂණ වාර්තාව")
    
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    with col_sel1:
        sel_grade = st.selectbox("ශ්‍රේණිය තෝරන්න:", GRADES, key="sub_grade")
    with col_sel2:
        sel_term = st.selectbox("වාරය තෝරන්න:", ["1 වන වාරය", "2 වන වාරය", "3 වන වාරය"], key="sub_term")
    with col_sel3:
        sel_subject = st.selectbox("විෂය තෝරන්න:", SUBJECTS, key="sub_subject")

    st.divider()

    # Filter Data
    sub_df = st.session_state.student_data[
        (st.session_state.student_data["Grade"] == sel_grade) &
        (st.session_state.student_data["Term"] == sel_term) &
        (st.session_state.student_data["Subject"] == sel_subject)
    ].copy()

    if sub_df.empty:
        st.info("තෝරාගත් පන්තිය, වාරය සහ විෂය සඳහා කිසිදු දත්තයක් ඇතුළත් කර නොමැත.")
    else:
        # Construct Official Printable Header
        st.markdown(f"""
        <div style="text-align: center; border: 2px solid #000; padding: 15px; background-color: #fcfcfc; font-family: 'Sinhala', sans-serif;">
            <h2 style="margin:0;">මහ/දෙනු/ සිරිසුමන ද්විභාෂා මූලික පිරිවෙණ</h2>
            <h3 style="margin:5px;">විභාග අංශය</h3>
            <p style="margin:0; font-weight:bold;">මූලික පිරිවෙණ් මධ්‍යවාර පරීක්ෂණය - ප්‍රතිඵල විශ්ලේෂණ වාර්තාව ({sel_term})</p>
            <div style="display: flex; justify-content: space-between; margin-top: 15px; font-weight: bold;">
                <span>ශ්‍රේණිය :- {sel_grade}</span>
                <span>විෂය :- {sel_subject}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        
        # Calculate Grading & Progress
        sub_df["සාමාර්ථය"] = sub_df["Marks"].apply(get_grade)
        sub_df["සාධන මට්ටම"] = sub_df["Marks"].apply(lambda x: f"{x}%")
        sub_df["ප්‍රගති මැනීම"] = sub_df["Marks"].apply(lambda x: "යහපත්" if x>=65 else ("මධ්‍යම" if x>=35 else "දුර්වල"))
        sub_df["විශ්ලේෂණයන්"] = sub_df["Marks"].apply(lambda x: "ලකුණු මට්ටම උසස් කරගත යුතුය" if x<50 else "සාධනීය මට්ටමක පවතී")

        # Table Display
        display_sub_df = sub_df.reset_index(drop=True)
        display_sub_df.index += 1
        display_sub_df = display_sub_df.reset_index().rename(columns={"index": "අනු අංකය", "Student ID": "විභාග අංකය"})
        
        show_table = display_sub_df[["අනු අංකය", "විභාග අංකය", "Name", "Marks", "සාධන මට්ටම", "සාමාර්ථය", "ප්‍රගති මැනීම", "විශ්ලේෂණයන්"]]
        st.dataframe(show_table, use_container_width=True)

        st.divider()

        # Marks Range Distribution Table (Matching Official Form)
        col_dist1, col_dist2 = st.columns([1, 1])
        
        with col_dist1:
            st.subheader("📊 ලකුණු පරාස අනුව සාධන මට්ටමට ළඟාවීම")
            ranges = [
                ("01-30", len(sub_df[(sub_df["Marks"] >= 1) & (sub_df["Marks"] <= 30)])),
                ("30-40", len(sub_df[(sub_df["Marks"] > 30) & (sub_df["Marks"] <= 40)])),
                ("40-50", len(sub_df[(sub_df["Marks"] > 40) & (sub_df["Marks"] <= 50)])),
                ("50-60", len(sub_df[(sub_df["Marks"] > 50) & (sub_df["Marks"] <= 60)])),
                ("60-70", len(sub_df[(sub_df["Marks"] > 60) & (sub_df["Marks"] <= 70)])),
                ("70-80", len(sub_df[(sub_df["Marks"] > 70) & (sub_df["Marks"] <= 80)])),
                ("80-90", len(sub_df[(sub_df["Marks"] > 80) & (sub_df["Marks"] <= 90)])),
                ("90-100", len(sub_df[(sub_df["Marks"] > 90) & (sub_df["Marks"] <= 100)]))
            ]
            dist_df = pd.DataFrame(ranges, columns=["ලකුණු පරාසය", "සාධන මට්ටමට ළඟාවීම (සිසුන් ගණන)"])
            st.table(dist_df)

        with col_dist2:
            st.subheader("📝 ප්‍රතිඵල සමාලෝචනය පිළිබඳ පොදු විශ්ලේෂණ සටහන")
            st.text_area("විෂයභාර ගුරුභවතාගේ නිගමන හා සටහන්:", value="මෙම වාරයේ පන්තියේ සමස්ත සාධන මට්ටම යහපත් තත්වයක පවතී. අඩු ලකුණු ලබාගත් සිසුන් සඳහා විශේෂ වැඩසටහන් ක්‍රියාත්මක කළ යුතුය.", height=200)

        # Official Signatures Section
        st.markdown("""
        <br><br>
        <div style="display: flex; justify-content: space-between; text-align: center; font-weight: bold;">
            <div>...............................................<br>(විෂයභාර ගුරුභවතා)</div>
            <div>...............................................<br>(අංශ ප්‍රධාන ගුරුභවතා)</div>
            <div>...............................................<br>(පරිවේණාධිපති හිමි)</div>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------
# TAB 3: STUDENT-WISE DEEP ANALYSIS
# ----------------------------------------------------
with tab3:
    st.header("👤 ශිෂ්‍යානුබද්ධ ප්‍රගති විශ්ලේෂණය")
    if st.session_state.student_data.empty:
        st.info("විශ්ලේෂණය සඳහා කිසිදු දත්තයක් ඇතුළත් කර නොමැත.")
    else:
        student_list = st.session_state.student_data["Student ID"].unique()
        selected_student = st.selectbox("විශ්ලේෂණය සඳහා ශිෂ්‍ය අංකය තෝරන්න:", student_list, key="st_select")
        
        student_df = st.session_state.student_data[st.session_state.student_data["Student ID"] == selected_student]
        s_name = student_df["Name"].iloc[0]
        s_grade = student_df["Grade"].iloc[0]
        
        st.subheader(f"ශිෂ්‍යයා: {s_name} | විභාග අංකය: {selected_student} | ශ්‍රේණිය: {s_grade}")
        
        # Plotly Comparison Chart
        fig = px.bar(student_df, x="Subject", y="Marks", color="Term", barmode="group",
                     title="වාර 3 හි විෂයයන් 10 ලකුණු සංසන්දනය", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary Pivot Table
        pivot_df = student_df.pivot(index="Subject", columns="Term", values="Marks").fillna(0)
        st.write("### වාර 3 හි විෂයයන් අනුව ලකුණු සාරාංශය")
        st.dataframe(pivot_df, use_container_width=True)

# ----------------------------------------------------
# TAB 4: CLASS OVERALL ANALYSIS
# ----------------------------------------------------
with tab4:
    st.header("🏫 සමස්ත පන්ති සාධන විශ්ලේෂණය")
    if st.session_state.student_data.empty:
        st.info("විශ්ලේෂණය සඳහා කිසිදු දත්තයක් ඇතුළත් කර නොමැත.")
    else:
        c_grade = st.selectbox("නිරීක්ෂණයට ශ්‍රේණිය තෝරන්න:", GRADES, key="cl_grade")
        c_term = st.selectbox("නිරීක්ෂණයට වාරය තෝරන්න:", ["1 වන වාරය", "2 වන වාරය", "3 වන වාරය"], key="cl_term")
        
        class_df = st.session_state.student_data[
            (st.session_state.student_data["Grade"] == c_grade) &
            (st.session_state.student_data["Term"] == c_term)
        ]
        
        if class_df.empty:
            st.warning("මෙම පන්තිය සහ වාරය සඳහා දත්ත නොමැත.")
        else:
            fig_class = px.box(class_df, x="Subject", y="Marks", points="all", title=f"{c_grade} - {c_term} විෂයයන් අනුව ලකුණු ව්‍යාප්තිය")
            st.plotly_chart(fig_class, use_container_width=True)

# ----------------------------------------------------
# TAB 5: DATA MANAGEMENT & CLEAR BUTTON
# ----------------------------------------------------
with tab5:
    st.header("⚙️ දත්ත පාලන මධ්‍යස්ථානය")
    st.dataframe(st.session_state.student_data, use_container_width=True)
    
    st.divider()
    st.subheader("🧹 දත්ත ඉවත් කිරීම (Reset Data)")
    
    col_del1, col_del2 = st.columns(2)
    with col_del1:
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
