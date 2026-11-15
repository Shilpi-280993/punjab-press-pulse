#!/usr/bin/env python3
"""Copy one day's files from the WhatsApp group into a dated folder.

Runs on the Mac side (device_bash VM). Reads WhatsApp Desktop's local database (a copy, never the
live file) to find the group's media for the date, then copies every file that WhatsApp has already
downloaded into <dest>/<YYYY-MM-DD>/ with its real file name. Files WhatsApp has not downloaded are
listed as missing in _manifest.json (turn on Documents auto-download in WhatsApp to avoid this).
Files saved into the dated folder by hand count as present (matched by exact file size), so they are
neither reported missing nor copied twice.

Usage: python3 wa_copy.py [--date YYYY-MM-DD] [--wa DIR] [--dest DIR] [--group NAME]
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile

GROUP = "PB Print Media Monitoring Core"
APPLE_EPOCH = 978307200  # 2001-01-01 in Unix seconds
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def find_wa():
    hits = glob.glob(os.path.expanduser("~/mnt/*/ChatStorage.sqlite"))
    return os.path.dirname(hits[0]) if hits else None


def find_dest():
    for pat in ["~/mnt/*/Personal/PB Print Media Monitor", "~/mnt/PB Print Media Monitor", "~/mnt/*/PB Print Media Monitor"]:
        hits = glob.glob(os.path.expanduser(pat))
        if hits:
            return hits[0]
    docs = glob.glob(os.path.expanduser("~/mnt/Documents/Personal"))
    return os.path.join(docs[0], "PB Print Media Monitor") if docs else None


def clean(name):
    name = re.sub(r"[/\\:\x00-\x1f]", "_", name).strip().strip(".")
    return name[:180]


def pdf_title(path):
    try:
        out = subprocess.run(["pdfinfo", path], capture_output=True, text=True, timeout=30).stdout
        m = re.search(r"^Title:\s+(.+)$", out, re.M)
        return m.group(1).strip() if m else ""
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=dt.datetime.now(IST).strftime("%Y-%m-%d"))
    ap.add_argument("--wa", default=None)
    ap.add_argument("--dest", default=None)
    ap.add_argument("--group", default=GROUP)
    a = ap.parse_args()
    wa = a.wa or find_wa()
    dest_root = a.dest or find_dest()
    if not wa:
        raise SystemExit("WhatsApp folder not found (connect ~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared).")
    if not dest_root:
        raise SystemExit("Destination folder not found (connect ~/Documents or the PB Print Media Monitor folder).")

    tmp = tempfile.mkdtemp()
    for ext in ["", "-wal", "-shm"]:
        src = os.path.join(wa, "ChatStorage.sqlite" + ext)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(tmp, "ChatStorage.sqlite" + ext))
    db = sqlite3.connect(os.path.join(tmp, "ChatStorage.sqlite"))
    chat = db.execute("select Z_PK from ZWACHATSESSION where ZPARTNERNAME = ?", (a.group,)).fetchone()
    if not chat:
        raise SystemExit(f"Group '{a.group}' not found in WhatsApp.")
    start = dt.datetime.strptime(a.date, "%Y-%m-%d").replace(tzinfo=IST).timestamp() - APPLE_EPOCH
    rows = db.execute(
        """select m.ZMESSAGEDATE, m.ZTEXT, mi.ZTITLE, mi.ZMEDIALOCALPATH, mi.ZFILESIZE
           from ZWAMESSAGE m join ZWAMEDIAITEM mi on mi.ZMESSAGE = m.Z_PK
           where m.ZCHATSESSION = ? and m.ZMESSAGEDATE >= ? and m.ZMESSAGEDATE < ?
           order by m.ZMESSAGEDATE""", (chat[0], start, start + 86400)).fetchall()

    day_dir = os.path.join(dest_root, a.date)
    os.makedirs(day_dir, exist_ok=True)
    copied, missing, existing = [], [], []
    # files already in the folder (copied earlier or saved by hand), matched by exact byte size
    sizes = {}
    for f in os.listdir(day_dir):
        fp = os.path.join(day_dir, f)
        if os.path.isfile(fp) and not f.startswith(("_", ".")):
            sizes[os.path.getsize(fp)] = f
    for ts, text, title, local, size in rows:
        if not size:
            continue  # stickers / empty items
        t = dt.datetime.fromtimestamp(ts + APPLE_EPOCH, IST).strftime("%H:%M:%S")
        label = (text or title or "").strip()
        if size in sizes:
            existing.append(sizes[size])
            continue
        src = os.path.join(wa, "Message", local) if local else None
        if not src or not os.path.exists(src):
            missing.append({"time": t, "name": label or "(no name)", "bytes": size})
            continue
        ext = os.path.splitext(src)[1].lower() or ".pdf"
        name = label or pdf_title(src) or f"file_{t.replace(':', '')}"
        name = clean(name)
        if not name.lower().endswith(ext):
            name += ext
        target = os.path.join(day_dir, name)
        n = 1
        while os.path.exists(target):
            if os.path.getsize(target) == os.path.getsize(src):
                break
            base, e = os.path.splitext(name)
            target = os.path.join(day_dir, f"{base} ({n}){e}")
            n += 1
        if os.path.exists(target) and os.path.getsize(target) == os.path.getsize(src):
            existing.append(os.path.basename(target))
            continue
        shutil.copy2(src, target)
        sizes[size] = os.path.basename(target)
        copied.append({"time": t, "file": os.path.basename(target), "bytes": size})

    manifest = {
        "date": a.date, "group": a.group, "checked_at": dt.datetime.now(IST).isoformat(timespec="seconds"),
        "files_in_group": len([r for r in rows if r[4]]), "copied_now": copied, "already_in_folder": existing,
        "missing_not_downloaded": missing,
        "files_in_folder": sorted(f for f in os.listdir(day_dir) if not f.startswith(("_", "."))),
    }
    with open(os.path.join(day_dir, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in manifest.items()}, indent=1))
    if missing:
        print("NOT DOWNLOADED in WhatsApp yet: " + "; ".join(m["name"] for m in missing))


if __name__ == "__main__":
    main()
