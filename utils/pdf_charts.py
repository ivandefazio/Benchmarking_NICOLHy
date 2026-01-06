# utils/pdf_charts.py

from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import mm


# ============================================================
# TOTAL SCORE — BAR CHART (PDF-NATIVE)
# ============================================================

def total_score_bar_chart(
    df_total_sorted,
    width: float,
    height: float = 70 * mm,
    chart_width_ratio: float = 0.6,
):
    """
    PDF-native bar chart for Total Score ranking.
    One bar per concept, uniform color.
    """

    drawing = Drawing(width, height)
    chart = VerticalBarChart()

    # Geometry
    chart.x = 30
    chart.y = 20
    chart.width = width * chart_width_ratio - 30
    chart.height = height - 40

    # Data (ONE series)
    labels = df_total_sorted.index.tolist()
    values = df_total_sorted["Total Score"].tolist()

    chart.data = [values]

    # Axes
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 20
    chart.valueAxis.labels.fontSize = 7

    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.angle = 30
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.boxAnchor = "ne"

    # Bars layout
    chart.barWidth = 12
    chart.groupSpacing = 10
    chart.barSpacing = 2

    # Single color for all bars
    chart.bars[0].fillColor = colors.HexColor("#4c72b0")
    chart.bars[0].strokeWidth = 0

    drawing.add(chart)

    # Title
    drawing.add(
        String(
            chart.x + chart.width / 2,
            height - 8,
            "Total score ranking (weighted)",
            fontSize=9,
            textAnchor="middle",
        )
    )

    return drawing


# ============================================================
# TOTAL SCORE — LEGEND TABLE
# ============================================================

def total_score_legend_table(df_total_sorted, styles):

    rows = [
        [
            Paragraph("<b>Concept</b>", styles["HeaderCell"]),
            Paragraph("<b>Total score</b>", styles["HeaderCell"]),
        ]
    ]

    for concept, row in df_total_sorted.iterrows():
        rows.append(
            [
                Paragraph(concept, styles["BodyCell"]),
                Paragraph(f"{row['Total Score']:.1f}", styles["BodyCell"]),
            ]
        )

    table = Table(rows, colWidths=[90, 55], hAlign="LEFT")

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    return table


# ============================================================
# MACRO-CATEGORY — GROUPED BAR CHART (CORRECT)
# ============================================================

def macro_category_bar_chart(
    df_macro_sorted,
    width: float,
    height: float = 65 * mm,
    chart_width_ratio: float = 0.55,
):
    """
    PDF-native grouped bar chart for macro-category contributions.

    One group per concept:
    - Performance
    - Safety
    - Producibility
    """

    drawing = Drawing(width, height)
    chart = VerticalBarChart()

    chart.x = 30
    chart.y = 20
    chart.width = width * chart_width_ratio - 30
    chart.height = height - 40

    # ------------------------------------------------
    # Data: one series per macro-category
    # ------------------------------------------------
    chart.data = [
        df_macro_sorted["Performance"].fillna(0).tolist(),
        df_macro_sorted["Safety"].fillna(0).tolist(),
        df_macro_sorted["Producibility"].fillna(0).tolist(),
    ]

    # ------------------------------------------------
    # Axes
    # ------------------------------------------------
    chart.valueAxis.valueMin = 0
    max_val = df_macro_sorted.sum(axis=1).max()
    chart.valueAxis.valueMax = int((max_val // 10 + 1) * 10)
    chart.valueAxis.valueStep = 10
    chart.valueAxis.valueStep = 20
    chart.valueAxis.labels.fontSize = 7

    chart.categoryAxis.categoryNames = df_macro_sorted.index.tolist()
    chart.categoryAxis.labels.angle = 20
    chart.categoryAxis.labels.dy = -5
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.boxAnchor = "ne"

    # ------------------------------------------------
    # Bar layout
    # ------------------------------------------------
    chart.barWidth = 7
    chart.groupSpacing = 10
    chart.barSpacing = 2

    palette = [
        colors.HexColor("#4c72b0"),  # Performance
        colors.HexColor("#dd8452"),  # Safety
        colors.HexColor("#55a868"),  # Producibility
    ]

    for bar, color in zip(chart.bars, palette):
        bar.fillColor = color
        bar.strokeWidth = 0

    drawing.add(chart)

    # ------------------------------------------------
    # Title
    # ------------------------------------------------
    drawing.add(
        String(
            chart.x + chart.width / 2,
            height - 8,
            "Macro-category contribution to total score",
            fontSize=9,
            textAnchor="middle",
        )
    )

    return drawing


# ============================================================
# MACRO-CATEGORY — COLOR LEGEND (PROPER)
# ============================================================

def macro_category_legend_table(styles):
    """
    Color legend for macro-category bar chart.
    """

    rows = [
        [
            Paragraph("<b>Color</b>", styles["HeaderCell"]),
            Paragraph("<b>Macro-category</b>", styles["HeaderCell"]),
        ],
        ["", Paragraph("Performance", styles["BodyCell"])],
        ["", Paragraph("Safety", styles["BodyCell"])],
        ["", Paragraph("Producibility", styles["BodyCell"])],
    ]

    table = Table(rows, colWidths=[20, 100], hAlign="LEFT")

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#4c72b0")),
                ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#dd8452")),
                ("BACKGROUND", (0, 3), (0, 3), colors.HexColor("#55a868")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    return table

def macro_category_value_table(df_macro_sorted, styles):

    header_style = styles["HeaderCell"]

    rows = [
        [
            Paragraph("<b>Concept</b>", header_style),
            Paragraph("<b><font color='#4c72b0'>Performance</font></b>", header_style),
            Paragraph("<b><font color='#dd8452'>Safety</font></b>", header_style),
            Paragraph("<b><font color='#55a868'>Producibility</font></b>", header_style),
        ]
    ]

    for concept, row in df_macro_sorted.iterrows():
        rows.append(
            [
                Paragraph(concept, styles["BodyCell"]),
                Paragraph(f"{row['Performance']:.1f}", styles["BodyCell"]),
                Paragraph(f"{row['Safety']:.1f}", styles["BodyCell"]),
                Paragraph(f"{row['Producibility']:.1f}", styles["BodyCell"]),
            ]
        )

    table = Table(
        rows,
        colWidths=[70, 70, 70, 90],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    return table