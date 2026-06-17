import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Impaqtr Hub", page_icon="🎯", layout="wide")

# Custom CSS for clean UI rendering
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; }
    div[data-testid="stMetric"] { background-color: #f8fafc; padding: 14px; border-radius: 6px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Impaqtr GTM Strategy & Diagnostics Hub")
st.markdown("---")

# ====================================================
# 🔗 HELPER FUNCTIONS
# ====================================================
def find_col(df, phrase):
    for c in df.columns:
        if phrase.lower() in str(c).lower(): return c
    return None

# ---- 📂 LOAD DATA: SHEET 1 (ANALYSIS) ----
try:
    df_raw_analysis = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Analysis", header=2)
    df_companies_raw_positions = df_raw_analysis.iloc[:18].copy()
    df_raw_analysis.columns = [str(col).strip() for col in df_raw_analysis.columns]
    df_companies = df_raw_analysis.iloc[:18].copy()

    if len(df_companies_raw_positions.columns) >= 2:
        comp_name_col = df_companies_raw_positions.columns[1]
    else:
        comp_name_col = find_col(df_companies, 'Company') or df_companies.columns[0]

    df_companies = df_companies.dropna(subset=[comp_name_col])

    data_proc_notes_col = find_col(df_companies, 'Data Process Notes')
    willingness_notes_col = find_col(df_companies, 'Willingness Notes')
    neutral_notes_col = find_col(df_companies, 'Neutral Party Notes')

    m_col = find_col(df_companies, 'Automated')        
    n_col = find_col(df_companies, 'Real-time')        
    q_col = find_col(df_companies, 'Breadth')          
    s_col = find_col(df_companies, 'Readiness')        

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

    # Reading directly from Column L to keep your precise data coding format
    strat_col = find_col(df_companies, 'Strategic reasons') 
    if strat_col:
        df_companies['Strategic_Display'] = df_companies[strat_col].astype(str).str.strip()
    else:
        df_companies['Strategic_Display'] = "No"

    gen_score_src = find_col(df_companies, 'General score')
    if gen_score_src:
        df_companies['General Score'] = pd.to_numeric(df_companies[gen_score_src], errors='coerce').round(1).fillna("N/A")
    else:
        df_companies['General Score'] = "N/A"
except Exception as e:
    st.sidebar.error(f"Error loading Analysis sheet: {e}")
    df_companies = pd.DataFrame()

# ---- 📂 LOAD DATA: SHEET 2 (SCORECARD PLANNING) ----
try:
    df_scan = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Scorecard Planning", header=None)
    
    header_idx = None
    for idx, row in df_scan.iterrows():
        row_str = [str(s).lower().strip() for s in row.values]
        if any('manufacturer' in s for s in row_str) and any('retailer' in s for s in row_str):
            header_idx = idx
            break
            
    if header_idx is not None:
        df_planning = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Scorecard Planning", header=header_idx)
        df_planning = df_planning.dropna(how='all', axis=1)
        df_planning.columns = [str(col).strip() for col in df_planning.columns]
        
        if len(df_planning.columns) > 0 and df_planning.columns[0] != 'Metric':
            df_planning.rename(columns={df_planning.columns[0]: 'Metric'}, inplace=True)
            
        valid_cols = [c for c in df_planning.columns if 'unnamed' not in c.lower()] 
        df_planning = df_planning[valid_cols]
        df_planning = df_planning.dropna(subset=['Metric'])
        df_planning = df_planning[df_planning['Metric'].astype(str).str.strip() != '']
    else:
        df_planning = pd.read_excel("Interview_Analysis_v3_1.xlsx", sheet_name="Scorecard Planning", header=8)
        if len(df_planning.columns) > 0 and df_planning.columns[0] != 'Metric':
            df_planning.rename(columns={df_planning.columns[0]: 'Metric'}, inplace=True)
except Exception as e:
    st.sidebar.error(f"Error loading Scorecard Planning Matrix: {e}")
    df_planning = pd.DataFrame(columns=['Metric', 'Manufacturer', 'Specialty Retail', 'Wholesaler', 'Retailer'])

# ====================================================
# 📌 SIDEBAR & NAVIGATION
# ====================================================
view_mode = st.sidebar.radio("Navigate Workspace:", [
    "🏢 Partner Deep-Dive Dashboard", 
    "📋 Capability Mapping Analytics",
    "🎯 Performance Scorecard Playbook",
    "🏆 Triple-Win Strategic Matrix",
    
])

df_filtered_companies = df_companies.copy() if not df_companies.empty else pd.DataFrame()
sub_ind_col = find_col(df_companies, 'Sub-Industry') if not df_companies.empty else None

if view_mode == "🏢 Partner Deep-Dive Dashboard" and not df_companies.empty:
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
    
    st.info("""
    **📖 Welcome to the Partner Deep-Dive Dashboard!**
    This panel aggregates variables on candidate accounts and pairs them directly with qualitative context lines transcribed during market discovery interviews.
    """, icon="ℹ️")

    with st.expander("📖 View Guide: Lineage & Interpretation Formulas", expanded=False):
       st.markdown("""

* **📂 Data Source:** Extracted directly from ther table below.

* **🧠 Maturity Score Calculation:** Computed by averaging columns corresponding to *Automated*, *Real-time*, *Breadth*, and *Readiness* scales [Scored out of 5.0].

* **🤝 Collaboration Status:** Result of how willing the companys interest to collaborate is based on the interviews

* **🏢 Company Size Slicing:** Map boundaries process revenue variables automatically: 
  * *Small* ($\leq$\\$10M) | *Medium* (\\$10M–\\$300M) | *Large* (\\$300M–\\$1B) | *Enterprise* ($>$\\$1B$).

* **💡 How to Read:** Filter accounts globally via the sidebar dashboard controls, select a specific enterprise from the central drill-down box, and evaluate their narrative roadblocks using the formatted text cards.
        """)

    if not df_filtered_companies.empty:
        df_view = pd.DataFrame()
        df_view["Company Name"] = df_filtered_companies[comp_name_col]
        if sub_ind_col: df_view["Industry"] = df_filtered_companies[sub_ind_col]
        df_view["Size"] = df_filtered_companies['Company Size']
        df_view["Maturity Score"] = df_filtered_companies['Raw Average']
        df_view["Possible commercial approach"] = df_filtered_companies['Strategic_Display']

        st.dataframe(df_view, use_container_width=True, hide_index=True)
        st.markdown("---")
        
        st.markdown("### 🔍 Drill-Down Into Account Details")
        selected_company = st.selectbox("Choose organization:", df_filtered_companies[comp_name_col].unique(), help="Select an audited account to load its granular parameters and qualitative feedback notes.")
        row = df_filtered_companies[df_filtered_companies[comp_name_col] == selected_company].iloc[0]
        
        c1, c2 = st.columns(2)
        c1.metric("🏢 Industry Vertical", str(row.get(sub_ind_col, 'N/A')))
        c2.metric("📈 Account Ecosystem Role", str(row.get(find_col(df_companies, 'Role'), 'N/A')))
        
        st.markdown("#### 📊 Diagnostic Vectors")
        v1, v2, v3 = st.columns(3)
        v1.metric("🧠 Maturity Score", f"{row.get('Raw Average', 0.0)} / 5.0", help="Arithmetic average of data automation, telemetry speed, and process maturity indicators.")
        v2.metric("🤝 Collaboration Status", str(row.get(find_col(df_companies, 'Interest'), 'N/A')), help="Qualitative evaluation capturing the partner's historical engagement willingness, operational openness, and speed in signing joint data contracts.")
        v3.metric("🎯 Possible commercial approach", str(row.get('Strategic_Display', 'No')), help="Indicates if the partner is categorized as an essential anchor account.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("### 📝 Specialized Qualitative Assessment Notes")
        note_c1, note_c2, note_c3 = st.columns(3)
        
        def clean_note(val):
            if pd.isna(val) or str(val).strip().lower() in ['nan', '-', '']: return "No notes logged."
            return str(val).strip()

        with note_c1:
            with st.container(border=True):
                st.markdown("**⚙️ Data Process Notes**")
                st.write(clean_note(row.get(data_proc_notes_col)) if data_proc_notes_col else "No notes logged.")
            
        with note_c2:
            with st.container(border=True):
                st.markdown("**🤝 Willingness Notes**")
                st.write(clean_note(row.get(willingness_notes_col)) if willingness_notes_col else "No notes logged.")
            
        with note_c3:
            with st.container(border=True):
                st.markdown("**🛡️ Neutral Party Notes**")
                st.write(clean_note(row.get(neutral_notes_col)) if neutral_notes_col else "No notes logged.")
    else:
        st.warning("No dataset loaded or matching the active filters.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("ℹ️ **Data Footnote:** Account metrics and descriptive notes are compiled from primary qualitative field discovery interviews (Rows 1–18 of `Analysis` worksheet in `Interview_Analysis_v3_1.xlsx`).")

# ====================================================
# TAB 3: CAPABILITY MAPPING ANALYTICS
# ====================================================
elif view_mode == "📋 Capability Mapping Analytics":
    st.subheader("📊 Ecosystem Data Capability Analytics")
    
    st.info("""
    **📖 Welcome to the Capability Mapping Module!**
    This matrix inspects data permissions row-by-row across primary industry role tracks to visualize data asymmetry, sharing permissions, and ecosystem blockages.
    """, icon="ℹ️")

    with st.expander("📖 View Guide: Metric Matrix Logic & Dynamic Counters", expanded=False):
        st.markdown("""
        * **📂 Data Source:** The matrix reads rows directly from the `Scorecard Planning` sheet.
        * **📬 Data Shares (S):** Scans selected columns for cell matches matching **'S'** (Active Sender profile).
        * **📩 Data Receives (R):** Scans selected columns for cell matches matching **'R'** (Active Receiver profile).
        * **🚫 Data Blocked (B):** Pinpoints operational, legal, or systemic pipeline bottlenecks starting with the letter **'B'**.
        * **💡 How to Read:** Select a dynamic industry role profile to audit individual performance indices, or pair two different roles to model systemic supply chain data loops.
        """)

    if not df_planning.empty:
        industry_roles = [col for col in ['Manufacturer', 'Specialty Retail', 'Wholesaler', 'Retailer'] if col in df_planning.columns]
        
        st.markdown("### 📌 Individual Role Audit", help="Isolates the data behavior signatures for a single selected vertical profile.")
        selected_role = st.selectbox("🎯 Select Industry Role to Profile:", industry_roles, key="single_role")
        
        df_clean_counts = df_planning[
            ~df_planning['Metric'].astype(str).str.contains(r'Planning|Total|%|=', case=False, na=False) & 
            ~df_planning[selected_role].astype(str).str.contains('%')
        ]
        
        series_clean = df_clean_counts[selected_role].astype(str).str.strip().str.upper()
        shares_count = sum(series_clean == 'S')
        receives_count = sum(series_clean == 'R')
        blocked_count = sum(series_clean.str.startswith('B', na=False))
        total_metrics = len(df_clean_counts)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📬 Data Shares Rows (S)", f"{shares_count}", help="Quantity of audited workflows where this profile serves as the active sender.")
        m2.metric("📩 Data Receives Rows (R)", f"{receives_count}", help="Quantity of workflows where this profile absorbs inbound external data fields.")
        m3.metric("🚫 Data Blocked Rows (B or B/PL)", f"{blocked_count}", delta=f"{blocked_count} barriers" if blocked_count > 0 else "Clean", delta_color="inverse", help="Active structural or legal blockages observed during interviews.")
        m4.metric("📊 Total Profiled Capabilities", f"{total_metrics}")

        st.markdown("---")
        st.markdown("### 🔄 Cross-Industry Ecosystem Collaboration Matrix")
        
        # Wrapped structural architecture explanation inside an unfoldable expander component
        with st.expander("📖 View Guide: Understanding Data Asymmetry & Hand-off Gaps", expanded=False):
            st.markdown("""
            > **🧠 System Architecture Insight: Understanding Data Asymmetry & Hand-off Gaps**
            > This simulator maps data health by evaluating supply chain hand-offs between an upstream data provider (**Sender**) and a downstream consumer (**Receiver**):
            > * **🤝 Perfect Collaboration Loop:** Achieved when the Sender actively broadcasts information (**S**) and the corresponding Receiver is architected to digest it (**R**). This implies zero data friction.
            > * **🚫 Active Friction / Blocked Rows:** Indicates systemic gridlocks. This happens when either party explicitly locks access due to strict operational limitations or private-label legal constraints (**B** or **B/PL**).
            > * **⚠️ Structural Gaps / Unused Data:** Occurs when there is an unaligned operational status (e.g., both parties are trying to receive but no one is sending, or data is broadcast but completely ignored downstream). This creates critical operational blindspots.
            """, unsafe_allow_html=True)

        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            role_a = st.selectbox("Sender / Supplier Role:", industry_roles, index=0, key="role_a")
        with comp_col2:
            default_idx = 1 if len(industry_roles) > 1 else 0
            role_b = st.selectbox("Receiver / Partner Role:", industry_roles, index=default_idx, key="role_b")

        columns_to_display = ['Metric']
        
        if role_a == role_b:
            st.info("💡 Select two different roles to evaluate systemic supply-chain pipeline handoffs.")
            columns_to_display += industry_roles
        else:
            columns_to_display += [role_a, role_b]
            
            status_a = df_clean_counts[role_a].astype(str).str.strip().str.upper()
            status_b = df_clean_counts[role_b].astype(str).str.strip().str.upper()

            perfect_collaboration = sum((status_a == 'S') & (status_b == 'R'))
            system_blocked = sum(status_a.str.startswith('B', na=False) | status_b.str.startswith('B', na=False))
            data_gap = total_metrics - (perfect_collaboration + system_blocked)

            c_split1, c_split2, c_split3 = st.columns(3)
            c_split1.metric("🤝 Perfect Collaboration Pipeline Rows", f"{perfect_collaboration}", help="Frictionless alignment rows where Role A actively broadcasts data (S) and Role B is ready to ingest it (R).")
            c_split2.metric("🚫 Active Friction / Blocked Rows", f"{system_blocked}", help="Pipeline disconnects where either role explicitly locks access via an active 'B' or 'B/PL' constraint row.")
            c_split3.metric("⚠️ Structural Gaps / Unused Data", f"{data_gap}", help="Data loop inefficiencies where data channels are disconnected or unutilized.")

        st.markdown("---")
        st.markdown("### 🗂️ Complete Alignment Audit Matrix")
        
        matrix_layout_col, legend_layout_col = st.columns([78, 22])
        df_filtered_matrix = df_planning[columns_to_display].copy()

        def format_cell_values(val):
            if pd.isna(val) or str(val).strip() in ['nan', '-', '—']: return "—"
            val_str = str(val).strip()
            try:
                if float(val_str) <= 1.0 and '.' in val_str: return f"{int(float(val_str) * 100)}%"
            except ValueError: pass
            return val_str

        for col in df_filtered_matrix.columns:
            if col != 'Metric': df_filtered_matrix[col] = df_filtered_matrix[col].apply(format_cell_values)

        def style_matrix_cells(row):
            styles = []
            metric_val = str(row['Metric']).strip()
            is_category_header = any(keyword in metric_val.lower() for keyword in ['planning', 'promotions', 'logistics', 'supply chain', 'inventory']) or ('phase' not in metric_val.lower() and row.drop('Metric').astype(str).str.contains('%').any())
            
            for col in df_filtered_matrix.columns:
                if col == 'Metric':
                    if is_category_header: styles.append('background-color: #1e293b; color: #ffffff; font-weight: bold; font-size: 15px;')
                    else: styles.append('font-weight: 500; color: #0f172a;')
                else:
                    cell_val = str(row[col]).strip().upper()
                    if '%' in cell_val: styles.append('background-color: #f1f5f9; color: #334155; font-weight: bold; text-align: center; border-bottom: 2px solid #cbd5e1;')
                    elif is_category_header: styles.append('background-color: #f1f5f9; color: #334155; font-weight: bold; text-align: center;')
                    elif cell_val == 'R': styles.append('background-color: #d1fae5; color: #065f46; font-weight: bold; text-align: center;')
                    elif cell_val == 'S': styles.append('background-color: #fef3c7; color: #92400e; font-weight: bold; text-align: center;')
                    elif cell_val.startswith('B'): styles.append('background-color: #fee2e2; color: #991b1b; font-weight: bold; text-align: center;')
                    else: styles.append('color: #94a3b8; text-align: center;')
            return styles

        with matrix_layout_col:
            styled_planning = df_filtered_matrix.style.apply(style_matrix_cells, axis=1)
            st.dataframe(styled_planning, use_container_width=True, hide_index=True, height=580)
        
        with legend_layout_col:
            with st.container(border=True):
                st.markdown("🗺️ **Ledger Legend**")
                legend_data = {
                    "Key": ["🟢 R", "🟡 S", "🔴 B", "🟤 B/PL", "🔵 —"],
                    "Status": ["Receives", "Shares", "Blocked", "Private Label Only", "Not Relevant"]
                }
                st.table(pd.DataFrame(legend_data))
                st.markdown("""
                **💡 Strategic Guide:**
                * **Percentage Meanings:** The values rowed beneath dark category bars indicate the percent ratio of interviewees who defined that domain as a major strategic priority.
                """)
    else:
        st.warning("Scorecard Planning table data is currently unreadable or empty.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("ℹ️ **Data Footnote:** The results come from interviews to retailers, manufacturers and wholesalers which responses were added to the table above.")

# ====================================================
# TAB 4: PERFORMANCE SCORECARD PLAYBOOK
# ====================================================
elif view_mode == "🎯 Performance Scorecard Playbook":
    st.subheader("🎯 Data Sharing Performance Scorecard Playbook")
    
    st.info("""
    **📖 Welcome to the Performance Scorecard Playbook!**
    This panel defines the strict, binding operational thresholds (SLAs) required to convert raw data sharing agreements into high-velocity supply chain executions.
    """, icon="ℹ️")

    with st.expander("📖 View Guide: Metric Definitions & Penalties", expanded=False):
        st.markdown("""
* **📂 Data Source:** Model protocols built around standard partner data integration contracts.
* **🟢 Healthy / 🟡 Warning / 🔴 Critical:** Color indicators mapping whether current actual transmission loops meet contractual expectations.
* **⚠️ Non-Compliance Penalty Impacts:** Explains the real strategic or financial drawbacks applied to individual partners if data completeness or latency boundaries are violated.

* ** Note: This is a real life example of how  a scorecard could look like between twop parties and is derived from research with the help of AI*
        """)
    
    scorecard_data = {
        "Strategic Domain": ["Data Quality", "Data Quality", "Alignment Velocity", "Alignment Velocity"],
        "Performance Indicator (KPI)": ["API Transmission Completeness", "Inventory Discrepancy Margin", "Promo Sell-Out Refresh Frequency", "Post-Campaign Processing Turnaround"],
        "Target SLA": [">= 99.5%", "<= 1.5%", "Real-time / Hourly", "<= 48 Hours"],
        "Current Actual": ["99.8%", "3.2%", "Daily Batch", "72 Hours"],
        "Execution Health": ["🟢 Healthy", "🔴 Critical Friction", "🟡 Warning", "🟡 Warning"],
        "Non-Compliance Penalty Impact": ["None (SLA Compliant)", "⚠️ 1.5% Trade Allowance Penalty Applied", "Warning Logged", "Warning Logged"]
    }
    df_sc = pd.DataFrame(scorecard_data)
    st.dataframe(df_sc, use_container_width=True, hide_index=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("ℹ️ **Data Footnote:** Performance standards and SLA penalty matrices are modeled based on standard industry supply-chain vendor compliance agreements and retail data governance literature.")

# ====================================================
# TAB 5: TRIPLE-WIN DATA COLLABORATION FRAMEWORK
# ====================================================
elif view_mode == "🏆 Triple-Win Strategic Matrix":

    st.subheader("🏆 Triple-Win Data Collaboration Framework")

    st.info("""
    This framework demonstrates how data sharing creates value across the ecosystem.
    
    For each stakeholder perspective:
    
    1. Data is shared
    2. Insights are generated
    3. Actions are taken
    4. Value is created for all parties
    
    The objective is to illustrate how collaboration can create a 'triple win' for:
    
    • Data Contributor
    • Business Partner
    • Shopper / End Customer
    """, icon="ℹ️")

    perspective = st.selectbox(
        "🎯 Select Data Contributor",
        [
            "Retailer Shares Data",
            "Manufacturer Shares Data",
            "Specialty Retailer Shares Data",
            "Wholesaler Shares Data"
        ]
    )

    framework = {

        "Retailer Shares Data": {

            "data_shared": [
                "Point-of-sale transactions",
                "Inventory levels",
                "Loyalty card insights",
                "Basket composition data"
            ],

            "insights": [
                "True consumer demand visibility",
                "Store-level demand patterns",
                "Promotion effectiveness",
                "Regional buying trends"
            ],

            "actions": [
                "Manufacturer adjusts production",
                "Improved assortment planning",
                "Targeted promotions",
                "Inventory optimization"
            ],

            "retailer_win": [
                "Improved supplier collaboration",
                "Reduced inventory holding costs",
                "Higher category performance"
            ],

            "manufacturer_win": [
                "Better forecasting accuracy",
                "More efficient production planning",
                "Improved trade-spend effectiveness"
            ],

            "shopper_win": [
                "Better product availability",
                "More relevant promotions",
                "Improved shopping experience"
            ],

            "evidence": [
                {
                    "metric": "Forecast Accuracy Improvement",
                    "impact": "15–30%",
                    "source": "McKinsey Supply Chain Analytics Research"
                },
                {
                    "metric": "Inventory Reduction",
                    "impact": "10–20%",
                    "source": "McKinsey"
                },
                {
                    "metric": "Stockout Reduction",
                    "impact": "20–50%",
                    "source": "Gartner"
                }
            ]
        },

        "Manufacturer Shares Data": {

            "data_shared": [
                "Production forecasts",
                "Product availability",
                "Innovation pipeline",
                "Marketing calendars"
            ],

            "insights": [
                "Future supply visibility",
                "Launch planning opportunities",
                "Promotional alignment",
                "Demand forecasting synchronization"
            ],

            "actions": [
                "Retailers adjust inventory",
                "Launch planning optimization",
                "Shelf-space allocation",
                "Improved replenishment scheduling"
            ],

            "retailer_win": [
                "Reduced out-of-stock risk",
                "Improved assortment planning",
                "Better promotional execution"
            ],

            "manufacturer_win": [
                "Higher sell-through",
                "Improved product launches",
                "Better trade ROI"
            ],

            "shopper_win": [
                "Access to new products",
                "Better availability",
                "More consistent shopping experience"
            ],

            "evidence": [
                {
                    "metric": "On-Shelf Availability Improvement",
                    "impact": "5–15%",
                    "source": "Accenture Consumer Goods Research"
                },
                {
                    "metric": "Supply Chain Cost Reduction",
                    "impact": "5–15%",
                    "source": "Accenture"
                },
                {
                    "metric": "Promotion Effectiveness Improvement",
                    "impact": "10–30%",
                    "source": "Deloitte"
                }
            ]
        },

        "Specialty Retailer Shares Data": {

            "data_shared": [
                "Customer preferences",
                "Consultation outcomes",
                "Product recommendation data",
                "Local market trends"
            ],

            "insights": [
                "Niche consumer needs",
                "Emerging category trends",
                "Product fit insights",
                "Segment-specific demand patterns"
            ],

            "actions": [
                "Targeted innovation",
                "Personalized merchandising",
                "Product assortment refinement",
                "Localized inventory allocation"
            ],

            "retailer_win": [
                "Reduced markdowns",
                "Improved conversion rates",
                "Higher category profitability"
            ],

            "manufacturer_win": [
                "Better product development",
                "Improved customer understanding",
                "Higher innovation success rates"
            ],

            "shopper_win": [
                "Personalized recommendations",
                "More relevant products",
                "Enhanced shopping journey"
            ],

            "evidence": [
                {
                    "metric": "Markdown Reduction",
                    "impact": "10–20%",
                    "source": "Deloitte Retail Analytics"
                },
                {
                    "metric": "Conversion Improvement",
                    "impact": "5–15%",
                    "source": "McKinsey Personalization Research"
                },
                {
                    "metric": "Customer Satisfaction Increase",
                    "impact": "10–20%",
                    "source": "PwC Consumer Intelligence"
                }
            ]
        },

        "Wholesaler Shares Data": {

            "data_shared": [
                "Regional demand trends",
                "Distribution inventory",
                "Shipment performance",
                "Cross-retailer demand signals"
            ],

            "insights": [
                "Network-wide demand visibility",
                "Supply bottlenecks",
                "Regional demand shifts",
                "Inventory imbalances"
            ],

            "actions": [
                "Improved replenishment planning",
                "Production optimization",
                "Regional inventory balancing",
                "Logistics optimization"
            ],

            "retailer_win": [
                "Improved supply reliability",
                "Lower inventory risk",
                "Faster replenishment"
            ],

            "manufacturer_win": [
                "Better demand visibility",
                "More efficient production scheduling",
                "Reduced logistics costs"
            ],

            "shopper_win": [
                "Reduced stockouts",
                "Stable product availability",
                "Consistent pricing"
            ],

            "evidence": [
                {
                    "metric": "Inventory Carrying Cost Reduction",
                    "impact": "10–30%",
                    "source": "Gartner Supply Chain Research"
                },
                {
                    "metric": "Service Level Improvement",
                    "impact": "5–15%",
                    "source": "Accenture Logistics Research"
                },
                {
                    "metric": "Stockout Reduction",
                    "impact": "20–50%",
                    "source": "Gartner"
                }
            ]
        }
    }

    selected = framework[perspective]

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 📊 Data Shared")
        for item in selected["data_shared"]:
            st.write(f"• {item}")

    with c2:
        st.markdown("### 💡 Insights Generated")
        for item in selected["insights"]:
            st.write(f"• {item}")

    with c3:
        st.markdown("### ⚙️ Actions Enabled")
        for item in selected["actions"]:
            st.write(f"• {item}")

    st.markdown("---")

    st.markdown("## 🏆 Triple-Win Outcomes")

    w1, w2, w3 = st.columns(3)

    with w1:
        st.success("🏪 Retailer Win")
        for item in selected["retailer_win"]:
            st.write(f"• {item}")

    with w2:
        st.success("🏭 Manufacturer Win")
        for item in selected["manufacturer_win"]:
            st.write(f"• {item}")

    with w3:
        st.success("🛒 Shopper Win")
        for item in selected["shopper_win"]:
            st.write(f"• {item}")

    st.markdown("---")

    st.markdown("## 📚 Supporting Research Evidence")

    evidence_df = pd.DataFrame(selected["evidence"])

    st.dataframe(
        evidence_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption("""
    Notes:
    
    • Impact ranges shown represent commonly reported benefits from analytics-enabled
      supply chain, retail collaboration, and demand-planning initiatives.
    
    • Results vary significantly based on industry, maturity, data quality,
      operating model, and implementation approach.
    
    • Sources come from expert interviews and research
    """)
