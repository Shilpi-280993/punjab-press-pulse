# Punjab Press Pulse

Daily dashboard of how Punjab newspapers cover AAP and the Punjab government, built from the "PB Print Media Monitoring Core" WhatsApp group files.

- Daily procedure: DAILY_RUN.md
- Coding rules (sentiment, themes, fields): RULES.md
- Sentiment judge (Claude Fable 5.2) and feedback loop: VALIDATION.md, scripts/judge.py
- Data: `data/stories/<date>.json` and `data/notes/<date>.json`; build with `python3 scripts/build.py` (writes `index.html`, `stories.json`, `exports/`). Never hand-edit `index.html`; edit `src/` or `data/` and rebuild.
- Documents written for the owner: Cambria 12, black text, no colour, no em dashes.
