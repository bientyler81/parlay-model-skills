"""Build master prompt v1.5 from v1.4 (the user asked Nov 18 2026 to add the new data tools to the method).
Adds Section 3B DATA TOOLS AND QUOTAS and one pointer line in Section 3. Run from 01_Master_Prompt/."""
import os, shutil

S3B = """## 3B. DATA TOOLS AND QUOTAS (installed Nov 18 2026; Claude runs these, Gemini cannot)
A tool result is a source like an opened page: name the tool, the book or provider, and the pull time (ET). Never fill a gap from memory when a tool can answer it. Prefer cached files (`_data/`, the week's `_scripts/data_<day>/` snapshots) before spending quota.

| Tool | How to run | Free limit | What it is for |
|---|---|---|---|
| Action Network odds API | `04_Research/Week<N>/_scripts/an_odds.py` | No key; no stated limit | **Primary market line (Section 4 item 6):** spread, total and ML from 7 named books (DraftKings, FanDuel, BetRivers, BetMGM, bet365, Caesars, Fanatics) plus the opening line. Vig-free ML = median of the 7 books. |
| OddsPapi | `python _tools/oddspapi.py fixtures / odds / compare / count` | **250 requests/month**; the script logs every call and stops at 240 | One `odds` call returns ~240 books for one game, including **Pinnacle, Circa, SBOBet** and **PrizePicks player-prop lines**. Use it for: (a) the PrizePicks number on any prop leg; (b) the market price at that PrizePicks number (FanDuel vig-free over/under via `compare`; DraftKings college props are over-only ladders, so they give no vig-free price); (c) a sharp-book (Pinnacle) check on coin flips. It does **not** carry PrizePicks Team Picks / game-winner multipliers: those still come from the app. Spend it on shortlisted games and props the user is considering, never the whole slate. Fixture dates are UTC. |
| CollegeFootballData (CFBD) | Weekly `cfbd.py` (2 calls per run); `cfbd` Python client; `cfbd` MCP tools in Claude Code (get-games, get-drives, get-plays, get-advanced-box-score, get-pregame-win-probability, etc.) | **1,000 calls/month, shared by all three** | Season advanced stats with garbage time removed (Section 7), plus targeted game, drive and play pulls. One MCP tool call = one CFBD call: no loops over the slate. |
| cfbfastR play-by-play | `"C:\\Program Files\\R\\R-4.6.2\\bin\\Rscript.exe" _tools\\export_cfb_pbp.R <season>` -> `_data/cfb_pbp_<season>.parquet` | No key, no quota | Every play with EPA and win probability, for custom splits (red zone, 4th down, by quarter, QB-specific EPA after a starter change) and for the Monday audit. **Not garbage-time filtered and includes FCS games:** filter before citing and say so (Section 3). Re-export each Monday to add the latest week. |
| EndzoneAPI | `endzoneapi-ncaaf` MCP server | **500 credits/month** (each response shows `_creditsMeta`; odds 10, line movement 25) | **Archive only for college lines:** closing lines 2012 on, pre-kickoff snapshots from 6-8 books for 2020-2025, player props and alt lines 2023-2025. Use it for backtests (key-number frequencies, how past lines moved, past prop lines). **Never cite it as a current line**: it had no 2026 lines when tested. |
| Open-Meteo | Plain URL, no key (`previous-runs-api.open-meteo.com/v1/forecast`, `wind_speed_unit=mph`, `timezone=America/New_York`) | 10,000 calls/day, non-commercial, CC BY 4.0 | Second weather source next to NWS for Section 6. The `_previous_day1/2` fields show how the forecast has moved. If NWS and Open-Meteo disagree across the 15 mph wind line, report both and treat the wind flag as unconfirmed. |
| VSiN betting splits, BCF Toys | Browser only (VSiN blocks automated reads) | n/a | Tier 3 context. Bet/handle splits are never a named reason to adjust a probability (Section 5). FEI is Tier 3 like SP+. |

QUOTA DISCIPLINE: run `python _tools/oddspapi.py count` before any OddsPapi pull and report the count when spending more than 5 requests. If a quota is near its limit, say so and fall back to the free sources instead of failing silently.
PROP LEGS: a PrizePicks prop leg's market start (Section 5) is the vig-free book price at the PrizePicks number when a book offers that exact line. When no book has the same number, start from the nearest main line, adjust with the key-number logic, and label the start `PP LINE ≠ BOOK LINE`. If the PrizePicks number was not captured from OddsPapi or the user's app, label it `PP line ASSUMED` and keep the leg Low confidence.

"""

POINTER_OLD = "- Lines and movement: VegasInsider CFB odds page, cross-checked against at least 2 other books (DraftKings, FanDuel, BetMGM, Action Network, Circa)."
POINTER_NEW = POINTER_OLD + "\n- Claude's odds, prop, play-by-play and weather tools, with their free limits, are listed in Section 3B."


def apply(s, gemini=False):
    assert s.count(POINTER_OLD) == 1, 'pointer anchor'
    s = s.replace(POINTER_OLD, POINTER_NEW)
    a = '## 4. PRE-ANALYSIS CHECKLIST'
    assert s.count(a) == 1, 'section 4 anchor'
    block = S3B
    if gemini:
        block = block.replace('(installed Nov 18 2026; Claude runs these, Gemini cannot)',
                              '(installed Nov 18 2026; CLAUDE ONLY)') + (
            "GEMINI NOTE: You cannot run these tools. When Claude's output cites one of them, treat the number as sourced but still re-checkable. "
            "Never claim to have pulled OddsPapi, CFBD, cfbfastR, EndzoneAPI or Open-Meteo data yourself.\n\n")
    return s.replace(a, block + a)


sk = open('Master_Prompt_v1.4_SKILL.md', encoding='utf-8', newline='').read().replace('\r\n', '\n')
sk = apply(sk)
sk = sk.replace('Master Prompt — v1.4', 'Master Prompt — v1.5', 1)
old_hdr = "v1.4 adopted Nov 17 2026 from the Week 11 audit (edits 1-4: Sections 5, 7, 9, 11). Sections 0-13 are Gemini's v1.2 text plus the v1.3 and v1.4 additions;"
assert old_hdr in sk, 'header anchor'
sk = sk.replace(old_hdr, "v1.4 adopted Nov 17 2026 from the Week 11 audit (edits 1-4: Sections 5, 7, 9, 11); v1.5 adopted Nov 18 2026 at the user's request (new Section 3B DATA TOOLS AND QUOTAS, plus a pointer in Section 3). Sections 0-13 are Gemini's v1.2 text plus the v1.3, v1.4 and v1.5 additions;")
open('Master_Prompt_v1.5_SKILL.md', 'w', encoding='utf-8', newline='').write(sk)

g = open('Master_Prompt_v1.4_for_Gemini.txt', encoding='utf-8', newline='').read().replace('\r\n', '\n')
g = apply(g, gemini=True).replace('MASTER PROMPT — v1.4', 'MASTER PROMPT — v1.5', 1)
open('Master_Prompt_v1.5_for_Gemini.txt', 'w', encoding='utf-8', newline='').write(g)

for dst in [os.path.join('..', '.claude', 'skills', 'cfb-parlay-model', 'SKILL.md'),
            os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'cfb-parlay-model', 'SKILL.md')]:
    shutil.copyfile('Master_Prompt_v1.5_SKILL.md', dst)
print('ok')
