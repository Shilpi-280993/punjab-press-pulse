#!/usr/bin/env python3
"""Daily PDF report for the owner, built from data/stories/D.json and data/notes/D.json.

  python3 scripts/report_pdf.py D        writes exports/Punjab_press_report_D.pdf

House style for documents written for the owner (CLAUDE.md): Cambria 12, black text, no colour,
no em dashes. Cambria is not installed on Linux, so the metric-compatible Caladea is used when
Cambria is missing.
"""
import collections
import json
import os
import sys
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = ("Positive", "Neutral", "Negative")


def register_fonts():
    candidates = [
        ("/usr/share/fonts/truetype/msttcorefonts/cambria.ttc", None),
        ("/usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf", "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"),
    ]
    for reg, bold in candidates:
        if os.path.exists(reg) and bold and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont("Body", reg))
            pdfmetrics.registerFont(TTFont("Body-Bold", bold))
            pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body", boldItalic="Body-Bold")
            return "Body", "Body-Bold"
    return "Times-Roman", "Times-Bold"


FONT, BOLD = register_fonts()
BLACK = colors.black
ST = {
    "title": ParagraphStyle("title", fontName=BOLD, fontSize=18, leading=22, textColor=BLACK, spaceAfter=4),
    "sub": ParagraphStyle("sub", fontName=FONT, fontSize=12, leading=15, textColor=BLACK, spaceAfter=10),
    "h": ParagraphStyle("h", fontName=BOLD, fontSize=14, leading=18, textColor=BLACK, spaceBefore=12, spaceAfter=6),
    "body": ParagraphStyle("body", fontName=FONT, fontSize=12, leading=15.5, textColor=BLACK, alignment=TA_LEFT, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName=FONT, fontSize=12, leading=14.5, textColor=BLACK),
    "celln": ParagraphStyle("celln", fontName=FONT, fontSize=12, leading=14.5, textColor=BLACK, alignment=2),
    "cellbn": ParagraphStyle("cellbn", fontName=BOLD, fontSize=12, leading=14.5, textColor=BLACK, alignment=2),
    "cellb": ParagraphStyle("cellb", fontName=BOLD, fontSize=12, leading=14.5, textColor=BLACK),
    "note": ParagraphStyle("note", fontName=FONT, fontSize=12, leading=15, textColor=BLACK, spaceAfter=4),
}


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("—", ", ")


def pct(n, d):
    return f"{n / d:.0%}" if d else "0%"


def cols(r):
    c = r.get("columns")
    return c if isinstance(c, int) else None


def table(header, rows, widths, num_cols=()):
    data = [[Paragraph(esc(h), ST["cellbn" if i in num_cols else "cellb"]) for i, h in enumerate(header)]]
    for row in rows:
        data.append([Paragraph(esc(v), ST["celln" if i in num_cols else "cell"]) for i, v in enumerate(row)])
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [("LINEABOVE", (0, 0), (-1, 0), 0.8, BLACK), ("LINEBELOW", (0, 0), (-1, 0), 0.6, BLACK),
             ("LINEBELOW", (0, -1), (-1, -1), 0.8, BLACK), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    for c in num_cols:
        style.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    t.setStyle(TableStyle(style))
    return t


def themes(rel, sent):
    g = {}
    for r in rel:
        if r["sentiment"] != sent or not r["theme_group"]:
            continue
        t = g.setdefault(r["theme_group"], {"n": 0, "papers": set(), "front": 0, "cols": 0, "sized": 0})
        t["n"] += 1; t["papers"].add(r["newspaper"]); t["front"] += r["page_weight"] == 3
        if cols(r) is not None:
            t["cols"] += cols(r); t["sized"] += 1
    items = sorted(g.items(), key=lambda kv: (-(kv[1]["cols"] if kv[1]["sized"] else 0), -kv[1]["n"]))[:10]
    return [[i + 1, k, v["n"], len(v["papers"]), v["front"], v["cols"] if v["sized"] else "-"] for i, (k, v) in enumerate(items)]


def main(d):
    rows = json.load(open(os.path.join(ROOT, "data", "stories", f"{d}.json"), encoding="utf-8"))
    npath = os.path.join(ROOT, "data", "notes", f"{d}.json")
    notes = json.load(open(npath, encoding="utf-8")) if os.path.exists(npath) else {}
    rel = [r for r in rows if r["sentiment"] in REL]
    c = collections.Counter(r["sentiment"] for r in rel)
    n = len(rel)
    opp = [r for r in rel if r["detailed_theme"].startswith("Opposition attack")]
    front = sum(1 for r in rel if r.get("front_page") is True)
    vals = {"relevant": f"{n:,}", "positive": f"{c['Positive']:,}", "neutral": f"{c['Neutral']:,}", "negative": f"{c['Negative']:,}",
            "positive_share": pct(c["Positive"], n), "neutral_share": pct(c["Neutral"], n), "negative_share": pct(c["Negative"], n),
            "front_pages": f"{front:,}", "opposition_statements": f"{len(opp):,}"}
    fill = lambda t: t.format(**vals) if t else ""
    long_date = date.fromisoformat(d).strftime("%A %d %B %Y").replace(" 0", " ")

    out = os.path.join(ROOT, "exports", f"Punjab_press_report_{d}.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title=f"Punjab print media monitor, {long_date}", author="Punjab Press Pulse")
    W = A4[0] - 4 * cm
    s = [Paragraph("Punjab print media monitor", ST["title"]),
         Paragraph(f"How the press covered AAP and the Punjab government: {esc(long_date)}", ST["sub"])]
    if notes.get("takeaway"):
        s.append(Paragraph(esc(fill(notes["takeaway"])), ST["body"]))

    s.append(Paragraph("The numbers", ST["h"]))
    tot_cols = sum(cols(r) or 0 for r in rel)
    num_rows = [["Stories read (all rows)", f"{len(rows):,}"], ["Relevant stories", vals["relevant"]],
                ["Positive", f"{vals['positive']} ({vals['positive_share']})"], ["Neutral", f"{vals['neutral']} ({vals['neutral_share']})"],
                ["Negative", f"{vals['negative']} ({vals['negative_share']})"], ["Relevant stories on front pages", vals["front_pages"]],
                ["Opposition statements", vals["opposition_statements"]],
                ["Government ads", f"{sum(1 for r in rows if r['sentiment'] == 'Govt ad'):,}"]]
    if any(cols(r) is not None for r in rel):
        num_rows.append(["Newspaper columns of relevant coverage", f"{tot_cols:,}"])
    s.append(table(["Measure", "Value"], num_rows, [W * 0.65, W * 0.35], num_cols=(1,)))
    for k in ("sources", "validation"):
        if notes.get(k):
            s.append(Spacer(1, 4)); s.append(Paragraph(esc(notes[k]), ST["note"]))

    for key, head in (("well", "What went well"), ("improve", "What to improve")):
        if notes.get(key):
            s.append(Paragraph(head, ST["h"]))
            for b, e in notes[key]:
                s.append(Paragraph(f"<b>{esc(b)}</b> {esc(e)}", ST["body"]))

    hdr = ["#", "Theme", "Stories", "Papers", "Front", "Columns"]
    wid = [W * 0.06, W * 0.50, W * 0.11, W * 0.11, W * 0.10, W * 0.12]
    s.append(KeepTogether([Paragraph("Top 10 positive themes", ST["h"]),
                           Paragraph("Ranked by newspaper columns of space; stories, papers and front pages for context.", ST["note"]),
                           table(hdr, themes(rel, "Positive"), wid, num_cols=(0, 2, 3, 4, 5))]))
    s.append(KeepTogether([Paragraph("Top 10 negative themes", ST["h"]),
                           table(hdr, themes(rel, "Negative"), wid, num_cols=(0, 2, 3, 4, 5))]))

    groups = collections.defaultdict(list)
    for r in rel:
        if r.get("story"):
            groups[r["story"]].append(r)
    big = []
    for st, h in groups.items():
        pos = sum(r["sentiment"] == "Positive" for r in h); neg = sum(r["sentiment"] == "Negative" for r in h)
        tone = "neutral" if len(h) - pos - neg > pos + neg else "positive" if pos > neg * 1.5 else "negative" if neg > pos * 1.5 else "mixed"
        sized = [cols(r) for r in h if cols(r) is not None]
        big.append([st, len({r["newspaper"] for r in h}), sum(r["page_weight"] == 3 for r in h), sum(sized) if sized else "-", tone])
    big.sort(key=lambda x: (-x[1], -x[2]))
    s.append(KeepTogether([Paragraph("Biggest stories of the day", ST["h"]),
                           Paragraph("One news event across papers. Columns are the total across all papers.", ST["note"]),
                           table(["Story", "Papers", "Front", "Columns", "Tone"], big[:12], [W * 0.50, W * 0.12, W * 0.11, W * 0.13, W * 0.14], num_cols=(1, 2, 3))]))

    v = collections.OrderedDict((k, [0, 0, False]) for k in ("BJP", "Congress", "SAD", "Other parties", "AAP leaders"))
    for r in rel:
        dt = r["detailed_theme"]
        k = {"Opposition attack: BJP": "BJP", "Opposition attack: Congress": "Congress", "Opposition attack: SAD": "SAD",
             "Opposition attack: Other": "Other parties"}.get(dt) or ("AAP leaders" if r.get("aap_voice") is True else None)
        if k:
            v[k][0] += 1
            if cols(r) is not None:
                v[k][1] += cols(r); v[k][2] = True
    tot = sum(x[0] for x in v.values())
    vrows = [[k + ("" if k == "AAP leaders" else " attacks"), x[0], pct(x[0], tot), x[1] if x[2] else "-"] for k, x in v.items()]
    vrows.sort(key=lambda x: -x[1])
    s.append(KeepTogether([Paragraph("Who is talking", ST["h"]),
                           Paragraph("Opposition attacks on the government by party, against AAP leaders' counter-attacks.", ST["note"]),
                           table(["Speaker", "Statements", "Share", "Columns"], vrows, [W * 0.46, W * 0.18, W * 0.18, W * 0.18], num_cols=(1, 2, 3))]))

    papers = collections.OrderedDict()
    for r in rel:
        p = papers.setdefault(r["newspaper"], [0, 0, 0, 0, 0])
        p[0] += 1; p[{"Positive": 1, "Neutral": 2, "Negative": 3}[r["sentiment"]]] += 1; p[4] += r.get("front_page") is True
    prow = sorted(([k] + vv for k, vv in papers.items()), key=lambda x: -x[1])
    s.append(KeepTogether([Paragraph("Newspaper by newspaper", ST["h"]),
                           table(["Newspaper", "Relevant", "Positive", "Neutral", "Negative", "Front"], prow,
                                 [W * 0.30, W * 0.14, W * 0.14, W * 0.14, W * 0.14, W * 0.14], num_cols=(1, 2, 3, 4, 5))]))
    s.append(Spacer(1, 10))
    s.append(Paragraph(f"Every story with its headline, page, size and sentiment is in AAP_media_analysis_{d}.csv and on the dashboard: "
                       f"https://shilpi-280993.github.io/punjab-press-pulse/#d={d}", ST["note"]))

    def footer(canvas, doc_):
        canvas.saveState(); canvas.setFont(FONT, 9); canvas.setFillColor(BLACK)
        canvas.drawString(2 * cm, 1.1 * cm, f"Punjab print media monitor, {long_date}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
