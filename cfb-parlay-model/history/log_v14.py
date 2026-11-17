"""Record v1.4 adoption in history, CLAUDE.md, project context, the proposal file and the Week 11 audit. Run from 01_Master_Prompt/."""
import os

def edit(p, pairs, append=None):
    raw = open(p, encoding='utf-8', newline='').read(); crlf = '\r\n' in raw; s = raw.replace('\r\n', '\n')
    for a, b in pairs:
        assert a in s, (p, a[:60]); s = s.replace(a, b, 1)
    if append: s = s.rstrip('\n') + '\n' + append
    if crlf: s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)

row = ("| v1.4 | Nov 17 2026 | Claude, from the Week 11 audit (approved by the user) | 1) Section 9: a QB listed Probable/Questionable/GTD or unnamed is UNCERTAIN until kickoff; dependent legs Low confidence, re-check at the final report. "
       "2) Section 5: travel disruption alone is not a named adjustment reason. 3) Section 11: PrizePicks Team Picks pricing check (app / fair per pick and ticket; under 90% of fair = PASS unless edge covers it; prefer 2-3 picks). "
       "4) Section 7: the 4th-down REGRESSION UP flag needs EPA or Deserved Win % to agree. |\n")
p = 'Master_Prompt_History.md'
s = open(p, encoding='utf-8').read()
i = s.index('| v1.3 |'); j = s.index('\n', i) + 1
s = s[:j] + row + s[j:]
s = s.replace('Files (current): `Master_Prompt_v1.3_SKILL.md` and `Master_Prompt_v1.3_for_Gemini.txt`. Earlier: `Master_Prompt_v1.2_SKILL.md`',
              'Files (current): `Master_Prompt_v1.4_SKILL.md` and `Master_Prompt_v1.4_for_Gemini.txt` (built by `build_v14.py`). Earlier: `Master_Prompt_v1.3_SKILL.md`, `Master_Prompt_v1.2_SKILL.md`')
open(p, 'w', encoding='utf-8').write(s)

edit(os.path.join('..', 'CLAUDE.md'), [('master prompt v1.3', 'master prompt v1.4'),
                                       ('`01_Master_Prompt/Master_Prompt_v1.3_SKILL.md`', '`01_Master_Prompt/Master_Prompt_v1.4_SKILL.md`'),
                                       ('## Non-negotiable rules (v1.3)', '## Non-negotiable rules (v1.4)')])
edit(os.path.join('Proposed', 'v1.4_proposed_from_Week11_audit.md'),
     [('Status: AWAITING THE USER (Approve / Reject / Modify).', 'Status: APPROVED by the user Nov 17 2026 (edits 1-4). Live in v1.4. The watch item stays a watch item.')])
edit(os.path.join('..', '08_Weekly_Reviews', 'Week11_Audit.md'),
     [('## 5. PROPOSED EDITS (await the user\'s Approve / Reject / Modify)', '## 5. PROPOSED EDITS (edits 1-4 APPROVED Nov 17 2026, live in v1.4; edit 5 stays a watch item)'),
      ('Week 11 is audited. **READY FOR WEEK 12 SLATE** once the user rules on edits 1-4 (edit 5 is a watch item, not a rule change).',
       'Week 11 is audited and edits 1-4 are approved (v1.4). **READY FOR WEEK 12 SLATE.**')])
edit(os.path.join('..', '00_PROJECT_CONTEXT.md'),
     [('The method is **master prompt v1.3**', 'The method is **master prompt v1.4**'),
      ('Awaiting the user. Then READY FOR WEEK 12.', 'APPROVED Nov 17 2026: live as master prompt v1.4. READY FOR WEEK 12 SLATE. Paste `01_Master_Prompt/Master_Prompt_v1.4_for_Gemini.txt` into the Gemini chat so Gemini runs v1.4 too.')])
open(os.path.join('..', '06_Chat_Archive', 'Session3_Week11_Audit.md'), 'a', encoding='utf-8').write(
    '- the user approved edits 1-4. Built master prompt v1.4 (`Master_Prompt_v1.4_SKILL.md` + Gemini copy); both skill copies updated and identical; history, CLAUDE.md, context and audit updated. READY FOR WEEK 12.\n')
print('ok')
