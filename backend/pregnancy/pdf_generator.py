"""Pixel-perfect recreation of the official paper Ifishi card (Sprint 5.5).

Tabular content uses ReportLab Table/TableStyle; canvas primitives are used
only for non-tabular elements (title/card-number boxes, checkboxes,
footnote, provisions).
"""
from io import BytesIO
from pathlib import Path

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


def mm_to_pt(mm):
    return mm * 2.8346


PAGE_W, PAGE_H = A4
MARGIN = mm_to_pt(10)
CONTENT_W = mm_to_pt(190)

GREY = colors.HexColor('#E8E8E8')
THIN = 0.5

COAT_OF_ARMS = Path(settings.BASE_DIR) / "static" / "coat_of_arms.png"

VISIT_NAMES = [
    "INSHURO YA MBERE",
    "INSHURO YA KABIRI",
    "INSHURO YA GATATU",
    "INSHURO YA KANE",
    "INSHURO YA GATANU",
    "INSHURO YA GATANDATU",
    "INSHURO YA KARINDWI",
    "INSHURO YA MUNANI",
]

ANC_HEADERS = [
    "IGIHE UMUBYEYI\nASUZUMIWEHO",
    "ITARIKI\nASUZUMIWEHO*",
    "UBUREBURE\nBWA\nNYABABYEYI",
    "IBIRO\nUMUBYEYI\nYIYONGEYE",
    "UKO UMWANA\nAMEZE MU\nNDA",
    "GUTERA\nK'UMUTIMA\nW'UMWANA",
    "ITARIKI\nAZAGARUKIRA",
    "ICYITONDERWA /\nICYONGER'WAHO\nUrugero:\nikimenyetso mpuruza",
]
ANC_COL_WIDTHS = [mm_to_pt(w) for w in (32, 20, 18, 18, 22, 22, 20, 38)]

PROVISIONS = [
    ("Ibinini by'icyuma n'acide folique", "iron_folic"),
    ("Mebendazole", "mebendazole"),
    ("MMS", "mms"),
    ("Urugi rw'inzitiramaraso", "mosquito_net"),
]

HEADER_CELL_STYLE = ParagraphStyle(
    "AncHeader",
    fontName="Helvetica-Bold",
    fontSize=7,
    leading=8.2,
    alignment=1,  # centered
)

VISIT_NAME_STYLE = ParagraphStyle(
    "VisitName",
    fontName="Helvetica",
    fontSize=7,
    leading=7.5,
)


def fmt_date(d):
    return d.strftime("%d/%m/%Y") if d else ""


def fmt_measure(value, unit):
    if value is None:
        return ""
    text = f"{value}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return f"{text} {unit}"


def _draw_table(c, data, col_widths, row_heights, style, y_top):
    """Draw a platypus Table with its top edge at y_top; returns new y."""
    table = Table(data, colWidths=col_widths, rowHeights=row_heights)
    table.setStyle(style)
    _, h = table.wrapOn(c, CONTENT_W, PAGE_H)
    table.drawOn(c, MARGIN, y_top - h)
    return y_top - h


def _checkbox(c, x, y_center, checked, size_mm=3):
    s = mm_to_pt(size_mm)
    c.setLineWidth(0.8)
    c.setStrokeColor(colors.black)
    if checked:
        c.setFillColor(colors.black)
        c.rect(x, y_center - s / 2, s, s, stroke=1, fill=1)
    else:
        c.rect(x, y_center - s / 2, s, s, stroke=1, fill=0)
    return x + s


def generate_ifishi_pdf(pregnancy, anc_visits):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = PAGE_H - MARGIN

    base_grid = [
        ("GRID", (0, 0), (-1, -1), THIN, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), mm_to_pt(2)),
        ("RIGHTPADDING", (0, 0), (-1, -1), mm_to_pt(1)),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    # ── FIX 1: header block — facility table left, coat of arms 45mm right ─
    arms_w = mm_to_pt(45)
    left_w = CONTENT_W - arms_w
    header_row_h = mm_to_pt(7)
    facility = [
        ("INTARA", pregnancy.province),
        ("AKARERE", pregnancy.district),
        ("IBITARO", pregnancy.hospital),
        ("IKIGO NDERABUZIMA", pregnancy.health_centre),
        ("POSTE DE SANTE (IVURIRO RY'IBANZE)", pregnancy.health_post),
    ]
    style = TableStyle(base_grid + [
        ("BACKGROUND", (0, 0), (0, -1), GREY),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 8),
        ("FONT", (1, 0), (1, -1), "Helvetica", 8),
    ])
    table = Table(
        [[label, value or ""] for label, value in facility],
        colWidths=[mm_to_pt(62), left_w - mm_to_pt(62)],
        rowHeights=[header_row_h] * 5,
    )
    table.setStyle(style)
    _, th = table.wrapOn(c, left_w, PAGE_H)
    table.drawOn(c, MARGIN, y - th)

    # Coat of arms vertically centered across the 5 rows.
    block_h = 5 * header_row_h
    if COAT_OF_ARMS.exists():
        img_h = mm_to_pt(24)
        img_w = img_h * 120 / 131
        img_x = MARGIN + left_w + (arms_w - img_w) / 2
        img_y = y - (block_h + img_h) / 2 + mm_to_pt(3)
        c.drawImage(str(COAT_OF_ARMS), img_x, img_y, width=img_w,
                    height=img_h, mask="auto")
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.black)
    right_edge = MARGIN + CONTENT_W
    c.drawRightString(right_edge, y - block_h + mm_to_pt(4.5),
                      "Repubulika y'u Rwanda")
    c.drawRightString(right_edge, y - block_h + mm_to_pt(1.5),
                      "Minisiteri y'Ubuzima")
    y -= block_h

    # ── FIX 3: title — left-aligned, bold, bordered box (flush w/ header) ─
    title_h = mm_to_pt(8)
    c.setLineWidth(THIN)
    c.setStrokeColor(colors.black)
    c.rect(MARGIN, y - title_h, CONTENT_W, title_h, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + mm_to_pt(2), y - title_h + mm_to_pt(2.4),
                 "IFISHI Y'UBUZIMA BW'UMUBYEYI N'UMWANA")
    y -= title_h

    # ── FIX 4: card number row — bordered box ──────────────────────────────
    num_h = mm_to_pt(7)
    c.rect(MARGIN, y - num_h, CONTENT_W, num_h, stroke=1, fill=0)
    c.setFont("Helvetica", 8)
    c.drawString(
        MARGIN + mm_to_pt(2), y - num_h + mm_to_pt(2.2),
        "NUMERO Y'IFISHI:  A) KWIPIMISHA INDA .................................."
        "  B) GUSUZUMWA NYUMA YO KUBYARA ..................................",
    )
    y -= num_h

    # ── FIX 5: Section I — UMWIRONDORO (2mm gap above label) ──────────────
    y -= mm_to_pt(2) + 7
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "I. UMWIRONDORO")
    y -= mm_to_pt(2)

    edd_text = fmt_date(pregnancy.edd_date)
    if pregnancy.is_lmp_estimated:
        edd_cell = Paragraph(
            f'<font name="Helvetica" size="9">{edd_text}</font> '
            f'<font name="Helvetica-Oblique" size="7">(uko bigereranijwe)'
            f'</font>',
            ParagraphStyle("Edd", fontName="Helvetica", fontSize=9, leading=10),
        )
    else:
        edd_cell = edd_text
    identity = [
        ("AMAZINA Y'UMUGORE", pregnancy.full_name),
        ("IMYAKA Y'UMUGORE", str(pregnancy.age)),
        ("INDA YA", str(pregnancy.gravida)),
        ("IMBYARO YA", str(pregnancy.parity)),
        ("ITARIKI UHERUKIRA MUMIHANGO (LMP)", fmt_date(pregnancy.lmp_date)),
        ("ITARIKI ASHOBORA KUBYARIRAHO (EDD)", edd_cell),
    ]
    y = _draw_table(
        c,
        [[label, value] for label, value in identity],
        [mm_to_pt(80), CONTENT_W - mm_to_pt(80)],
        [mm_to_pt(5)] * 6,
        TableStyle(base_grid + [
            ("BACKGROUND", (0, 0), (0, -1), GREY),
            ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 8),
            ("FONT", (1, 0), (1, -1), "Helvetica", 9),
        ]),
        y,
    )

    # ── FIX 6: Section II — KWIPIMISHA INDA (2mm gap above label) ─────────
    y -= mm_to_pt(2) + 7
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "II. KWIPIMISHA INDA")
    y -= mm_to_pt(2)

    header_cells = [
        Paragraph(h.replace("\n", "<br/>"), HEADER_CELL_STYLE)
        for h in ANC_HEADERS
    ]
    visits_by_number = {v.visit_number: v for v in anc_visits}
    rows = [header_cells]
    for number, name in enumerate(VISIT_NAMES, start=1):
        v = visits_by_number.get(number)
        rows.append([
            Paragraph(name, VISIT_NAME_STYLE),  # wraps within its column
            fmt_date(v.visit_date) if v else "",
            fmt_measure(v.mother_height_cm, "cm") if v else "",
            fmt_measure(v.mother_weight_kg, "kg") if v else "",
            (v.fetal_position if v else ""),
            (v.fetal_heartbeat if v else ""),
            fmt_date(v.next_visit_date) if v else "",
            (v.notes if v else ""),
        ])
    y = _draw_table(
        c,
        rows,
        ANC_COL_WIDTHS,
        [mm_to_pt(18)] + [mm_to_pt(9)] * 8,
        TableStyle(base_grid + [
            ("BACKGROUND", (0, 0), (-1, 0), GREY),
            ("FONT", (0, 1), (-1, -1), "Helvetica", 7),
            # Tight padding in the header row so the long Kinyarwanda
            # column titles wrap at word boundaries, not mid-word.
            ("LEFTPADDING", (0, 0), (-1, 0), 1),
            ("RIGHTPADDING", (0, 0), (-1, 0), 1),
            # Col 1 data cells: "INSHURO YA GATANDATU" is 88.7pt at 7pt
            # Helvetica; the 32mm column fits it on one line only with
            # minimal padding.
            ("LEFTPADDING", (0, 1), (0, -1), 1),
            ("RIGHTPADDING", (0, 1), (0, -1), 0),
        ]),
        y,
    )

    # ── FIX 7: IHEREZO RY'INDA — label spanning two checkbox sub-rows ─────
    iherezo_top = y
    sub_h = mm_to_pt(7)  # 14mm total
    right_w = CONTENT_W - ANC_COL_WIDTHS[0]
    y = _draw_table(
        c,
        [["IHEREZO RY'INDA", ""], ["", ""]],
        [ANC_COL_WIDTHS[0], right_w],
        [sub_h, sub_h],
        TableStyle(base_grid + [
            ("SPAN", (0, 0), (0, 1)),
            ("FONT", (0, 0), (0, 0), "Helvetica-Bold", 8),
        ]),
        y,
    )
    # Checkbox items overlaid on the right cell (canvas — non-tabular).
    outcome_lines = [
        ["YAVUYEMO", "YAVUTSE IDASHYITSE", "YAVUTSE ISHYITSE"],
        ["UBURYO INDA YAVUTSE", "UMWANA YAVUTSE APFUYE",
         "UMWANA YAVUTSE ARI MUZIMA"],
    ]
    for line, labels in enumerate(outcome_lines):
        cy = iherezo_top - sub_h * line - sub_h / 2
        cx = MARGIN + ANC_COL_WIDTHS[0] + mm_to_pt(3)
        for label in labels:
            cx = _checkbox(c, cx, cy, checked=False) + mm_to_pt(1.5)
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.black)
            c.drawString(cx, cy - 2.4, label)
            cx += c.stringWidth(label, "Helvetica", 7) + mm_to_pt(7)

    # ── FIX 8: bottom rows ─────────────────────────────────────────────────
    bottom_labels = [
        "ITARIKI ABYARIYEHO CYANGWA INDA IRANGIRIYE",
        "IBIRO UMWANA AVUKANYE",
        "UBUREBURE UMWANA AVUKANYE",
        "UBURYO BWOKUBONEZA URUBYARO UMUBYEYI YAHISEMO",
    ]
    y = _draw_table(
        c,
        [[label, ""] for label in bottom_labels],
        [mm_to_pt(80), CONTENT_W - mm_to_pt(80)],
        [mm_to_pt(6)] * len(bottom_labels),
        TableStyle(base_grid + [
            ("BACKGROUND", (0, 0), (0, -1), GREY),
            # Size 7 so the longest label fits on one line.
            ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 7),
        ]),
        y,
    )

    # ── FIX 9: footnote (2mm below bottom rows) ────────────────────────────
    y -= mm_to_pt(2) + 5
    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.black)
    c.drawString(
        MARGIN, y,
        "1 Numero y'ifishi igomba gusa niyo dufite muri registre ya CPN",
    )

    # ── FIX 10: provisions — KIBASUMBA digital addition (3mm below note) ──
    y -= mm_to_pt(3)
    c.setLineWidth(THIN)
    c.setStrokeColor(colors.black)
    c.line(MARGIN, y, MARGIN + CONTENT_W, y)
    y -= mm_to_pt(5)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, "IBININI N'IBIKORESHO BYAHAWE UMUBYEYI (KIBASUMBA)")

    row_h = mm_to_pt(6)
    for label, field in PROVISIONS:
        y -= row_h
        cy = y + row_h / 2
        after_box = _checkbox(c, MARGIN, cy, getattr(pregnancy, f"{field}_given"))
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.black)
        c.drawString(after_box + mm_to_pt(4), cy - 2.4, label)
        date = getattr(pregnancy, f"{field}_date")
        if date:
            c.drawRightString(MARGIN + CONTENT_W, cy - 2.4, fmt_date(date))
        # Light separator between provision rows.
        c.setLineWidth(0.3)
        c.setStrokeColor(colors.HexColor('#BBBBBB'))
        c.line(MARGIN, y, MARGIN + CONTENT_W, y)

    c.save()
    return buf.getvalue()
