"""Record v1.6 adoption (Week 12 audit edits 1-2, approved by the user Nov 24 2026). Run from 01_Master_Prompt/."""
import os


def edit(p, pairs, append=None):
    raw = open(p, encoding='utf-8', newline='').read(); crlf = '\r\n' in raw; s = raw.replace('\r\n', '\n')
    for a, b in pairs:
        assert a in s, (p, a[:60]); s = s.replace(a, b, 1)
    if append: s = s.rstrip('\n') + '\n' + append
    if crlf: s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)


row = ("| v1.6 | Nov 24 2026 | Claude, from the Week 12 audit (approved by the user) | 1) Section 7: a Pythagorean flag alone is context, not a named reason; it can't move a probability, cut a grade or drop a leg "
       "unless the CFBD garbage-time-filtered EPA margin agrees (otherwise print it and lower confidence one step). Evidence: Pythag flags 2-5 ATS in Week 12, 5-7 over Weeks 11-12. "
       "2) Section 10: CONDITIONAL KEEP must name its condition and settling report; unresolved at the ticket's lock = Drop. Evidence: Indiana ML (starter never named, QB rotation, lost). |\n")
p = 'Master_Prompt_History.md'
s = open(p, encoding='utf-8').read()
i = s.index('| v1.5 |'); j = s.index('\n', i) + 1
s = s[:j] + row + s[j:]
a = 'Files (current): `Master_Prompt_v1.5_SKILL.md` and `Master_Prompt_v1.5_for_Gemini.txt` (built by `build_v15.py`). Earlier: `Master_Prompt_v1.4_SKILL.md`'
assert a in s
s = s.replace(a, 'Files (current): `Master_Prompt_v1.6_SKILL.md` and `Master_Prompt_v1.6_for_Gemini.txt` (built by `build_v16.py`). Earlier: `Master_Prompt_v1.5_SKILL.md`, `Master_Prompt_v1.4_SKILL.md`')
open(p, 'w', encoding='utf-8').write(s)

edit(os.path.join('..', 'CLAUDE.md'), [('master prompt v1.5', 'master prompt v1.6'),
                                       ('`01_Master_Prompt/Master_Prompt_v1.5_SKILL.md`', '`01_Master_Prompt/Master_Prompt_v1.6_SKILL.md`'),
                                       ('## Non-negotiable rules (v1.5)', '## Non-negotiable rules (v1.6)')],
     append=None)
edit(os.path.join('..', '00_PROJECT_CONTEXT.md'),
     [('- The method is **master prompt v1.5**', '- The method is **master prompt v1.6**'),
      ("adopted Nov 18 2026 at the user's request. See `01_Master_Prompt/Master_Prompt_History.md`.",
       "adopted Nov 18 2026 at the user's request. v1.6 (Week 12 audit: Pythag flag = context unless filtered EPA agrees; conditional Keep -> Drop if unresolved at lock) adopted Nov 24 2026. See `01_Master_Prompt/Master_Prompt_History.md`."),
      ('  1. Paste `01_Master_Prompt/Master_Prompt_v1.5_for_Gemini.txt` into the Gemini chat so Gemini runs v1.5 too.',
       '  1. Paste `01_Master_Prompt/Master_Prompt_v1.6_for_Gemini.txt` into the Gemini chat so Gemini runs v1.6 too.'),
      ("**Awaiting the user's Approve/Reject/Modify; READY FOR WEEK 13 SLATE after that.**",
       "**Both APPROVED by the user Nov 24 2026: live as master prompt v1.6 (both skill copies identical; Gemini copy saved). READY FOR WEEK 13 SLATE.**")])
edit(os.path.join('..', '01_Master_Prompt', 'Proposed', 'v1.6_proposed_from_Week12_audit.md'),
     [('Status: AWAITING THE USER (Approve / Reject / Modify each edit).', 'Status: APPROVED by the user Nov 24 2026 (edits 1-2). Live in v1.6. Watch items stay watch items.')])
edit(os.path.join('..', '08_Weekly_Reviews', 'Week12_Audit.md'),
     [('## 5. PROPOSED EDITS (awaiting the user: Approve / Reject / Modify)', '## 5. PROPOSED EDITS (edits 1-2 APPROVED Nov 24 2026, live in v1.6)'),
      ('Week 12 is audited. Two proposed edits are waiting for the user\'s review. **READY FOR WEEK 13 SLATE once edits 1-2 are approved, rejected or modified.**',
       'Week 12 is audited and edits 1-2 are approved (v1.6). **READY FOR WEEK 13 SLATE.**')])
open(os.path.join('..', '06_Chat_Archive', 'Session5_Week12_Audit.md'), 'a', encoding='utf-8').write(
    '- the user approved both edits (Nov 24). Master prompt v1.6 built by `01_Master_Prompt/build_v16.py`; both skill copies updated and identical; Gemini copy `Master_Prompt_v1.6_for_Gemini.txt` saved; logged by `log_v16.py`. READY FOR WEEK 13 SLATE.\n')
print('ok')
