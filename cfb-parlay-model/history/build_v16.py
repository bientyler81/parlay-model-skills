"""Build master prompt v1.6 from v1.5 (Week 12 audit edits 1-2, approved by the user Nov 24 2026).
Edit 1: Section 7 Pythagorean flag is context unless filtered EPA agrees. Edit 2: Section 10 conditional Keep -> Drop if unresolved at lock.
Run from 01_Master_Prompt/. Writes v1.6 SKILL + Gemini copies and installs the SKILL in both skill folders."""
import os, shutil

PY_OLD = "If actual win % deviates by $\\ge 0.18$, flag REGRESSION DOWN or REGRESSION UP."
PY_NEW = PY_OLD + (" A Pythagorean flag by itself is **context, not a named reason** (Section 5): it cannot move a probability, lower a grade, "
                   "or drop a leg unless the team's garbage-time-filtered EPA margin (CFBD) also says its record is ahead of (DOWN) or behind (UP) its play. "
                   "Without that agreement, print the flag and lower data confidence one step only.")
KEEP_OLD = "- Keep, Replace, or Drop (provide up to 2 cross-game replacements for any Drop)."
KEEP_NEW = KEEP_OLD + ("\n- CONDITIONAL KEEP: a conditional Keep (\"Keep only after X\") must name its condition and the report that settles it. "
                       "If X is not confirmed on an opened page before the ticket's lock, the leg is **Drop** for that ticket. Expected or likely is not confirmed.")


def apply(s):
    for a, b in ((PY_OLD, PY_NEW), (KEEP_OLD, KEEP_NEW)):
        assert s.count(a) == 1, a[:50]
        s = s.replace(a, b)
    return s


sk = open('Master_Prompt_v1.5_SKILL.md', encoding='utf-8', newline='').read().replace('\r\n', '\n')
sk = apply(sk).replace('Master Prompt — v1.5', 'Master Prompt — v1.6', 1)
old_hdr = "v1.5 adopted Nov 18 2026 at the user's request (new Section 3B DATA TOOLS AND QUOTAS, plus a pointer in Section 3). Sections 0-13 are Gemini's v1.2 text plus the v1.3, v1.4 and v1.5 additions;"
assert old_hdr in sk, 'header anchor'
sk = sk.replace(old_hdr, "v1.5 adopted Nov 18 2026 at the user's request (new Section 3B DATA TOOLS AND QUOTAS, plus a pointer in Section 3); "
                "v1.6 adopted Nov 24 2026 from the Week 12 audit (edits 1-2: Sections 7, 10). Sections 0-13 are Gemini's v1.2 text plus the v1.3, v1.4, v1.5 and v1.6 additions;")
open('Master_Prompt_v1.6_SKILL.md', 'w', encoding='utf-8', newline='').write(sk)

g = open('Master_Prompt_v1.5_for_Gemini.txt', encoding='utf-8', newline='').read().replace('\r\n', '\n')
g = apply(g).replace('MASTER PROMPT — v1.5', 'MASTER PROMPT — v1.6', 1)
open('Master_Prompt_v1.6_for_Gemini.txt', 'w', encoding='utf-8', newline='').write(g)

for dst in [os.path.join('..', '.claude', 'skills', 'cfb-parlay-model', 'SKILL.md'),
            os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'cfb-parlay-model', 'SKILL.md')]:
    shutil.copyfile('Master_Prompt_v1.6_SKILL.md', dst)
print('ok')
