# =================================================
# PDF EXPORT — MCDA EXECUTIVE (PDF-SAFE)
# =================================================

import os
import tempfile
from datetime import datetime

import pandas as pd
import plotly.io as pio

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from core.config import KPI_LABELS


# -------------------------------------------------
# Helper: make Plotly figure PDF-safe
# -------------------------------------------------
def export_plotly_pdf(fig, path, width=900, height=600):
    fig_dict = fig.to_dict()
    fig_dict["layout"]["paper_bgcolor"] = "white"
    fig_dict["layout"]["plot_bgcolor"] = "white"
    fig_dict["layout"]["font"]["color"] = "black"

    pio.write_image(
        fig_dict,
        path,
        width=width,
        height=height,
        scale=2
    )


def export_mcda_pdf(file_path, input_summary, norm_summary, figures):

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    elements = []
    tmp_files = []

    small = ParagraphStyle(
        "Small", parent=styles["Normal"], fontSize=8, leading=10
    )

    # =================================================
    # PAGE 1 — EXECUTIVE SUMMARY
    # =================================================
    elements.append(Paragraph("MCDA – Decision Support Summary", styles["Title"]))
    elements.append(
        Paragraph(
            f"<i>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>",
            styles["Normal"]
        )
    )
    elements.append(Spacer(1, 20))

    # --- Total Score
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    export_plotly_pdf(figures["Total Score"], tmp.name, 900, 500)
    elements.append(Image(tmp.name, width=400, height=220))
    tmp_files.append(tmp.name)

    elements.append(Spacer(1, 14))

    # --- Radar
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    export_plotly_pdf(figures["Radar"], tmp.name, 700, 700)
    elements.append(Image(tmp.name, width=360, height=360))
    tmp_files.append(tmp.name)

    elements.append(PageBreak())

    # =================================================
    # PAGE 2 — DECISION DRIVERS
    # =================================================
    elements.append(Paragraph("Decision drivers & robustness", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    grid_imgs = []
    for key in ["Macro-categories", "Pareto", "Tornado"]:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.close()
        export_plotly_pdf(figures[key], tmp.name, 700, 450)
        grid_imgs.append(tmp.name)
        tmp_files.append(tmp.name)

    table = Table(
        [
            [Image(grid_imgs[0], 260, 160), Image(grid_imgs[1], 260, 160)],
            [Image(grid_imgs[2], 260, 160), ""],
        ],
        colWidths=[doc.width / 2] * 2
    )

    elements.append(table)
    elements.append(PageBreak())

    # =================================================
    # PAGE 3 — INPUT & ASSUMPTIONS
    # =================================================
    elements.append(Paragraph("Input summary", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    input_pdf = input_summary.set_index("Concept").T.reset_index()
    input_pdf["KPI"] = input_pdf["index"].map(lambda k: KPI_LABELS.get(k, k))
    input_pdf.drop(columns=["index"], inplace=True)

    data = [[c for c in input_pdf.columns]]
    for _, r in input_pdf.iterrows():
        data.append(
            [r["KPI"]] +
            [f"{v:.2f}" if isinstance(v, (int, float)) else "-" for v in r[1:]]
        )

    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Normalization & weights", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    norm_pdf = norm_summary.copy()
    norm_pdf["KPI"] = norm_pdf["KPI"].map(lambda k: KPI_LABELS.get(k, k))

    data = [norm_pdf.columns.tolist()] + norm_pdf.values.tolist()
    t2 = Table(data, repeatRows=1)
    t2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]))

    elements.append(t2)

    # =================================================
    # BUILD
    # =================================================
    doc.build(elements)

    for f in tmp_files:
        try:
            os.remove(f)
        except OSError:
            pass