# Daily run: Punjab print media monitor

Run once a day (scheduled 10:23 IST, after the morning files land in WhatsApp). Date D = today in IST unless the run is told another date.

Places:
- Mac folder: `~/Documents/Personal/PB Print Media Monitor/` (dated subfolders `D/`, scripts in `_system/scripts/`, live copy of the dashboard in `Dashboard/`). On the device shell it is `$HOME/mnt/Documents/Personal/PB Print Media Monitor` (or `$HOME/mnt/PB Print Media Monitor` if only that folder is connected).
- WhatsApp Desktop data: `~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared` (read only; never write there).
- Repo `Shilpi-280993/punjab-press-pulse` (GitHub Pages: https://shilpi-280993.github.io/punjab-press-pulse/). Clone with `git clone --depth 1`.

## Steps

1. Copy the day's files (device shell):
   `python3 "<Mac folder>/_system/scripts/wa_copy.py" --date D`
   It writes `D/_manifest.json`. If the monitoring deck (`Print Media Monitoring <d> <Month> <yyyy>.pdf`) is not in `D/`, send a push notification listing the missing files ("open WhatsApp on the Mac so they download, or check that Documents auto-download is on") and stop. If only some editions are missing, carry on and name them in the notes' `sources` line and in the final notification.

2. Bring the files to the workspace: clone the repo, then `device_stage_files` every PDF in `D/` (batches under 500 MB). Skip `_Print Media Monitoring ...` duplicates (same deck, same size) and anything that is not a newspaper or the deck (e.g. a shared "Analysis Report"), but read such a report only as a cross-check, never as a source.

3. Deck: `python3 scripts/deck_text.py "<deck>.pdf" /tmp/deck.json`. Slides have the typed English headlines; slides with `needs_visual: true` have only a header, so read their clippings from the slide image (`pdftoppm -r 90 -f N -l N -png`). Look at the image whenever the typed text is ambiguous or seems to merge two headlines. One row per clipping, coded by RULES.md. The deck sections (AAP / BJP / INC / SAD / Others coverage) help with who is speaking but do not decide sentiment.

4. Full editions (all 15 papers): for each edition PDF, render every page at about 70 to 90 dpi and read it. Add every Punjab-government, AAP or state-matter story that is not already a deck row for that paper (`source: "Full edition"`), including Dainik Savera's district pages. Identify unnamed files by their masthead. Split this across subagents, one per edition (give each the RULES.md text and that paper's deck headlines so it does not duplicate them), and have each return rows as JSON.

5. Merge: one list for D, deck rows first, story_id from 1, set `story` labels on the biggest 10 to 15 events (same label across papers), check event theme groups against earlier days in `data/stories/`. Write `data/stories/D.json` and `data/notes/D.json` (format in RULES.md; every number in the notes must be counted from the rows).

6. Build and check: `python3 scripts/build.py` (it validates fields), then open `index.html` headlessly (playwright) and confirm: no console errors, D appears first in the date picker, the takeaway and the "Biggest stories" table show D's data, and "All dates" still works.

7. Publish: commit `data/`, `exports/`, `index.html`, `stories.json` with message `Add D` and push to `main` (`git -c push.negotiate=true push`).

8. Save to the Mac: commit `exports/AAP_media_analysis_D.csv` into `D/`, and `index.html` + `stories.json` into `Dashboard/` (overwrite).

9. Push notification (one line): relevant stories, negative and positive shares, the top event, missing files if any, and the dashboard link.
