# =================================================
# PLOTLY CHARTS — EXECUTIVE DARK BASELINE
# =================================================

import plotly.graph_objects as go
import pandas as pd
import numpy as np

from core.config import KPI_LABELS


# -------------------------------------------------
# COMMON DARK LAYOUT
# -------------------------------------------------
def _dark_layout(title, y_title=None, x_title=None, height=350):

    return dict(
        title=dict(text=title, font=dict(color="white")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(
            title=x_title,
            gridcolor="rgba(255,255,255,0.15)"
        ),
        yaxis=dict(
            title=y_title,
            gridcolor="rgba(255,255,255,0.15)"
        )
    )


# =================================================
# TOTAL SCORE — BAR CHART (HERO)
# =================================================
def total_score_bar(df_total: pd.DataFrame):

    colors = [
        "lightgray" if idx == "Concept 0" else "#4c72b0"
        for idx in df_total.index
    ]

    fig = go.Figure(
        go.Bar(
            x=df_total.index,
            y=df_total["Total Score"],
            marker_color=colors
        )
    )

    fig.update_layout(
        **_dark_layout(
            title="Aggregated total score (weighted)",
            y_title="Total score (0–100)",
            height=500
        ),
        bargap=0.3,
    )


    fig.update_yaxes(range=[0, 100])
    return fig


# =================================================
# CONFIGURABLE RADAR — KPI SELECTION (PROPOSAL B)
# =================================================
def configurable_radar(
    df_total: pd.DataFrame,
    kpis: list,
    baseline: str = "Concept 0",
    title: str = "Radar chart"
):
    """
    Generic configurable radar chart.
    - kpis: list of KPI keys (columns in df_total)
    """


    labels = [KPI_LABELS.get(k, k) for k in kpis]

    angles = np.linspace(0, 2 * np.pi, len(kpis), endpoint=False).tolist()
    angles += angles[:1]

    fig = go.Figure()

    for concept in df_total.index:
        values = df_total.loc[concept, kpis].tolist()
        values += values[:1]

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels + [labels[0]],
                fill="toself",
                name=concept,
                line=dict(
                    dash="dash" if concept == baseline else "solid",
                    width=2
                ),
                opacity=0.85 if concept != baseline else 0.6
            )
        )

    fig.update_layout(
        title=dict(text=title, font=dict(color="white")),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(255,255,255,0.25)"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        height=430,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )

    return fig


# =================================================
# MACRO RADAR — PERFORMANCE / SAFETY / PRODUCIBILITY
# =================================================
def macro_radar(
    df_total: pd.DataFrame,
    macro_map: dict,
    baseline: str = "Concept 0"
):
    """
    macro_map example:
    {
        "Performance": [...],
        "Safety": [...],
        "Producibility": [...]
    }
    """

    df_macro = pd.DataFrame(index=df_total.index)

    for macro, kpis in macro_map.items():
        df_macro[macro] = df_total[kpis].mean(axis=1)

    labels = df_macro.columns.tolist()
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig = go.Figure()

    for concept in df_macro.index:
        values = df_macro.loc[concept].tolist()
        values += values[:1]

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels + [labels[0]],
                fill="toself",
                name=concept,
                line=dict(
                    dash="dash" if concept == baseline else "solid",
                    width=2
                ),
                opacity=0.85 if concept != baseline else 0.6
            )
        )

    fig.update_layout(
        title=dict(
            text="Macro-category radar",
            font=dict(color="white")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor="rgba(255,255,255,0.25)"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        height=420,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )

    return fig


# =================================================
# MACRO CATEGORIES — STACKED BAR
# =================================================
def macro_stacked_bar(df_total: pd.DataFrame, weights: dict):

    macro_map = {
        "Performance": [
            "Volume_Occupation", "Boil_off", "Specific_Heat_Capacity",
            "Resistance_to_Thermal_Deformations", "Load_Bearing",
            "Adaptability_to_Tank_Shapes"
        ],
        "Safety": [
            "Fire_Resistance", "Air_Condensation_Avoidance",
            "FMECA_Score", "Health_Risk_for_Workers"
        ],
        "Producibility": [
            "LCA", "CAPEX", "OPEX", "Commercial_Uptake"
        ]
    }

    df_macro = pd.DataFrame(index=df_total.index)

    for macro, kpis in macro_map.items():
        df_macro[macro] = df_total[kpis].mul(
            [weights[k] for k in kpis], axis=1
        ).sum(axis=1)

    scaling = df_total["Total Score"] / df_macro.sum(axis=1)
    df_macro = df_macro.mul(scaling, axis=0)

    colors = {
        "Performance": "#4c72b0",
        "Safety": "#dd8452",
        "Producibility": "#55a868"
    }

    fig = go.Figure()

    for macro in df_macro.columns:
        fig.add_bar(
            x=df_macro.index,
            y=df_macro[macro],
            name=macro,
            marker_color=colors[macro]
        )

    fig.update_layout(
        barmode="stack",
        **_dark_layout(
            title="Macro-category contribution (weighted)",
            y_title="Total score",
            height=380
        )
    )

    fig.update_yaxes(range=[0, 120])
    return fig


# =================================================
# KPI BAR CHART — CARD (RAW / NORMALIZED)
# =================================================
def kpi_bar_chart(
    kpi_name: str,
    raw_series: pd.Series,
    norm_series: pd.Series,
    mode: str = "raw",
    unit: str = ""
):

    if mode == "raw":
        y = raw_series
        y_title = f"{kpi_name} [{unit}]" if unit else kpi_name
    else:
        y = norm_series
        y_title = f"{kpi_name} score"

    colors = [
        "lightgray" if c == "Concept 0" else "#4c72b0"
        for c in y.index
    ]

    fig = go.Figure(
        go.Bar(
            x=y.index,
            y=y.values,
            marker_color=colors
        )
    )

    fig.update_layout(
        **_dark_layout(
            title=kpi_name,
            y_title=y_title,
            x_title="Concept",
            height=260
        )
    )

    return fig


# =================================================
# PARETO — KPI WEIGHTS
# =================================================
def pareto_weights(weights: dict):

    df = (
        pd.DataFrame.from_dict(weights, orient="index", columns=["Weight"])
        .sort_values("Weight", ascending=False)
    )

    labels = [KPI_LABELS.get(k, k) for k in df.index]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=df["Weight"],
            marker_color="#4c72b0"
        )
    )

    fig.update_layout(
        **_dark_layout(
            title="Pareto chart – KPI weights",
            y_title="Assigned weight",
            height=320
        )
    )

    return fig


# =================================================
# KPI VARIABILITY
# =================================================
def kpi_variability(df_total: pd.DataFrame, weights: dict):

    kpis = list(weights.keys())
    variability = df_total[kpis].std().sort_values(ascending=False)

    labels = [KPI_LABELS.get(k, k) for k in variability.index]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=variability.values,
            marker_color="#dd8452"
        )
    )

    fig.update_layout(
        **_dark_layout(
            title="KPI variability across concepts",
            y_title="Std. deviation (0–100)",
            height=320
        )
    )

    return fig


# =================================================
# TORNADO — SENSITIVITY
# =================================================
def tornado_sensitivity(df_total: pd.DataFrame, weights: dict):

    sensitivity = []

    for kpi, w in weights.items():

        w_plus = weights.copy()
        w_minus = weights.copy()

        w_plus[kpi] = w * 1.2
        w_minus[kpi] = w * 0.8

        total_plus = sum(
            df_total[k] * wv for k, wv in w_plus.items()
        ) / sum(w_plus.values())

        total_minus = sum(
            df_total[k] * wv for k, wv in w_minus.items()
        ) / sum(w_minus.values())

        sensitivity.append(
            (KPI_LABELS.get(kpi, kpi), total_plus.mean() - total_minus.mean())
        )

    df_tornado = pd.DataFrame(
        sensitivity, columns=["KPI", "Impact"]
    ).sort_values("Impact")

    fig = go.Figure(
        go.Bar(
            x=df_tornado["Impact"],
            y=df_tornado["KPI"],
            orientation="h",
            marker_color="#c44e52"
        )
    )

    fig.update_layout(
        **_dark_layout(
            title="Tornado chart – sensitivity to KPI weights",
            x_title="Δ average total score",
            height=360
        )
    )

    return fig

# =================================================
# KPI BAR CHART — CARD (RAW / NORMALIZED)
# =================================================
def kpi_bar_chart(
    kpi_name: str,
    raw_series: pd.Series,
    norm_series: pd.Series,
    mode: str = "raw",
    unit: str = ""
):

    if mode == "raw":
        y = raw_series
        y_title = f"{kpi_name} [{unit}]" if unit else kpi_name
    else:
        y = norm_series
        y_title = f"{kpi_name}"

    colors = [
        "lightgray" if c == "Concept 0" else "#4c72b0"
        for c in y.index
    ]

    fig = go.Figure(
        go.Bar(
            x=y.index,
            y=y.values,
            marker_color=colors
        )
    )

    # layout base
    fig.update_layout(
        **_dark_layout(
            title=kpi_name,
            y_title=y_title,
            height=260
        )
    )

    # 👉 modifica asse X SEPARATAMENTE
    fig.update_xaxes(
        tickangle=-45,
        gridcolor="rgba(255,255,255,0.15)"
    )

    return fig