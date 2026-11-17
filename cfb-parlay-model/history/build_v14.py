"""Build master prompt v1.4 from v1.3 (edits approved by the user Nov 17 2026). Run from 01_Master_Prompt/."""
import shutil, os

E = [
 # Edit 2: Section 5 travel
 ("significant motivation/rest asymmetry.\n",
  "significant motivation/rest asymmetry.\n"
  "- TRAVEL IS NOT A NAMED REASON: Travel disruption by itself (late arrival, same-day flight, bus trip, changed kickoff) is not a reason to move probabilities off the market; the market prices it within hours. Adjust only for confirmed consequences (e.g., a player ruled out).\n"),
 # Edit 4: Section 7 4th-down flag
 ("as a prime `REGRESSION UP` candidate for the following week.",
  "as a prime `REGRESSION UP` candidate for the following week, but only if EPA/play or post-game win expectancy (Deserved Win %) also favors that team (Section 13D). Yardage alone never earns the tag."),
 # Edit 1: Section 9 QB status
 ("- For SEC & Big Ten games: State exact status from the official conference availability report (Out, Doubtful, Questionable, Game-Time Decision).",
  "- For SEC & Big Ten games: State exact status from the official conference availability report (Out, Doubtful, Questionable, Game-Time Decision).\n"
  "- QB STATUS IS UNCERTAIN UNTIL KICKOFF: A starting QB listed Probable, Questionable or Game-Time Decision, or a QB whose coach has not named a starter, is UNCERTAIN until confirmed by the game-day report or warmups. Any leg that depends on that QB carries Low confidence and must be re-checked at the final report; if the ticket locks before then, say so in the lock-timing item."),
 # Edit 3: Section 11 PrizePicks
 ("- Format alignment: Confirm payout structure (flat DFS pick'em vs. dynamic pick'em vs. open sportsbook odds) per Section 5's FORMAT & ALT-SPREAD ISOLATION rule before proposing leg swaps to hit a target multiplier.",
  "- Format alignment: Confirm payout structure (flat DFS pick'em vs. dynamic pick'em vs. open sportsbook odds) per Section 5's FORMAT & ALT-SPREAD ISOLATION rule before proposing leg swaps to hit a target multiplier.\n"
  "- PRIZEPICKS TEAM PICKS PRICING CHECK: Before the parlay verdict, record the app's multiplier for each pick and the ticket total (user's report or screenshot). Compute each pick's app / fair (fair = 1 / vig-free market probability) and the ticket's app / fair. Because the margin applies per pick, prefer 2-3 picks. A ticket paying under 90% of fair is a PASS unless the model's combined edge (product of model p / product of market p) is at least fair / app. Flag any single pick paying 100%+ of fair as a value pick."),
]

def apply(s):
    for a, b in E:
        assert s.count(a) == 1, ('anchor not unique/found', a[:70], s.count(a))
        s = s.replace(a, b)
    return s

sk = open('Master_Prompt_v1.3_SKILL.md', encoding='utf-8', newline='').read()
sk = sk.replace('\r\n', '\n')
sk = apply(sk)
sk = sk.replace('Master Prompt — v1.3', 'Master Prompt — v1.4', 1)
old_hdr = "v1.3 adopted Nov 10 2026 from Claude's verified Week 10 audit (edits 1-3: Sections 8, 13B, 13D). Sections 0-13 are Gemini's v1.2 text plus those three v1.3 additions;"
assert old_hdr in sk, 'header anchor'
sk = sk.replace(old_hdr, "v1.3 adopted Nov 10 2026 from Claude's verified Week 10 audit (edits 1-3: Sections 8, 13B, 13D); v1.4 adopted Nov 17 2026 from the Week 11 audit (edits 1-4: Sections 5, 7, 9, 11). Sections 0-13 are Gemini's v1.2 text plus the v1.3 and v1.4 additions;")
assert 'v1.4' in sk.split('\n')[5]
open('Master_Prompt_v1.4_SKILL.md', 'w', encoding='utf-8', newline='').write(sk)

g = open('Master_Prompt_v1.3_for_Gemini.txt', encoding='utf-8', newline='').read().replace('\r\n', '\n')
g = apply(g).replace('MASTER PROMPT — v1.3', 'MASTER PROMPT — v1.4', 1)
open('Master_Prompt_v1.4_for_Gemini.txt', 'w', encoding='utf-8', newline='').write(g)

for dst in [os.path.join('..', '.claude', 'skills', 'cfb-parlay-model', 'SKILL.md'),
            os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'cfb-parlay-model', 'SKILL.md')]:
    shutil.copyfile('Master_Prompt_v1.4_SKILL.md', dst)
print('ok')
