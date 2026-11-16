"""
AI panel: send one CFB/NFL question to several models through OpenRouter, in parallel,
with the sport's master prompt as the shared system prompt, then tally their votes.

Standard library only. Usage (run from anywhere):

  python panel.py --sport nfl --prompt-file ticket.md
  python panel.py --sport cfb --prompt "L1: Georgia -3.5 ..."      # or pipe the prompt on stdin
  python panel.py --sport nfl --prompt-file t.md --models google/gemini-4-carbon,openai/gpt-6.1-sol
  python panel.py --sport nfl --prompt-file t.md --online           # let models search the web (extra cost)
  python panel.py --sport nfl --prompt-file t.md --mock             # test without a key or spending money
  python panel.py --list-models gemini                              # browse OpenRouter model IDs

API key (never stored in this folder, which is published):
  1. environment variable OPENROUTER_API_KEY, or
  2. a file ~/.openrouter.env containing   OPENROUTER_API_KEY=sk-or-...

Master prompt: newest  "<SPORT> Model/01_Master_Prompt/Master_Prompt_v*_for_Gemini.txt"  found next to the
current folder (or pass --master <file>, or --project "<folder>").

Number the legs in your prompt L1, L2, ... and every model ends with a VOTES block the script can count.
"""
import argparse
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Claude is already the main analyst in Claude Code, so the default panel is five OTHER labs.
DEFAULT_MODELS = [
    "google/gemini-4-carbon",
    "openai/gpt-6.1-sol",
    "x-ai/grok-4.7",
    "deepseek/deepseek-v4.1-flash-1017",
    "mistralai/mistral-large-4-0",
]
API = "https://openrouter.ai/api/v1"

VOTES_FOOTER = """

--- PANEL FORMAT (required) ---
You are one of several independent AI models answering this. Answer fully using the framework above.
Do not invent lines, injuries or weather: if something isn't given here, mark it UNVERIFIED.
At the very end, add this block, one line per leg (use the leg labels L1, L2, ... from the request):

VOTES
L1 | TAKE or PASS or FADE | your win probability for the leg as written, e.g. 57%
"""

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- key + master prompt

def load_key():
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    f = Path.home() / ".openrouter.env"
    if f.is_file():
        lines = f.read_text(encoding="utf-8-sig").splitlines()  # -sig: Notepad/PowerShell may add a BOM
        for line in lines:
            k, _, v = line.partition("=")
            if k.strip() == "OPENROUTER_API_KEY" and v.strip():
                return v.strip().strip('"').strip("'")
        for line in lines:  # also accept the bare key on its own line
            if line.strip().strip('"').strip("'").startswith("sk-or-"):
                return line.strip().strip('"').strip("'")
    return ""


def _version(p):
    m = re.search(r"_v(\d+)\.(\d+)_for_Gemini\.txt$", p.name)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


def find_project(sport, start):
    want = f"{sport.upper()} Model"
    for base in [start, *start.parents][:4]:
        if base.name.lower() == want.lower() and (base / "01_Master_Prompt").is_dir():
            return base
        cand = base / want
        if (cand / "01_Master_Prompt").is_dir():
            return cand
    return None


def find_master(project):
    files = [p for p in (project / "01_Master_Prompt").glob("Master_Prompt_v*_for_Gemini.txt") if _version(p) >= (0, 0)]
    return max(files, key=_version) if files else None


# ---------------------------------------------------------------- OpenRouter

def call_model(model, system, prompt, key, max_tokens, timeout=240):
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "usage": {"include": True},
    }).encode("utf-8")
    req = urllib.request.Request(f"{API}/chat/completions", data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "X-Title": "AI Panel (Claude Code)",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"network error: {e.reason}") from None
    if data.get("error"):
        raise RuntimeError(str(data["error"].get("message", data["error"]))[:300])
    choice = (data.get("choices") or [{}])[0]
    text = (choice.get("message") or {}).get("content") or ""
    if isinstance(text, list):
        text = "".join(p.get("text", "") for p in text if isinstance(p, dict))
    if not text.strip():
        raise RuntimeError(f"empty reply (finish_reason={choice.get('finish_reason')})")
    usage = data.get("usage") or {}
    return text.strip(), usage.get("cost")


def mock_model(model, prompt):
    time.sleep(random.uniform(0.3, 1.2))
    legs = sorted(set(re.findall(r"\bL(\d+)\b", prompt)), key=int) or ["1"]
    rng = random.Random(model + prompt)
    lines = [f"(mock answer from {model}) Leg-by-leg read below."]
    lines += ["", "VOTES"]
    for n in legs:
        v = rng.choices(["TAKE", "PASS", "FADE"], [6, 2, 2])[0]
        lines.append(f"L{n} | {v} | {rng.randint(48, 66)}%")
    return "\n".join(lines), 0.0


# ---------------------------------------------------------------- votes

VOTE_RE = re.compile(r"^\W*L(\d+)\W*\|\s*\**\s*(TAKE|PASS|FADE)\b\**\s*(?:\|\s*~?(\d{1,3}(?:\.\d+)?)\s*%?)?", re.I | re.M)


def parse_votes(text):
    tail = text[text.upper().rfind("VOTES"):] if "VOTES" in text.upper() else text
    votes = {}
    for m in VOTE_RE.finditer(tail):
        prob = float(m.group(3)) if m.group(3) else None
        votes[f"L{m.group(1)}"] = (m.group(2).upper(), prob)
    return votes


def tally_table(results):
    ok = [r for r in results if r["ok"]]
    legs = sorted({leg for r in ok for leg in r["votes"]}, key=lambda s: int(s[1:]))
    if not legs:
        return "_No VOTES blocks found — read the answers directly._"
    short = [r["model"].split("/")[-1] for r in ok]
    head = "| Leg | TAKE | PASS | FADE | Avg win prob | " + " | ".join(short) + " |"
    sep = "|---" * (5 + len(short)) + "|"
    rows = [head, sep]
    for leg in legs:
        calls = [r["votes"].get(leg) for r in ok]
        counts = {k: sum(1 for c in calls if c and c[0] == k) for k in ("TAKE", "PASS", "FADE")}
        probs = [c[1] for c in calls if c and c[1] is not None]
        avg = f"{sum(probs) / len(probs):.0f}%" if probs else "—"
        cells = [f"{c[0]} {c[1]:.0f}%" if c and c[1] is not None else (c[0] if c else "—") for c in calls]
        rows.append(f"| {leg} | {counts['TAKE']} | {counts['PASS']} | {counts['FADE']} | {avg} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


# ---------------------------------------------------------------- main

def list_models(query):
    with urllib.request.urlopen(f"{API}/models", timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))["data"]
    q = (query or "").lower()
    hits = sorted((m for m in data if q in m["id"].lower() and not m["id"].endswith(":batch")),
                  key=lambda m: -m.get("created", 0))
    for m in hits[:40]:
        p = m.get("pricing", {})
        print(f"{m['id']:<48} in ${float(p.get('prompt', 0)) * 1e6:>6.2f}/M  out ${float(p.get('completion', 0)) * 1e6:>6.2f}/M")


def main():
    ap = argparse.ArgumentParser(description="Ask several OpenRouter models the same CFB/NFL question and tally votes.")
    ap.add_argument("--sport", choices=["cfb", "nfl"])
    ap.add_argument("--prompt-file")
    ap.add_argument("--prompt")
    ap.add_argument("--master", help="system prompt file (default: newest Master_Prompt_v*_for_Gemini.txt)")
    ap.add_argument("--project", help="the '<SPORT> Model' folder (default: searched from the current folder)")
    ap.add_argument("--models", help="comma-separated OpenRouter model IDs")
    ap.add_argument("--online", action="store_true", help="append :online so models can search the web (extra cost)")
    ap.add_argument("--max-tokens", type=int, default=6000)
    ap.add_argument("--out", help="report path (default: <project>/04_Research/AI_Panel/<timestamp>.md)")
    ap.add_argument("--no-votes", action="store_true", help="don't ask models for a VOTES block")
    ap.add_argument("--mock", action="store_true", help="fake answers, no key or cost")
    ap.add_argument("--list-models", nargs="?", const="", metavar="FILTER")
    a = ap.parse_args()

    if a.list_models is not None:
        list_models(a.list_models)
        return 0
    if not a.sport:
        ap.error("--sport is required")

    prompt = Path(a.prompt_file).read_text(encoding="utf-8") if a.prompt_file else (a.prompt or "")
    if not prompt and not sys.stdin.isatty():
        prompt = sys.stdin.read()
    if not prompt.strip():
        ap.error("give the question with --prompt-file, --prompt, or stdin")

    project = Path(a.project) if a.project else find_project(a.sport, Path.cwd())
    master = Path(a.master) if a.master else (find_master(project) if project else None)
    if not master or not master.is_file():
        print(f"ERROR: couldn't find the {a.sport.upper()} master prompt. Pass --master <file> or --project <folder>.")
        return 2
    system = master.read_text(encoding="utf-8")

    key = "" if a.mock else load_key()
    if not a.mock and not key:
        print("ERROR: no OpenRouter key. Set OPENROUTER_API_KEY, or create ~/.openrouter.env with the line\n"
              "  OPENROUTER_API_KEY=sk-or-...\n(get a key at https://openrouter.ai/keys). Use --mock to test without one.")
        return 2

    models = [m.strip() for m in (a.models.split(",") if a.models else DEFAULT_MODELS) if m.strip()]
    if a.online:
        models = [m if m.endswith(":online") else m + ":online" for m in models]
    user_prompt = prompt + ("" if a.no_votes else VOTES_FOOTER)

    print(f"Panel: {len(models)} models · system prompt {master.name} · {'MOCK' if a.mock else 'live'}", flush=True)
    started, results = time.time(), []

    def run(model):
        t0 = time.time()
        try:
            text, cost = mock_model(model, prompt) if a.mock else call_model(model, system, user_prompt, key, a.max_tokens)
            return {"model": model, "ok": True, "text": text, "cost": cost, "votes": parse_votes(text),
                    "seconds": round(time.time() - t0, 1)}
        except Exception as e:  # one failure never sinks the panel
            return {"model": model, "ok": False, "error": str(e), "seconds": round(time.time() - t0, 1)}

    with ThreadPoolExecutor(max_workers=len(models)) as pool:
        for fut in as_completed([pool.submit(run, m) for m in models]):
            r = fut.result()
            results.append(r)
            status = f"ok, {len(r['votes'])} votes" if r["ok"] else f"FAILED: {r['error']}"
            print(f"  {r['model']:<44} {r['seconds']:>6}s  {status}", flush=True)
    results.sort(key=lambda r: models.index(r["model"]))

    costs = [r.get("cost") for r in results if r.get("cost") is not None]
    total_cost = f"${sum(costs):.4f}" if costs else "n/a"
    ok = [r for r in results if r["ok"]]
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    report = [
        f"# AI panel — {a.sport.upper()} — {datetime.now():%Y-%m-%d %H:%M}",
        f"- System prompt: `{master.name}`",
        f"- Models: {len(ok)}/{len(results)} answered · {round(time.time() - started, 1)}s · cost {total_cost}"
        + (" · MOCK" if a.mock else "") + (" · web search on" if a.online else ""),
        "", "## Vote tally", tally_table(results),
        "", "## Request", prompt.strip(),
    ]
    for r in results:
        report += ["", f"## {r['model']} ({r['seconds']}s" + (f", ${r['cost']:.4f}" if r.get("cost") else "") + ")"]
        report.append(r["text"] if r["ok"] else f"**FAILED:** {r['error']}")
    text = "\n".join(report) + "\n"

    out = Path(a.out) if a.out else ((project or Path.cwd()) / "04_Research" / "AI_Panel" / f"{stamp}_{a.sport}.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")

    print("\n## Vote tally\n" + tally_table(results))
    print(f"\nCost: {total_cost} · full answers saved to: {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
