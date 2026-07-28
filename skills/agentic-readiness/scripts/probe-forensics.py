#!/usr/bin/env python3
"""Extract objective friction evidence from a probe subagent's transcript.

The probe's own journal says what it *felt*. This says what it actually *did*:
how many tool calls it burned, which ones errored, where it stalled, and
whether it searched for the same thing over and over.

Usage:
    probe-forensics.py --list
    probe-forensics.py --name <agent-name>
    probe-forensics.py --path <agent-xxx.jsonl>

Stdlib only. Read-only. Emits Markdown on stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from glob import glob
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"


# --------------------------------------------------------------------------
# locating transcripts
# --------------------------------------------------------------------------


def find_transcripts() -> list[tuple[Path, dict]]:
    """Every subagent transcript on disk, newest first, with its meta."""
    out: list[tuple[Path, dict]] = []
    for meta_path in glob(str(PROJECTS / "*" / "*" / "subagents" / "*.meta.json")):
        jsonl = Path(meta_path[: -len(".meta.json")] + ".jsonl")
        if not jsonl.exists():
            continue
        try:
            meta = json.loads(Path(meta_path).read_text())
        except (json.JSONDecodeError, OSError):
            meta = {}
        out.append((jsonl, meta))
    out.sort(key=lambda pair: pair[0].stat().st_mtime, reverse=True)
    return out


def resolve_by_name(name: str) -> Path:
    for jsonl, meta in find_transcripts():
        if meta.get("name") == name:
            return jsonl
    # Fall back to a substring match on the filename; the on-disk convention
    # embeds the agent name, but that is an implementation detail and may move.
    for jsonl, _ in find_transcripts():
        if name in jsonl.name:
            return jsonl
    sys.exit(
        f"No subagent transcript found for name {name!r}.\n"
        "Run with --list to see what is on disk. If nothing matches, Claude Code\n"
        "may have changed its storage layout — fall back to journal + diff evidence\n"
        "and record in the report that transcript corroboration was unavailable."
    )


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------


def iter_blocks(obj):
    """Yield every dict nested anywhere in the entry (shape-tolerant)."""
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from iter_blocks(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_blocks(item)


def parse_ts(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def summarize(path: Path) -> str:
    calls: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    bash: list[tuple[datetime | None, str]] = []
    searches: Counter[str] = Counter()
    reads: Counter[str] = Counter()
    stamps: list[tuple[datetime, str]] = []
    pending: dict[str, str] = {}  # tool_use_id -> tool name

    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = parse_ts(entry.get("timestamp"))
            label = ""

            for block in iter_blocks(entry):
                kind = block.get("type")

                if kind == "tool_use":
                    name = block.get("name", "?")
                    calls[name] += 1
                    label = label or name
                    if block.get("id"):
                        pending[block["id"]] = name
                    args = block.get("input") or {}
                    if not isinstance(args, dict):
                        continue
                    if name == "Bash" and args.get("command"):
                        bash.append((ts, str(args["command"])[:160]))
                    if name in ("Grep", "Glob") and args.get("pattern"):
                        searches[f"{name}:{args['pattern']}"] += 1
                    if name in ("Read", "read_file") and args.get("file_path"):
                        reads[str(args["file_path"])] += 1

                elif kind == "tool_result" and block.get("is_error"):
                    errors[pending.get(block.get("tool_use_id", ""), "unknown")] += 1

            if ts:
                stamps.append((ts, label))

    if not stamps:
        return f"No parseable entries in `{path}`."

    stamps.sort(key=lambda pair: pair[0])
    span = stamps[-1][0] - stamps[0][0]
    total = sum(calls.values())

    gaps = [
        (stamps[i + 1][0] - stamps[i][0], stamps[i][1], stamps[i + 1][0])
        for i in range(len(stamps) - 1)
    ]
    gaps.sort(key=lambda g: g[0], reverse=True)

    lines: list[str] = []
    add = lines.append

    add(f"### Transcript forensics — `{path.name}`")
    add("")
    add(f"- **Wall clock**: {span} ({stamps[0][0].isoformat()} → {stamps[-1][0].isoformat()})")
    add(f"- **Tool calls**: {total}")
    add(f"- **Errored results**: {sum(errors.values())}")
    add("")

    add("**Calls by tool**")
    add("")
    add("| Tool | Calls | Errors |")
    add("| --- | ---: | ---: |")
    for name, n in calls.most_common():
        add(f"| {name} | {n} | {errors.get(name, 0)} |")
    add("")

    repeated = [(pat, n) for pat, n in searches.most_common() if n > 1]
    if repeated:
        add("**Repeated searches** — the same query issued more than once is churn:")
        add("")
        for pat, n in repeated[:15]:
            add(f"- `{pat}` ×{n}")
        add("")

    rereads = [(f, n) for f, n in reads.most_common() if n > 1]
    if rereads:
        add(f"**Re-read files** ({len(reads)} unique files read):")
        add("")
        for f, n in rereads[:10]:
            add(f"- `{f}` ×{n}")
        add("")

    if bash:
        add(f"**Bash timeline** ({len(bash)} commands) — read this for the bootstrap and validate phases:")
        add("")
        for ts, cmd in bash:
            when = ts.strftime("%H:%M:%S") if ts else "--:--:--"
            add(f"- `{when}` `{cmd}`")
        add("")

    add("**Longest stalls** — a long gap after a tool call is where thinking or retrying happened:")
    add("")
    for delta, after, until in gaps[:8]:
        if delta.total_seconds() < 20:
            continue
        add(f"- {delta} after `{after or 'model turn'}` (until {until.strftime('%H:%M:%S')})")
    add("")

    return "\n".join(lines)


# --------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="list subagent transcripts on disk")
    group.add_argument("--name", help="agent name passed to the Agent tool")
    group.add_argument("--path", help="explicit path to an agent-*.jsonl")
    args = ap.parse_args()

    if args.list:
        for jsonl, meta in find_transcripts()[:40]:
            mtime = datetime.fromtimestamp(jsonl.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            name = meta.get("name") or meta.get("agentType") or "(unnamed)"
            model = meta.get("model", "?")
            print(f"{mtime}  {name:<32} {model:<8} {jsonl}")
        return

    path = Path(args.path) if args.path else resolve_by_name(args.name)
    if not path.exists():
        sys.exit(f"Not found: {path}")
    print(summarize(path))


if __name__ == "__main__":
    main()
