"""Record v1.5 adoption in history, CLAUDE.md, project context and the session archive. Run from 01_Master_Prompt/."""
import os


def edit(p, pairs, append=None):
    raw = open(p, encoding='utf-8', newline='').read(); crlf = '\r\n' in raw; s = raw.replace('\r\n', '\n')
    for a, b in pairs:
        assert a in s, (p, a[:60]); s = s.replace(a, b, 1)
    if append: s = s.rstrip('\n') + '\n' + append
    if crlf: s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)


row = ("| v1.5 | Nov 18 2026 | Claude, at the user's request | New Section 3B DATA TOOLS AND QUOTAS: Action Network odds API (primary 7-book line), OddsPapi (250/month; PrizePicks prop lines, Pinnacle/Circa/SBOBet, FanDuel price at the PP number), "
       "CFBD (1,000/month shared by the pipeline, Python client and MCP server), cfbfastR play-by-play (no quota; filter garbage time), EndzoneAPI (archive only for college lines; never a current line), Open-Meteo (second weather source), VSiN/BCF Toys (Tier 3). "
       "Adds quota discipline and a PROP LEGS rule (market start = book price at the PrizePicks number; `PP LINE ≠ BOOK LINE` and `PP line ASSUMED` labels, partly porting the NFL MPP / PP-ASSUMED ideas). Pointer line added in Section 3. |\n")
p = 'Master_Prompt_History.md'
s = open(p, encoding='utf-8').read()
i = s.index('| v1.4 |'); j = s.index('\n', i) + 1
s = s[:j] + row + s[j:]
s = s.replace('Files (current): `Master_Prompt_v1.4_SKILL.md` and `Master_Prompt_v1.4_for_Gemini.txt` (built by `build_v14.py`). Earlier: `Master_Prompt_v1.3_SKILL.md`',
              'Files (current): `Master_Prompt_v1.5_SKILL.md` and `Master_Prompt_v1.5_for_Gemini.txt` (built by `build_v15.py`). Earlier: `Master_Prompt_v1.4_SKILL.md`, `Master_Prompt_v1.3_SKILL.md`')
open(p, 'w', encoding='utf-8').write(s)

edit(os.path.join('..', 'CLAUDE.md'), [('master prompt v1.4', 'master prompt v1.5'),
                                       ('`01_Master_Prompt/Master_Prompt_v1.4_SKILL.md`', '`01_Master_Prompt/Master_Prompt_v1.5_SKILL.md`'),
                                       ('## Non-negotiable rules (v1.4)', '## Non-negotiable rules (v1.5)')])
edit(os.path.join('..', '00_PROJECT_CONTEXT.md'),
     [('- The method is **master prompt v1.4**', '- The method is **master prompt v1.5**'),
      ('adopted Nov 17 2026. See `01_Master_Prompt/Master_Prompt_History.md`.',
       'adopted Nov 17 2026. v1.5 (Section 3B DATA TOOLS AND QUOTAS: the new odds, prop, play-by-play and weather tools with their free limits) adopted Nov 18 2026 at the user\'s request. See `01_Master_Prompt/Master_Prompt_History.md`.'),
      ('  1. Paste `01_Master_Prompt/Master_Prompt_v1.4_for_Gemini.txt` into the Gemini chat so Gemini runs v1.4 too.',
       '  1. Paste `01_Master_Prompt/Master_Prompt_v1.5_for_Gemini.txt` into the Gemini chat so Gemini runs v1.5 too.')])
open(os.path.join('..', '06_Chat_Archive', 'Session4_Week12_Shortlist.md'), 'a', encoding='utf-8').write(
    '- Wed Nov 18: installed and tested data tools (`_tools/README.md`): cfbd client, CFBD MCP server, uv, R + cfbfastR (2026 play-by-play exported), OddsPapi (works; PrizePicks prop lines; 4/250 used), '
    'EndzoneAPI (key works after re-save; NCAAF MCP only; no current college lines, archive only; 494/500 credits), Open-Meteo (no key). '
    'the user asked to put them in the method: master prompt v1.5 adds Section 3B DATA TOOLS AND QUOTAS; both skill copies updated and identical; Gemini copy saved.\n')
print('ok')
