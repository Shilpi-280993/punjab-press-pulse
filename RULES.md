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
| aap_voice | true only when an AAP leader or minister is attacking or rebutting the opposition (BJP, Congress, SAD, others) or the Centre, including fights over Punjab's rights and rebuttals of opposition criticism. Not for announcements, delivery, outreach events, festival greetings or campaign claims, even when an AAP leader is quoted (tightened 16 Nov 2026). |
| story | Optional. Short label for a news event that ran in several papers, e.g. `Punjab Da Crorepati quiz launch`. Use the same label on every row of that event. Label the 10 to 15 biggest events of the day. |
| ref | Where the clipping is, so the judge can find it: `deck slide 41` or `<edition file name> p.7`. Required from 15 Nov 2026. |
| columns | How many newspaper columns wide the story runs (whole number, 1 to 12): count the text columns under its headline at the story's widest point, headline and photo included. Read it from the clipping, or render the edition page if the deck crop is unclear. From 15 Nov 2026. |
| confidence | `high`, `medium` or `low`: the coder's confidence in the sentiment. Use `low` when the clipping is hard to read or two labels could fit; every low row goes to the judge. From 15 Nov 2026. |
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

From the sentiment judge, 15 Nov 2026:

5. Central agencies and central projects with no Punjab government role are `Not about AAP/Govt` (`Others`), even when Punjab places are named: CBI raids in national cases (Mahadev betting app), CBI court verdicts on FCI officials and millers, NHAI tenders, private bodies' office-bearer appointments and features on private enterprise. Seen 6 times (Neutral or Positive changed to Not about).
6. New case: a non-party protest front (for example the Qaumi Insaaf Morcha for Bandi Singhs) is relevant, not `Opposition internal`. If its headline only states its own stance (such as staying out of elections), it is Neutral; it is Negative only when the attack on the government is the headline's lead.
7. New case: a protest against a private employer becomes relevant when the item says the police acted for the employer (detaining protesters, removing their tent). Code it Negative under `Crime & law and order`, not `Schools, health & employees`, since the workers are not government staff.

From owner review, 15 Nov 2026:

8. `Court rebukes & govt finances` is for court rebukes, fines and strain on state finances, so it is never Positive. A court ruling in the government's favour (for example a penalty upheld in an illegal mining case) goes to `Governance, Assembly & politics` with detailed theme `Anti-corruption`, or to the group of its subject. Neutral finance items (bond issues, borrowing) may stay in the group.

From the sentiment judge, 16 Nov 2026:

9. New case: another state's police or ATS case (for example a Rajasthan rail-blast arrest of Punjab residents) is treated like a central agency case under Lesson 5: `Not about AAP/Govt` unless the clipping gives Punjab Police or the Punjab government a role.
10. New case: a consumer complaint against a private business (a gas agency not delivering, staff misbehaving) is `Not about AAP/Govt` when it only asks the administration to act and reports no government decision, failure or reply.

From the sentiment judge, 17 Nov 2026:

11. Positive needs government delivery or action in the headline's lead. Items where the government or AAP is only incidental are Neutral: an AAP leader merely receiving an invitation, a court denying bail at a hearing, abandoned or rusted grenades found by villagers and destroyed, a routine notice of a free camp by an autonomous university. Seen 6 times (Positive changed to Neutral).
12. Lesson 4 applies when the opposition's own event leads even if AAP appears in it: a Congress candidates' meeting, a Congress leader's own yatra announcement, Congress infighting at a yatra where AAP workers showed black flags further down. All `Not about AAP/Govt` (`Opposition internal`). Seen 3 times.
13. New case: a central agency (ED) probe whose subject is Punjab's own officials or a state authority's decisions is relevant, not Lesson 5. ED questioning of GMADA officers over master plan changes or losses to the exchequer is Negative (`Governance, Assembly & politics`, `Anti-corruption`); a procedural court or attachment step in such a case (judicial custody for a retired ADC in a PMLA case built on a Punjab Vigilance FIR, ED attaching a middleman's accounts in the suspended DIG Bhullar case) is Neutral in the same theme. Code every paper's copy of the event alike.
14. New case: a drug recovery from the state's own policeman (opium found on an IRB ASI on jail security, caught by jail staff) is Neutral under `Crime & law and order`, not a Lesson 1 Positive and not a crime Negative.

From the sentiment judge, 19 Nov 2026:

15. Lesson 1 needs an arrest, seizure, raid or recovery in the lead. A case registered on the state's own initiative with none of these (an FIR against men already declared proclaimed offenders or absconders, cases against unknown persons on a Mining Department letter) or police only "close to" the culprits is Neutral under `Crime & law and order`. Seen 4 times (Positive changed to Neutral).
16. A crime reported through an FIR on the victim's complaint with no arrest (motorcycle theft, a bid to grab a widow's land, vandalism of a couple's home, a fake property registry) is a crime report: Negative, `Crime & law and order`, not Neutral and not `Not about AAP/Govt`. Seen 3 times (Neutral changed to Negative).
17. Lesson 12 is decided by the printed headline. When the headline carries only the opposition's own event or slogan (a BJP leader flagging off a yatra, a Congress leader's cycle rally, a SAD women's event) and the attack on AAP is only in the strap or body, the row is `Not about AAP/Govt` (`Opposition internal`); it is Negative only when the attack is the headline's lead. Seen 3 times, both ways.
18. New case: a religious body's no-show at talks with the government (the Akal Takht expert committee skipping the meeting on the Satkar Act) is Neutral when the headline only reports the absence or the government's renewed invitation; it is Negative only when the headline leads with a standoff, hurdle or rejection of the law. Code every paper's copy by this test.
19. New case: stray or rabid dog attacks (dogs from a carcass dump killing a sleeping labourer, a rabid dog biting field workers) are a civic matter the administration owns: relevant and Negative, `Civic services & infrastructure`, `Civic issues`, even when no blame is quoted.
From the sentiment judge, 20 Nov 2026:

21. Lesson 11 also covers routine administration: a courtesy call, a DC's or ADC's routine review meeting or inspection with directions to speed up, candidates filing nomination papers, and an MLA's warning or assurance about future work are Neutral, not Positive. Seen 7 times (3 coder Positives changed to Neutral, 4 blind-check Positives rejected).
22. An item that leads with a grievance about a state body's inaction or a new burden it imposes is Negative even when no opposition party speaks: a dharna called because police have not arrested an accused, residents saying the administration ignores repeated tree felling, a civic certificate tied to a new challan condition. Seen 4 times (Neutral changed to Negative).
23. Lesson 5 does not apply when a state official, a local body or an AAP MP leads the item, even if the scheme or money is central (crop residue machine subsidy, Census, MPLADS works): the row stays relevant. Seen 3 times.
24. New case: an accident or fire with no government angle in the headline is Negative only when the item itself records a failure of a state service (sparking power lines, fire tenders arriving late after repeated calls); otherwise it is `Not about AAP/Govt` (a private tipper hitting a village gate).
25. New case: a BSF recovery is `Not about AAP/Govt` unless Punjab Police took part in the operation itself (a joint search, an arrest or a tip-off); taking custody of the seizure and registering the FIR is not a role.
26. New case: a penalty or stricture on a state official by a statutory watchdog (State Information Commission, Lokpal, human rights or SC commission) is treated like a court rebuke: Negative.

From the sentiment judge, 22 Nov 2026:

27. New case: a Lok Adalat held by the judiciary or the legal services authority that only reports cases settled (cheque-bounce cases, state-level totals) is `Not about AAP/Govt` (`Others`): it records no state government decision, delivery or failure. Seen 8 times once every paper's copy was aligned (Neutral changed to Not about).
28. Lesson 3 covers AAP's own party-promotion events: announcements and preparations for AAP's Foundation Day rally in Moga, and an AAP leader's public meeting to mobilise workers for it, are Positive (`AAP organisation & outreach`), as on 16, 17 and 20 Nov. Lesson 21 keeps internal courtesies (felicitations, nominations, courtesy calls) Neutral. Seen 3 times (Neutral changed to Positive).
29. Lesson 25 is decided by who acted, not by the intro: a BSF recovery described as "joint action" stays `Not about AAP/Govt` when the body shows the BSF handing the haul to Punjab Police, who only weighed it and registered the FIR. Seen 3 times (Positive changed to Not about).

From the sentiment judge, 23 Nov 2026:

30. Lessons 11 and 21 again: a minister attending a kabaddi cup, an AAP leader's visit to a saint, a police plan for nakas and a doctor's health advice that only mentions a scheme are Neutral, not Positive. Seen 5 times (3 coder and 2 blind-check Positives).
31. A private or union event (a trust's marathon, a union's own meeting) and an accident with no state failure in the item are `Not about AAP/Govt`, even when an MLA or officials attend or the police register the case (Lessons 5 and 24). Seen 3 times (Neutral or Negative changed to Not about).
32. A health drive that is under way and reaching people (pulse polio drops being given, "N children given drops", a drive launched with drops administered) is Positive under `Schools, health & employees`, `Health services`; only a notice of a future drive is Neutral. 13 copies were aligned to this ruling.
33. New case: when a court raps a central body (BBMB) in a case where the Punjab government is a party and owns the project (the Kharar sarovar), but the hearing gives Punjab neither a rebuke nor a ruling in its favour, the row is relevant and Neutral under the subject's group (`Punjab's rights: water, PU, Chandigarh`), in every paper.
34. New case: a seasonal illness or health-advice feature (viral fever, coughs and colds as the weather changes) that reports no shortage, failure or new service of the state health system is `Not about AAP/Govt` (`Weather (not govt)`), even when government hospital doctors are quoted.
35. New case: a trial court's conviction or sentence in an ordinary Punjab Police case (robbery, snatching) is relevant and Neutral under `Crime & law and order`, neither `Not about AAP/Govt` nor a Lesson 1 Positive.

From the sentiment judge, 25 Nov 2026:

36. New case: when the printed headline has no tilt and no speaker (a round-up line such as "Politics heats up in Punjab after Akali-BJP alliance"), the strap, photo and lead decide; if they are an AAP minister's attack on the opposition, the row is Positive, `AAP leaders' counter-attacks`, aap_voice true. The reverse does not hold: a main headline with its own tilt (a woman shot dead) is not overridden by a strap (shooters arrested); that row stays Negative under Lesson 1's "in the lead" test.
37. New case: a report of events held or results under the state's own games (Khedan Watan Punjab Diyan), with the games named in the headline, is Positive under `Hockey & sports`; a notice of future fixtures is Neutral; a protest or complaint at the games is Negative. 3 more copies were aligned.
38. New case: an enforcement drive by a civic body, the administration or traffic police that reports challans or fines actually issued (more than 30 challans for plastic bags in Patiala) is Positive (`Civic services & infrastructure`, or `Police action` when by police); a planned drive, warning or appeal alone stays Neutral under Lesson 21.
39. New case: a wild animal incident is relevant when the wildlife or forest department or the administration responds in the item. It is Neutral when the headline leads with the animal's attacks and the response is under way (cage set, SDM visit); Positive when the headline carries a completed capture or rescue; Negative only when the lead is a complaint that the department has not acted.

From the merge, 25 Nov 2026:

40. The deck repeats the same clipping in more than one section (on 25 Nov the AAP, BJP and SAD sections each carried the same front-page alliance stories and AAP reaction boxes). Before coding, match deck rows across all slides by paper, page and headline, and mark every later copy `Duplicate`, including multi-quote reaction boxes whose quotes are already rows. The District Front Page file can also include a page the deck already covers (25 Nov: Punjabi Tribune page 8); rows for stories already on a deck slide are `Duplicate`.

From the merge, 19 Nov 2026 (seen again 25 Nov, when PDF pages 66 to 78 repeated pages 19 to 24 and 45 to 51):

20. Dainik Savera's PDF can print the same district page twice (19 Nov: Bathinda 1 to Malwa 6 and Moga 4 to Moga 8 each appeared on two PDF pages). Rows from the second copy of a page are `Duplicate`, as for repeated deck clippings.

## Daily commentary (data/notes/<date>.json)

```
{"sources": "What was read: the deck's N clippings plus every page of the 15 full editions ...",
 "takeaway": "{negative_share} of the {relevant} relevant stories were negative and {positive_share} positive; <two sentences on what drove the day>",
 "well": [["Bold point.", "Evidence with paper counts."], [..], [..]],
 "improve": [["Bold point.", "Evidence with paper counts."], [..], [..]]}
```
Placeholders in braces are filled by the dashboard: relevant, positive, neutral, negative, positive_share, neutral_share, negative_share, front_pages, opposition_statements. Every number written into the text must come from that day's rows.
