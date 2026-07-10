import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT


# Palette matched to the platform's teal/sage theme so the exported
# dossier feels like part of the same product, not a generic PDF.
TEAL      = colors.HexColor("#0f766e")
TEAL_DIM  = colors.HexColor("#d3ece7")
SAGE      = colors.HexColor("#6b8f5c")
INK       = colors.HexColor("#16211a")
MUTED     = colors.HexColor("#7c8977")
RED       = colors.HexColor("#dc2626")
AMBER     = colors.HexColor("#b45309")
LINE      = colors.HexColor("#dce5d6")
ROW_ALT   = colors.HexColor("#f6f8f4")

STATUS_COLORS = {
    "Open":                RED,
    "Under Investigation": AMBER,
    "Closed":              SAGE,
    "Charge Sheeted":      TEAL,
}


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontSize=18, textColor=INK,
            spaceAfter=2, alignment=TA_LEFT, fontName="Helvetica-Bold",
        ),
        "eyebrow": ParagraphStyle(
            "eyebrow", parent=base["Normal"], fontSize=8.5, textColor=TEAL,
            spaceAfter=10, alignment=TA_LEFT, fontName="Helvetica-Bold",
            letterSpacing=1.2,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontSize=11.5, textColor=INK,
            spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontSize=9.5, textColor=INK,
            leading=14,
        ),
        "meta": ParagraphStyle(
            "meta", parent=base["Normal"], fontSize=8.5, textColor=MUTED,
            leading=12,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], fontSize=7.5, textColor=MUTED,
            alignment=TA_RIGHT,
        ),
    }
    return styles


def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(20 * mm, 15 * mm, doc.pagesize[0] - 20 * mm, 15 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 11 * mm, "KSP Crime Intelligence Platform \u2014 For official use only")
    canvas.drawRightString(
        doc.pagesize[0] - 20 * mm, 11 * mm,
        f"Page {canvas.getPageNumber()} \u2014 Generated {datetime.now().strftime('%d %b %Y, %H:%M')}"
    )
    canvas.restoreState()


def generate_suspect_case_pdf(cluster):
    """
    Builds a case dossier PDF for a single identity cluster (suspect):
    summary, all known aliases, and the full FIR history table.
    Returns an in-memory PDF (BytesIO) ready to send to the browser.
    """
    styles = _styles()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=22 * mm,
    )

    story = []

    story.append(Paragraph("KARNATAKA STATE POLICE &nbsp;\u00b7&nbsp; CRIME INTELLIGENCE", styles["eyebrow"]))
    story.append(Paragraph("Suspect Identity Dossier", styles["title"]))
    story.append(Paragraph(
        f"Cluster ID: <b>{cluster['cluster_id']}</b> &nbsp;\u00b7&nbsp; "
        f"Confidential \u2014 generated for internal investigative use only",
        styles["meta"]
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE))
    story.append(Spacer(1, 12))

    primary_name = cluster["names_found"][0]
    story.append(Paragraph("Summary", styles["h2"]))

    summary_data = [
        ["Primary identity", primary_name],
        ["Aliases detected", f"{cluster['alias_count']} fake identities"],
        ["Match confidence", f"{cluster['confidence']}%"],
        ["Districts active in", ", ".join(cluster["districts"])],
        ["Total FIRs on record", str(len(cluster["records"]))],
    ]
    summary_table = Table(summary_data, colWidths=[45 * mm, 115 * mm])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR", (1, 0), (1, -1), INK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(summary_table)

    story.append(Paragraph("Known Aliases", styles["h2"]))
    alias_header = ["Name used", "Age", "District", "Crime type"]
    alias_rows = [alias_header] + [
        [rec["accused_name"], str(rec["accused_age"]), rec["district"], rec["crime_type"]]
        for rec in cluster["records"]
    ]
    alias_table = Table(alias_rows, colWidths=[50 * mm, 18 * mm, 45 * mm, 47 * mm], repeatRows=1)
    alias_table.setStyle(_zebra_table_style())
    story.append(alias_table)

    story.append(Paragraph("Full FIR History", styles["h2"]))
    fir_header = ["FIR ID", "Name used", "District", "Crime type", "Date", "Status"]
    fir_rows = [fir_header]
    for rec in cluster["records"]:
        fir_rows.append([
            rec["fir_id"], rec["accused_name"], rec["district"],
            rec["crime_type"], rec["fir_date"], rec["case_status"],
        ])
    fir_table = Table(fir_rows, colWidths=[26 * mm, 34 * mm, 32 * mm, 32 * mm, 22 * mm, 14 * mm], repeatRows=1)
    style_cmds = _zebra_table_style().getCommands()[:]
    fir_table.setStyle(TableStyle(style_cmds))
    story.append(fir_table)

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "This dossier is generated automatically from FIR records using identity-deduplication "
        "(Soundex + fuzzy name matching). Confidence scores reflect statistical similarity, not "
        "confirmed legal identity, and should be corroborated before action is taken.",
        styles["meta"]
    ))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    buf.seek(0)
    return buf


def _zebra_table_style():
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DIM),
        ("TEXTCOLOR", (0, 0), (-1, 0), TEAL),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
