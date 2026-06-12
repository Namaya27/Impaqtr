import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Impaqtr Hub", page_icon="🎯", layout="wide")

# Custom CSS for the "Big Boxes" and general UI
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; }
    .stTextArea textarea { font-size: 14px; }
    div[data-testid="stMetric"] { background-color: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Impaqtr GTM Strategy & Diagnostics Hub")
st.markdown("---")

# ====================================================
# 🔗 LIVE LINKS & HELPER FUNCTIONS
# ====================================================
SURVEY_SHARE_LINK = "https://forms.google.com" 

def find_col(df, phrase):
    for c in df.columns:
        if phrase.lower() in str(c).lower(): return c
    return None

# ---- 📂 LOAD DATA ----
df_raw_analysis = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Analysis", header=2)

# Expanded to row 17 to capture all companies down to Excel Row 19 safely
df_companies_raw_positions = df_raw_analysis.iloc[:17].copy()

df_raw_analysis.columns = [str(col).strip() for col in df_raw_analysis.columns]
df_companies = df_raw_analysis.iloc[:17].copy()

# 🧠 LOCK COLUMN C: Explicitly identify Company Name (Real)
if len(df_companies_raw_positions.columns) >= 3:
    comp_name_col = df_companies_raw_positions.columns[2]  # Direct Column C lock
else:
    comp_name_col = find_col(df_companies, 'Real') or df_companies.columns[0]

df_companies = df_companies.dropna(subset=[comp_name_col])

# ---- 📊 DATA MATURITY ENGINE (Columns M, N, Q, S) ----
m_col = find_col(df_companies, 'Automated')        # M
n_col = find_col(df_companies, 'Real-time')        # N
q_col = find_col(df_companies, 'Breadth')          # Q
s_col = find_col(df_companies, 'Readiness')        # S

target_maturity_cols = [c for c in [m_col, n_col, q_col, s_col] if c is not None]

if target_maturity_cols:
    for col in target_maturity_cols:
        df_companies[col] = pd.to_numeric(df_companies[col], errors='coerce').fillna(0)
    df_companies['Raw Average'] = df_companies[target_maturity_cols].mean(axis=1).round(1)
else:
    df_companies['Raw Average'] = 0.0

def assign_maturity_tier(score):
    if score <= 2.0: return "Low"
    elif score < 4.0: return "Medium"
    else: return "High"

df_companies['Maturity_Tier_Internal'] = df_companies['Raw Average'].apply(assign_maturity_tier)

# ---- 🛠️ 4-TIER COMPANY SIZE CALCULATOR ----
def calculate_size_tier(val):
    if pd.isna(val): return "Unknown"
    clean_val = str(val).replace('$', '').replace(',', '').strip()
    try:
        n = float(clean_val)
        if n <= 10000000: return "Small"
        elif 10000000 < n <= 300000000: return "Medium"
        elif 300000000 < n <= 1000000000: return "Large"
        else: return "Enterprise"
    except: return "Unknown"

grd_col = find_col(df_companies, 'Size') or find_col(df_companies, 'Turnover')
df_companies['Company Size'] = df_companies[grd_col].apply(calculate_size_tier) if grd_col else "Unknown"

# ---- 🛡️ THIRD PARTY TWEAKED SUM ENGINE ----
sens_col = find_col(df_companies, 'Data sensitivity')
comp_col = find_col(df_companies, 'Compliance')
proc_col = find_col(df_companies, 'Data processing')
p3_cols = [c for c in [sens_col, comp_col, proc_col] if c is not None]

def tweak_sum(val):
    if val == 1: return 1.0
    elif val == 2: return 3.0
    elif val == 3: return 5.0
    return float(val)

if p3_cols:
    for col in p3_cols: df_companies[col] = pd.to_numeric(df_companies[col], errors='coerce').fillna(0)
    df_companies['Third Party Sum'] = df_companies[p3_cols].sum(axis=1).apply(tweak_sum).round(1)
else:
    df_companies['Third Party Sum'] = 0.0

# General Score cleanup
gen_score_src = find_col(df_companies, 'General score')
if gen_score_src:
    df_companies['General Score'] = pd.to_numeric(df_companies[gen_score_src], errors='coerce').round(1).fillna("N/A")
else:
    df_companies['General Score'] = "N/A"

# Pointers for the 3 new notes columns
dp_notes_src = find_col(df_companies, 'Data Process Notes')
w_notes_src = find_col(df_companies, 'Willingness Notes')
np_notes_src = find_col(df_companies, 'Neutral Party Notes')

# ---- 📂 LOAD SCORECARD PLANNING ----
try:
    df_planning = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Scorecard Planning", header=3)
    df_planning = df_planning.dropna(how='all', axis=1)
    df_planning.columns = [str(col).strip() for col in df_planning.columns]
    valid_cols = [c for c in df_planning.columns if 'unnamed' not in c.lower() and 'notes' not in c.lower()]
    df_planning = df_planning[valid_cols]
    df_planning = df_planning.dropna(subset=['Metric'])
except:
    df_planning = pd.DataFrame(columns=['Metric', 'Manufacturer', 'Specialty Retail', 'Wholesaler', 'Retailer'])

# ====================================================
# 📌 SIDEBAR & NAVIGATION
# ====================================================
view_mode = st.sidebar.radio("Navigate Workspace:", [
    "🏢 Partner Deep-Dive Dashboard", 
    "📊 Tool Target Prioritization",
    "📋 Capability Mapping Analytics",
    "🎯 Performance Scorecard Playbook",
    "🏆 Triple-Win Strategic Matrix",
    "📝 Live Survey Feedback Center"
])

df_filtered_companies = df_companies.copy()
sub_ind_col = find_col(df_companies, 'Sub-Industry')

if view_mode == "🏢 Partner Deep-Dive Dashboard":
    st.sidebar.markdown("---")
    st.sidebar.header("🎛️ Account Matrix Slicers")
    
    if sub_ind_col:
        unique_industries = df_companies[sub_ind_col].dropna().unique().astype(str)
        industry_options = ["All Industries"] + sorted(list(unique_industries))
        selected_ind = st.sidebar.selectbox("Filter by Industry:", industry_options)
        if selected_ind != "All Industries":
            df_filtered_companies = df_filtered_companies[df_filtered_companies[sub_ind_col].astype(str) == selected_ind]
            
    mat_labels = {"All Maturity Tiers": "All", "Low": "Low (<=2)", "Medium": "Medium (2-4)", "High": "High (>=4)"}
    selected_mat = st.sidebar.selectbox("Filter by Maturity:", list(mat_labels.values()))
    if selected_mat != "All":
        key = [k for k, v in mat_labels.items() if v == selected_mat][0]
        df_filtered_companies = df_filtered_companies[df_filtered_companies['Maturity_Tier_Internal'] == key]

    size_labels = {"All": "All", "Small": "Small (<10M)", "Medium": "Medium (10-300M)", "Large": "Large (300M-1B)", "Enterprise": "Enterprise (>1B)"}
    selected_size = st.sidebar.selectbox("Filter by Size:", list(size_labels.values()))
    if selected_size != "All":
        key = [k for k, v in size_labels.items() if v == selected_size][0]
        df_filtered_companies = df_filtered_companies[df_filtered_companies['Company Size'] == key]

# ====================================================
# TAB 1: PARTNER DASHBOARD
# ====================================================
if view_mode == "🏢 Partner Deep-Dive Dashboard":
    st.subheader("🏢 Partner Deep-Dive Dashboard")
    
    df_view = pd.DataFrame()
    df_view["Company Name"] = df_filtered_companies[comp_name_col]
    if sub_ind_col: df_view["Industry"] = df_filtered_companies[sub_ind_col]
    df_view["Size"] = df_filtered_companies['Company Size']
    df_view["Maturity Score"] = df_filtered_companies['Raw Average']
    df_view["Third Party"] = df_filtered_companies['Third Party Sum']
    df_view["General Score"] = df_filtered_companies['General Score']

    st.dataframe(df_view, use_container_width=True, hide_index=True)
    st.markdown("---")
    
    st.markdown("### 🔍 Drill-Down Into Account Details")
    if not df_filtered_companies.empty:
        selected_company = st.selectbox("Choose organization:", df_filtered_companies[comp_name_col].unique())
        row = df_filtered_companies[df_filtered_companies[comp_name_col] == selected_company].iloc[0]
        
        c1, c2 = st.columns(2)
        c1.metric("🏢 Industry", str(row.get(sub_ind_col, 'N/A')))
        c2.metric("📈 Account Role", str(row.get(find_col(df_companies, 'Role'), 'N/A')))
        
        st.markdown("#### 📊 Diagnostic Vectors")
        v1, v2, v3 = st.columns(3)
        v1.metric("🧠 Maturity Score", f"{row.get('Raw Average', 0.0)} / 5.0")
        v2.metric("🤝 Collaboration", str(row.get(find_col(df_companies, 'Interest'), 'N/A')))
        v3.metric("🛡️ Third Party Score", f"{row.get('Third Party Sum', 0.0)}")

        # High-contrast qualitative notes block placed above General Score
        st.markdown("#### 📝 Specialized Qualitative Assessment Notes")
        n_col1, n_col2, n_col3 = st.columns(3)
        
        def clean_note(val):
            if pd.isna(val) or str(val).strip().lower() in ['nan', '', '—']:
                return "*No notes logged for this track.*"
            return str(val).strip()

        with n_col1:
            with st.container(border=True):
                st.markdown("**⚙️ Data Process Notes**")
                val_dp = clean_note(row.get(dp_notes_src)) if dp_notes_src else "*No notes logged for this track.*"
                st.markdown(f"<div style='min-height: 100px; font-size:14px; color:#1e293b;'>{val_dp}</div>", unsafe_allow_html=True)
            
        with n_col2:
            with st.container(border=True):
                st.markdown("**🤝 Willingness Notes**")
                val_w = clean_note(row.get(w_notes_src)) if w_notes_src else "*No notes logged for this track.*"
                st.markdown(f"<div style='min-height: 100px; font-size:14px; color:#1e293b;'>{val_w}</div>", unsafe_allow_html=True)
            
        with n_col3:
            with st.container(border=True):
                st.markdown("**🛡️ Neutral Party Notes**")
                val_np = clean_note(row.get(np_notes_src)) if np_notes_src else "*No notes logged for this track.*"
                st.markdown(f"<div style='min-height: 100px; font-size:14px; color:#1e293b;'>{val_np}</div>", unsafe_allow_html=True)

        st.markdown("---")

        # General Score Evaluation Box
        col_g, col_blank = st.columns([1.5, 2])
        with col_g.container(border=True):
            st.markdown("### 🏆 Master Account Evaluation")
            st.header(f"🎯 General Score: {row.get('General Score', 'N/A')}")

        st.markdown("---")
        st.markdown("### ✍️ General Strategic Interview Remarks")
        st.text_area("Analysis Remarks:", placeholder="Enter generic qualitative context...", height=100, key=f"notes_{selected_company}")
    else:
        st.warning("No companies match the selected sidebar filters.")

# ====================================================
# TAB 2: TARGET PRIORITIZATION (🛠️ ROADMAP LAYOUT UPDATED)
# ====================================================
elif view_mode == "📊 Tool Target Prioritization":
    st.subheader("🎯 Account Prioritization & GTM Roadmap")
    
    def get_tier(row):
        try:
            g = float(row['General Score'])
            m = row['Raw Average']
            if g >= 4.0 or (g >= 3.0 and m >= 3.5): return "🔥 Tier 1: Strategic Lead"
            elif g >= 2.5: return "⚡ Tier 2: Acceleration Target"
            return "💎 Tier 3: Tactical Niche"
        except: return "💎 Tier 3: Tactical Niche"

    df_p = pd.DataFrame()
    df_p["Company"] = df_companies[comp_name_col]
    df_p["Score"] = df_companies['General Score']
    df_p["Tier"] = df_companies.apply(get_tier, axis=1)
    
    t_order = ["🔥 Tier 1: Strategic Lead", "⚡ Tier 2: Acceleration Target", "💎 Tier 3: Tactical Niche"]
    df_p["Tier"] = pd.Categorical(df_p["Tier"], categories=t_order, ordered=True)
    st.dataframe(df_p.sort_values("Tier"), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🗺️ GTM Alignment Outreach Roadmap")
    
    # 📝 ROADMAP TEXT HOOKS (Add your text inside the triple quotes below when ready!)
    PHASE_1_TEXT = """
    * * * """
    
    PHASE_2_TEXT = """
    * * * """
    
    PHASE_3_TEXT = """
    * * * """

    # 🛠️ Lateral Step-by-Step Column Roadmap Layout
    step1, step2, step3 = st.columns(3)
    
    with step1:
        st.markdown("<h3 style='color: #6366f1;'>🚀 Phase 1: Tier 1</h3>", unsafe_allow_html=True)
        st.caption("⏱️ **Timeline:** Weeks 1 - 4")
        with st.container(border=True):
            st.markdown("**Strategic Priority Focus:**")
            if PHASE_1_TEXT.strip():
                st.markdown(PHASE_1_TEXT)
            else:
                st.info("💡 *Placeholder: Drop your customized Phase 1 operational roadmap goals here.*")
                st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True) # visual buffer
                
    with step2:
        st.markdown("<h3 style='color: #10b981;'>⚡ Phase 2: Tier 2</h3>", unsafe_allow_html=True)
        st.caption("⏱️ **Timeline:** Weeks 5 - 8")
        with st.container(border=True):
            st.markdown("**Strategic Priority Focus:**")
            if PHASE_2_TEXT.strip():
                st.markdown(PHASE_2_TEXT)
            else:
                st.info("💡 *Placeholder: Drop your customized Phase 2 operational roadmap goals here.*")
                st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True) # visual buffer
                
    with step3:
        st.markdown("<h3 style='color: #f59e0b;'>💎 Phase 3: Tier 3</h3>", unsafe_allow_html=True)
        st.caption("⏱️ **Timeline:** Weeks 9+")
        with st.container(border=True):
            st.markdown("**Strategic Priority Focus:**")
            if PHASE_3_TEXT.strip():
                st.markdown(PHASE_3_TEXT)
            else:
                st.info("💡 *Placeholder: Drop your customized Phase 3 operational roadmap goals here.*")
                st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True) # visual buffer

# ====================================================
# TAB 3: CAPABILITY MAPPING ANALYTICS
# ====================================================
elif view_mode == "📋 Capability Mapping Analytics":
    st.subheader("📊 Ecosystem Data Capability Analytics")
    st.markdown("This dashboard breaks down your spreadsheet metrics by industry role to evaluate operational friction.")

    if not df_planning.empty:
        industry_roles = [col for col in df_planning.columns if col != 'Metric' and 'Phase' not in col]
        
        st.markdown("### 📌 Individual Role Audit")
        selected_role = st.selectbox("🎯 Select Industry Role to Profile:", industry_roles, key="single_role")
        
        series_clean = df_planning[selected_role].astype(str).str.strip().str.lower()
        shares_count = sum(series_clean.str.contains('shares', na=False))
        receives_count = sum(series_clean.str.contains('receives', na=False))
        blocked_count = sum(series_clean.str.contains('blocked', na=False))
        total_metrics = len(df_planning)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📬 Data Shares Rows", f"{shares_count}")
        m2.metric("📩 Data Receives Rows", f"{receives_count}")
        m3.metric("🚫 Data Blocked Rows", f"{blocked_count}", delta=f"{blocked_count} blockages" if blocked_count > 0 else "Clean", delta_color="inverse")
        m4.metric("📊 Total Profiled Capabilities", f"{total_metrics}")

        with st.container(border=True):
            st.markdown(f"#### 🔍 Detailed Strategic Insights: {selected_role}")
            
            blocked_metrics = df_planning[df_planning[selected_role].astype(str).str.strip().str.lower() == 'blocked']['Metric'].tolist()
            shares_metrics = df_planning[df_planning[selected_role].astype(str).str.strip().str.lower() == 'shares']['Metric'].tolist()
            receives_metrics = df_planning[df_planning[selected_role].astype(str).str.strip().str.lower() == 'receives']['Metric'].tolist()
            
            b_list = ", ".join([f"'{m}'" for m in blocked_metrics[:3]]) if blocked_metrics else "None identified"
            s_list = ", ".join([f"'{m}'" for m in shares_metrics[:2]]) if shares_metrics else "None identified"
            r_list = ", ".join([f"'{m}'" for m in receives_metrics[:2]]) if receives_metrics else "None identified"

            if selected_role == "Manufacturer":
                st.write(f"⚠️ **Ecosystem Blockages ({blocked_count}):** The Manufacturer encounters critical integration blind spots around **{b_list}**. This stems from standard security postures regarding direct infrastructure visibility.")
                st.write(f"🤝 **Sharing Disposition:** They are highly eager to push upstream supply details such as **{s_list}** to reduce inventory channel echo effects.")
                st.write(f"📥 **Inbound Appetite:** They demonstrate an absolute urgency to ingest **{r_list}** in order to align factory production with store-level reality.")
            
            elif selected_role == "Retailer":
                st.write(f"⚠️ **Ecosystem Blockages ({blocked_count}):** The Retailer exhibits localized compliance locks around **{b_list}**, usually to defend customer margins and proprietary transaction panels.")
                st.write(f"🤝 **Sharing Disposition:** They selectively output clear downstream metrics like **{s_list}** when tied to structural joint venture rewards.")
                st.write(f"📥 **Inbound Appetite:** They seek immediate visibility into **{r_list}** to guarantee shelf fill rates without holding costly stock buffers.")

            elif selected_role == "Specialty Retail":
                st.write(f"⚠️ **Ecosystem Blockages ({blocked_count}):** Specialty players are heavily constrained by **{b_list}** due to specialized, legacy ERP infrastructures or isolated store networks.")
                st.write(f"🤝 **Sharing Disposition:** They generate hyper-focused niche datasets like **{s_list}**, which carry incredible trend velocity value for strategic manufacturers.")
                st.write(f"📥 **Inbound Appetite:** They rely heavily on pulling **{r_list}** to secure accurate size/color allocations.")

            else: # Wholesaler
                st.write(f"⚠️ **Ecosystem Blockages ({blocked_count}):** Wholesalers face execution friction across **{b_list}** due to complex split-pallet and fragmented third-party transit routes.")
                st.write(f"🤝 **Sharing Disposition:** They actively distribute aggregate regional flow signals like **{s_list}** to stabilize supply fluctuations.")
                st.write(f"📥 **Inbound Appetite:** They continuously pull bulk alignment updates like **{r_list}** to avoid terminal warehouse overstocking.")

        st.markdown("---")
        
        st.markdown("### 🔄 Cross-Industry Ecosystem Collaboration Matrix")
        st.markdown("Select two distinct industry actors to verify how data handoffs interact in real practice.")

        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            role_a = st.selectbox("Sender / Supplier Role:", industry_roles, index=0, key="role_a")
        with comp_col2:
            default_idx = 1 if len(industry_roles) > 1 else 0
            role_b = st.selectbox("Receiver / Partner Role:", industry_roles, index=default_idx, key="role_b")

        if role_a == role_b:
            st.info("💡 Select two different roles to evaluate systemic supply-chain pipeline handoffs.")
        else:
            status_a = df_planning[role_a].astype(str).str.strip().str.lower()
            status_b = df_planning[role_b].astype(str).str.strip().str.lower()

            perfect_collaboration = sum((status_a == 'shares') & (status_b == 'receives'))
            system_blocked = sum((status_a == 'blocked') | (status_b == 'blocked'))
            data_gap = total_metrics - (perfect_collaboration + system_blocked)

            c_split1, c_split2, c_split3 = st.columns(3)
            c_split1.metric("🤝 Perfect Collaboration Pipeline Rows", f"{perfect_collaboration}", help="Rows where one shares and the other receives.")
            c_split2.metric("🚫 Active Friction / Blocked Rows", f"{system_blocked}", help="Total explicit security blocks present across either party.")
            c_split3.metric("⚠️ Structural Gaps / Unused Data", f"{data_gap}", help="Data produced but not ingested, or demanded but not systematically delivered.")

            with st.container(border=True):
                st.markdown(f"#### 🧠 Collaborative Health Check: {role_a} ➡️ {role_b}")
                st.write(f"When a **{role_a}** interacts with a **{role_b}**, there are **{perfect_collaboration} metrics** ready for seamless automated sync pipelines. However, **{system_blocked} direct architectural blocks** are stalling collaborative velocity.")

        st.markdown("---")

        st.markdown("### 🗂️ Complete Alignment Audit Matrix")
        def format_cell_values(val):
            if pd.isna(val) or str(val).strip() in ['nan', '-', '—']: return "—"
            return str(val).strip()

        for col in df_planning.columns:
            if col != 'Metric': df_planning[col] = df_planning[col].apply(format_cell_values)

        def style_matrix_cells(val):
            val_clean = str(val).strip().lower()
            if 'receives' in val_clean: return 'background-color: #d1fae5; color: #065f46; font-weight: bold;'
            elif 'shares' in val_clean: return 'background-color: #fef3c7; color: #92400e; font-weight: bold;'
            elif 'blocked' in val_clean: return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
            return 'color: #1e293b;'

        styled_planning = df_planning.style.map(style_matrix_cells, subset=df_planning.columns[1:])
        st.dataframe(styled_planning, use_container_width=True, hide_index=True, height=500)

# ====================================================
# TAB 4: PERFORMANCE SCORECARD PLAYBOOK
# ====================================================
elif view_mode == "🎯 Performance Scorecard Playbook":
    st.subheader("🎯 Data Sharing Performance Scorecard Playbook")
    st.markdown("### How a Collaborative Company Manages Operational KPIs & SLA Penalties")
    st.markdown("This operational engine outlines the targets, actual metrics, and commercial consequences of non-compliance.")

    scorecard_data = {
        "Strategic Domain": ["Data Quality", "Data Quality", "Alignment Velocity", "Alignment Velocity", "Ecosystem Growth", "Ecosystem Growth"],
        "Performance Indicator (KPI)": [
            "API Data Transmission Completeness", 
            "Inventory Discrepancy Margin", 
            "Promo Sell-Out Refresh Frequency", 
            "Post-Campaign Processing Turnaround", 
            "Joint Retail-Manufacturer Sprints", 
            "On-Shelf Availability (OSA) Lift"
        ],
        "Target SLA": [">= 99.5%", "<= 1.5%", "Real-time / Hourly", "<= 48 Hours", ">= 4 Sprints / Year", "+ 5.0% Max Out"],
        "Current Actual": ["99.8%", "3.2%", "Daily Batch", "72 Hours", "2 Sprints", "+ 2.1%"],
        "Execution Health": ["🟢 Healthy", "🔴 Critical Friction", "🟡 Warning", "🟡 Warning", "🔴 Critical Friction", "🟡 Warning"],
        "Non-Compliance Penalty Impact": [
            "None (SLA Compliant)",
            "⚠️ 1.5% Trade Allowance Penalty Applied",
            "Warning Logged (No financial penalty yet)",
            "Warning Logged (No financial penalty yet)",
            "⚠️ Loss of Premium Partner Pipeline Status",
            "Co-Investment Funding Reduced by 0.5%"
        ]
    }
    df_sc = pd.DataFrame(scorecard_data)

    def style_health_and_penalties(val):
        val_str = str(val)
        if "🟢" in val_str or "Compliant" in val_str: 
            return 'background-color: #d1fae5; color: #065f46; font-weight: bold;'
        elif "🟡" in val_str or "Warning" in val_str: 
            return 'background-color: #fef3c7; color: #92400e; font-weight: bold;'
        elif "🔴" in val_str or "⚠️" in val_str or "Reduced" in val_str: 
            return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
        return ''

    st.dataframe(
        df_sc.style.map(style_health_and_penalties, subset=['Execution Health', 'Non-Compliance Penalty Impact']), 
        use_container_width=True, 
        hide_index=True
    )

    st.markdown("---")
    st.markdown("### 🛠️ Execution Playbook Strategy & Penalty Framework")
    sc_col1, sc_col2 = st.columns(2)
    with sc_col1.container(border=True):
        st.markdown("#### 🚨 Commercial & Financial Penalties")
        st.write("• **The Margin Deduction Rule:** If data latency or discrepancy breaches the critical threshold for 2 consecutive reporting cycles, the retailer automatically clawbacks **1.5% of trade promotional funding**.")
        st.write("• **Ecosystem Demotion:** Failure to join scheduled data alignment sprints drops the partner's logistics ranking, resulting in a loss of preferred routing priority at warehouses.")
    with sc_col2.container(border=True):
        st.markdown("#### 📈 Escalation & Remediation Pathways")
        st.write("• **Phase 1 (Grace Period):** Yellow warnings grant a 7-day automatic data buffer window to clean up processing logic before financial impact triggers.")
        st.write("• **Phase 2 (Cure Loop):** Reaching target data completeness metrics for 30 consecutive days automatically wipes historical non-compliance points clean.")

# ====================================================
# TAB 5: TRIPLE-WIN STRATEGIC MATRIX
# ====================================================
elif view_mode == "🏆 Triple-Win Strategic Matrix":
    st.subheader("🏆 Triple-Win Ecosystem Optimization Framework")
    st.markdown("Select an explicit stakeholder domain below to generate optimization opportunities across the collaborative landscape.")

    partner_focus = st.selectbox("🎯 Analyze Strategic Perspective From:", ["Retailer", "Manufacturer", "Specialty Retail", "Wholesaler"])
    
    perspective_insights = {
        "Retailer": {"retailer_win": ["Direct data ownership optimizes inventory holdings and turns", "Dynamic margin protections through synchronized promotional visibility", "Drastically lower store-level out-of-stocks"], "manufacturer_win": ["Receives clean sell-out metrics to optimize warehouse production scheduling", "Faster post-promo data processing loops for immediate budget planning"], "shopper_win": ["Guaranteed multi-channel product availability", "Fairer value distributions and relevant localized promotional pricing"], "color": "#6366f1", "metric_label": "Retailer Efficiency Leap", "metric_val": "+22% Turn"},
        "Manufacturer": {"retailer_win": ["Receives verified manufacturing forecasting models to plan long-term assortment space", "Reduction of administrative validation bottlenecks"], "manufacturer_win": ["Protects brand shelf equity through precise real-time sell-out alignment", "Direct compliance validation of trade execution across retail nodes"], "shopper_win": ["Fresher inventory batches directly sourced from streamlined distribution pathways", "Fewer fragmented supply blockages"], "color": "#10b981", "metric_label": "Manufacturer Fill Rate Optimization", "metric_val": "98.4% Achieved"},
        "Specialty Retail": {"retailer_win": ["High-value specialty margin optimization via ultra-tailored size/color/category tracking", "Localized trend-velocity alignment eliminates markdown dependencies"], "manufacturer_win": ["Deeper visibility into specialized shopper penetration niches", "Agile asset deployment for exclusive specialty product rollouts"], "shopper_win": ["Ultra-curated, zero-friction discovery experience across boutique channels", "Immediate access to highly targeted inventory variants"], "color": "#f59e0b", "metric_label": "Markdown Reductions", "metric_val": "-15% Waste"},
        "Wholesaler": {"retailer_win": ["Stabilized decentralized supply sourcing with bulk fulfillment assurances", "Aggregated supply visibility mitigates individual lead-time vulnerabilities"], "manufacturer_win": ["Aggregated multi-tier downstream distribution visibility clearing supply blindness", "Optimized large-scale batch order commitments"], "shopper_win": ["Uninterrupted staple goods presence at baseline regional competitive points", "Protected localized price points"], "color": "#ec4899", "metric_label": "Logistics Buffer Capacity", "metric_val": "3.8x Multiplier"}
    }
    focus = perspective_insights[partner_focus]

    st.markdown(f"### 🎚️ Playbook Standpoint: **{partner_focus} Strategic Perspective Scorecard**")
    st.markdown(f"The metrics and strategic gains below show exactly how a **{partner_focus}** optimizes their shared ecosystem relationships.")

    tw1, tw2, tw3 = st.columns(3)
    with tw1:
        with st.container(border=True):
            st.markdown(f"<h3 style='color: {focus['color']};'>🏪 Retailer Strategic Gain</h3>", unsafe_allow_html=True)
            for item in focus['retailer_win']: st.write(f"🔹 {item}")
    with tw2:
        with st.container(border=True):
            st.markdown(f"<h3 style='color: {focus['color']};'>🏭 Manufacturer Strategic Gain</h3>", unsafe_allow_html=True)
            for item in focus['manufacturer_win']: st.write(f"🔹 {item}")
    with tw3:
        with st.container(border=True):
            st.markdown(f"<h3 style='color: {focus['color']};'>🛒 Shopper Core Experience Gain</h3>", unsafe_allow_html=True)
            for item in focus['shopper_win']: st.write(f"🔹 {item}")
            st.metric(focus['metric_label'], focus['metric_val'])

# ====================================================
# TAB 6: SURVEY FEEDBACK
# ====================================================
elif view_mode == "📝 Live Survey Feedback Center":
    st.subheader("📝 Live Capability Strategic Survey Desk")
    st.link_button("🚀 Launch Live Alignment Survey Form", SURVEY_SHARE_LINK, use_container_width=True, type="primary")
