# Coding rules: Punjab print media monitor

These rules reproduce the analysis built for 27 and 28 Oct 2026 (951 stories, audited on 31 Oct). Apply them the same way every day so dates stay comparable.

## What counts as a story

- One row per news item per newspaper. The same event in 12 papers is 12 rows, linked by the same `story` label.
- Sources: every clipping in the daily monitoring deck (`source: "Monitoring deck"`), plus stories found in the full editions that the deck missed (`source: "Full edition"`).
- A clipping repeated in the deck (same paper, same page, same item) is coded once; a second copy gets `sentiment: "Duplicate"`, `theme_group: ""`, `detailed_theme: "Duplicate"`.

## Fields (every row)

| Field | Values |
|---|---|
| story_id | Integer, unique within the date. Deck stories first in slide order, then full-edition stories. |
| source | `Monitoring deck` or `Full edition` |
| newspaper | Ajit, Jagbani, Punjabi Tribune, Punjabi Jagran, Rozana Spokesman, Punjab Kesari, Dainik Jagran, Dainik Bhaskar, Dainik Savera, The Tribune, Hindustan Times, Times of India, Indian Express, The Savera Times |
| language | Punjabi (Ajit, Jagbani, Punjabi Tribune, Punjabi Jagran, Rozana Spokesman), Hindi (Punjab Kesari, Dainik Jagran, Dainik Bhaskar, Dainik Savera), English (others) |
| page | Page label as printed: `1`, `2`, `J2`, `Bathinda 1`, `Ludhiana 3` |
| front_page | true only for page 1 of the main edition |
| page_weight | 3 = front page, 2 = pages 2 and 3 or a district front page, 1 = everything else |
| headline | Short English rendering of the headline (translate Punjabi and Hindi). Keep names and numbers exact. |
| sentiment | `Positive`, `Neutral`, `Negative` (relevant stories only), or `Not about AAP/Govt`, `Govt ad`, `Duplicate` |
| theme_group | Ranked group (see list). Empty string for Not about AAP/Govt, Govt ad, Duplicate. |
| detailed_theme | Finer label (see examples). |
| aap_voice | true when an AAP leader or minister is the speaker making the point (including the CM attacking the BJP or the Centre) |
| story | Optional. Short label for a news event that ran in several papers, e.g. `Punjab Da Crorepati quiz launch`. Use the same label on every row of that event. Label the 10 to 15 biggest events of the day. |
| ref | Where the clipping is, so the judge can find it: `deck slide 41` or `<edition file name> p.7`. Required from 15 Nov 2026. |
| date | YYYY-MM-DD |

## Relevance

Relevant = about AAP, the Punjab government, a Punjab minister or official, or a state matter the government owns (law and order, services, schemes, finances). Not relevant: opposition parties' internal affairs (`Opposition internal`), national or foreign news with no Punjab government angle (`Others`), weather (`Weather (not govt)`). Government advertisements are `Govt ad` with detailed_theme `Government advertising`.

## Sentiment, from the government's point of view

- Positive: delivery, launches, grants, schemes reaching people, police action (seizures, arrests, raids, demolition of smugglers' property are always Positive), AAP leaders' counter-attacks, wins on Punjab's rights.
- Negative: opposition attacks, crime and murders, protests against the government, court rebukes, shortages, civic failures, defections from AAP, AAP MLAs criticising their own government.
- Neutral: factual items with no clear tilt (Election Commission orders, routine Assembly business, hearings).
- Judge by the headline's lead. If the headline leads with a family demanding the CM or DGP resign, it is Negative even when an arrest is mentioned.

## Theme groups (keep these names)

Standing groups: Opposition attacks on the govt · Police action on gangs, arms & drugs · Crime & law and order · Governance, Assembly & politics · Civic services & infrastructure · Schools, health & employees · Welfare schemes · Farmers, stubble & paddy · Drugs & medicine access · Court rebukes & govt finances · Punjab's rights: water, PU, Chandigarh · Religious outreach: Valmiki, Kartarpur · AAP leaders' counter-attacks · AAP organisation & outreach · Hockey & sports

Event groups: when one event or controversy runs in many papers, give it its own group (27 to 28 Oct examples: `Jhota murder protest`, `CM's OSD questioned by CBI`, `100 mini buses & transport`). Reuse the exact name on later days while the event continues.

Detailed theme examples: `Opposition attack: BJP` / `: Congress` / `: SAD` / `: Other` (always Negative; the dashboard counts share of voice from these), `Assembly uproar`, `Defections from AAP`, `Police action vs drugs` / `vs arms` / `vs gangs` / `vs crime`, `Law & order / crime`, `Murder`, `Attack on police`, `Custodial/drug death protest`, `Paddy procurement`, `Agriculture & stubble`, `Employee protests`, `Health services`, `Civic issues`, `Development works`, `Social welfare`, `AAP attack on opposition (drugs)`, `AAP attack on BJP (national)`, `Election Commission`, `Anti-corruption`, `Own MLAs' complaints`.

## Lessons from audits and the sentiment judge (apply when coding, not after)

The daily sentiment judge (VALIDATION.md) adds a dated rule here whenever the same kind of correction appears 3 or more times in a day, or it finds a case these rules do not cover. Read the last 7 days of `data/audit/*.csv` as worked examples before coding.

From the 31 Oct audit:

1. Police seizures, raids and arrests are Positive, theme `Police action on gangs, arms & drugs`.
2. The CM or an AAP leader attacking the BJP, Congress or SAD is `aap_voice: true` and Positive (`AAP leaders' counter-attacks`, or `Punjab's rights` when about water, PU or Chandigarh).
3. An AAP halqa in-charge's public meeting is `AAP outreach`, Positive.
4. Announcements of opposition rallies and opposition-versus-opposition rows are `Not about AAP/Govt` (`Opposition internal`).

## Daily commentary (data/notes/<date>.json)

```
{"sources": "What was read: the deck's N clippings plus every page of the 15 full editions ...",
 "takeaway": "{negative_share} of the {relevant} relevant stories were negative and {positive_share} positive; <two sentences on what drove the day>",
 "well": [["Bold point.", "Evidence with paper counts."], [..], [..]],
 "improve": [["Bold point.", "Evidence with paper counts."], [..], [..]]}
```
Placeholders in braces are filled by the dashboard: relevant, positive, neutral, negative, positive_share, neutral_share, negative_share, front_pages, opposition_statements. Every number written into the text must come from that day's rows.
