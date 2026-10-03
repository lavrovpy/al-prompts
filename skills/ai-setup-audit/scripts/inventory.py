#!/usr/bin/env python3
"""Read-only inventory of a machine's AI coding-agent setup, printed as Markdown.

Never prints secret values: secret detection reports file, key name, and file mode only.
Never opens chat/session history beyond counting files and matching tool-call names.

Usage: inventory.py [--section all|claude|codex|skills|secrets|tools] [--no-transcripts]
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
CODEX = os.path.join(HOME, ".codex")
AGENTS_SKILLS = os.path.join(HOME, ".agents", "skills")
DAY = 86400


def p(*a):
    print(*a)


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def ts(ms_or_s):
    if not ms_or_s:
        return "-"
    s = ms_or_s / 1000 if ms_or_s > 1e11 else ms_or_s
    return time.strftime("%Y-%m-%d", time.localtime(s))


def mtime(path):
    try:
        return os.lstat(path).st_mtime
    except OSError:
        return 0


def frontmatter(skill_md):
    try:
        text = open(skill_md, errors="replace").read()
    except OSError:
        return {}, ""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if km:
            fm[km.group(1)] = km.group(2).strip().strip('"')
    return fm, m.group(2)


def dir_hash(path):
    h = hashlib.sha256()
    for root, dirs, files in os.walk(path, followlinks=True):
        dirs.sort()
        for name in sorted(files):
            fp = os.path.join(root, name)
            h.update(os.path.relpath(fp, path).encode())
            try:
                with open(fp, "rb") as f:
                    h.update(f.read())
            except OSError:
                pass
    return h.hexdigest()[:12]


def du_mb(path):
    try:
        out = subprocess.run(["du", "-sk", path], capture_output=True, text=True, timeout=120).stdout
        return int(out.split()[0]) // 1024
    except Exception:
        return -1


def newest(path, depth=2):
    best = mtime(path)
    base = path.rstrip("/").count("/")
    for root, dirs, files in os.walk(path):
        if root.count("/") - base >= depth:
            dirs[:] = []
        for n in files + dirs:
            best = max(best, mtime(os.path.join(root, n)))
    return best


# ---------------------------------------------------------------- Claude Code


def mcp_calls_from_transcripts():
    """Map MCP server (normalized) -> [sessions_with_calls, last_mtime] from real tool_use records."""
    # Anchored on tool_use: a bare "name":"mcp__…" also matches deferred-tool listings, which every session carries.
    pat = re.compile(r'"type":"tool_use","id":"[^"]*","name":"mcp__(.+?)__[^"]+"')
    agg = {}
    root = os.path.join(CLAUDE, "projects")
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".jsonl"):
                continue
            fp = os.path.join(dirpath, f)
            try:
                text = open(fp, errors="ignore").read()
            except OSError:
                continue
            mt = mtime(fp)
            for server in set(pat.findall(text)):
                e = agg.setdefault(server, [0, 0])
                e[0] += 1
                e[1] = max(e[1], mt)
    return agg


def section_claude(scan_transcripts):
    p("## Claude Code\n")
    settings = load_json(os.path.join(CLAUDE, "settings.json")) or {}
    cj = load_json(os.path.join(HOME, ".claude.json")) or {}

    p("### settings.json")
    p(f"- keys: {', '.join(sorted(settings))}")
    if "mcpServers" in settings:
        p("- **`mcpServers` is set in settings.json** — not a settings key; servers load from `~/.claude.json` / `.mcp.json`")
    perms = settings.get("permissions", {})
    p(f"- permissions.defaultMode: {perms.get('defaultMode', '-')}; allow rules: {len(perms.get('allow', []))}")
    for rule in perms.get("allow", []):
        p(f"  - allow `{rule}`")
    overrides = settings.get("skillOverrides", {})
    if overrides:
        p(f"- skillOverrides: {json.dumps(overrides)}")

    p("\n### Plugins (installed vs enabled vs used)")
    inst = (load_json(os.path.join(CLAUDE, "plugins", "installed_plugins.json")) or {}).get("plugins", {})
    enabled = settings.get("enabledPlugins", {})
    usage = cj.get("pluginUsage", {})
    p("| plugin | version | enabled | updated | usage | last used |")
    p("|---|---|---|---|---|---|")
    for name, entries in sorted(inst.items()):
        e = entries[0]
        u = usage.get(name, {})
        p(f"| {name} | {e.get('version')} | {enabled.get(name, 'unset')} | {e.get('lastUpdated', '')[:10]} | {u.get('usageCount', 0)} | {ts(u.get('lastUsedAt'))} |")
    p("\nSessionStart/Stop hooks injected by enabled plugins:")
    for name, entries in sorted(inst.items()):
        if enabled.get(name) is not True:
            continue
        ip = entries[0].get("installPath", "")
        for hp in (os.path.join(ip, "hooks", "hooks.json"), os.path.join(ip, "hooks.json")):
            hooks = (load_json(hp) or {}).get("hooks", {})
            for ev, arr in hooks.items():
                for m in arr:
                    for h in m.get("hooks", [m]):
                        cmd = (h.get("command") or h.get("prompt") or "")[:90]
                        p(f"- {name}: {ev} {m.get('matcher', '')} `{cmd}`")

    p("\n### Marketplaces")
    km = load_json(os.path.join(CLAUDE, "plugins", "known_marketplaces.json")) or {}
    for name, m in sorted(km.items()):
        src = m.get("source", {})
        p(f"- {name}: {src.get('repo') or src.get('url')} lastUpdated={m.get('lastUpdated', '')[:10]} autoUpdate={m.get('autoUpdate', False)}")

    p("\n### MCP servers")
    calls = mcp_calls_from_transcripts() if scan_transcripts else {}
    norm = lambda s: re.sub(r"[^A-Za-z0-9_-]", "_", s)
    rows = [("user", n, c) for n, c in cj.get("mcpServers", {}).items()]
    for proj, pc in cj.get("projects", {}).items():
        rows += [(proj, n, c) for n, c in pc.get("mcpServers", {}).items()]
    p("| scope | server | launch | sessions with real calls | last call |")
    p("|---|---|---|---|---|")
    for scope, n, c in rows:
        launch = (c.get("url") or "").split("?")[0] or " ".join(
            [c.get("command", "")] + ["<masked>" if re.search(r"(sk-|key|token|secret)", a, re.I) else a for a in c.get("args", [])]
        )[:70]
        k = calls.get(norm(n), [0, 0])
        p(f"| {scope} | {n} | `{launch}` | {k[0] if scan_transcripts else 'n/a'} | {ts(k[1]) if k[1] else '-'} |")
    if scan_transcripts:
        other = {k: v for k, v in calls.items() if k not in {norm(r[1]) for r in rows}}
        if other:
            p("\nOther MCP servers with real calls (plugins, claude.ai connectors, IDE):")
            for k, v in sorted(other.items(), key=lambda kv: -kv[1][1]):
                p(f"- {k}: {v[0]} sessions, last {ts(v[1])}")

    p("\n### Skill usage (Skill tool / slash invocations)")
    su = cj.get("skillUsage", {})
    for name, u in sorted(su.items(), key=lambda kv: -(kv[1].get("lastUsedAt", 0) if isinstance(kv[1], dict) else 0)):
        if isinstance(u, dict):
            p(f"- {name}: {u.get('usageCount')}× last {ts(u.get('lastUsedAt'))}")

    gone = [k for k in cj.get("projects", {}) if not os.path.exists(k)]
    p(f"\n### ~/.claude.json projects: {len(cj.get('projects', {}))} total, {len(gone)} point at missing paths")

    leftovers = [f for f in os.listdir(os.path.join(CLAUDE, "commands")) if f.endswith(".bak")] if os.path.isdir(os.path.join(CLAUDE, "commands")) else []
    if leftovers:
        p(f"- leftover command backups: {', '.join(leftovers)}")
    trash = os.path.join(CLAUDE, "skills", ".trash")
    if os.path.isdir(trash):
        p(f"- skills/.trash: {len(os.listdir(trash))} entries, {du_mb(trash)} MB")
    p()


# ---------------------------------------------------------------------- Codex


def section_codex():
    p("## Codex\n")
    cfg_path = os.path.join(CODEX, "config.toml")
    if not os.path.exists(cfg_path):
        p("- no ~/.codex/config.toml\n")
        return
    try:
        import tomllib
        cfg = tomllib.load(open(cfg_path, "rb"))
    except Exception as e:
        p(f"- config.toml did not parse: {e}\n")
        return
    p(f"- model: {cfg.get('model')}  approval_policy: {cfg.get('approval_policy', 'unset')}  sandbox_mode: {cfg.get('sandbox_mode', 'unset')}  approvals_reviewer: {cfg.get('approvals_reviewer', 'unset')}")
    broad = {HOME, os.path.join(HOME, "Desktop"), os.path.join(HOME, "Downloads"), os.path.join(HOME, "Documents"), "/"}
    projects = cfg.get("projects", {})
    p(f"- trusted projects: {len(projects)}")
    for path in projects:
        if path in broad:
            p(f"  - **broad trust**: {path}")
        elif not os.path.exists(path):
            p(f"  - missing path: {path}")
        elif os.path.isdir(path) and not any(files for _, _, files in os.walk(path)):
            p(f"  - empty folder: {path}")
    p("- MCP servers:")
    for name, s in cfg.get("mcp_servers", {}).items():
        args = s.get("args", [])
        flags = []
        if any("@latest" in a for a in args):
            flags.append("unpinned @latest")
        if any(re.search(r"(api[-_]?key|token|secret)", a, re.I) for a in args):
            flags.append("**key passed in args**")
        if s.get("enabled") is False:
            flags.append("disabled")
        launch = s.get("url") or " ".join([s.get("command", "")] + [a if not re.search(r"(sk-|key|token)", a, re.I) else "<masked>" for a in args])
        p(f"  - {name}: `{launch[:80]}` {' '.join(flags)}")
    for table in ("notice",):
        if table in cfg:
            p(f"- [{table}] present: {list(cfg[table].keys())}")

    rules_dir = os.path.join(CODEX, "rules")
    if os.path.isdir(rules_dir):
        shells = {"/bin/zsh", "/bin/bash", "/bin/sh", "zsh", "bash", "sh", "env"}
        for rf in sorted(os.listdir(rules_dir)):
            if not rf.endswith(".rules"):
                continue
            lines = open(os.path.join(rules_dir, rf)).read().splitlines()
            allows = [l for l in lines if 'decision="allow"' in l]
            p(f"- rules/{rf}: {len(allows)} allow rules")
            for i, l in enumerate(lines, 1):
                m = re.search(r"pattern=\[(.*?)\]", l)
                if not m:
                    continue
                toks = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
                if len(toks) == 1 and toks[0] in shells:
                    p(f"  - **line {i}: blanket allow for `{toks[0]}`** — matches every command the agent wraps in that shell")
                elif len(toks) <= 3 and toks and toks[-1] in {"python", "node", "bash", "sh", "origin"}:
                    p(f"  - line {i}: broad allow `{' '.join(toks)}`")
                elif len(" ".join(toks)) > 90:
                    p(f"  - line {i}: one-off rule `{' '.join(toks)[:70]}…`")

    legacy = [f for f in ("config.json", "instructions.md", "update-check.json") if os.path.exists(os.path.join(CODEX, f))]
    if legacy:
        p(f"- legacy files: {', '.join(legacy)}")
    agents_md = os.path.join(CODEX, "AGENTS.md")
    if os.path.exists(agents_md):
        p(f"- AGENTS.md: {'symlink -> ' + os.readlink(agents_md) if os.path.islink(agents_md) else str(os.path.getsize(agents_md)) + ' bytes'}")
    baks = [f for f in os.listdir(CODEX) if ".bak" in f or f.endswith(".tmp") or ".tmp-" in f]
    if baks:
        p(f"- backup/tmp files in ~/.codex: {len(baks)} (check .bak files for secrets)")
    p()


# --------------------------------------------------------------------- Skills


def skill_dirs():
    roots = {
        "~/.agents/skills": AGENTS_SKILLS,
        "~/.claude/skills": os.path.join(CLAUDE, "skills"),
        "~/.codex/skills": os.path.join(CODEX, "skills"),
    }
    for label, root in roots.items():
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if name.startswith(".") or name == "synced":
                continue
            yield label, name, os.path.join(root, name)


def section_skills():
    p("## Skills\n")
    lock = (load_json(os.path.join(HOME, ".agents", ".skill-lock.json")) or {}).get("skills", {})
    settings = load_json(os.path.join(CLAUDE, "settings.json")) or {}
    overrides = settings.get("skillOverrides", {})
    su = (load_json(os.path.join(HOME, ".claude.json")) or {}).get("skillUsage", {})
    seen = {}
    p("| location | skill | kind | source | model-invoked | desc chars | override | uses | modified |")
    p("|---|---|---|---|---|---|---|---|---|")
    bodies = {}
    for label, name, path in skill_dirs():
        if os.path.islink(path):
            target = os.readlink(path)
            kind = "BROKEN link" if not os.path.exists(path) else f"link → {target}"
        else:
            kind = "real dir"
        fm, body = frontmatter(os.path.join(path, "SKILL.md"))
        bodies[name] = body
        src = lock.get(name, {}).get("source", "")
        model = "no" if fm.get("disable-model-invocation") == "true" else "yes"
        u = su.get(name, {})
        uses = f"{u.get('usageCount')}× {ts(u.get('lastUsedAt'))}" if isinstance(u, dict) and u else "-"
        p(f"| {label} | {name} | {kind} | {src} | {model} | {len(fm.get('description', ''))} | {overrides.get(name, '')} | {uses} | {ts(mtime(os.path.join(path, 'SKILL.md')))} |")
        if os.path.exists(path) and not os.path.islink(path):
            seen.setdefault(name, []).append((label, dir_hash(path)))
    p("\nReal copies of the same skill in more than one place (same hash = identical, different = drifted):")
    dup = False
    for name, copies in sorted(seen.items()):
        if len(copies) > 1:
            dup = True
            p(f"- {name}: " + ", ".join(f"{l} [{h}]" for l, h in copies))
    if not dup:
        p("- none")
    off = [k for k, v in overrides.items() if v == "off"]
    p("\nSkills that delegate to a skill switched `off` (broken chains):")
    broken = False
    for name, body in bodies.items():
        for o in off:
            if o != name and re.search(rf'(/{re.escape(o)}\b|"{re.escape(o)}"|`{re.escape(o)}`)', body):
                broken = True
                p(f"- {name} → {o}")
    if not broken:
        p("- none")
    p()


# -------------------------------------------------------------------- Secrets

SECRET_KEY = re.compile(r'["\']?([A-Za-z0-9_-]*(?:api[_-]?key|token|secret|password)[A-Za-z0-9_-]*)["\']?\s*[:=]\s*["\']?([^"\'\s,}]{8,})', re.M | re.I)
NOT_SECRET_KEY = re.compile(r"(date|at|count|time|seen|usage|limit|type|expir\w*|_env_var|url|uri|id)$", re.I)
SECRET_PREFIXES = [
    (label, re.compile(rx))
    for label, rx in [
        ("sk-* key", r"\bsk-[A-Za-z0-9-]{10,}"),
        ("Context7 key", r"\bctx7sk-[A-Za-z0-9-]{10,}"),
        ("GitHub token", r"\bgh[po]_[A-Za-z0-9]{20,}"),
        ("GitLab token", r"\bglpat-[A-Za-z0-9_-]{15,}"),
        ("GitLab OAuth secret", r"\bgloas-[A-Za-z0-9]{20,}"),
        ("Slack token", r"\bxox[abp]-[A-Za-z0-9-]{10,}"),
        ("Google API key", r"\bAIza[A-Za-z0-9_-]{30,}"),
        ("Groq key", r"\bgsk_[A-Za-z0-9]{20,}"),
    ]
]
PLACEHOLDER = re.compile(r"^(\$\{|<|your|xxx|\*\*\*|true|false|none|null|\d+$)", re.I)

CONFIG_GLOBS = [
    "~/.claude.json", "~/.claude/settings.json", "~/.claude/settings.local.json",
    "~/.codex/config.toml", "~/.codex/*.toml*", "~/.cursor/mcp.json", "~/.cursor/cli-config.json",
    "~/.config/opencode/opencode.json*", "~/.gemini/settings.json", "~/.gemini/*/mcp_config.json",
    "~/.kilocode/cli/config.json", "~/.kilocode/cli/global/secrets.json", "~/.cline/data/secrets.json",
    "~/.copilot/config.json", "~/.copilot/mcp-config.json", "~/.cli-proxy-api/*.json",
    "~/Library/Application Support/Claude/claude_desktop_config.json",
    "~/Library/Application Support/Code/User/mcp.json", "~/Library/Application Support/Code - Insiders/User/mcp.json",
    "~/Library/Application Support/Code - Insiders/User/profiles/*/mcp.json", "~/Library/Application Support/Cursor/User/mcp.json",
]


def section_secrets():
    import glob
    p("## Plaintext secrets in config files (values never printed)\n")
    p("| file | mode | key names / token types | copies of same value elsewhere |")
    p("|---|---|---|---|")
    found = {}
    for g in CONFIG_GLOBS:
        for fp in glob.glob(os.path.expanduser(g)):
            if not os.path.isfile(fp):
                continue
            try:
                text = open(fp, errors="ignore").read()
            except OSError:
                continue
            hits = []
            for k, v in SECRET_KEY.findall(text):
                if not PLACEHOLDER.match(v) and not v.startswith("http") and not NOT_SECRET_KEY.search(k):
                    hits.append((k, hashlib.sha256(v.encode()).hexdigest()[:8]))
            for label, rx in SECRET_PREFIXES:
                for v in rx.findall(text):
                    hits.append((label, hashlib.sha256(v.encode()).hexdigest()[:8]))
            if hits:
                found[fp] = (oct(stat.S_IMODE(os.stat(fp).st_mode)), hits)
    by_hash = {}
    for fp, (_, hits) in found.items():
        for _, h in hits:
            by_hash.setdefault(h, set()).add(fp)
    for fp, (mode, hits) in sorted(found.items()):
        names = sorted({k for k, _ in hits})
        shared = sorted({os.path.basename(o) for _, h in hits for o in by_hash[h] if o != fp})
        flag = " **world-readable**" if mode.endswith("4") else ""
        p(f"| {fp.replace(HOME, '~')} | {mode}{flag} | {', '.join(names)} | {', '.join(shared) or '-'} |")
    if not found:
        p("| none found | | | |")
    p("\nThe scan covers known config files only; grep further for a specific key *name* when a finding suggests copies elsewhere.\n")


# ---------------------------------------------------------------------- Tools

TOOLS = [
    # (label, data dirs, binaries, app bundle, history subpaths to keep)
    ("Claude Code", ["~/.claude"], ["claude"], None, ["projects", "history.jsonl"]),
    ("Codex", ["~/.codex"], ["codex"], "ChatGPT.app", ["sessions", "archived_sessions", "history.jsonl", "history.json"]),
    ("Cursor", ["~/.cursor"], ["cursor", "cursor-agent"], "Cursor.app", ["chats", "acp-sessions"]),
    ("Gemini CLI / Antigravity", ["~/.gemini"], ["gemini"], "Antigravity.app", ["antigravity", "history", "tmp"]),
    ("OpenCode", ["~/.opencode", "~/.config/opencode"], ["opencode"], None, ["~/.local/share/opencode"]),
    ("Amp", ["~/.amp", "~/.config/amp"], ["amp"], None, ["~/.local/share/amp"]),
    ("Pi", ["~/.pi"], ["pi"], None, ["agent/sessions"]),
    ("Kilo Code", ["~/.kilocode"], ["kilo", "kilocode"], None, ["cli/global/tasks", "cli/history.json"]),
    ("Cline", ["~/.cline"], ["cline"], None, ["data/tasks"]),
    ("Copilot CLI", ["~/.copilot"], ["copilot"], None, ["session-state"]),
    ("Grok CLI", ["~/.grok"], ["grok"], None, ["sessions"]),
    ("Windsurf", ["~/.windsurf", "~/.codeium"], ["windsurf"], "Windsurf.app", []),
    ("Kiro", ["~/.kiro"], ["kiro"], "Kiro.app", []),
    ("Trae", ["~/.trae-aicc", "~/.trae"], [], "Trae.app", []),
    ("Junie", ["~/.junique", "~/.junie"], [], None, []),
    ("CodeRabbit", ["~/.coderabbit"], ["coderabbit"], None, []),
    ("LM Studio", ["~/.lmstudio"], ["lms"], "LM Studio.app", ["conversations"]),
    ("Ollama", ["~/.ollama"], ["ollama"], "Ollama.app", ["history"]),
    ("CLIProxyAPI", ["~/.cli-proxy-api"], ["cliproxyapi"], None, []),
    ("mcp-remote auth cache", ["~/.mcp-auth"], [], None, []),
]


def section_tools():
    p("## AI tools on this machine\n")
    p("| tool | installed | data dirs (MB) | last activity | history to keep |")
    p("|---|---|---|---|---|")
    for label, dirs, bins, app, hist in TOOLS:
        dirs = [os.path.expanduser(d) for d in dirs if os.path.exists(os.path.expanduser(d))]
        installed = [b for b in bins if shutil.which(b)] + ([app] if app and os.path.exists(f"/Applications/{app}") else [])
        if not dirs and not installed:
            continue
        sizes = ", ".join(f"{d.replace(HOME, '~')} {du_mb(d)}" for d in dirs)
        last = ts(max((newest(d) for d in dirs), default=0))
        keep = []
        for h in hist:
            hp = os.path.expanduser(h) if h.startswith("~") else (os.path.join(dirs[0], h) if dirs else "")
            if hp and os.path.exists(hp):
                keep.append(hp.replace(HOME, "~"))
        p(f"| {label} | {', '.join(installed) or '**not installed**'} | {sizes or '-'} | {last} | {', '.join(keep) or '-'} |")
    p("\nBroken symlinks in agent config dirs:")
    roots = [CLAUDE + "/skills", CODEX + "/skills", AGENTS_SKILLS] + [os.path.expanduser(d) for d in ("~/.pi", "~/.gemini", "~/.cursor", "~/.config/opencode", "~/.copilot", "~/.grok")]
    broken = []
    for r in roots:
        if not os.path.isdir(r):
            continue
        base = r.count("/")
        for root, dirs, files in os.walk(r):
            if root.count("/") - base >= 4 or "node_modules" in root:
                dirs[:] = []
                continue
            for n in dirs + files:
                fp = os.path.join(root, n)
                if os.path.islink(fp) and not os.path.exists(fp):
                    broken.append(fp.replace(HOME, "~"))
    p("\n".join(f"- {b}" for b in broken) or "- none")
    p()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", default="all", choices=["all", "claude", "codex", "skills", "secrets", "tools"])
    ap.add_argument("--no-transcripts", action="store_true", help="skip scanning Claude transcripts for MCP calls")
    a = ap.parse_args()
    p(f"# AI setup inventory — {time.strftime('%Y-%m-%d')}\n")
    if a.section in ("all", "claude"):
        section_claude(not a.no_transcripts)
    if a.section in ("all", "codex"):
        section_codex()
    if a.section in ("all", "skills"):
        section_skills()
    if a.section in ("all", "secrets"):
        section_secrets()
    if a.section in ("all", "tools"):
        section_tools()


if __name__ == "__main__":
    sys.exit(main())
