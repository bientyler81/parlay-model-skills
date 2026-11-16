---
name: ai-panel
description: "Use when the user wants a multi-model second opinion through OpenRouter on a college football (CFB) or NFL slate, ticket, parlay, or leg list — e.g. 'run it through the panel', 'ask five models', 'what do the other AIs think', 'OpenRouter', 'get a consensus'. Sends the sport's master prompt plus the ticket to several models in parallel and tallies their TAKE/PASS/FADE votes. Works alongside cfb-parlay-model and nfl-parlay-model; does not replace them."
---

# AI panel (OpenRouter)

Sends one question to several AI models at once through OpenRouter, with the sport's **master prompt** as
the shared system prompt (the newest `Master_Prompt_v*_for_Gemini.txt`, the same one Gemini gets), and
counts their votes. **You (Claude) stay the primary analyst and the judge.** The panel is a set of critics,
not a confirming vote.

## When to run it
- The user asks for the panel / OpenRouter / several models / a consensus on a ticket or slate.
- Do your own analysis with `cfb-parlay-model` or `nfl-parlay-model` FIRST, so the panel gets verified inputs
  and you have your own read to compare against.

## Steps

1. **Write the request to a temp file** (your scratchpad), containing only verified facts:
   - every leg labeled `L1`, `L2`, ... with the exact line and odds, and the source and time you verified them;
   - injuries / QB status / weather you verified, with sources;
   - what you want (grade the ticket, pick a side, find the weakest leg, etc.).
   The script appends a required `VOTES` footer, so models end with `L1 | TAKE/PASS/FADE | 57%` lines.

2. **Run the panel** (from the workspace; it finds the `CFB Model` / `NFL Model` folder on its own):
   ```bash
   python ~/.claude/skills/ai-panel/panel.py --sport nfl --prompt-file "<request file>"
   ```
   Options: `--models a,b,c` (OpenRouter IDs), `--online` (models may search the web; extra cost),
   `--master <file>`, `--project <folder>`, `--mock` (no key, no cost), `--list-models gemini` (browse IDs).
   Default panel: Gemini 4 Carbon, GPT-6.1 Sol, Grok 4.7, DeepSeek v4.1 Flash, Mistral Large 4 —
   five labs other than Anthropic, since Claude is already in the room. Runs in parallel; ~1–3 min.

3. **Read the full report** the script saves (`<SPORT> Model/04_Research/AI_Panel/<timestamp>_<sport>.md`),
   not just the tally. It has every model's full answer.

4. **Report back to the user:**
   - the vote table per leg (TAKE / PASS / FADE counts, average win probability), next to **your own call**;
   - where the panel split, and where the majority disagrees with you or with the master prompt's rules —
     with the dissenters' actual reasons;
   - any line, injury, or stat a panel model stated that was NOT in your request: mark it **UNVERIFIED**
     and check it on a live page before it influences anything (same rule as Gemini: past answers had
     hallucinated lines and stale QBs);
   - the run's cost (printed by the script).

## Rules
- **Agreement is not proof.** These models share training data and saw the same inputs. Never raise stakes,
  add legs, or upgrade a grade because many models agree. A split is useful information; unanimity is weak
  evidence.
- The master prompt's grading rules (break-even math, key numbers, correlation, availability checks) override
  any panel opinion.
- Don't run the panel for every message — it costs money each run. Use it when asked or for a final ticket check.

## Setup (first run)
If the script prints `no OpenRouter key`, tell the user to create a key at https://openrouter.ai/keys and save it
**themselves** in a file named `.openrouter.env` in their home folder, containing one line:
`OPENROUTER_API_KEY=sk-or-...` (or set the environment variable `OPENROUTER_API_KEY`).
Never ask the user to paste the key into the chat, and never write the key into this skill folder — this
folder is published to a public repo. `--mock` tests everything without a key.
