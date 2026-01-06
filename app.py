# app.py
import streamlit as st

from core.state import init_session_state

from ui.tab_input import render as render_tab_input
from ui.tab_normalization import render as render_tab_normalization
from ui.tab_results import render as render_tab_results



# =================================================
# PAGE CONFIGURATION
# =================================================
st.set_page_config(
    page_title="MCDA – Multi-Criteria Decision Making Analysis",
    layout="wide"
)

# =================================================
# LOAD GLOBAL CSS
# =================================================
with open("styles/theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =================================================
# TITLE
# =================================================
st.markdown("# MCDA – Multi-Criteria Decision Making Analysis")

# =================================================
# INIT STATE
# =================================================
init_session_state()

# =================================================
# TABS
# =================================================

tab_input, tab_norm, tab_results = st.tabs(
    ["1️⃣ INPUT", "2️⃣ NORMALIZATION & WEIGHTS", "3️⃣ RESULTS"]
)

with tab_input:
    render_tab_input()

with tab_norm:
    render_tab_normalization()

with tab_results:
    render_tab_results()