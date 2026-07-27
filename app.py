import streamlit as st
import pandas as pd
from monday_client import LAST_FETCH_WARNINGS, fetch_monday_board_data
from agent import query_bi_agent, generate_leadership_briefing

# 1. Page Configuration
st.set_page_config(
    page_title="Skylark Drones | Executive BI Console",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive UI polish
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)


# 2. Session State Initialization
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "deals_df" not in st.session_state:
        st.session_state.deals_df = pd.DataFrame()
    if "work_orders_df" not in st.session_state:
        st.session_state.work_orders_df = pd.DataFrame()
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
    if "data_warnings" not in st.session_state:
        st.session_state.data_warnings = []
    if "selected_data_view" not in st.session_state:
        st.session_state.selected_data_view = "deals"


def load_data(force_reload: bool = False):
    if not st.session_state.data_loaded or force_reload:
        with st.spinner("Syncing Monday.com boards..."):
            try:
                deals, work_orders = fetch_monday_board_data()
                st.session_state.deals_df = deals
                st.session_state.work_orders_df = work_orders
                st.session_state.data_warnings = LAST_FETCH_WARNINGS.copy()
                st.session_state.data_loaded = True
                if deals.empty and work_orders.empty:
                    st.warning("Monday.com sync completed, but no board data was returned.")
                else:
                    st.toast("Data synchronized successfully!", icon="✅")
            except Exception as e:
                st.session_state.data_warnings = [str(e)]
                st.error(f"Error synchronizing data from Monday.com: {e}")


init_session()

# Auto-load on startup, including sessions that cached an empty result before a fix.
if (
    not st.session_state.data_loaded
    or (
        st.session_state.deals_df.empty
        and st.session_state.work_orders_df.empty
        and not st.session_state.data_warnings
    )
):
    load_data()


# 3. Sidebar Controls
with st.sidebar:
    st.title("🛸 Skylark BI")
    st.caption("Executive Intelligence Assistant")
    st.divider()

    # Sync Button
    if st.button("🔄 Sync Monday.com Data", use_container_width=True, type="secondary"):
        load_data(force_reload=True)

    st.divider()
    
    # Quick Prompt Shortcuts
    st.markdown("### 💡 Quick Prompts")
    prompts = [
        "How's our pipeline looking for the Mining sector?",
        "What are our top 3 open deals by value?",
        "Show operational status across work orders.",
        "Highlight any deals with unassigned owners or missing dates."
    ]
    for q in prompts:
        if st.button(q, use_container_width=True):
            st.session_state.pending_query = q

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# 4. Main Executive Dashboard Header
st.title("Executive Intelligence Console")

sync_col, deal_btn, work_order_btn = st.columns([1, 1, 1])
with sync_col:
    if st.button("Sync Monday.com Data", use_container_width=True, type="primary"):
        load_data(force_reload=True)
with deal_btn:
    if st.button("Deal Data", use_container_width=True):
        st.session_state.selected_data_view = "deals"
with work_order_btn:
    if st.button("Work Order Data", use_container_width=True):
        st.session_state.selected_data_view = "work_orders"

for warning in st.session_state.data_warnings:
    st.warning(warning)

if st.session_state.selected_data_view == "deals":
    st.markdown("#### Deal Data")
    if not st.session_state.deals_df.empty:
        st.dataframe(st.session_state.deals_df, use_container_width=True)
        st.caption(f"Total Rows: {len(st.session_state.deals_df)}")
    else:
        st.warning("No Deals data loaded. Click 'Sync Monday.com Data' in the sidebar.")
else:
    st.markdown("#### Work Order Data")
    if not st.session_state.work_orders_df.empty:
        st.dataframe(st.session_state.work_orders_df, use_container_width=True)
        st.caption(f"Total Rows: {len(st.session_state.work_orders_df)}")
    else:
        st.info("No Work Orders data returned or configured.")

st.divider()

# 5. Dashboard Tabbed Navigation
chat_tab, briefing_tab = st.tabs([
    "💬 AI Executive Copilot", 
    "📑 Leadership Briefings"
])


# --- TAB 1: AI COPILOT ---
with chat_tab:
    st.subheader("Interactive Pipeline Assistant")
    
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle incoming input
    user_input = st.chat_input("Ask a question about sales pipeline, revenue, or operations...")
    if "pending_query" in st.session_state:
        user_input = st.session_state.pop("pending_query")

    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing Monday.com records..."):
                response_text = query_bi_agent(
                    user_input, 
                    st.session_state.deals_df, 
                    st.session_state.work_orders_df
                )
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})


# --- TAB 2: LEADERSHIP BRIEFING GENERATOR ---
with briefing_tab:
    st.subheader("Automated Executive Updates")
    st.caption("Generate tailored summaries for leadership meetings based on active data.")
    
    b_col1, b_col2 = st.columns([1, 2])
    
    with b_col1:
        st.markdown("#### Briefing Parameters")
        
        # Sector selector based on active dataframe
        available_sectors = ["All"]
        if not st.session_state.deals_df.empty and "Sector" in st.session_state.deals_df.columns:
            unique_sectors = [s for s in st.session_state.deals_df["Sector"].dropna().unique() if s != "Unassigned / Unknown"]
            available_sectors.extend(sorted(unique_sectors))
            
        selected_sectors = st.multiselect("Target Sectors", available_sectors, default=["All"])
        selected_period = st.selectbox("Reporting Period", ["Current Quarter", "Year to Date", "Monthly Focus"])
        
        if st.button("🚀 Generate Briefing", type="primary", use_container_width=True):
            with st.spinner("Compiling executive summary..."):
                briefing_res = generate_leadership_briefing(
                    st.session_state.deals_df, 
                    st.session_state.work_orders_df, 
                    selected_sectors, 
                    selected_period
                )
                st.session_state.current_briefing = briefing_res

    with b_col2:
        st.markdown("#### Generated Executive Briefing")
        if "current_briefing" in st.session_state:
            st.info(st.session_state.current_briefing)
        else:
            st.write("Select parameters on the left and click **Generate Briefing** to create a structured report.")
