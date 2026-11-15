# Parlay Model Skills

Claude Code skills for two sports-betting evaluation models, plus every past version of their master prompts.

| Skill | Sport | Current version | Folder |
|---|---|---|---|
| `cfb-parlay-model` | College football (NCAA) | v1.3 | [`cfb-parlay-model/`](cfb-parlay-model/) |
| `nfl-parlay-model` | NFL | v0.13 | [`nfl-parlay-model/`](nfl-parlay-model/) |

Each skill folder holds:

- `SKILL.md`: the current skill, the file Claude loads.
- `history/`: every `Master_Prompt_v*_SKILL.md` version, the model-neutral `_for_Gemini.txt` copies, `Master_Prompt_History.md` (changelog), templates, and `Proposed/` drafts that have not been adopted yet.

## Install a skill

Copy a skill folder's `SKILL.md` into `~/.claude/skills/<skill-name>/SKILL.md` (all projects) or `<project>/.claude/skills/<skill-name>/SKILL.md` (one project).

## How this repo stays current

`tools/sync_skills.py` runs from Claude Code hooks. Whenever a skill file or a `01_Master_Prompt/` file is written or edited, and at the end of each Claude turn, it:

1. Finds every skill in `~/.claude/skills/` and in each project's `.claude/skills/`, plus each project's `01_Master_Prompt/` history. New skills are picked up automatically.
2. Mirrors them into this repo (added, updated and removed files). Personal details are replaced with placeholders such as `the user` and `<private claude.ai artifact link>`, and chat transcripts are left out.
3. Checks the repo for any personal details that slipped through and blocks the push if it finds one.
4. Commits and pushes, then prints a report listing each changed file, the commit, and the SHA-256 of each current `SKILL.md`.

Run it by hand any time:

```bash
python tools/sync_skills.py --dry-run
python tools/sync_skills.py
```

These skills are analysis frameworks, not betting advice. Nothing here promises a win.
