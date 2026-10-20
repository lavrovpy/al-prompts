"""T3 Code: a frontend that drives Claude Code and Codex, so it adds no calls of its own.

It claims the backend calls it started, so they are labelled "T3 Code → <agent>" and counted once.
Codex records T3 as its originator; Claude sessions are matched from T3's provider event logs,
its turn-item projection, and its worktree paths.
"""
import glob
import os
import re
import sqlite3
import sys

NAME = "t3code"
FRONTEND = "T3 Code"
SESSION_RE = re.compile(r'"(?:sessionId|session_id)":"([0-9a-f-]{36})"')


def _root(ctx):
    return ctx.path(".t3", "userdata")


def detect(ctx):
    root = _root(ctx)
    return [p for p in [os.path.join(root, "statev2.sqlite")] + glob.glob(os.path.join(root, "logs", "provider", "events.*"))
            if os.path.exists(p)]


def records(ctx):
    return iter(())


def claims(ctx):
    root = _root(ctx)
    for f in glob.glob(os.path.join(root, "logs", "provider", "events.*")):
        with open(f, errors="ignore") as fh:
            for sid in set(SESSION_RE.findall(fh.read())):
                yield dict(frontend=FRONTEND, session=sid)
    db_path = os.path.join(root, "statev2.sqlite")
    if os.path.exists(db_path):
        db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            rows = db.execute("select json_extract(payload_json, '$.nativeItemRef.nativeId') "
                              "from orchestration_v2_projection_turn_items")
            for (native_id,) in rows:
                if native_id:
                    yield dict(frontend=FRONTEND, id=native_id)
        except sqlite3.Error as err:
            print(f"t3code: turn-item query failed ({err}); Claude calls fall back to session and path claims",
                  file=sys.stderr)
        finally:
            db.close()
    yield dict(frontend=FRONTEND, cwd="/.t3/worktrees/")
