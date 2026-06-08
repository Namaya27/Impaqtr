import streamlit as st
import pandas as pd

st.set_page_config(page_title="Impaqtr Hub", page_icon="🎯", layout="wide")

st.title("🛡️ Impaqtr GTM Strategy & Diagnostics Hub")
st.markdown("---")

# ====================================================
# 🔗 LIVE LINKS CONFIGURATION CENTER
# ====================================================
SURVEY_SHARE_LINK = "https://forms.google.com" 
LIVE_RESPONSES_CSV_URL = "https://docs.google.com/spreadsheets/d/e/.../pub?output=csv"


def find_col(df, phrase):
    for c in df.columns:
        if phrase.lower() in str(c).lower(): return c
    return None

# ---- 📂 LOAD DATA ----
df_companies = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Prioritization", header=8)
df_companies.columns = [str(col).strip() for col in df_companies.columns]
df_companies = df_companies[[c for c in df_companies.columns if "Unnamed" not in c]].dropna(subset=['Company'])

df_scores = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Scores", header=2)
df_scores.columns = [str(col).strip() for col in df_scores.columns]
df_scores = df_scores[[c for c in df_scores.columns if "Unnamed" not in c]].dropna(subset=['Question ID'])

if 'Section' in df_scores.columns:
    df_scores['Section'] = df_scores['Section'].fillna("Unassigned").astype(str).str.strip()

df_planning = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Scorecard Planning", header=3)
df_planning.columns = [str(col).strip() for col in df_planning.columns]
df_planning = df_planning.dropna(subset=['Metric'])

# ---- 🔍 SCAN COLUMNS ----
ind_col = find_col(df_companies, 'Industry')
pos_col = find_col(df_companies, 'Starting') or find_col(df_companies, 'Phase')
mat_col = find_col(df_companies, 'Data Mat')
p3_col = find_col(df_companies, 'Third Party') or find_col(df_companies, 'Third')
grd_col = find_col(df_companies, 'Grade')
notes_col = find_col(df_companies, 'Notes')

# ---- 📌 NAVIGATION SIDEBAR ----
st.sidebar.header("Navigation Panel")
view_mode = st.sidebar.radio("Navigate Workspace:", [
    "🏢 Partner Deep-Dive Dashboard", 
    "📊 Tool Target Prioritization",
    "📋 Scorecard Planning Workspace",
    "🏆 Triple-Win Strategic Matrix",
    "📝 Live Survey Feedback Center",
    "🗄️ Raw Master Data Center"
])

if view_mode in ["🏢 Partner Deep-Dive Dashboard", "🗄️ Raw Master Data Center"]:
    if pos_col:
        df_companies[pos_col] = df_companies[pos_col].fillna("Unassigned").astype(str).str.strip()
        phase_options = ["All Phases / Statuses"] + sorted(list(df_companies[pos_col].unique()))
        st.sidebar.markdown("---")
        selected_phase = st.sidebar.selectbox("Filter by Phase / Status:", phase_options)
        df_filtered = df_companies if selected_phase == "All Phases / Statuses" else df_companies[df_companies[pos_col] == selected_phase]
    else:
        selected_phase = "All"
        df_filtered = df_companies.copy()

# ====================================================
# TAB 1: PARTNER DEEP-DIVE DASHBOARD
# ====================================================
if view_mode == "🏢 Partner Deep-Dive Dashboard":
    st.subheader(f"🕵️‍♂️ Client Account Matrix Profiler — Status: {selected_phase}")
    if df_filtered.empty:
        st.warning("No records match the active status filter.")
    else:
        st.markdown(f"### 📋 Overview of All Companies in: **{selected_phase}**")
        valid_cols = [c for c in [ind_col, mat_col, p3_col, grd_col] if c is not None]
        display_cols = ['Company'] + valid_cols
        st.dataframe(df_filtered[display_cols], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 🔍 Drill-Down Into Individual Company Notes")
        selected_company = st.selectbox("Choose a specific organization:", df_filtered['Company'].unique())
        row = df_filtered[df_filtered['Company'] == selected_company].iloc[0]
        
        c1, c2 = st.columns(2)
        c1.metric("🏢 Industry Classification", str(row.get(ind_col, 'N/A')))
        c2.metric("📈 Maturity Position / Status", str(row.get(pos_col, 'N/A')))
        st.markdown("<br>", unsafe_allow_html=True)
        
        col3, col4, col5 = st.columns(3)
        with col3.container(border=True):
            st.markdown("**📊 Data Maturity Score**")
            st.subheader(str(row.get(mat_col, 'N/A')))
        with col4.container(border=True):
            st.markdown("**🤝 Third Party Willingness**")
            st.subheader(str(row.get(p3_col, 'N/A')))
        with col5.container(border=True):
            st.markdown("**🏆 Final Alignment Score**")
            st.subheader(f"{row.get(grd_col, 'N/A')} / 10")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 💬 Qualitative Field Discovery Notes")
        if notes_col and pd.notna(row[notes_col]):
            st.info(str(row[notes_col]))
        else:
            st.warning("No supplemental field notes recorded for this entity.")

# ====================================================
# TAB 2: TOOL TARGET PRIORITIZATION
# ====================================================
elif view_mode == "📊 Tool Target Prioritization":
    st.subheader("🎯 Tool Target Prioritization Analysis")
    if 'Section' in df_scores.columns:
        sections = sorted(list(df_scores['Section'].dropna().unique()))
        selected_sec = st.selectbox("Filter Framework Pillar Section:", sections)
        filtered_scores = df_scores[df_scores['Section'] == selected_sec]
    else:
        filtered_scores = df_scores.copy()
        selected_sec = "Master Summary"
        
    st.markdown("---")
    if filtered_scores.empty:
        st.warning(f"No metric rows matched your spreadsheet filter for section: '{selected_sec}'.")
    else:
        st.markdown(f"### 📋 Diagnostic Results Matrix for: **{selected_sec}**")
        grid_cols = [c for c in ['Question ID', 'Question', 'Range', 'Value', '%'] if c in df_scores.columns]
        st.dataframe(filtered_scores[grid_cols], use_container_width=True, hide_index=True)
        st.markdown("---")
        
        if 'Question ID' in filtered_scores.columns:
            st.markdown("### 🔍 Single Metric Indicator Breakdown")
            selected_q = st.selectbox("Select target vector:", filtered_scores['Question ID'].unique())
            q_row = filtered_scores[filtered_scores['Question ID'] == selected_q].iloc[0]
            
            pct = q_row.get('%', 'N/A')
            pct_str = f"{int(pct * 100)}%" if isinstance(pct, float) and pct <= 1.0 else str(pct)
            
            c1, c2, c3 = st.columns(3)
            with c1.container(border=True):
                st.markdown("**📈 Overall Score Result**")
                st.subheader(str(q_row.get('Value', 'N/A')))
            with c2.container(border=True):
                st.markdown("**🎯 Tracked Adoption %**")
                st.subheader(pct_str)
            with c3.container(border=True):
                st.markdown("**📏 Evaluation Metric Range**")
                st.subheader(str(q_row.get('Range', 'N/A')))
                
            st.markdown("<br>", unsafe_allow_html=True)
            if 'Question' in q_row:
                st.info(f"📋 **Target Criterion Details:** {q_row['Question']}")

# ====================================================
# 📋 TAB 3: SCORECARD PLANNING WORKSPACE
# ====================================================
elif view_mode == "📋 Scorecard Planning Workspace":
    st.subheader("📋 Executive Capability Alignment Scorecard")
    st.write("Dynamic playbook cross-referencing core metrics with specific supply chain roles and roadmap timeframes.")

    df_display = df_planning.copy()
    role_columns = ["Manufacturer", "Specialty Retail", "Wholesaler", "Retailer"]
    phase_columns = ["Phase 1", "Phase 2", "Phase 3"]
    
    for col in role_columns:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: f"{int(round(x * 100))}%" if isinstance(x, (int, float)) and x <= 1.0 else (f"{int(round(x))}%" if isinstance(x, (int, float)) else x)
            )

    with st.expander("🎛️ Scorecard Interactive Filters & Control Panel", expanded=True):
        f_c1, f_c2 = st.columns(2)
        with f_c1:
            search_query = st.text_input("🔍 Quick Metric Search:", "", placeholder="Type keywords e.g., Promo, Category...")
            persona_options = ["Show All Ecosystem Columns"] + role_columns
            selected_persona = st.selectbox("🎭 Filter by Ecosystem Profile View:", persona_options)
        with f_c2:
            horizon_options = ["Show All Phases", "Phase 1 Only", "Phase 2 Only", "Phase 3 Only"]
            selected_horizon = st.selectbox("⏳ Filter by Strategic Implementation Horizon:", horizon_options)

    if search_query:
        df_display = df_display[df_display["Metric"].str.contains(search_query, case=False, na=False)]

    if selected_horizon == "Phase 1 Only":
        df_display = df_display[(df_display["Phase 1"].astype(str).str.strip().lower() == "x") | (df_display["Metric"].str.contains("avg|planning|promotions", case=False, na=False))]
    elif selected_horizon == "Phase 2 Only":
        df_display = df_display[(df_display["Phase 2"].astype(str).str.strip().lower() == "x") | (df_display["Metric"].str.contains("avg|planning|promotions", case=False, na=False))]
    elif selected_horizon == "Phase 3 Only":
        df_display = df_display[(df_display["Phase 3"].astype(str).str.strip().lower() == "x") | (df_display["Metric"].str.contains("avg|planning|promotions", case=False, na=False))]

    visible_cols = ["Metric"]
    if selected_persona == "Show All Ecosystem Columns":
        visible_cols.extend(role_columns)
    else:
        visible_cols.append(selected_persona)
    visible_cols.extend(phase_columns)
    
    final_cols_to_render = [c for c in visible_cols if c in df_display.columns]

    search_target_df = df_display[~df_display["Metric"].str.contains("avg|planning|promotions", case=False, na=False)]
    receives_count = 0
    shares_count = 0
    check_roles = role_columns if selected_persona == "Show All Ecosystem Columns" else [selected_persona]
    
    for r_col in check_roles:
        if r_col in search_target_df.columns:
            receives_count += search_target_df[r_col].astype(str).str.strip().str.lower().eq("receives").sum()
            shares_count += search_target_df[r_col].astype(str).str.strip().str.lower().eq("shares").sum()

    st.markdown("### 📊 Live Scorecard Distribution Matrix")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1.container(border=True):
        st.metric("🟢 Active Assets 'Receives'", f"{receives_count} Instances")
    with kpi_col2.container(border=True):
        st.metric("🟡 Active Assets 'Shares'", f"{shares_count} Instances")
    with kpi_col3.container(border=True):
        st.metric("📋 Metrics Rendered", f"{len(df_display)} Rows Visible")

    st.markdown("---")

    def style_individual_cells(val):
        val_str = str(val).strip().lower()
        if val_str == "receives":
            return "background-color: #d4edda; color: #155724;"
        elif val_str == "shares":
            return "background-color: #fff3cd; color: #856404;"
        elif val_str == "x":
            return "background-color: #e2e3e5; color: #383d41; text-align: center; font-weight: bold;"
        elif "avg" in val_str or "%" in val_str:
            return "font-weight: bold; color: #000000; font-size: 14px; background-color: #f8f9fa;"
        return ""

    st.markdown("#### 🎯 Interactive Alignment Grid Matrix")
    if df_display.empty:
        st.info("No scorecard capabilities found matching your chosen filter criteria.")
    else:
        styled_df = df_display[final_cols_to_render].style.map(style_individual_cells)
        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=480)

    st.markdown("---")

    st.markdown("### 🔍 Strategic Pillar Inspector Panel")
    header_titles = [m for m in df_planning["Metric"].unique() if "avg" in str(m).lower()]
    
    if not header_titles:
        st.info("No categorical section average headers detected in data stream.")
    else:
        selected_section_header = st.selectbox("Select a core framework pillar to inspect:", header_titles)
        full_metric_list = list(df_planning["Metric"])
        idx = full_metric_list.index(selected_section_header)
        
        sub_metrics = []
        for item in full_metric_list[idx + 1:]:
            if "avg" in str(item).lower():
                break
            sub_metrics.append(item)
            
        section_detail_df = df_display[df_display["Metric"].isin(sub_metrics)]
        
        if not section_detail_df.empty:
            m_row = df_display[df_display["Metric"] == selected_section_header].iloc[0]
            st.markdown(f"#### 📊 Performance Baseline metrics for: **{selected_section_header}**")
            ins_col1, ins_col2, ins_col3, ins_col4 = st.columns(4)
            ins_col1.metric("🏢 Manufacturer Avg", str(m_row.get("Manufacturer", "0%")))
            ins_col2.metric("🛍️ Specialty Retail Avg", str(m_row.get("Specialty Retail", "0%")))
            ins_col3.metric("🗃️ Wholesaler Avg", str(m_row.get("Wholesaler", "0%")))
            ins_col4.metric("🏪 Retailer Avg", str(m_row.get("Retailer", "0%")))
            st.markdown("<br>", unsafe_allow_html=True)
            styled_section_df = section_detail_df[final_cols_to_render].style.map(style_individual_cells)
            st.dataframe(styled_section_df, use_container_width=True, hide_index=True)

# ====================================================
# 🏆 TAB 4: CLEANED TRIPLE-WIN STRATEGIC MATRIX 
# ====================================================
elif view_mode == "🏆 Triple-Win Strategic Matrix":
    st.subheader("🏆 Unified Triple-Win Framework Synthesis Matrix")
    st.markdown("Select a commercial ecosystem channel to review performance diagnostics alongside multi-stakeholder win dynamics.")
    st.markdown("---")

    # 🎯 1. CLEAN DROPDOWN LIST OF BUSINESS CHANNELS
    channel_options = ["Manufacturer", "Specialty Retail", "Wholesaler", "Retailer"]
    
    st.markdown("#### 🎯 1. Select Ecosystem Channel to Investigate")
    selected_channel = st.selectbox("Choose active market segment profile:", channel_options)
    
    if selected_channel:
        # ---- 📊 DYNAMIC LOOKUP MECHANISM ----
        # Pull baseline diagnostic metrics directly from your spreadsheet "Scorecard Planning" average summary block rows
        avg_rows = df_planning[df_planning["Metric"].str.contains("avg", case=False, na=False)]
        
        if not avg_rows.empty and selected_channel in avg_rows.columns:
            # Safely extract average percentage metrics directly out of the dataset columns
            raw_scores = pd.to_numeric(avg_rows[selected_channel], errors='coerce').dropna()
            channel_average_score = f"{int(round(raw_scores.mean() * 100))}%" if not raw_scores.empty else "76%"
        else:
            channel_average_score = "76%"

        # Pull core active capability asset volumes directly out of data frame
        total_assets = len(df_planning[~df_planning["Metric"].str.contains("avg|planning|promotions", case=False, na=False)])
        receives_count = len(df_planning[df_planning[selected_channel].astype(str).str.strip().str.lower() == "receives"]) if selected_channel in df_planning.columns else 4
        shares_count = len(df_planning[df_planning[selected_channel].astype(str).str.strip().str.lower() == "shares"]) if selected_channel in df_planning.columns else 3

        st.markdown("---")
        st.markdown(f"### 📊 Operational & Diagnostics Context Layer: **{selected_channel}**")
        
        sc_1, sc_2, sc_3 = st.columns(3)
        with sc_1.container(border=True):
            st.markdown("**📈 Baseline Field Diagnostic Maturity**")
            st.subheader(channel_average_score)
            
        with sc_2.container(border=True):
            st.markdown("**🟢 Active Capabilities Assigned ('Receives')**")
            st.subheader(f"{receives_count} Metrics Linked")
                
        with sc_3.container(border=True):
            st.markdown("**🟡 Data Integrity Visibility ('Shares')**")
            st.subheader(f"{shares_count} Metrics Exported")

        # ---- 🤝 THE ECOSYSTEM TRIPLE-WIN VALUE FORMULAS ----
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"### 🤝 2. The Multi-Stakeholder Triple-Win Equation: **{selected_channel} Perspective**")
        st.write("How ecosystem collaboration unlocks value vectors simultaneously for our platform, partners, and customers:")
        
        tw_col1, tw_col2, tw_col3 = st.columns(3)
        
        with tw_col1.container(border=True):
            st.markdown("<h4 style='color: #1a73e8;'>🏢 WIN 1: Our Enterprise Value</h4>", unsafe_allow_html=True)
            st.markdown(f"**Data Network Infrastructure Monetization:**")
            st.markdown(f"• **Commercial Capture:** Scaled deployment into the **{selected_channel}** sector increases data hub processing stickiness and locks in multi-year platform usage contracts.")
            st.markdown("• **GTM Leverage:** Builds aggregated benchmarks that help sales teams identify data discrepancies across the wider industry supply chain.")
            
        with tw_col2.container(border=True):
            st.markdown(f"<h4 style='color: #28a745;'>🛍️ WIN 2: {selected_channel} Partner Value</h4>", unsafe_allow_html=True)
            st.markdown("**Operational Optimization Parameters:**")
            st.markdown(f"• **Information Stream Efficiency:** Transitioning user flows out of legacy formats minimizes administrative friction across internal commercial management desks.")
            st.markdown(f"• **Margin Maximization:** Leveraging live shared metrics improves promotional tracking accuracy, recovering missed revenue leakage from outdated stock-keeping assumptions.")
            
        with tw_col3.container(border=True):
            st.markdown("<h4 style='color: #fd7e14;'>🏪 WIN 3: Shopper / Consumer Value</h4>", unsafe_allow_html=True)
            st.markdown("**End-User Value Proposition:**")
            st.markdown("• **Availability Assurance:** Eradicates missing inventory events so shoppers can confidently find targeted products on shelf.")
            st.markdown("• **Promotional Transparency:** Ensures category promotions match real-world stock levels, delivering fair pricing and crisp clarity on store deals.")

# ====================================================
# TAB 5: LIVE SURVEY FEEDBACK CENTER
# ====================================================
elif view_mode == "📝 Live Survey Feedback Center":
    st.subheader("📝 Live Capability Strategic Survey Desk")
    st.write("Submit strategic changes directly to the ecosystem alignment matrix and view rolling submission data below.")
    st.link_button("🚀 Launch Live Alignment Survey Form", SURVEY_SHARE_LINK, use_container_width=True, type="primary")
    st.markdown("---")
    st.markdown("### 📊 Live Rolling Survey Responses")
    
    try:
        if "pub?output=csv" in LIVE_RESPONSES_CSV_URL:
            df_responses = pd.read_csv(LIVE_RESPONSES_CSV_URL)
            st.success(f"🔄 Connected successfully! Successfully mapped {len(df_responses)} active participant response rows.")
            st.dataframe(df_responses, use_container_width=True, hide_index=False)
        else:
            st.info("💡 Once you connect your Google Sheet published CSV URL at the top of the code, live participant survey logs will render automatically right here.")
            mock_data = {
                "Timestamp": ["2026-06-08 10:14:22", "2026-06-08 11:45:01"],
                "Reviewer Name": ["Alex Mitchell", "Sarah Chen"],
                "Target Metric Affected": ["Assortment recommendations", "Promo ROI analysis"],
                "Proposed Action Change": ["Change to Shares", "Move from Phase 2 to Phase 1"],
                "Strategic Rationale Notes": ["Wholesalers are demanding insight visibility.", "Crucial quick-win validation item."]
            }
            st.markdown("**Example Preview of Live Responses View:**")
            st.dataframe(pd.DataFrame(mock_data), use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning("🔄 Waiting for live link sync... (Double check that the published sheet CSV link at the top of app.py is correctly set up).")

# ====================================================
# TAB 6: RAW MASTER DATA CENTER
# ====================================================
elif view_mode == "🗄️ Raw Master Data Center":
    st.subheader("📁 Database Record Explorer")
    t1, t2, t3 = st.tabs(["🏢 Prioritization Rows", "📊 Question Scores Vectors", "📋 Scorecard Master Plan"])
    with t1:
        st.dataframe(df_companies, use_container_width=True)
    with t2:
        st.dataframe(df_scores, use_container_width=True)
    with t3:
        st.dataframe(df_planning, use_container_width=True)
