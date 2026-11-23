---
name: weekly-rundown
description: Full game-by-game NFL rundown for the current (or a named) week, in bullet points, with every stat ranked and explained. Use whenever the user asks for "this week's rundown", "give me the rundown", "rundown for week N", "run the rundown", "all the games this week with all the stats", or anything similar. Info only, no grades. Typed as /weekly-rundown (optionally with a week number).
---

# Weekly rundown (method v0.16)

the user wants one command that produces the full Week-N rundown without having to spell it out. The model output is `04_Research/Week11/04_Full_Rundown_Nov21.md`: match its structure, depth and tone exactly. Every game gets tons of bullets, every number gets context (rank out of 32, league average, what it means), and nothing gets left out.

This is **information, not picks**. Don't set probability ranges or grades here. If the user then asks to grade something, switch to the `nfl-parlay-model` skill (the v0.16 method) and log any leg that gets a range.

## Step 0. Context (read, don't skip)
1. `00_PROJECT_CONTEXT.md` ("Where things stand") and the latest `08_Weekly_Reviews/Week*_Review.md`, especially the next-week watchlist (section 8). Every watchlist item must show up in the rundown.
2. Any files already in `04_Research/Week<N>/` (earlier scans, single-game write-ups). Reuse facts that are still current, and say what changed.

## Step 1. Pull the data (one script, about 1-2 minutes)
From the project folder:
```
.venv\Scripts\python.exe -I -X utf8 02_Tools\weekly_rundown\build_rundown.py
```
- No `--week` = auto: the earliest week with 3+ games still to play. If the user names a week, pass `--week N`.
- If a lines file from today already exists for that week and nothing has moved, use `--skip-odds` to save PropLine calls (it reuses today's file).
- PropLine budget: the script uses 1 + (number of games) calls. Stay under 100 a day.

It writes:
- `04_Research/Data/week<N>_propline_lines_<mondd>.csv`: every book, main and alternate lines.
- `04_Research/Data/week<N>_team_stats_<mondd>.csv`: records, Pythagorean, last 4, ATS, overs, EPA, success, pace, explosive rate, sacks, turnovers, red zone, with a `_rk` rank column for each.
- `04_Research/Week<N>/rundown_facts_<mondd>.json`: everything per game. Market (core-three vig-free prices, lines by book, moneylines, the PrizePicks number each side needs for 55.2%), the previous pull for movement, weather (NWS hourly plus daily wording; Open-Meteo abroad), kickoff (ET), venue, roof, surface, divisional, rest, both teams' stats, and league averages.

Read the facts JSON with Python, not by eye. Notes on the fields:
- `spread_home` is the home team's line (negative = home favored).
- `needs.home` is in the home team's view, `needs.away` in the away team's view.
- `luck` = win % minus Pythagorean; ±0.15 or more is a flag.
- Ranks: 1 = best. For points allowed, sacks taken, turnovers given and seconds per play, 1 is the lowest.

## Step 2. Injuries (EndzoneAPI MCP)
- `get_injuries` for the season and week, all teams. It costs 2 credits; the output is large, so parse the saved file with Python.
- List Out / Doubtful / Questionable players with injury and practice status. Flag starters, QBs and kickers.
- Say which report it is (Wed / Thu / Fri / Sat) and when the next one posts.
- Report credits used. Budget: about 100 a week, stop at 50 left in the month.
- If a QB or key player's status is unclear, `get_depth_chart` (2 credits) for that team only.

## Step 3. QBs and the news that matters (opened pages only)
- Confirm both starting QBs for every game. A QB who isn't on the report and started last week counts as confirmed. Anything else (QB questionable, a QB change, a rookie start) needs an opened team or beat page. Use the `web-fetch` agent or WebFetch, never a search snippet.
- Explain any line move of 1.5+ points since the last pull, or any move across 3 or 7. If the cause can't be found on an opened page, write "cause not confirmed".
- Team context from beat writers where time allows. Note which teams have none.

## Step 4. Write the rundown
Save as `04_Research/Week<N>/NN_Full_Rundown_<Mon><DD>.md`, where NN is the next number in that folder. Title: `# Week N full rundown, every game — <Day Mon DD, YYYY, time ET>`.

Top of the file:
- **How to read the numbers:** ranks out of 32, the league averages from the JSON, EPA scale, Pythagorean, vig-free, "PrizePicks needs", sources, and "This is information, not picks."
- Results of any games already played this week (from nflverse), and a rest note: byes last week, short or long rest.

Then **one section per game in kickoff order**: `## N. Away Team (W-L) @ Home Team (W-L)`, then a bold line with kickoff ET, venue and city, roof and surface, divisional Y/N (plus neutral site, flexed, international). Under it, these bold sub-headers, each with several bullets:
1. **The betting market:** spread by book and the vig-free cover %; total and over %; favorite's moneyline %; movement since the last pull (and why, or "not confirmed"); the PrizePicks numbers each side and each total side needs.
2. **Quarterbacks:** both starters, how they were confirmed, backups, recent QB history and notable numbers.
3. **Injuries that matter:** out, doubtful and questionable for both teams, and why each one matters.
4. **Weather:** temperature, rain %, wind and gusts, the NWS wording, whether the 15+ mph wind or 50%+ rain rule applies, and whether it changed since the line was set. Domes: one line.
5. **Records and form:** overall, home and away splits, last 4 with point differential, last game's result, ATS, overs, Pythagorean vs actual with REGRESSION UP or DOWN flags.
6. **Scoring:** points for and against per game, with ranks.
7. **Efficiency:** EPA per play and success rate, offense and defense, with ranks.
8. **Pace and explosive plays:** plays per game and neutral seconds per play with ranks; explosive rate for each offense against the other team's defense.
9. **Turnovers, sacks, red zone:** each with ranks and what the matchup means.
10. **What it all means:** 4-6 bullets. What the market expects and why, the case for each side, what's already priced in, what to watch at the lock recheck, and which PrizePicks hook would matter.

Writing rules:
- Plain English. Every number gets context, like "11.2% (4th)" or "vs the 9.3% league average".
- Times in ET. Label sources and dates.
- No snippets as data. Keep each game self-contained.
- End with **"Not covered yet"**: missing beat-writer context, unconfirmed causes, reports still to come, and PrizePicks numbers not yet known.

## Step 5. Deliver and keep the folder current
1. Send the file with SendUserFile (display: render). In chat, give a short summary: the biggest line moves, QB and injury news, weather flags, luck flags, and the most valuable hooks.
2. Add the new data files to `04_Research/Data/README_data.md` if their layout is new. Normally it isn't, so add one line per file.
3. Update `00_PROJECT_CONTEXT.md` ("Where things stand") with one short block: the file, the key changes, and API use.
4. Report usage: PropLine calls (the script prints the daily counter) and EndzoneAPI credits.
5. Offer the next step: grading the PrizePicks board once the user sends screenshots.
