# =================================================
# TAB 3 — RESULTS (EXECUTIVE-FIRST LAYOUT)
# =================================================

import streamlit as st
import pandas as pd
import tempfile
import os

from core.config import QUANT_KPIS, ALL_KPIS, KPI_LABELS
from core.normalization import normalize

from ui.charts import (
    total_score_bar,
    configurable_radar,
    macro_radar,
    macro_stacked_bar,
    pareto_weights,
    kpi_variability,
    tornado_sensitivity,
    kpi_bar_chart,
)

from utils.pdf_export import export_mcda_snapshot
from ui.tab_input import get_input_summary
from ui.tab_normalization import get_norm_summary


# -------------------------------------------------
# MACRO DEFINITIONS
# -------------------------------------------------
MACRO_MAP = {
    "Performance": [
        "Volume_Occupation",
        "Boil_off",
        "Specific_Heat_Capacity",
        "Load_Bearing",
        "Resistance_to_Thermal_Deformations",
        "Adaptability_to_Tank_Shapes",
    ],
    "Safety": [
        "Fire_Resistance",
        "Air_Condensation_Avoidance",
        "FMECA_Score",
        "Health_Risk_for_Workers",
    ],
    "Producibility": [
        "LCA",
        "CAPEX",
        "OPEX",
        "Commercial_Uptake",
    ],
}


def render():

    # =================================================
    # SAFETY CHECK
    # =================================================
    if sum(st.session_state["weights"].values()) == 0:
        st.error("All KPI weights are zero.")
        st.stop()

    # =================================================
    # NORMALIZATION PIPELINE
    # =================================================

    # --- LCA
    df_lca = st.session_state["LCA_raw"]
    cfg_lca = st.session_state["norm_config"]["LCA"]
    df_lca_norm = df_lca.apply(lambda c: normalize(c, **cfg_lca))
    lca_scores = df_lca_norm.mean(axis=0)

    # --- Quantitative KPIs
    df_qn = pd.DataFrame(index=st.session_state["quantitative_data"].index)
    for kpi in QUANT_KPIS:
        cfg = st.session_state["norm_config"][kpi]
        df_qn[kpi] = normalize(
            st.session_state["quantitative_data"][kpi],
            **cfg
        )

    # --- Qualitative KPIs
    df_qln = st.session_state["qualitative_data"].apply(
        lambda c: normalize(c, "qualitative")
    )

    # --- Aggregate table
    df_total = pd.concat(
        [lca_scores.rename("LCA"), df_qn, df_qln],
        axis=1
    )

    total_weight = sum(st.session_state["weights"].values())
    df_total["Total Score"] = (
        sum(df_total[k] * st.session_state["weights"][k] for k in ALL_KPIS)
        / total_weight
    )

    df_total_sorted = df_total.sort_values("Total Score", ascending=False)
    
    # =================================================
    # MACRO-CATEGORY TABLE (for PDF export)
    # =================================================
    df_macro = pd.DataFrame(index=df_total.index)

    for macro, kpis in MACRO_MAP.items():
        df_macro[macro] = df_total[kpis].mul(
            [st.session_state["weights"][k] for k in kpis], axis=1
        ).sum(axis=1)

    # scale so that sum of macros = Total Score
    scaling = df_total["Total Score"] / df_macro.sum(axis=1)
    df_macro = df_macro.mul(scaling, axis=0)

    # keep same ordering as total score ranking
    df_macro_sorted = df_macro.loc[df_total_sorted.index]

    # =================================================
    # HERO SECTION — EXECUTIVE SUMMARY
    # =================================================
    st.markdown("## Executive summary")

    col_summary, col_charts = st.columns([0.6, 1.8])

    # =================================================
    # LEFT — KPI WINNER SUMMARY (STRETCHED + INDENTED)
    # =================================================
    with col_summary:
        summary_box = st.container(border=True)

        with summary_box:
            # --- Internal indentation via spacer column
            pad, content = st.columns([0.04, 0.92])

            with pad:
                st.write("")

            with content:
                # --- Ranking
                winner = df_total_sorted.index[0]
                second = df_total_sorted.index[1]

                winner_score = df_total_sorted.iloc[0]["Total Score"]
                second_score = df_total_sorted.iloc[1]["Total Score"]
                delta_vs_second = winner_score - second_score

                # --- Macro averages
                macro_scores = {}
                macro_deltas = {}

                for macro, kpis in MACRO_MAP.items():
                    macro_df = df_total[kpis].mean(axis=1)
                    macro_scores[macro] = macro_df[winner]
                    macro_deltas[macro] = macro_df[winner] - macro_df[second]

                # --- Vertical spacing
                st.write("")
                st.write("")

                # =================================================
                # BEST CONCEPT + RANK BADGE
                # =================================================
                col_name, col_rank = st.columns([0.75, 0.25])

                with col_name:
                    st.metric(
                        label="BEST CONCEPT",
                        value=winner,
                    )

                with col_rank:
                    st.markdown(
                        ":green[**1st**]",
                        help="Top-ranked concept based on total score",
                    )

                st.write("")

                # =================================================
                # TOTAL SCORE
                # =================================================
                st.metric(
                    label="TOTAL SCORE",
                    value=f"{winner_score:.1f}",
                    delta=f"{delta_vs_second:+.1f} pts vs #2",
                )

                st.divider()

                # =================================================
                # MACRO SUMMARY
                # =================================================
                st.caption("Macro-category performance (vs #2)")

                col_p, col_s, col_r = st.columns(3)

                with col_p:
                    st.metric(
                        label="Performance",
                        value=f"{macro_scores['Performance']:.1f}",
                        delta=f"{macro_deltas['Performance']:+.1f}",
                    )

                with col_s:
                    st.metric(
                        label="Safety",
                        value=f"{macro_scores['Safety']:.1f}",
                        delta=f"{macro_deltas['Safety']:+.1f}",
                    )

                with col_r:
                    st.metric(
                        label="Producibility",
                        value=f"{macro_scores['Producibility']:.1f}",
                        delta=f"{macro_deltas['Producibility']:+.1f}",
                    )

                # --- Bottom spacing to stretch box
                st.write("")
                st.write("")
                st.write("")
                st.write("")

    # ---------------- HERO CHARTS (SIDE BY SIDE) ----------------
    with col_charts:

        col_bar, col_radar = st.columns([1.1, 1])

        # --- Total score bar chart
        with col_bar:
            st.plotly_chart(
                total_score_bar(df_total_sorted),
                use_container_width=True
            )

        # --- Radar chart
        with col_radar:

            radar_mode = st.selectbox(
                "Radar view:",
                options=[
                    "Performance",
                    "Safety",
                    "Producibility",
                    "Custom selection",
                ],
                key="hero_radar_mode"
            )

            if radar_mode == "Custom selection":
                radar_kpis = st.multiselect(
                    "Select KPIs",
                    options=[k for k in ALL_KPIS if k != "Total Score"],
                    default=MACRO_MAP["Performance"],
                    format_func=lambda k: KPI_LABELS.get(k, k),
                    key="hero_radar_kpis"
                )
            else:
                radar_kpis = MACRO_MAP[radar_mode]

            if len(radar_kpis) < 3:
                st.info("Select at least **3 KPIs** to display the radar chart.")
            else:
                st.plotly_chart(
                    configurable_radar(
                        df_total=df_total,
                        kpis=radar_kpis,
                        title=f"{radar_mode} radar",
                    ),
                    use_container_width=True
                )

    # =================================================
    # MACRO INSIGHTS
    # =================================================
    st.markdown("---")
    st.markdown("## Macro-level insights")

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.plotly_chart(
            macro_radar(df_total, MACRO_MAP),
            use_container_width=True
        )

    with col_m2:
        st.plotly_chart(
            macro_stacked_bar(df_total, st.session_state["weights"]),
            use_container_width=True
        )

    # =================================================
    # KPI EXPLORER
    # =================================================
    st.markdown("---")
    st.markdown("## KPI explorer")

    mode_label = st.radio(
        "",
        options=["Pre-normalization", "Post-normalization"],
        horizontal=True,
    )

    display_mode = "raw" if mode_label == "Pre-normalization" else "normalized"

    raw_q = st.session_state["quantitative_data"]
    norm_q = df_qn

    KPI_UNITS = {
        "CAPEX": "€",
        "OPEX": "€",
        "Volume_Occupation": "m³",
        "Boil_off": "W/m²",
        "Specific_Heat_Capacity": "kJ/kgK",
        "Load_Bearing": "kN",
        "LCA": "",
    }

    explorer_kpis = ["LCA"] + QUANT_KPIS

    cols = st.columns(4)
    col_idx = 0

    for kpi in explorer_kpis:
        label = KPI_LABELS.get(kpi, kpi)
        unit = KPI_UNITS.get(kpi, "")

        with cols[col_idx].container(border=True):

            if kpi == "LCA":
                raw_series = df_lca.mean(axis=0)
                norm_series = lca_scores
            else:
                raw_series = raw_q[kpi]
                norm_series = norm_q[kpi]

            st.plotly_chart(
                kpi_bar_chart(
                    kpi_name=label,
                    raw_series=raw_series,
                    norm_series=norm_series,
                    mode=display_mode,
                    unit=unit,
                ),
                use_container_width=True,
            )

        col_idx += 1
        if col_idx == 4:
            cols = st.columns(4)
            col_idx = 0

    # =================================================
    # SENSITIVITY & ROBUSTNESS
    # =================================================
    st.markdown("---")
    st.markdown("## Sensitivity & robustness")

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.plotly_chart(
            pareto_weights(st.session_state["weights"]),
            use_container_width=True,
        )

    with col_s2:
        st.plotly_chart(
            kpi_variability(df_total, st.session_state["weights"]),
            use_container_width=True,
        )

    st.plotly_chart(
        tornado_sensitivity(df_total, st.session_state["weights"]),
        use_container_width=True,
    )


    # =================================================
    # EXPORT
    # =================================================
    st.markdown("---")
    st.markdown("## Export")

    if st.button("Export MCDA snapshot (PDF)"):

        with st.spinner("Generating PDF snapshot..."):

            # --- Collect summaries (tables only)
            df_inputs = get_input_summary()
            df_norm = get_norm_summary()

            # --- Metadata
            from datetime import datetime

            metadata = {
                "Tool": "Internal MCDA Tool",
                "Snapshot": "MCDA Configuration Snapshot",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }

            # --- Timestamped filename
            filename = f"MCDA_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf"

            # --- Temporary file for export
            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False,
            ) as tmp_pdf:

                export_mcda_snapshot(
                    output_path=tmp_pdf.name,
                    metadata=metadata,
                    df_inputs=df_inputs,
                    df_norm=df_norm,
                    df_total_sorted=df_total_sorted,
                    df_macro_sorted=df_macro_sorted,
                )

                # --- Download button
                with open(tmp_pdf.name, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf",
                    )

            # --- Cleanup
            os.unlink(tmp_pdf.name)