# core/state.py
import streamlit as st
import pandas as pd
import numpy as np
from core.config import CONFIGS, QUANT_KPIS, QUAL_KPIS, ALL_KPIS, LCA_CATEGORIES

def init_session_state():
    if "LCA_raw" not in st.session_state:
        st.session_state["LCA_raw"] = pd.DataFrame(
            np.nan, index=LCA_CATEGORIES, columns=CONFIGS
        )

    if "quantitative_data" not in st.session_state:
        st.session_state["quantitative_data"] = pd.DataFrame(
            np.nan, index=CONFIGS, columns=QUANT_KPIS
        )

    if "qualitative_data" not in st.session_state:
        st.session_state["qualitative_data"] = pd.DataFrame(
            np.nan, index=CONFIGS, columns=QUAL_KPIS
        )

    if "weights" not in st.session_state:
        st.session_state["weights"] = {k: 2 for k in ALL_KPIS}

    if "norm_config" not in st.session_state:
        st.session_state["norm_config"] = {
            kpi: {
                "method": "minmax" if kpi in QUANT_KPIS else "qualitative",
                "direction": "maximize",
                "target": None
            }
            for kpi in ALL_KPIS
        }
        st.session_state["norm_config"]["LCA"]["method"] = "target"


def reset_to_nan():
    st.session_state["LCA_raw"].loc[:] = np.nan
    st.session_state["quantitative_data"].loc[:] = np.nan
    st.session_state["qualitative_data"].loc[:] = np.nan