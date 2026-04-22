# =================================================
# TAB 1 — INPUT
# =================================================

import streamlit as st
import numpy as np
import pandas as pd

from core.config import (
    CONFIGS,
    QUANT_KPIS,
    QUAL_KPIS,
    ALL_KPIS,
    LCA_CATEGORIES,
    KPI_LABELS,
)
from core.state import reset_to_nan


def render():

    # =================================================
    # QUICK ACTIONS
    # =================================================
    with st.container(border=True):
        st.markdown("#### Quick actions")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Fill all inputs with realistic random values"):
                st.session_state["LCA_raw"].iloc[:, :] = np.random.uniform(
                    5, 25, st.session_state["LCA_raw"].shape
                )

                st.session_state["quantitative_data"].iloc[:, :] = np.column_stack([
                    np.random.uniform(8e5, 1.3e6, len(CONFIGS)),
                    np.random.uniform(2.5e5, 4.5e5, len(CONFIGS)),
                    np.random.uniform(30, 70, len(CONFIGS)),
                    np.random.uniform(2.5, 6.0, len(CONFIGS)),
                    np.random.uniform(2.4, 3.2, len(CONFIGS)),
                    np.random.uniform(150, 220, len(CONFIGS)),
                ])

                st.session_state["qualitative_data"].iloc[:, :] = np.random.randint(
                    1, 6, st.session_state["qualitative_data"].shape
                )

                st.success("✅ All inputs randomly filled")

        with c2:
            if st.button("Reset all inputs (NaN)"):
                reset_to_nan()
                st.rerun()

    # =================================================
    # INPUT SECTIONS
    # =================================================
    col_q, col_div, col_ql = st.columns([3, 0.05, 3])

    def display_value(x, fallback=0.0):
        return fallback if pd.isna(x) else float(x)

    # ================= QUANTITATIVE =================
    with col_q:
        with st.container(border=True):
            st.markdown("#### Quantitative KPIs")

            # ---------- LCA ----------
            with st.expander(KPI_LABELS["LCA"]):
                for cat in LCA_CATEGORIES:
                    cols = st.columns([2] + [1] * len(CONFIGS))
                    cols[0].markdown(f"**{cat}**")

                    for c, concept in zip(cols[1:], CONFIGS):
                        key = f"LCA_{cat}_{concept}"

                        c.number_input(
                            concept,
                            value=display_value(
                                st.session_state["LCA_raw"].loc[cat, concept], 0.0
                            ),
                            key=key,
                            on_change=lambda c=cat, k=concept, key=key:
                                st.session_state["LCA_raw"].loc.__setitem__(
                                    (c, k), st.session_state[key]
                                ),
                        )

            # ---------- Other quantitative KPIs ----------
            for kpi in QUANT_KPIS:
                label = KPI_LABELS[kpi]
                with st.expander(label):
                    cols = st.columns(len(CONFIGS))
                    for c, concept in zip(cols, CONFIGS):
                        key = f"{kpi}_{concept}"

                        c.number_input(
                            concept,
                            value=display_value(
                                st.session_state["quantitative_data"].loc[concept, kpi],
                                0.0,
                            ),
                            key=key,
                            on_change=lambda kpi=kpi, cpt=concept, key=key:
                                st.session_state["quantitative_data"].loc.__setitem__(
                                    (cpt, kpi), st.session_state[key]
                                ),
                        )

    # ================= DIVIDER =================
    with col_div:
        st.markdown(
            "<div style='height:100%;border-left:1px solid rgba(255,255,255,0.15)'></div>",
            unsafe_allow_html=True,
        )

    # ================= QUALITATIVE =================
    with col_ql:
        with st.container(border=True):
            st.markdown("#### Qualitative KPIs")

            for kpi in QUAL_KPIS:
                label = KPI_LABELS[kpi]
                with st.expander(label):
                    cols = st.columns(len(CONFIGS))
                    for c, concept in zip(cols, CONFIGS):
                        key = f"{kpi}_{concept}"

                        c.slider(
                            concept,
                            1,
                            5,
                            value=(
                                3
                                if pd.isna(
                                    st.session_state["qualitative_data"].loc[concept, kpi]
                                )
                                else int(
                                    st.session_state["qualitative_data"].loc[concept, kpi]
                                )
                            ),
                            key=key,
                            on_change=lambda kpi=kpi, cpt=concept, key=key:
                                st.session_state["qualitative_data"].loc.__setitem__(
                                    (cpt, kpi), st.session_state[key]
                                ),
                        )

    # =================================================
    # INPUT SUMMARY
    # =================================================
    summary = pd.DataFrame(index=CONFIGS, columns=ALL_KPIS, dtype=float)

    summary["LCA"] = st.session_state["LCA_raw"].mean(axis=0)

    summary.loc[:, QUANT_KPIS] = (
        st.session_state["quantitative_data"]
        .reindex(index=CONFIGS, columns=QUANT_KPIS)
    )

    summary.loc[:, QUAL_KPIS] = (
        st.session_state["qualitative_data"]
        .reindex(index=CONFIGS, columns=QUAL_KPIS)
    )

    def highlight_missing(v):
        if pd.isna(v):
            return (
                "background-color: rgba(255, 99, 71, 0.35);"
                "color: #ffffff;"
                "font-weight: 600;"
            )
        return ""

    with st.container(border=True):
        st.markdown("### Input summary (all KPIs)")
        st.caption("Missing values are highlighted")

        completion = 100 * (1 - summary.isna().sum().sum() / summary.size)
        st.progress(int(completion))
        st.caption(f"Input completeness: {completion:.1f}%")

        summary_display = summary.rename(columns=KPI_LABELS)

        st.dataframe(
            summary_display
            .style
            .map(highlight_missing)
            .format("{:.2f}"),
            use_container_width=True,
        )

        missing_count = summary.isna().sum().sum()
        if missing_count > 0:
            st.warning(f"⚠️ {missing_count} KPI values are missing.")
        else:
            st.success("✅ All KPI inputs are complete.")


def get_input_summary():
    summary = pd.DataFrame(index=CONFIGS, columns=ALL_KPIS, dtype=float)

    summary["LCA"] = st.session_state["LCA_raw"].mean(axis=0)

    summary.loc[:, QUANT_KPIS] = (
        st.session_state["quantitative_data"]
        .reindex(index=CONFIGS, columns=QUANT_KPIS)
    )

    summary.loc[:, QUAL_KPIS] = (
        st.session_state["qualitative_data"]
        .reindex(index=CONFIGS, columns=QUAL_KPIS)
    )

    return summary.reset_index().rename(columns={"index": "Concept"})
