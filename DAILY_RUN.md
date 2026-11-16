# Daily run: Punjab print media monitor

Run once a day (scheduled 10:26 IST, after the morning files land in WhatsApp). Date D = today in IST unless the run is told another date.

Places:
- Mac folder: `~/Documents/Personal/PB Print Media Monitor/` (dated subfolders `D/`, scripts in `_system/scripts/`, live copy of the dashboard in `Dashboard/`). On the device shell it is `$HOME/mnt/Documents/Personal/PB Print Media Monitor` (or `$HOME/mnt/PB Print Media Monitor` if only that folder is connected).
- WhatsApp Desktop data: `~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared` (read only; never write there).
- Repo `Shilpi-280993/punjab-press-pulse` (GitHub Pages: https://shilpi-280993.github.io/punjab-press-pulse/). Clone with `git clone --depth 1`.

## Steps

1. Copy the day's files (device shell):
   `python3 "<Mac folder>/_system/scripts/wa_copy.py" --date D`
   It writes `D/_manifest.json`. If the monitoring deck (`Print Media Monitoring <d> <Month> <yyyy>.pdf`) is not in `D/`, send a push notification listing the missing files ("open WhatsApp on the Mac so they download, or check that Documents auto-download is on") and stop. If only some editions are missing, carry on and name them in the notes' `sources` line and in the final notification.

2. Bring the files to the workspace: clone the repo, then `device_stage_files` every PDF in `D/` (batches under 500 MB). If there are two deck files (e.g. `Print Media Monitoring <date>.pdf` and `... (1).pdf`, or a `_` copy), they can differ: use the one whose `pdftotext` output is longest (most typed headlines) and skip the other. Files saved as `file_NNNNNN.pdf` are unnamed editions: identify them by masthead (Dainik Savera is the ~86 to 91 page Hindi one). Skip the second deck copy, the `STATE FRONT PAGE ...` file (it only repeats the main editions' front pages; dropped 15 Nov 2026), and anything that is not a newspaper, the deck or the `DISTRICT FRONT PAGE ...` file (e.g. a shared "Analysis Report"), but read such a report only as a cross-check, never as a source.

3. Deck: `python3 scripts/deck_text.py "<deck>.pdf" /tmp/deck.json`. Split the slides two ways (from 16 Nov 2026, to save usage): slides with typed headlines (`needs_visual: false` and non-empty `headlines`) go to one Sonnet subagent that codes them from the text alone, rendering a slide image only when the text is ambiguous, seems to merge two headlines, or a confidence would otherwise be low; slides with `needs_visual: true` go to Sonnet subagents of about 30 slides each that read the images. Skip the section title slides and the "Front Page News" summary slides (they repeat clippings coded later). Slides have the typed English headlines; slides with `needs_visual: true` have only a header, so read their clippings from the slide image (`pdftoppm -r 90 -f N -l N -png`). Look at the image whenever the typed text is ambiguous or seems to merge two headlines. One row per clipping, coded by RULES.md. The deck sections (AAP / BJP / INC / SAD / Others coverage) help with who is speaking but do not decide sentiment.

Coding subagents and the blind judges run on Sonnet (Agent tool, `model: "sonnet"`); only the final adjudication uses Claude Fable 5.2. Every coded row carries `columns` (how many newspaper columns wide the story runs; see RULES.md) and a `confidence` field (high/medium/low): mark `low` whenever the headline is hard to read or the rules could fit two labels, because every low row is sent to the judge.

Before coding, read RULES.md including its Lessons, and the last 7 days of `data/audit/*.csv` as worked examples of past corrections; pass both to every coding subagent.

4. Full-edition sweep (from 15 Nov 2026, to save usage): sweep only Dainik Savera (all pages, including its district pages), The Savera Times (all pages, including its district editions) and the `DISTRICT FRONT PAGE ...` file. Do not sweep the other papers' main editions: on 15 Nov they added only 0 to 16 stories each because the deck already covers them, so their coverage comes from the deck alone. For each file, render every page at about 70 to 90 dpi and read it. Add every Punjab-government, AAP or state-matter story that is not already a deck row for that paper (`source: "Full edition"`). Identify unnamed files by their masthead; in the District Front Page file skip any page that is the same page as one in a main edition PDF. Split this across Sonnet subagents (`model: "sonnet"`), about 30 pages each (Dainik Savera in three parts, the District file in two), give each the RULES.md text and that paper's deck headlines so it does not duplicate them, and have each return rows as JSON.

5. Merge: one list for D, deck rows first, every row with its `ref`, story_id from 1, set `story` labels on the biggest 10 to 15 events (same label across papers), check event theme groups against earlier days in `data/stories/`. Write `data/stories/D.json` and `data/notes/D.json` (format in RULES.md; every number in the notes must be counted from the rows).

6. Sentiment judge (VALIDATION.md): `python3 scripts/judge.py prep D` (picks every low-confidence row plus a random sample of 100 other rows), run the blind judges (Agent tool, `model: "sonnet"`, one per batch, in parallel), `python3 scripts/judge.py compare D`, run the Claude Fable 5.2 adjudication (`model: "fable"`) on the disagreements; its ruling is final, then `python3 scripts/judge.py apply D`. Turn any correction pattern seen 3 or more times, and every "new case", into a dated rule under Lessons in RULES.md, and recount the notes text if the changes affect it.

7. Build and check: `python3 scripts/build.py` (it validates fields), then `node scripts/dashboard_pdf.js "$PWD" D` (run from a directory where `require('playwright')` resolves) for a PDF of the dashboard as it looks on screen (`exports/Punjab_press_dashboard_D.pdf`), then open `index.html` headlessly (playwright) and confirm: no console errors, D appears first in the date picker, the takeaway and the "Biggest stories" table show D's data, and "All dates" still works.

8. Publish: commit `data/` (stories, notes, judge, audit), `RULES.md`, `exports/`, `index.html`, `stories.json` with message `Add D` and push to `main` (`git -c push.negotiate=true push`).

9. Save to the Mac: commit `exports/AAP_media_analysis_D.csv`, `exports/Punjab_press_dashboard_D.pdf` and `data/audit/D.csv` (as `judge_audit_D.csv`) into `D/`, and `index.html` + `stories.json` into `Dashboard/` (overwrite).

10. Push notification (one line): relevant stories, negative and positive shares, the judge's agreement rate and number of labels changed, the top event, missing files if any, and the dashboard link.
