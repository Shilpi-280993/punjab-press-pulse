#!/usr/bin/env python3
"""Sentiment judge helper (see VALIDATION.md).

  python3 scripts/judge.py prep D      blind batches for the judge (no sentiment or theme)
  python3 scripts/judge.py compare D   agreement + disagreements.json for adjudication
  python3 scripts/judge.py apply D     apply final rulings, write audit CSV/JSON, add note line
"""
import collections
import csv
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELS = {"Positive", "Neutral", "Negative", "Not about AAP/Govt", "Govt ad"}
JUDGE = "Claude Fable 5.2"
BATCH = 50
SAMPLE = 100  # random rows judged per day, on top of every low-confidence row


def p(*a):
    return os.path.join(ROOT, *a)


def load(path, default=None):
    if not os.path.exists(path):
        if default is not None:
            return default
        raise SystemExit(f"Missing {os.path.relpath(path, ROOT)}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def judged_rows(d):
    return [r for r in load(p("data", "stories", f"{d}.json")) if r["sentiment"] != "Duplicate"]


def pick_sample(d, rows):
    """Every row the coder marked low confidence, plus a random sample of SAMPLE rows (seeded by date,
    spread across papers) from the rest."""
    import random
    low = [r for r in rows if str(r.get("confidence", "")).lower() == "low"]
    rest = [r for r in rows if r not in low]
    rng = random.Random(d)
    k = min(len(rest), SAMPLE)
    by_paper = collections.defaultdict(list)
    for r in rest:
        by_paper[r["newspaper"]].append(r)
    for v in by_paper.values():
        rng.shuffle(v)
    picked = []
    while len(picked) < k:  # round-robin across papers so every paper is checked
        for v in by_paper.values():
            if v and len(picked) < k:
                picked.append(v.pop())
    return low + picked, len(low)


def sampled_ids(d):
    sp = p("data", "judge", d, "sample.json")
    return set(load(sp)["story_ids"]) if os.path.exists(sp) else None


def prep(d):
    rows, n_low = pick_sample(d, judged_rows(d))
    save(p("data", "judge", d, "sample.json"), {"story_ids": sorted(int(r["story_id"]) for r in rows), "low_confidence": n_low,
                                               "of_rows": len(judged_rows(d))})
    print(f"Sample: {n_low} low-confidence rows + {len(rows) - n_low} random rows = {len(rows)} of {len(judged_rows(d))}")
    rows = sorted(rows, key=lambda r: (r["newspaper"], r["story_id"]))
    out_dir = p("data", "judge", d)
    for old in glob.glob(os.path.join(out_dir, "batch_*.json")):
        os.remove(old)
    batches, cur, paper = [], [], None
    for r in rows:
        if cur and (len(cur) >= BATCH or (r["newspaper"] != paper and len(cur) >= BATCH * 0.6)):
            batches.append(cur); cur = []
        paper = r["newspaper"]
        cur.append({k: r.get(k, "") for k in ["story_id", "newspaper", "page", "headline", "ref", "source"]})
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches, 1):
        save(os.path.join(out_dir, f"batch_{i:02d}.json"), b)
    no_ref = sum(1 for r in rows if not r.get("ref"))
    print(f"{len(rows)} rows to judge in {len(batches)} batches -> data/judge/{d}/batch_NN.json")
    if no_ref:
        print(f"Warning: {no_ref} rows have no ref; the judge will have to find their clipping by headline.")


def blind_labels(d):
    lab = {}
    for f in sorted(glob.glob(p("data", "judge", d, "blind_*.json"))):
        for x in load(f):
            lab[int(x["story_id"])] = x
    return lab


def compare(d):
    rows = {int(r["story_id"]): r for r in judged_rows(d)}
    sample = sampled_ids(d)
    if sample is not None:
        rows = {k: v for k, v in rows.items() if k in sample}
    lab = blind_labels(d)
    missing = sorted(set(rows) - set(lab))
    bad = [sid for sid, x in lab.items() if x.get("sentiment") not in LABELS]
    agree, dis = 0, []
    for sid, r in rows.items():
        x = lab.get(sid)
        if not x or x.get("sentiment") not in LABELS:
            continue
        if x["sentiment"] == r["sentiment"] and not x.get("headline_fix"):
            agree += 1
        else:
            dis.append({"story_id": sid, "newspaper": r["newspaper"], "page": r["page"], "ref": r.get("ref", ""),
                        "headline": r["headline"], "coder": r["sentiment"], "coder_theme": r["theme_group"],
                        "judge": x["sentiment"], "judge_confidence": x.get("confidence", ""),
                        "judge_reason": x.get("reason", ""), "headline_fix": x.get("headline_fix", "")})
    n = agree + len(dis)
    save(p("data", "judge", d, "disagreements.json"), dis)
    print(f"Judged {n} of {len(rows)} rows. Agreement {agree}/{n} = {agree / n:.1%}." if n else "No judged rows.")
    print(f"{len(dis)} rows to adjudicate -> data/judge/{d}/disagreements.json")
    if missing:
        print(f"Not judged (rerun a judge on these): {missing[:40]}{' ...' if len(missing) > 40 else ''}")
    if bad:
        print(f"Invalid judge labels for: {bad[:40]}")


def apply(d):
    sp = p("data", "stories", f"{d}.json")
    stories = load(sp)
    by_id = {int(r["story_id"]): r for r in stories}
    lab = blind_labels(d)
    dis = {x["story_id"]: x for x in load(p("data", "judge", d, "disagreements.json"))}
    adj = {int(x["story_id"]): x for x in load(p("data", "judge", d, "adjudication.json"), [])}
    pending = sorted(set(dis) - set(adj))
    if pending:
        raise SystemExit(f"No final ruling yet for {len(pending)} disagreements: {pending[:30]}")
    audit, patterns, new_cases = [], collections.Counter(), []
    for sid, x in sorted(adj.items()):
        r = by_id.get(sid)
        if not r:
            continue
        final = x.get("final")
        if final not in LABELS:
            raise SystemExit(f"Story {sid}: invalid final label {final!r}")
        changes = []
        if final != r["sentiment"]:
            changes.append(("sentiment", r["sentiment"], final))
        for fld in ["theme_group", "detailed_theme"]:
            if x.get(fld) and x[fld] != r.get(fld):
                changes.append((fld, r.get(fld, ""), x[fld]))
        if final in {"Not about AAP/Govt", "Govt ad"} and r.get("theme_group"):
            changes.append(("theme_group", r["theme_group"], ""))
        fix = dis.get(sid, {}).get("headline_fix")
        if fix and fix != r["headline"]:
            changes.append(("headline", r["headline"], fix))
        seen = set()
        for fld, before, after in changes:
            if fld in seen:
                continue
            seen.add(fld)
            audit.append([d, sid, r["newspaper"], r["headline"], fld, before, after, x.get("reason", ""),
                          x.get("rule", ""), dis.get(sid, {}).get("coder", ""), lab.get(sid, {}).get("sentiment", "")])
            r[fld] = after
            if fld == "sentiment":
                patterns[(before, after, x.get("rule", "") or "unspecified")] += 1
        if str(x.get("rule", "")).lower() == "new case":
            new_cases.append((sid, x.get("reason", "")))
    save(sp, stories)

    judged = [sid for sid in by_id if by_id[sid]["sentiment"] != "Duplicate" and sid in lab]
    agree_n = len(judged) - len(dis)
    changed_sent = sum(1 for a in audit if a[4] == "sentiment")
    summary = {"date": d, "judge": JUDGE, "rows_judged": len(judged), "blind_agreement": agree_n,
               "agreement_rate": round(agree_n / len(judged), 4) if judged else None,
               "disagreements": len(dis), "sentiment_changed": changed_sent,
               "coder_kept": len(dis) - len({a[1] for a in audit if a[4] == 'sentiment'}),
               "patterns": [{"before": b, "after": a, "rule": ru, "count": c} for (b, a, ru), c in patterns.most_common()],
               "new_cases": [{"story_id": s, "reason": rs} for s, rs in new_cases]}
    save(p("data", "audit", f"{d}.json"), summary)
    with open(p("data", "audit", f"{d}.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Story #", "Newspaper", "Headline", "Field", "Before", "After", "Reason", "Rule",
                    "Coder label", "Judge blind label"])
        w.writerows(audit)

    notes_p = p("data", "notes", f"{d}.json")
    notes = load(notes_p, {})
    if judged:
        total = len([r for r in stories if r["sentiment"] != "Duplicate"])
        scope = f"a sample of {len(judged):,} of the {total:,} stories" if len(judged) < total else f"all {len(judged):,} stories"
        notes["validation"] = (f"Sentiment checked by {JUDGE} as an independent judge on {scope}: it agreed with the "
                               f"coding on {agree_n:,} ({agree_n / len(judged):.0%}); after review "
                               f"{changed_sent} labels were changed.")
        save(notes_p, notes)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("patterns", "new_cases")}, indent=1))
    print("Correction patterns (3 or more = add a dated rule to RULES.md Lessons):")
    for (b, a, ru), c in patterns.most_common():
        print(f"  {b} -> {a} x{c}  [{ru}]")
    for s, rs in new_cases:
        print(f"  New case, story {s}: {rs}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in {"prep", "compare", "apply"}:
        raise SystemExit(__doc__)
    {"prep": prep, "compare": compare, "apply": apply}[sys.argv[1]](sys.argv[2])
