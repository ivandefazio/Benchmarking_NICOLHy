# =================================================
# TAB 2 — NORMALIZATION & WEIGHTS (REFINED UI)
# =================================================

import streamlit as st
import pandas as pd

from core.config import QUANT_KPIS, ALL_KPIS, KPI_LABELS


# -------------------------------------------------
# TABLE STYLING HELPERS
# -------------------------------------------------
def style_norm_table(df: pd.DataFrame):

    def color_method(val):
        if val == "minmax":
            return "background-color: rgba(76,114,176,0.25);"
        if val == "target":
            return "background-color: rgba(85,168,104,0.25);"
        if val == "qualitative":
            return "background-color: rgba(129,114,179,0.25);"
        return ""

    def color_direction(val):
        if val == "maximize":
            return "color: #7bd389; font-weight: 600;"
        if val == "minimize":
            return "color: #ff7f7f; font-weight: 600;"
        return ""

    return (
        df.style
        .map(color_method, subset=["Method"])
        .map(color_direction, subset=["Direction"])
        .set_properties(**{"text-align": "left"})
        .set_table_styles(
            [
                {"selector": "th", "props": [("text-align", "left")]},
                {"selector": "td", "props": [("text-align", "left")]},
            ]
        )
        .format(
            {
                "Weight": "{:.0f}",
            }
        )
    )


def render():

    # =================================================
    # TOP SECTION — NORMALIZATION + WEIGHTS
    # =================================================
    col_left, col_right = st.columns(2)

    # ================= NORMALIZATION =================
    with col_left:
        with st.container(border=True):
            st.markdown("## Normalization settings")
            st.caption(
                "Define how each KPI is normalized. "
                "These assumptions determine how raw values are transformed."
            )

            # ---------- Quantitative KPIs ----------
            st.markdown("#### Quantitative KPIs")

            for kpi in ["LCA"] + QUANT_KPIS:
                label = KPI_LABELS[kpi]
                cfg = st.session_state["norm_config"][kpi]

                with st.expander(label):
                    method = st.selectbox(
                        "Normalization method",
                        ["minmax", "target"],
                        index=0 if cfg["method"] == "minmax" else 1,
                        key=f"{kpi}_method",
                    )

                    direction = st.selectbox(
                        "Optimization direction",
                        ["maximize", "minimize"],
                        index=0 if cfg["direction"] == "maximize" else 1,
                        key=f"{kpi}_direction",
                    )

                    target = None
                    if method == "target":
                        target = st.number_input(
                            "Target value",
                            value=cfg["target"] if cfg["target"] is not None else 1.0,
                            key=f"{kpi}_target",
                        )

                    # 🔒 single point of truth
                    st.session_state["norm_config"][kpi] = {
                        "method": method,
                        "direction": direction,
                        "target": target,
                    }

            # ---------- Qualitative KPIs ----------
            st.markdown("#### Qualitative KPIs")
            st.info("Fixed mapping: **1 → 0**  **5 → 100**")

    # ================= WEIGHTS =================
    with col_right:
        with st.container(border=True):
            st.markdown("## KPI Weights")
            st.caption(
                "Assign relative importance to each KPI. "
                "Weights directly affect the final MCDA score."
            )

            cols = st.columns(2)
            for i, kpi in enumerate(ALL_KPIS):
                label = KPI_LABELS[kpi]

                with cols[i % 2]:
                    st.session_state["weights"][kpi] = st.slider(
                        label,
                        0,
                        5,
                        value=st.session_state["weights"][kpi],
                        step=1,
                        key=f"weight_{kpi}",
                    )

    st.markdown("---")

    # =================================================
    # SUMMARY — AUDIT & TRANSPARENCY
    # =================================================
    with st.container(border=True):
        st.markdown("### Normalization & weights summary")
        st.caption(
            "Compact overview of the full MCDA configuration. "
            "Color cues highlight normalization logic and optimization intent."
        )

        summary_rows = []
        for kpi in ALL_KPIS:
            cfg = st.session_state["norm_config"][kpi]

            summary_rows.append(
                {
                    "KPI": KPI_LABELS[kpi],
                    "Weight": st.session_state["weights"][kpi],
                    "Method": cfg["method"],
                    "Direction": cfg["direction"],
                    "Target": cfg["target"] if cfg["target"] is not None else "–",
                }
            )

        df_summary = pd.DataFrame(summary_rows)

        st.dataframe(
            style_norm_table(df_summary),
            use_container_width=True,
        )


def get_norm_summary():
    """
    Technical summary for export / PDF (uses KPI keys, not labels)
    """
    rows = []

    for kpi in ALL_KPIS:
        cfg = st.session_state["norm_config"][kpi]
        rows.append(
            {
                "KPI": kpi,
                "Weight": st.session_state["weights"][kpi],
                "Method": cfg["method"],
                "Direction": cfg["direction"],
                "Target": cfg["target"],
            }
        )

    return pd.DataFrame(rows)
