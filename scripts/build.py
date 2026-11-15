#!/usr/bin/env python3
"""Build the Punjab Press Pulse dashboard from per-date data.

Inputs (repo root):
  data/stories/<YYYY-MM-DD>.json   coded stories for one date (list of rows)
  data/notes/<YYYY-MM-DD>.json     commentary for one date (sources, takeaway, well, improve)
  src/shim_head.html, src/body.html, src/tail1.html, src/tail2.html

Outputs:
  index.html                       single-file dashboard (GitHub Pages serves this)
  stories.json                     every date combined
  exports/AAP_media_analysis_<date>.csv   one CSV per date

Usage: python3 scripts/build.py [--out DIR]
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = {"Positive", "Neutral", "Negative"}
REQUIRED = ["story_id", "source", "newspaper", "language", "page", "front_page", "page_weight",
            "headline", "sentiment", "theme_group", "detailed_theme", "aap_voice", "date"]
SENTIMENTS = REL | {"Not about AAP/Govt", "Govt ad", "Duplicate"}


def load_dir(sub):
    out = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "data", sub, "*.json"))):
        d = os.path.basename(p)[:-5]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            continue
        with open(p, encoding="utf-8") as f:
            out[d] = json.load(f)
    return out


def validate(stories):
    problems = []
    for d, rows in stories.items():
        ids = set()
        for r in rows:
            miss = [k for k in REQUIRED if k not in r]
            if miss:
                problems.append(f"{d} story {r.get('story_id')}: missing {miss}")
            if r.get("date") != d:
                problems.append(f"{d} story {r.get('story_id')}: date field is {r.get('date')}")
            if r.get("sentiment") not in SENTIMENTS:
                problems.append(f"{d} story {r.get('story_id')}: unknown sentiment {r.get('sentiment')!r}")
            if r.get("story_id") in ids:
                problems.append(f"{d}: duplicate story_id {r.get('story_id')}")
            ids.add(r.get("story_id"))
    return problems


def write_csv(d, rows, out_dir):
    path = os.path.join(out_dir, "exports", f"AAP_media_analysis_{d}.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cols = ["Story #", "Source", "Newspaper", "Page", "Front page", "Headline (English)", "Relevant to AAP/Govt",
            "Sentiment", "Theme (ranked group)", "Detailed theme", "AAP spokesperson voice", "Page weight", "Story"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r["story_id"], r["source"], r["newspaper"], r["page"], "Yes" if r["front_page"] else "No",
                        r["headline"], "Yes" if r["sentiment"] in REL else "No", r["sentiment"], r["theme_group"],
                        r["detailed_theme"], "Yes" if r["aap_voice"] else "", r["page_weight"], r.get("story", "")])
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=ROOT)
    a = ap.parse_args()
    stories = load_dir("stories")
    notes = load_dir("notes")
    probs = validate(stories)
    if probs:
        print("Data problems:\n  " + "\n  ".join(probs[:50]))
        sys.exit(1)
    all_rows = [r for d in sorted(stories) for r in stories[d]]
    src = {n: open(os.path.join(ROOT, "src", n), encoding="utf-8").read()
           for n in ["shim_head.html", "body.html", "tail1.html", "tail2.html"]}
    notes_js = "<script>window.NOTES_DATA = " + json.dumps(notes, ensure_ascii=False) + ";</script>\n"
    data_js = json.dumps(all_rows, ensure_ascii=False)
    html = src["shim_head.html"] + notes_js + src["body.html"] + src["tail1.html"] + data_js + src["tail2.html"]
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(a.out, "stories.json"), "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False)
    for d in sorted(stories):
        write_csv(d, stories[d], a.out)
    missing_notes = [d for d in stories if d not in notes]
    print(f"Built index.html: {len(all_rows)} stories across {len(stories)} dates ({', '.join(sorted(stories))}).")
    if missing_notes:
        print("Warning: no commentary for " + ", ".join(missing_notes))


if __name__ == "__main__":
    main()
