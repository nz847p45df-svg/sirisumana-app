import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="සිරි සුමන පිරිවෙන් ලකුණු පද්ධතිය",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #8B0000;
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #444;
        font-size: 15px;
        margin-bottom: 15px;
    }
    .stButton>button {
        width: 100%;
        background-color: #8B0000;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 45px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>මහ/දෙනු/සිරිසුමන ද්විභාෂා ප්‍රාථමික පිරිවෙන</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>📱 ජංගම දුරකථන ලකුණු ඇතුළත් කිරීම් හා විශ්ලේෂණ පද්ධතිය</div>", unsafe_allow_html=True)

DATA_FILE = "student_marks_db.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Index No", "Student Name", "Grade", "Term", 
        "Pali", "Sanskrit", "Tripi. Studies", "Sinhala", 
        "Mathematics", "English", "Health Sci.", "History", "Social Sci.", "Geog. Phy."
    ])

def get_grade_symbol(marks):
    try:
        m = float(marks)
        if m >= 75: return "A (ඉතා හොඳයි)"
        elif m >= 65: return "B (හොඳයි)"
        elif m >= 50: return "C (සාමාන්‍යයි)"
        elif m >= 35: return "S (ප්‍රමාණවත්)"
        else: return "W/F (සංවර්ධනය විය යුතුයි)"
    except:
        return "N/A"

menu = [
    "📝 ලකුණු ඇතුළත් කිරීම (Data Input)", 
    "📊 විෂයානුබද්ධ විශ්ලේෂණය (Subject Analysis)", 
    "📈 ප්‍රගති ප්‍රස්ථාර (Progress Graphs)", 
    "📋 සියලුම සටහන් (All Records)"
]
choice = st.selectbox("මෙනුව තෝරන්න (Select Menu):", menu)

st.write("---")

if choice == "📝 ලකුණු ඇතුළත් කිරීම (Data Input)":
    st.subheader("📲 නව ලකුණු ඇතුළත් කිරීම")
    
    with st.form("mobile_mark_entry"):
        index_no = st.text_input("විභාග අංකය (Index No)")
        student_name = st.text_input("ශිෂ්‍යයාගේ නම")
        grade = st.selectbox("ශ්‍රේණිය", ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"])
        term = st.selectbox("වාරය", ["1st Term", "2nd Term", "3rd Term"])
        
        st.write("---")
        st.write("**විෂය ලකුණු:**")
        
        pali = st.number_input("පාලි (Pali)", 0, 100, 0)
        sanskrit = st.number_input("සංස්කෘත (Sanskrit)", 0, 100, 0)
        tripi = st.number_input("ත්‍රිපිටක ධර්මය (Tripi. Studies)", 0, 100, 0)
        sinhala = st.number_input("සිංහල (Sinhala)", 0, 100, 0)
        maths = st.number_input("ගණිතය (Mathematics)", 0, 100, 0)
        english = st.number_input("ඉංග්‍රීසි (English)", 0, 100, 0)
        health = st.number_input("සෞඛ්‍යය (Health Sci.)", 0, 100, 0)
        history = st.number_input("ඉතිහාසය (History)", 0, 100, 0)
        social = st.number_input("සමාජ අධ්‍යයනය (Social Sci.)", 0, 100, 0)
        geog = st.number_input("භූගෝල විද්‍යාව (Geog. Phy.)", 0, 100, 0)

        submitted = st.form_submit_button("💾 ලකුණු සුරකින්න (Save)")

        if submitted:
            new_row = {
                "Index No": index_no, "Student Name": student_name, "Grade": grade, "Term": term,
                "Pali": pali, "Sanskrit": sanskrit, "Tripi. Studies": tripi, "Sinhala": sinhala,
                "Mathematics": maths, "English": english, "Health Sci.": health, "History": history,
                "Social Sci.": social, "Geog. Phy.": geog
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ ලකුණු සාර්ථකව පද්ධතියට ඇතුළත් විය!")

elif choice == "📊 විෂයානුබද්ධ විශ්ලේෂණය (Subject Analysis)":
    st.subheader("📊 විෂය විශ්ලේෂණ වාර්තාව")
    if df.empty:
        st.info("දත්ත ඇතුළත් කර නොමැත.")
    else:
        selected_grade = st.selectbox("ශ්‍රේණිය තෝරන්න", df["Grade"].unique())
        selected_term = st.selectbox("වාරය තෝරන්න", df["Term"].unique())
        subject_list = ["Mathematics", "Sinhala", "Pali", "Sanskrit", "English", "Health Sci.", "History", "Social Sci.", "Geog. Phy."]
        selected_subject = st.selectbox("විශ්ලේෂණය කළ යුතු විෂය", subject_list)

        filtered_df = df[(df["Grade"] == selected_grade) & (df["Term"] == selected_term)]

        if not filtered_df.empty:
            analysis_df = filtered_df[["Index No", "Student Name", selected_subject]].copy()
            analysis_df["තත්ත්වය"] = analysis_df[selected_subject].apply(get_grade_symbol)
            
            st.dataframe(analysis_df, use_container_width=True)

            avg_score = analysis_df[selected_subject].mean()
            st.metric("පන්තියේ සාමාන්‍යය", f"{avg_score:.1f}")

            grade_counts = analysis_df["තත්ත්වය"].value_counts().reset_index()
            grade_counts.columns = ["තත්ත්වය", "ශිෂ්‍ය ගණන"]
            
            fig = px.bar(grade_counts, x="තත්ත්වය", y="ශිෂ්‍ය ගණන", color="තත්ත්වය", title="සාමාර්ථ බෙදීයාම")
            st.plotly_chart(fig, use_container_width=True)

elif choice == "📈 ප්‍රගති ප්‍රස්ථාර (Progress Graphs)":
    st.subheader("📈 වාරාන්තර ප්‍රගතිය")
    if not df.empty:
        selected_student = st.selectbox("ශිෂ්‍යයා තෝරන්න", df["Student Name"].unique())
        st_df = df[df["Student Name"] == selected_student]
        
        if not st_df.empty:
            subject_cols = ["Pali", "Sanskrit", "Tripi. Studies", "Sinhala", "Mathematics", "English", "Health Sci.", "History", "Social Sci.", "Geog. Phy."]
            melted_df = pd.melt(st_df, id_vars=["Term"], value_vars=subject_cols, var_name="Subject", value_name="Marks")
            
            fig_progress = px.line(melted_df, x="Subject", y="Marks", color="Term", markers=True)
            st.plotly_chart(fig_progress, use_container_width=True)

elif choice == "📋 සියලුම සටහන් (All Records)":
    st.subheader("📋 සමස්ත ලකුණු ලැයිස්තුව")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Excel/CSV Download", data=csv, file_name="SiriSumana_Marks.csv", mime="text/csv")
