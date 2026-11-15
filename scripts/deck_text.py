#!/usr/bin/env python3
"""Turn the daily 'Print Media Monitoring <date>.pdf' deck into a slide list.

Each slide of the deck is one newspaper page with clippings; most slides carry the English headline
text typed by the monitoring team. This script reads that text layer (pdftotext) and writes JSON:
  [{"slide": 6, "section": "Front Page News", "header": "PUNJABI JAGRAN JALANDHAR FRONT PAGE", "newspaper": "Punjabi Jagran",
    "page": "1", "front_page": true, "headlines": ["...", ...], "needs_visual": false}, ...]
The deck is grouped into sections (Front Page News, AAP / BJP / INC / SAD / Others News Coverage).
Slides with a header but no headline text (needs_visual: true) must be read from the image.

Usage: python3 deck_text.py DECK.pdf OUT.json
"""
import json
import re
import subprocess
import sys

PAPERS = [  # (pattern in header, canonical name, language)
    (r"PUNJABI TRIBUNE", "Punjabi Tribune", "Punjabi"), (r"PUNJABI JAGRAN", "Punjabi Jagran", "Punjabi"),
    (r"DAINIK JAGRAN", "Dainik Jagran", "Hindi"), (r"DAINIK BHASKAR", "Dainik Bhaskar", "Hindi"),
    (r"DAINIK SAVERA", "Dainik Savera", "Hindi"), (r"SAVERA TIMES|THE SAVERA", "The Savera Times", "English"),
    (r"PUNJAB KESARI", "Punjab Kesari", "Hindi"), (r"ROZANA SPOKESMAN|SPOKESMAN", "Rozana Spokesman", "Punjabi"),
    (r"JAGBANI", "Jagbani", "Punjabi"), (r"\bAJIT\b", "Ajit", "Punjabi"), (r"HINDUSTAN TIMES|\bHT\b", "Hindustan Times", "English"),
    (r"TIMES OF INDIA|\bTOI\b", "Times of India", "English"), (r"INDIAN EXPRESS", "Indian Express", "English"),
    (r"\bTRIBUNE\b", "The Tribune", "English"),
]


def paper_of(header):
    for pat, name, lang in PAPERS:
        if re.search(pat, header, re.I):
            return name, lang
    return None, None


def page_of(header):
    if re.search(r"FRONT\s*PAGE", header, re.I):
        return "1"
    m = re.search(r"PAGE\s*([A-Z]?\d+)", header, re.I)
    return m.group(1) if m else ""


def main(deck, out):
    txt = subprocess.run(["pdftotext", "-layout", deck, "-"], capture_output=True, text=True).stdout
    slides, section = [], ""
    for i, page in enumerate(txt.split("\f"), start=1):
        lines = [l.rstrip() for l in page.split("\n")]
        nonblank = [l for l in lines if l.strip()]
        if not nonblank:
            if i <= txt.count("\f"):
                slides.append({"slide": i, "section": section, "header": "", "newspaper": None, "page": "", "front_page": False,
                               "headlines": [], "needs_visual": True})
            continue
        header = re.sub(r"\s+", " ", nonblank[0].strip())
        paper, lang = paper_of(header)
        if not paper and re.search(r"COVERAGE|FRONT PAGE NEWS", header, re.I):
            section = header.title()
        # headline blocks are separated by blank lines; join wrapped lines
        blocks, cur, seen_header = [], [], False
        for l in lines:
            if not seen_header:
                if re.sub(r"\s+", " ", l.strip()) == header:
                    seen_header = True
                continue
            if l.strip():
                cur.append(l.strip())
            elif cur:
                blocks.append(" ".join(cur)); cur = []
        if cur:
            blocks.append(" ".join(cur))
        blocks = [re.sub(r"\s+", " ", b) for b in blocks if len(b) > 3]
        pg = page_of(header)
        slides.append({"slide": i, "section": section, "header": header, "newspaper": paper, "language": lang, "page": pg,
                       "front_page": pg == "1", "headlines": blocks,
                       "needs_visual": bool(paper) and not blocks})
    with open(out, "w", encoding="utf-8") as f:
        json.dump(slides, f, ensure_ascii=False, indent=1)
    n_head = sum(len(s["headlines"]) for s in slides)
    n_vis = sum(s["needs_visual"] for s in slides)
    unknown = sorted({s["header"] for s in slides if s["header"] and not s["newspaper"]})
    print(f"{len(slides)} slides, {n_head} typed headlines, {n_vis} slides to read from the image.")
    if unknown:
        print("Slides without a known newspaper header (title/section slides?): " + " | ".join(unknown[:15]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
