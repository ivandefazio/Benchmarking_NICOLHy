# utils/pdf_export.py

from typing import Optional, Dict
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from core.config import KPI_LABELS
from utils.pdf_charts import (
    total_score_bar_chart,
    total_score_legend_table,
    macro_category_bar_chart,
    macro_category_value_table,
)


# ============================================================
# DOCUMENT SETUP
# ============================================================

PAGE_SIZE = landscape(A4)

MARGINS = dict(
    leftMargin=15 * mm,
    rightMargin=15 * mm,
    topMargin=14 * mm,
    bottomMargin=14 * mm,
)


# ============================================================
# STYLES
# ============================================================

def build_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="PdfTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            spaceAfter=10,
        )
    )

    styles.add(
        ParagraphStyle(
            name="PdfHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            spaceBefore=12,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="HeaderCell",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=9,
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodyCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9,
        )
    )

    styles.add(
        ParagraphStyle(
            name="MetaCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
        )
    )

    return styles


# ============================================================
# HELPERS
# ============================================================

def format_value(val) -> str:
    if pd.isna(val):
        return "–"
    if isinstance(val, (int, float)):
        return f"{val:.2f}"
    return str(val)


def dataframe_to_table(df: pd.DataFrame, styles, col_widths) -> Table:
    data = []

    # Header
    data.append(
        [Paragraph(str(c), styles["HeaderCell"]) for c in df.columns]
    )

    # Body
    for _, row in df.iterrows():
        data.append(
            [Paragraph(format_value(v), styles["BodyCell"]) for v in row]
        )

    table = Table(
        data,
        colWidths=col_widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    return table


# ============================================================
# MAIN EXPORT FUNCTION
# ============================================================

def export_mcda_snapshot(
    output_path: str,
    *,
    metadata: Dict[str, str],
    df_inputs: pd.DataFrame,
    df_norm: pd.DataFrame,
    df_total_sorted: Optional[pd.DataFrame] = None,
    df_macro_sorted: Optional[pd.DataFrame] = None,
):
    """
    Export MCDA configuration snapshot (tables + PDF-native charts),
    using an engineering-grade, dense layout.
    """

    styles = build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=PAGE_SIZE,
        **MARGINS,
    )

    story = []

    # ========================================================
    # TITLE + METADATA
    # ========================================================
    story.append(
        Paragraph("MCDA – Decision Support Snapshot", styles["PdfTitle"])
    )

    meta_rows = [
        [
            Paragraph(str(k), styles["HeaderCell"]),
            Paragraph(str(v), styles["MetaCell"]),
        ]
        for k, v in metadata.items()
    ]

    meta_table = Table(
        meta_rows,
        colWidths=[0.25 * doc.width, 0.75 * doc.width],
    )

    meta_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ========================================================
    # INPUT SUMMARY
    # ========================================================
    story.append(Paragraph("Input summary", styles["PdfHeading"]))

    df_inputs_pdf = df_inputs.set_index("Concept").T.reset_index()
    df_inputs_pdf.rename(columns={"index": "KPI"}, inplace=True)
    df_inputs_pdf["KPI"] = df_inputs_pdf["KPI"].map(
        lambda k: KPI_LABELS.get(k, k)
    )

    col_widths = [doc.width / len(df_inputs_pdf.columns)] * len(df_inputs_pdf.columns)

    story.append(
        dataframe_to_table(
            df_inputs_pdf,
            styles,
            col_widths,
        )
    )

    story.append(Spacer(1, 18))

    # ========================================================
    # NORMALIZATION & WEIGHTS
    # ========================================================
    story.append(Paragraph("Normalization & weights", styles["PdfHeading"]))

    df_norm_pdf = df_norm.copy()
    df_norm_pdf["KPI"] = df_norm_pdf["KPI"].map(
        lambda k: KPI_LABELS.get(k, k)
    )

    col_widths = [
        0.32 * doc.width,
        0.10 * doc.width,
        0.18 * doc.width,
        0.18 * doc.width,
        0.22 * doc.width,
    ]

    story.append(
        dataframe_to_table(
            df_norm_pdf,
            styles,
            col_widths,
        )
    )

    # ========================================================
    # TOTAL SCORE — BAR CHART + LEGEND
    # ========================================================
    if df_total_sorted is not None:
        story.append(Spacer(1, 22))
        story.append(Paragraph("Total score ranking", styles["PdfHeading"]))
        story.append(Spacer(1, 6))

        chart = total_score_bar_chart(
            df_total_sorted=df_total_sorted,
            width=doc.width,
            chart_width_ratio=0.6,
        )

        legend = total_score_legend_table(
            df_total_sorted=df_total_sorted,
            styles=styles,
        )

        story.append(
            Table(
                [[chart, legend]],
                colWidths=[0.65 * doc.width, 0.35 * doc.width],
                hAlign="LEFT",
                style=[
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ],
            )
        )

    # ========================================================
    # MACRO-CATEGORY CONTRIBUTION — BAR CHART + LEGEND
    # ========================================================
    if df_macro_sorted is not None:
        story.append(Spacer(1, 26))
        story.append(Paragraph("Macro-category contribution", styles["PdfHeading"]))
        story.append(Spacer(1, 6))

        chart = macro_category_bar_chart(
            df_macro_sorted=df_macro_sorted,
            width=doc.width,
        )

        legend = macro_category_value_table(
            df_macro_sorted=df_macro_sorted,
            styles=styles,
        )

        story.append(
            Table(
                [[chart, legend]],
                colWidths=[
                    0.60 * doc.width,
                    0.40 * doc.width,
                ],
                hAlign="LEFT",
                style=[
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ],
            )
        )

    # ========================================================
    # BUILD
    # ========================================================
    doc.build(story)