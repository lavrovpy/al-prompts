"""Block until a scene has a new, settled @claude note, then print the notes and exit.

    python3 -I watch.py <sceneId>

Exit 0: notes ready (JSON on stdout). Exit 2: five API failures in a row.
Exit 3: the 110-minute limit, under the 2-hour cap on background commands.
A note is ready once its text has not changed for SETTLE seconds, because
Excalidraw saves while the user types. Notes already answered are listed in
the scene's handled.json (written by reply.mjs) and are skipped until edited.
The match is exact on "@claude" (case-insensitive); a typo does not fire.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCENE = sys.argv[1]
CACHE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "whiteboard" / SCENE
HANDLED = CACHE / "handled.json"
INTERVAL, SETTLE, LIMIT = 20, 25, 110 * 60
CLI = ["npx", "-y", "@excalidraw/cli@0.3.0"]


def fetch() -> dict:
    out = subprocess.run([*CLI, "scenes", "content", "get", SCENE], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip()[:300])
    return json.loads(out.stdout)


def mentions(scene: dict) -> dict[str, dict]:
    return {
        e["id"]: e
        for e in scene["elements"]
        if not e.get("isDeleted")
        and e.get("type") == "text"
        and (e.get("customData") or {}).get("owner") != "claude"
        and "@claude" in (e.get("text") or "").lower()
    }


start, errors = time.time(), 0
seen: dict[tuple[str, int], float] = {}
while time.time() - start < LIMIT:
    try:
        scene = fetch()
        errors = 0
    except Exception as exc:
        errors += 1
        print(f"fetch failed ({errors}): {exc}", file=sys.stderr)
        if errors >= 5:
            sys.exit(2)
        time.sleep(INTERVAL)
        continue

    handled = json.loads(HANDLED.read_text()) if HANDLED.exists() else {}
    now, ready = time.time(), []
    for eid, e in mentions(scene).items():
        if handled.get(eid) == e["version"]:
            continue
        if now - seen.setdefault((eid, e["version"]), now) >= SETTLE:
            ready.append({"id": eid, "version": e["version"], "text": e["text"], "containerId": e.get("containerId")})
    if ready:
        print(json.dumps({"scene": SCENE, "notes": ready}, ensure_ascii=False))
        sys.exit(0)
    time.sleep(INTERVAL)

sys.exit(3)
