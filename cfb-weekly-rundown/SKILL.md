---
name: cfb-weekly-rundown
description: Full game-by-game college football (CFB) rundown for the current (or a named) week, in bullet points, with every stat ranked out of FBS and explained, plus charts (slate overview and one matchup/price chart per game). Use whenever the user asks for "this week's rundown", "give me this week's rundown", "rundown for week N", "run the rundown", "all the games this week with all the stats", or anything similar for college football. Info only, no grades. Typed as /cfb-weekly-rundown (optionally with a week number or team names to add). Named cfb-weekly-rundown so it never collides with the NFL project's weekly-rundown skill.
---

# CFB weekly rundown (master prompt v1.5)

the user wants one command that produces the full Week-N college football rundown without spelling it out. The NFL version (`../NFL Model/04_Research/Week11/04_Full_Rundown_Nov21.md`) is the model: match its structure, depth and tone. Every game gets plenty of bullets, every number gets context ("#12 of 138", the FBS average, what it means), and nothing gets left out.

This is **information, not picks**. Don't set probability ranges or grades here. If the user then asks to grade something, switch to the `cfb-parlay-model` skill (PRE-ANALYSIS CHECKLIST, verification gate, brutality filter) and log any leg that gets a range.

**Monday gate (CLAUDE.md, Section 13A):** on a Monday, the prior week's audit comes before looking at the next slate. If the audit for last week isn't in `08_Weekly_Reviews/` yet, say so in one line and ask whether to run it first. the user may choose to run the rundown anyway.

## Step 0. Context (read, don't skip)
1. `00_PROJECT_CONTEXT.md` ("Where things stand") and the latest `08_Weekly_Reviews/Week*_Audit.md`, especially its forward takeaways and regression flags. Every watchlist item must show up in the rundown.
2. Files already in `04_Research/Week<N>/` (earlier shortlists, re-checks, rundowns). Reuse facts that are still current, and say what changed.
3. Get the time from PowerShell `Get-Date` (Git Bash's `TZ=America/New_York date` prints UTC on this machine).

## Step 1. Pull the data (one script, about 8-12 minutes)
From the project folder:
```
python -X utf8 _tools\weekly_rundown\build_rundown.py
```
- No `--week` = auto: the earliest week with 3+ FBS games still to play. If the user names a week, pass `--week N`.
- Slate: every game with a Power 4 team (SEC, Big Ten, Big 12, ACC) or Notre Dame, plus any AP Top 25 team. `--add "Boise State,Tulane"` adds teams the user names. `--full-fbs` = every game with an FBS team.
- `--skip-odds`, `--skip-weather`, `--skip-qbs` skip those pulls. `--include-played` keeps finished games.
- **Quotas:**
  - CFBD: at most 7 calls per run. Responses are cached in `_data/cfbd_cache/<date>/` for 6 hours, so a second run the same day costs 0. The 1,000/month quota is shared with every CFBD tool (Section 3B). `--refresh-cfbd` forces new calls; use it only when stats must be re-pulled mid-day.
  - Action Network (lines), ESPN (box-score QBs), NWS and Open-Meteo (weather) need no key and have no tight quota.
  - **OddsPapi is not used here.** Spend it only on shortlisted games or props the user is considering (`python _tools\oddspapi.py`, 250/month).

It writes:
- `04_Research/Week<N>/rundown_data/week<N>_lines_<mondd>.csv`: every book's spread, total and moneyline (7 named books plus Action Network's opening line and consensus).
- `04_Research/Week<N>/rundown_data/week<N>_team_stats_<mondd>.csv`: every FBS team's records, splits, last 4, ATS and overs (vs DraftKings closing lines), Pythagorean and luck flag, and the advanced stats, each with a `_rk` rank column.
- `04_Research/Week<N>/rundown_facts_<mondd>.json`: everything per game. It covers:
  - market: modal and median lines, vig-free cover/over/moneyline %, books
  - movement vs the opening line and the previous pull, with key numbers crossed
  - price ladders and the 55.2% "needs"
  - kickoff ET, venue (dome, grass, elevation, coordinates), neutral site, conference game, FCS flag, rest days
  - QBs from each team's last two box scores
  - weather (NWS hourly plus Open-Meteo, including the previous-run forecasts)
  - both teams' stats, plus FBS averages

Read the facts JSON with Python, not by eye. Notes on the fields:
- `market.spread_home_modal` is the home team's line (negative = home favored).
- `ladders` are **estimated from key numbers**: master prompt 5B weights on a 16.5-point margin curve, anchored to the market price. The Action Network feed has no alternate-line ladders. Always say "estimated" when quoting a "needs" number.
- `ladders.needs_55_2.away` is in the away team's view.
- `stats.luck` = win % minus Pythagorean. A gap of 0.18 or more sets `luck_flag` (Section 7).
- Ranks: 1 = best. For points allowed, PPA allowed, sacks taken, turnovers given, havoc allowed and seconds per play, 1 is the lowest.
- The script prints the API use at the end. Keep that line for Step 6.

## Step 2. Charts and draft (about 3 minutes, no API calls)
```
python -X utf8 _tools\weekly_rundown\make_charts.py --week N
python -X utf8 _tools\weekly_rundown\draft_rundown.py --week N
```
`make_charts.py` writes PNGs to `04_Research/Week<N>/charts_<mondd>/`.

Slate charts:
- `00_market_favorites.png`: each favorite's win %, in kickoff order (a tick marks the previous pull).
- `01_line_movement.png`: spread movement since the previous pull, or since the opening line when there isn't one. Key numbers 3, 7, 10 and 14 are marked.
- `02_efficiency_map.png`: offense PPA against defense PPA, in four quadrants, every team labeled.
- `03_luck_check.png`: Pythagorean vs actual, with flags at 18+ points.

Per game, `gNN_<AWAY>_<HOME>.png`:
- 18 stat ranks out of FBS (away blue, home orange)
- the away team's price ladder and the over ladder, both estimated from key numbers, with the 55.2% lines
- game-window wind (NWS bars, Open-Meteo gusts, the 15 mph and 22 mph lines). Domes say so.

**Look at a few PNGs (Read the image) before using them:** the efficiency map, one game chart, and any game with a wind flag. If labels overlap or a panel is empty, fix `make_charts.py` rather than dropping the chart.

`draft_rundown.py` writes `04_Research/Week<N>/NN_Full_Rundown_<Mon><DD>.md`, where NN is the next number in the folder. It already contains every number from the facts file, in the full layout. Lines marked `[FILL]` are yours to complete from opened pages. Then edit the draft into the finished rundown.

## Step 3. Availability (opened pages only)
- **Big Ten and SEC:** the official reports via HD Intelligence. Open the pages in the browser, wait ~5 seconds, then read `document.body.innerText`:
  - `https://app.hdintelligence.com/?source=B10&sport=Football&conf=B10&type=report`
  - `https://app.hdintelligence.com/?source=SEC&sport=Football&conf=SEC&type=report`
  - Big Ten posts by 8 PM ET three, two and one days before kickoff, plus a gameday report 2 hours before. SEC posts Wed-Fri evenings plus gameday.
  - Say which report it is, and REPORT PENDING if it isn't up yet.
- **ACC, Big 12, Notre Dame and G5:** no official report. Use beat writers and team sites via the `web-fetch` agent or WebFetch, never a search snippet. Mark rumors SPECULATION (Section 9).
- List Out / Doubtful / Questionable for both teams and say why each matters. Flag QBs, starters and kickers.

## Step 4. QBs and the news that matters
- Confirm both starting QBs for every game. Count a QB as confirmed when he started the last game (`qbs.last_starter`), the QB didn't change between the last two games, and he's not on the report. Anything else needs an opened page: a QB change (`qbs.change` = true), a QB listed Probable, Questionable or GTD (UNCERTAIN until kickoff, Section 9), or a coach who hasn't named a starter.
- Explain every line move of 1.5+ points, or across 3 or 7 (`movement.flag`). If the cause can't be found on an opened page, write "cause not confirmed".
- Team context (Section 9A) from beat writers where time allows: CFP stakes, bowl chase, coaching changes. Note which teams have none.

## Step 5. Finish the rundown
Keep the draft's layout. Title: `# Week N full rundown, every game — <Day Mon DD, YYYY, time ET>`.

Top of the file:
- **How to read the numbers** (from the draft): ranks out of N, FBS averages, the PPA scale, Pythagorean, vig-free, the estimated "PrizePicks needs", sources, and "This is information, not picks."
- Results of any games already played this week (CFBD /games, or ESPN), and a rest note covering byes, short weeks and Thanksgiving games.

Next comes **"## The slate in charts"**: the four slate PNGs with relative paths. Replace each `[FILL]` with one plain sentence: how to read the chart and the one thing it shows this week.

Then **one section per game in kickoff order**:
- Header: `## N. #AP Away (W-L) @ Home (W-L)`.
- A bold line with kickoff ET, venue and city, dome or open-air, grass or turf, conference game Y/N, neutral site, FCS opponent.
- The game's chart right after the bold line, with one sentence on how to read it.

Then these 10 bold sub-headers, each with several bullets:
1. **The betting market:** spread by book and the vig-free cover %; total and over %; the favorite's moneyline %; movement since the opening line and the last pull (and why, or "cause not confirmed"); key numbers crossed; the estimated PrizePicks numbers each side and each total side needs.
2. **Quarterbacks:** both starters and how they were confirmed, backups, recent QB history and notable numbers.
3. **Injuries that matter:** out, doubtful and questionable for both teams, why each matters, and which report it is.
4. **Weather:** temperature, rain %, wind and gusts from both sources, the NWS wording, whether the 15+ mph sustained / 22+ mph gust rule or the 50%+ rain note applies, how the forecast moved, and altitude where relevant. Domes: one line.
5. **Records and form:** overall, home and away, last 4 with point differential, last game, ATS, overs, Pythagorean vs actual with REGRESSION UP or DOWN flags, and rest days.
6. **Scoring:** points for and against per game, with ranks and the FBS average.
7. **Efficiency:** PPA per play and success rate, offense and defense, passing and rushing splits, with ranks (garbage time removed).
8. **Pace and explosive plays:** plays per game and seconds per play with ranks; explosiveness for each offense against the other team's defense; line yards.
9. **Turnovers, havoc, sacks, scoring chances:** each with ranks, and what the matchup means.
10. **What it all means:** 4-6 bullets. What the market expects and why, the case for each side, what's already priced in, what to watch at the lock recheck, and which PrizePicks hook would matter.

Writing rules:
- Plain English. Every number gets context, like "11.2% (#4 of 138)" or "vs the 6.4% FBS average".
- Times in ET. Label sources and dates.
- No snippets as data. Keep each game self-contained.
- No `[FILL]` markers left in the finished file. If something truly couldn't be found, say so plainly ("report pending", "cause not confirmed").
- End with **"Not covered yet"**: reports still to come, unconfirmed QB decisions and line-move causes, missing beat-writer context, and PrizePicks numbers not yet known.

## Step 6. Deliver and keep the folder current
1. Send the rundown with SendUserFile (display: render), plus the four slate chart PNGs, so they show on the user's phone too. In chat, give a short summary: the biggest line moves, QB and injury news, weather flags, luck flags, and the most valuable hooks.
2. Update `00_PROJECT_CONTEXT.md` ("Where things stand") with one short block: the file, the key changes, and API use.
3. Report usage: CFBD calls (new and cached; 1,000/month shared), Action Network, ESPN, NWS and Open-Meteo calls, and OddsPapi (0 unless used on purpose, and the count from `python _tools\oddspapi.py count`).
4. Offer the next step: grading legs with the `cfb-parlay-model` skill once the user sends the PrizePicks board.
