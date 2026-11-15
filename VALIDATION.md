# Sentiment judge: validating the day's classification

After the day's rows are coded (DAILY_RUN.md step 5, by Sonnet subagents) and before the dashboard is built, a sample of rows is checked by the strongest model available as an independent judge. Use the Agent tool with `model: "fable"` (Claude Fable 5.2). The judge never sees the coders' work while forming its own view.

Judged labels: `Positive`, `Neutral`, `Negative`, `Not about AAP/Govt`, `Govt ad`. Rows already marked `Duplicate` are skipped.

## Stage 1: blind labelling

1. `python3 scripts/judge.py prep D` picks the rows to judge (from 15 Nov 2026, to save usage): every row the coder marked `confidence: "low"`, plus a random sample of the rest spread across papers (seeded by the date), about 100 rows in all. The list is in `data/judge/D/sample.json`. It writes `data/judge/D/batch_NN.json`: about 50 rows each, grouped by newspaper, with story_id, newspaper, page, headline, ref and source only. Sentiment and theme are removed.
2. Start one judge subagent per batch, all with `model: "fable"`, in parallel. Give each: the full text of RULES.md, the batch file contents, and the path of the staged PDFs so it can look at each clipping (`pdftoppm -r 90 -f N -l N -png` on the deck for `deck slide N`; the edition page for full-edition rows). Prompt:

   > You are the judge of sentiment for a Punjab newspaper monitor. For each row, look at the clipping and decide its label from the Punjab government's and AAP's point of view, strictly by the rules given. Judge the headline's lead, not the whole article. Return only JSON: a list of {"story_id", "sentiment", "confidence" (high/medium/low), "reason" (one short sentence naming the rule or the words that decide it)}. If the English headline is a wrong translation of the clipping, add "headline_fix" with a corrected headline.

   Save each answer as `data/judge/D/blind_NN.json`.

## Stage 2: compare

`python3 scripts/judge.py compare D` measures agreement between coders and judge and writes `data/judge/D/disagreements.json` (both labels, the judge's reason, headline, ref).

## Stage 3: adjudication (judge has the final word)

Start one more `model: "fable"` subagent with RULES.md, the disagreements file and the staged PDFs. Prompt:

> Two classifiers disagreed on these rows. For each, look at the clipping again and give the final label by the rules. You may keep either label. Return only JSON: a list of {"story_id", "final", "reason", "rule" (rule name or "new case"), and, if the sentiment change also changes the theme, "theme_group" and "detailed_theme" from the RULES.md lists}.

Save as `data/judge/D/adjudication.json`. Low-confidence agreements are not re-judged.

## Stage 4: apply and feed back

1. `python3 scripts/judge.py apply D` applies every final ruling to `data/stories/D.json`, logs each change in `data/audit/D.csv`, writes `data/audit/D.json` (agreement rate, changes by type) and puts a one-line validation note into `data/notes/D.json`, which the dashboard shows under "The numbers".
2. It prints the correction patterns of the day (for example `Neutral -> Positive x6, police seizures`). Any pattern seen 3 or more times, or any ruling marked "new case", becomes a dated rule under "Lessons" in RULES.md, so the next day's coders apply it from the start.
3. Recount anything in the notes text (takeaway, well, improve) that the changes affect.
4. If agreement falls below 85%, say so in the final notification.
