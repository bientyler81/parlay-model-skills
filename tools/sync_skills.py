"""Mirror every Claude skill (and its master-prompt version history) into this repo, then commit and push.

Sources it scans:
  - User-level skills:     ~/.claude/skills/<name>/
  - Project-level skills:  <Agent Projects>/<project>/.claude/skills/<name>/
  - Master prompt history: <Agent Projects>/<project>/01_Master_Prompt/  (skill name read from the newest
                           Master_Prompt_v*_SKILL.md front matter). If a skill has no installed copy on this
                           computer (e.g. nfl-parlay-model lives on claude.ai), the newest versioned SKILL file
                           is used as the current SKILL.md.

Privacy: before a file is copied here it is cleaned with the rules in tools/redactions.local.json
(gitignored, never uploaded): some files are skipped, personal details are replaced with placeholders, and
the push is blocked if any leak pattern is still found in the repo. Without that file, nothing syncs.

Repo layout it writes:
  <skill-name>/SKILL.md      current skill (plus any other files in the installed skill folder)
  <skill-name>/history/...   mirror of the project's 01_Master_Prompt folder

Usage:
  python tools/sync_skills.py            sync, commit, push, print a verification report
  python tools/sync_skills.py --dry-run  show what would change, touch nothing
  python tools/sync_skills.py --hook     Claude Code hook mode: reads hook JSON on stdin, only acts when a
                                         skill or master-prompt file was touched (or on Stop/SessionStart),
                                         prints hook JSON so the user and Claude see what was pushed.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = REPO.parent  # ...\Agent Projects
USER_SKILLS = Path.home() / ".claude" / "skills"
IGNORE_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
SKIP_USER_SKILL_DIRS = {"synced", ".trash"}  # claude.ai-synced copies are managed by the app, not by us
RULES_FILE = REPO / "tools" / "redactions.local.json"
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv", ".py", ".yaml", ".yml", ".html", ".js", ".css", ""}


def load_rules():
    if not RULES_FILE.is_file():
        raise RuntimeError(f"{RULES_FILE.name} is missing, so personal details can't be removed; nothing synced.")
    raw = json.loads(RULES_FILE.read_text(encoding="utf-8"))
    return {
        "exclude_paths": set(raw.get("exclude_paths", [])),
        "exclude_content": [re.compile(x) for x in raw.get("exclude_if_content_matches", [])],
        "replacements": [(re.compile(a), b) for a, b in raw.get("replacements", [])],
        "leaks": [re.compile(x) for x in raw.get("leak_patterns", [])],
    }


def is_text(path):
    return path.suffix.lower() in TEXT_SUFFIXES


def cleaned_bytes(src, rules):
    data = src.read_bytes()
    if not is_text(src):
        return data
    text = data.decode("utf-8", errors="surrogateescape")
    for rx, repl in rules["replacements"]:
        text = rx.sub(repl, text)
    return text.encode("utf-8", errors="surrogateescape")


def excluded(rel, src, rules):
    if rel in rules["exclude_paths"]:
        return True
    if is_text(src) and rules["exclude_content"]:
        text = src.read_text(encoding="utf-8", errors="replace")
        return any(rx.search(text) for rx in rules["exclude_content"])
    return False


def leak_scan(rules):
    """Return 'file:line' hits for any leak pattern in files git would upload."""
    hits = []
    for rel in git("ls-files", "-co", "--exclude-standard").splitlines():
        f = REPO / rel
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            if any(rx.search(line) for rx in rules["leaks"]):
                hits.append(f"{rel}:{n}")
    return hits


def version_key(path):
    m = re.search(r"_v(\d+)\.(\d+)_SKILL\.md$", path.name)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


def front_matter_name(path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.match(r"---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return None
    n = re.search(r'^name:\s*"?([^"\n]+?)"?\s*$', m.group(1), re.M)
    return n.group(1).strip() if n else None


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files_under(folder):
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.name not in IGNORE_NAMES and "__pycache__" not in p.parts:
            yield p


def discover():
    """Return {skill_name: {"installed": [dirs], "history": dir or None, "newest_versioned": path or None}}."""
    skills = {}

    def entry(name):
        return skills.setdefault(name, {"installed": [], "history": None, "newest_versioned": None})

    if USER_SKILLS.is_dir():
        for d in sorted(USER_SKILLS.iterdir()):
            if d.is_dir() and d.name not in SKIP_USER_SKILL_DIRS and (d / "SKILL.md").is_file():
                entry(front_matter_name(d / "SKILL.md") or d.name)["installed"].append(d)

    for project in sorted(PROJECTS_ROOT.iterdir()):
        if not project.is_dir() or project == REPO:
            continue
        sk = project / ".claude" / "skills"
        if sk.is_dir():
            for d in sorted(sk.iterdir()):
                if d.is_dir() and (d / "SKILL.md").is_file():
                    entry(front_matter_name(d / "SKILL.md") or d.name)["installed"].append(d)
        mp = project / "01_Master_Prompt"
        if mp.is_dir():
            versioned = [p for p in mp.glob("Master_Prompt_v*_SKILL.md") if version_key(p) >= (0, 0)]
            if versioned:
                newest = max(versioned, key=version_key)
                name = front_matter_name(newest)
                if name:
                    e = entry(name)
                    e["history"] = mp
                    e["newest_versioned"] = newest
    return skills


def plan(skills, rules):
    """Build {repo_relative_path: source_path} plus warnings."""
    desired, warnings, summary = {}, [], []
    for name, info in sorted(skills.items()):
        installed = info["installed"]
        if installed:
            # Prefer the copy edited most recently; warn if copies disagree.
            current_dir = max(installed, key=lambda d: (d / "SKILL.md").stat().st_mtime)
            hashes = {sha(d / "SKILL.md") for d in installed}
            if len(hashes) > 1:
                warnings.append(f"{name}: installed copies differ ({', '.join(str(d) for d in installed)}); "
                                f"uploaded the newest: {current_dir}")
            for f in files_under(current_dir):
                desired[f"{name}/{f.relative_to(current_dir).as_posix()}"] = f
            current_src = current_dir / "SKILL.md"
        elif info["newest_versioned"]:
            current_src = info["newest_versioned"]
            desired[f"{name}/SKILL.md"] = current_src
        else:
            continue
        nv = info["newest_versioned"]
        if installed and nv and sha(nv) != sha(current_src):
            warnings.append(f"{name}: installed SKILL.md does not match newest versioned file {nv.name}")
        if info["history"]:
            for f in files_under(info["history"]):
                desired[f"{name}/history/{f.relative_to(info['history']).as_posix()}"] = f
        summary.append((name, current_src))
    skipped = [rel for rel, src in desired.items() if excluded(rel, src, rules)]
    for rel in skipped:
        del desired[rel]
    return desired, warnings, summary


def apply(desired, skill_names, dry_run, rules):
    changed = []
    for rel, src in desired.items():
        dst = REPO / rel
        data = cleaned_bytes(src, rules)
        if dst.is_file() and dst.read_bytes() == data:
            continue
        changed.append(("updated" if dst.exists() else "added", rel))
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
    # Remove files that vanished from a skill's sources (only inside skill folders we manage this run).
    for name in skill_names:
        folder = REPO / name
        if not folder.is_dir():
            continue
        for f in files_under(folder):
            rel = f.relative_to(REPO).as_posix()
            if rel not in desired:
                changed.append(("removed", rel))
                if not dry_run:
                    f.unlink()
    return changed


def git(*args, check=True):
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout.strip()


def commit_and_push(changed):
    lines = []
    git("add", "-A")
    staged = git("diff", "--cached", "--name-status")
    if staged:
        names = sorted({c[1].split("/")[0] for c in changed}) or ["repo"]
        msg = f"Sync skills: {', '.join(names)}\n\n" + "\n".join(f"{k}: {p}" for k, p in changed) + \
              "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
        r = subprocess.run(["git", "-C", str(REPO), "commit", "-q", "-F", "-"], input=msg, text=True,
                           capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"git commit failed: {r.stderr.strip() or r.stdout.strip()}")
        lines.append(f"Committed {git('rev-parse', '--short', 'HEAD')}")
    remote = git("remote", "get-url", "origin", check=False)
    if not remote:
        if staged:
            lines.append("No GitHub remote set yet; committed locally, nothing pushed.")
        return lines, False
    ahead = git("rev-list", "--count", "@{u}..HEAD", check=False)
    if ahead == "0":
        if not staged:
            return lines, True  # fully in sync, say nothing
        lines.append("Remote already up to date.")
        return lines, True
    r = subprocess.run(["git", "-C", str(REPO), "push", "-q", "-u", "origin", "HEAD"], capture_output=True,
                       text=True)
    if r.returncode != 0:
        lines.append(f"PUSH FAILED (commit kept locally, will retry next sync): {r.stderr.strip()}")
        return lines, False
    lines.append(f"Pushed to {remote.removesuffix('.git')} at {git('rev-parse', '--short', 'HEAD')}")
    return lines, True


def report(changed, warnings, summary, push_lines):
    out = []
    if changed:
        out.append(f"Skill sync: {len(changed)} file(s) changed")
        for kind, rel in changed[:40]:
            out.append(f"  {kind}: {rel}")
        if len(changed) > 40:
            out.append(f"  ... and {len(changed) - 40} more")
    out += push_lines
    if changed or push_lines:
        for name, src in summary:
            repo_copy = REPO / name / "SKILL.md"
            h = sha(repo_copy) if repo_copy.is_file() else sha(src)
            note = " (personal details removed)" if repo_copy.is_file() and h != sha(src) else ""
            out.append(f"  {name}/SKILL.md sha256 {h[:12]}{note} <- {src}")
    out += [f"WARNING: {w}" for w in warnings]
    return "\n".join(out)


def hook_should_run(payload):
    event = payload.get("hook_event_name", "")
    if event in ("Stop", "SessionStart", "SessionEnd"):
        return True
    tool_input = payload.get("tool_input") or {}
    path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "").replace("\\", "/")
    return bool(re.search(r"/\.claude/skills/|/01_Master_Prompt/", path))


def main():
    dry_run = "--dry-run" in sys.argv
    hook = "--hook" in sys.argv
    event = ""
    if hook:
        try:
            payload = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            payload = {}
        event = payload.get("hook_event_name", "")
        if not hook_should_run(payload):
            return 0
    try:
        rules = load_rules()
        skills = discover()
        desired, warnings, summary = plan(skills, rules)
        changed = apply(desired, [s[0] for s in summary], dry_run, rules)
        leaks = [] if dry_run else leak_scan(rules)
        if leaks:
            push_lines = ["PUSH BLOCKED: personal details still found in " + ", ".join(leaks[:10]) +
                          ". Add a rule to tools/redactions.local.json, then sync again."]
        else:
            push_lines = [] if dry_run else commit_and_push(changed)[0]
        text = report(changed, warnings, summary, push_lines)
    except Exception as exc:  # never break the session over a sync problem
        text = f"Skill sync error: {exc}"
    if dry_run and not text:
        text = "Dry run: repo already matches all skill sources."
    if not hook:
        print(text or "Skills already in sync with GitHub.")
        return 0
    if text:
        out = {"systemMessage": text}
        if event in ("PostToolUse", "SessionStart"):
            out["hookSpecificOutput"] = {"hookEventName": event,
                                         "additionalContext": "GitHub skill sync ran:\n" + text}
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
