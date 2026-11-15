# CFB Master Prompt history

| Version | Date | Where | What changed |
|---|---|---|---|
| v1.0 | before Nov 6 2026 | Gemini | CFB version of the NFL model (v0.x): checklist, market-first probabilities, CFB key-number table (3, 7, 14, 10, 17/21), coin-flip cap, ~16-17 pt margin SD (2.5 prob pts per point), weather, pace, availability (SEC/Big Ten official reports; beat writers elsewhere), brutality filter, correlation, board entry. Setup turns were not reachable when copied. |
| v1.1 | Nov 9 2026 | Gemini | Added Section 0 MONDAY AUDIT MODE and Section 13 Monday Post-Mortem & Self-Improvement Audit (every P4 game, autopsies, cause tags, proposed edits, gatekeeper). |
| v1.2 | Nov 10 2026 | Gemini, from Week 10 audit | 1) HARD VERIFICATION GATE (no grades without live odds + QBs). 2) ANEMIC-OFFENSE ANCHOR CAP in 10A (bottom-35 offense can't grade above B- as a heavy fav). 3) FORMAT & ALT-SPREAD ISOLATION in Sections 5 and 11 (confirm flat vs dynamic payout; no ML-to-spread swaps without their own brutality filter). 4) 4th-down conversion tracking and REGRESSION UP flag in Sections 7 and 13D. |

| v1.3 | Nov 10 2026 | Claude, from verified Week 10 audit (approved by the user) | 1) Section 13D: a REGRESSION UP/DOWN tag needs EPA/play or Deserved Win % to agree with the yardage gap. 2) Section 8: WEEKLY PATTERN COUNTS, print the full count with its denominator. 3) Section 13B: closing lines cite 2 named sources per game; Gemini audit tables are UNVERIFIED until re-opened. |

Files (current): `Master_Prompt_v1.3_SKILL.md` and `Master_Prompt_v1.3_for_Gemini.txt`. Earlier: `Master_Prompt_v1.2_SKILL.md` (Claude skill copy, same text as `.claude/skills/cfb-parlay-model/SKILL.md`) and `Master_Prompt_v1.2_for_Gemini.txt` (exactly as Gemini printed it).

## Ideas from the NFL model not yet in the CFB model (proposals only; the user approves)
- MPP: start from the market price at the PrizePicks number, not the book's own number.
- Snippet rule: injury/QB news seen only in a search snippet or relayed report gets zero probability credit.
- `PP line ASSUMED` tag when the app number isn't captured; keep those legs out of CLV.
- Log every graded leg (Played? = N) and capture closing lines for CLV.
