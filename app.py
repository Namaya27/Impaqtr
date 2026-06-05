import streamlit as st
import pandas as pd

st.set_page_config(page_title="Impaqtr Hub", page_icon="🎯", layout="wide")

# Premium Presentation Layout Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-top: 4px solid #1E3A8A;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 26px;
        font-weight: bold;
        color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Impaqtr GTM Strategy & Diagnostics Hub")
st.markdown("---")

try:
    # ---- 📂 SHEET 1: PRIORITIZATION TAB (Company Accounts) ----
    # Row 9 in Excel maps to header=8 in python code
    df_companies = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Prioritization", header=8)
    df_companies.columns = [str(col).strip() for col in df_companies.columns]
    
    # Filter columns to drop blank spacer fields
    comp_cols = [c for c in df_companies.columns if "Unnamed" not in c and "nan" not in c.lower() and c != ""]
    df_companies = df_companies[comp_cols].dropna(subset=['Company'])

    # ---- 📂 SHEET 2: SCORES TAB (Diagnostic Framework) ----
    # Row 3 in Excel maps to header=2 in python code. Capitalized 'Scores' to match your sheet name!
    df_scores = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Scores", header=2)
    df_scores.columns = [str(col).strip() for col in df_scores.columns]
    
    # Clean out blank spacer margins
    score_cols = [c for c in df_scores.columns if "Unnamed" not in c and "nan" not in c.lower() and c != ""]
    df_scores = df_scores[score_cols].dropna(subset=['Question ID'])

    # ---- 📌 INTERACTIVE SIDEBAR NAVIGATION ----
    view_mode = st.sidebar.radio("Navigate Workspace:", [
        "🏢 Partner Deep-Dive Dashboard", 
        "📊 Live Framework Scorecard", 
        "🗄️ Raw Master Data Center"
    ])

    # ----------------------------------------------------
    # VIEW 1: PARTNER DEEP-DIVE
    # ----------------------------------------------------
    if view_mode == "🏢 Partner Deep-Dive Dashboard":
        st.subheader("🕵️‍♂️ Client Account Matrix Profiler")
        st.write("Isolate a custom corporate interview record to examine partner alignment indicators.")
        
        company_list = df_companies['Company'].unique()
        selected_company = st.selectbox("Choose a target organization:", company_list)
        company_row = df_companies[df_companies['Company'] == selected_company].iloc[0]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Diagnostic Metric Display Panel
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Industry Classification", value=str(company_row.get('Industry', 'N/A')))
        with col2:
            st.metric(label="Maturity Position", value=str(company_row.get('Starting Pl', 'N/A')))
        with col3:
            st.metric(label="Operational Grade", value=f"{company_row.get('Grade', 'N/A')} / 10")
        with col4:
            st.metric(label="Data Maturity Score", value=str(company_row.get('Data Matu', 'N/A')))

        st.markdown("---")
        st.markdown("### 📋 Primary Qualitative Discovery Notes")
        if 'Notes' in company_row and pd.notna(company_row['Notes']):
            st.info(f"💬 **Interview Insights:** {company_row['Notes']}")
        else:
            st.warning("No supplemental field notes recorded for this entity yet.")

    # ----------------------------------------------------
    # VIEW 2: LIVE FRAMEWORK SCORECARD
    # ----------------------------------------------------
    elif view_mode == "📊 Live Framework Scorecard":
        st.subheader("💯 Framework Diagnostic Performance Radar")
        st.write("Aggregated indicators parsed from your master scores structure configuration.")
        
        sections = df_scores['Section'].unique()
        selected_sec = st.selectbox("Filter Framework Pillar:", sections)
        filtered_scores = df_scores[df_scores['Section'] == selected_sec]
        
        q_list = filtered_scores['Question ID'].unique()
        selected_q = st.selectbox("Select Diagnostic Metric Vector:", q_list)
        q_row = filtered_scores[filtered_scores['Question ID'] == selected_q].iloc[0]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Fetch data safely
        val = q_row.get('Value', 'N/A')
        pct = q_row.get('%', 'N/A')
        rng = q_row.get('Range', 'N/A')
        
        # Simplified percentage safety clean-up to avoid layout syntax bugs
        if isinstance(pct, float) and pct <= 1.0:
            pct_str = f"{int(pct * 100)}%"
        else:
            pct_str = str(pct)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'>📈 <br><b>Overall Sample Score</b><br><span class='metric-val'>{val}</span></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'>🎯 <br><b>Adoption Percentage</b><br><span class='metric-val'>{pct_str}</span></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'>📏 <br><b>Scale Metric Context</b><br><span class='metric-val'>{rng}</span></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"📋 **Evaluation Target Criterion:** {q_row.get('Question', 'N/A')}")
        
        st.markdown("---")
        st.write("### 📊 Active Diagnostic Sub-Matrix")
        display_cols = [c for c in ['Question ID', 'Question', 'Range', 'Value', '%'] if c in df_scores.columns]
        st.dataframe(filtered_scores[display_cols], use_container_width=True)

    # ----------------------------------------------------
    # VIEW 3: RAW MASTER DATA CENTER
    # ----------------------------------------------------
    elif view_mode == "🗄️ Raw Master Data Center":
        st.subheader("📁 Database Record Explorer")
        st.write("Below are the completely cleaned data tables stripped of empty formatting blocks.")
        
        t1, t2 = st.tabs(["🏢 Prioritization Tracker Rows", "📊 Question Scores Vectors"])
        with t1:
            st.dataframe(df_companies, use_container_width=True)
        with t2:
            st.dataframe(df_scores, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Master Integration Interrupted: {e}")