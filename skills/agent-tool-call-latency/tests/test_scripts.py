"""Run: python3 -m unittest discover -s skills/agent-tool-call-latency/tests"""
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS)

import aggregate  # noqa: E402
import extract  # noqa: E402
from common import Context, first_cmd, guess_kind, iso_ms, mcp_names, redact, since_ms  # noqa: E402

T0 = "2026-10-01T10:00:00.000Z"


def iso(seconds):
    return f"2026-10-01T10:{int(seconds) // 60:02d}:{seconds % 60:06.3f}Z"


def read_jsonl(path):
    with open(path) as fh:
        return [json.loads(line) for line in fh]


def read_text(path):
    with open(path) as fh:
        return fh.read()


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def claude_rows(cwd="/home/u/proj", session="s-claude"):
    meta = dict(sessionId=session, cwd=cwd, entrypoint="cli", version="2.1.300")
    return [
        # Two parallel calls in one message: the message's second block streams 2 s after the first.
        dict(meta, type="assistant", timestamp=iso(0), permissionMode="auto",
             message=dict(id="m1", content=[dict(type="tool_use", id="tu1", name="Bash", input=dict(command="pnpm e2e"))])),
        dict(meta, type="assistant", timestamp=iso(2),
             message=dict(id="m1", content=[dict(type="tool_use", id="tu2", name="Read", input=dict(file_path="a"))])),
        dict(meta, type="user", timestamp=iso(2.05), message=dict(content=[dict(type="tool_result", tool_use_id="tu2")])),
        dict(meta, type="user", timestamp=iso(12), permissionDecision=dict(reasonType="classifier", source="config"),
             message=dict(content=[dict(type="tool_result", tool_use_id="tu1", is_error=False)])),
        dict(meta, type="assistant", timestamp=iso(13),
             message=dict(id="m2", content=[dict(type="tool_use", id="tu3", name="mcp__playwright__browser_click", input={})])),
        dict(meta, type="user", timestamp=iso(14), message=dict(content=[dict(type="tool_result", tool_use_id="tu3")])),
    ]


def codex_rows(originator="Codex Desktop"):
    return [
        dict(timestamp=T0, type="session_meta", payload=dict(type="session_meta", id="s-codex", cwd="/home/u/proj",
                                                             originator=originator, source="cli")),
        dict(timestamp=T0, type="event_msg", payload=dict(type="item_completed", started_at_ms=1790000000000,
                                                          completed_at_ms=1790000004000,
                                                          item=dict(type="CommandExecution", id="c1", exit_code=1,
                                                                    command=["/bin/zsh", "-lc", "pytest -q"]))),
        dict(timestamp=iso(5), type="response_item", payload=dict(type="function_call", call_id="f1", name="wait_agent")),
        dict(timestamp=iso(35), type="response_item", payload=dict(type="function_call_output", call_id="f1")),
    ]


class Helpers(unittest.TestCase):
    def test_first_cmd_skips_prefixes_wrappers_and_value_flags(self):
        self.assertEqual(first_cmd("cd /x && FOO=1 timeout 60 pnpm --filter app e2e"), "pnpm e2e")
        self.assertEqual(first_cmd("lockf -t 600 /tmp/x.lock pnpm test"), "pnpm test")
        self.assertEqual(first_cmd("python3 - <<'EOF'"), "python3 <inline>")

    def test_redact_masks_tokens_and_keeps_the_command(self):
        out = redact("GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuv gh pr list")
        self.assertNotIn("ghp_", out)
        self.assertIn("gh pr list", out)

    def test_redact_masks_a_password_inside_a_url(self):
        out = redact("DB=postgresql://app:s3cret@localhost:5432/db psql; git clone https://github.com/a/b")
        self.assertNotIn("s3cret", out)
        self.assertIn("postgresql://app:[REDACTED]@localhost", out)
        self.assertIn("https://github.com/a/b", out)

    def test_redact_masks_the_whole_password_in_a_url(self):
        for cmd, expected in [("mysql://root:p@ssw0rd@host", "mysql://root:[REDACTED]@host"),
                              ("HTTPS://u:pw@host", "HTTPS://u:[REDACTED]@host"),
                              ("redis://:pw@host", "redis://:[REDACTED]@host"),
                              ("mysql://root:pa/ss@db", "mysql://root:[REDACTED]@db"),
                              ("curl https://u:pw@host/users/@me", "curl https://u:[REDACTED]@host/users/@me")]:
            self.assertEqual(redact(cmd), expected)

    def test_redact_leaves_urls_without_a_password(self):
        for cmd in ("curl http://localhost:3000?email=a@b.com", "curl http://localhost:3000/users/@me",
                    "npm view https://registry.npmjs.org/@types/node", "git clone ssh://git@host:22/repo"):
            self.assertEqual(redact(cmd), cmd)

    def test_mcp_names_split_only_unambiguous_spellings(self):
        self.assertEqual(mcp_names("mcp__claude_ai_Notion__notion-search"), ("claude_ai_Notion", "notion-search"))
        self.assertEqual(mcp_names("mcp:github.get_pr"), ("github", "get_pr"))
        for name in ("mcp_claude_ai_Notion_search", "mcp-context7-resolve-library-id"):
            self.assertEqual(mcp_names(name), (None, None))

    def test_redact_masks_other_common_secret_shapes(self):
        # Assembled at run time: a literal token here trips the forge's secret scanning on push.
        fake = "abcdefghijklmnopqrstuvwxyz0123456789"
        secrets = {"github_pat_" + fake: "git push", "sk_" + "live_" + fake: "stripe", "npm_" + fake: "npm publish",
                   "AIza" + fake: "curl", "hf_" + fake: "huggingface-cli"}
        for token, rest in secrets.items():
            self.assertNotIn(token, redact(f"{rest} {token}"))
        for cmd, secret in [("curl -H 'Authorization: token abc123def' x", "abc123def"),
                            ("curl -H 'X-Api-Key: k3y-value' x", "k3y-value"),
                            ("psql --password hunter2 db", "hunter2"),
                            ("mysql -u root -phunter2 db", "hunter2"),
                            ("curl -u admin:hunter2 https://x", "hunter2"),
                            ("OPENAI_KEY=abc123 node app.js", "abc123")]:
            out = redact(cmd)
            self.assertNotIn(secret, out, cmd)
        self.assertEqual(redact("pnpm --filter app test"), "pnpm --filter app test")

    def test_iso_ms_accepts_any_fraction_and_rejects_garbage(self):
        self.assertEqual(iso_ms("2026-10-01T10:00:00.5Z"), iso_ms("2026-10-01T10:00:00.500Z"))
        self.assertEqual(iso_ms("2026-10-01T10:00:00.1234567Z"), iso_ms("2026-10-01T10:00:00.123456Z"))
        self.assertIsNone(iso_ms("yesterday"))
        self.assertIsNone(iso_ms(None))

    def test_guess_kind(self):
        self.assertEqual(guess_kind("run_terminal_command"), "shell")
        self.assertEqual(guess_kind("str_replace_editor"), "edit")
        self.assertEqual(guess_kind("mcp__github__get_pr"), "mcp")
        self.assertEqual(guess_kind("mcp-context7-resolve-library-id"), "mcp")


class Adapters(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.ctx = Context(self.home, since_ms("2026-09-01"))

    def extract_path(self, *extra, env=None):
        out = os.path.join(self.home, "work", "calls.jsonl")
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "extract.py"), "--home", self.home, "--since",
                        "2026-09-01", "--out", out, *extra], check=True, capture_output=True,
                       env=env or dict(os.environ, AGENT_LATENCY_HOOK_LOG=os.path.join(self.home, "no-hooks.jsonl")))
        return out

    def extract(self, *extra):
        return {c["id"]: c for c in read_jsonl(self.extract_path(*extra))}

    def test_claude_times_parallel_calls_from_the_end_of_their_message(self):
        write_jsonl(os.path.join(self.home, ".claude/projects/p/s.jsonl"), claude_rows())
        calls = self.extract()
        self.assertEqual(calls["tu1"]["dur_ms"], 10_000)  # from the message's last block, not its own
        self.assertEqual(calls["tu2"]["dur_ms"], 50)  # returned mid-stream, so its own block is the start
        self.assertEqual(calls["tu1"]["kind"], "shell")
        self.assertEqual(calls["tu1"]["approval"], "classifier")
        self.assertEqual(calls["tu1"]["mode"], "auto")
        self.assertEqual(calls["tu3"]["mcp_server"], "playwright")
        self.assertNotIn("_cwd", calls["tu1"])

    def test_codex_items_function_calls_and_kinds(self):
        write_jsonl(os.path.join(self.home, ".codex/sessions/2026/10/01/r.jsonl"), codex_rows())
        calls = self.extract()
        self.assertEqual(calls["c1"]["dur_ms"], 4000)
        self.assertEqual(calls["c1"]["command"], "pytest -q")
        self.assertTrue(calls["c1"]["error"])
        self.assertEqual(calls["c1"]["timing"], "exact")
        self.assertEqual(calls["f1"]["kind"], "wait")
        self.assertEqual(calls["f1"]["dur_ms"], 30_000)

    def test_t3_claims_relabel_and_dedupe_copied_history(self):
        rows = claude_rows(cwd="/home/u/.t3/worktrees/proj/x")
        write_jsonl(os.path.join(self.home, ".claude/projects/p/s.jsonl"), rows)
        write_jsonl(os.path.join(self.home, ".claude/projects/p/s-resumed.jsonl"), rows)
        os.makedirs(os.path.join(self.home, ".t3/userdata"))
        sqlite3.connect(os.path.join(self.home, ".t3/userdata/statev2.sqlite")).close()
        calls = self.extract()
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls["tu1"]["harness"], "T3 Code → Claude Code")

    def test_codex_review_session_with_a_string_subagent_source(self):
        rows = codex_rows()
        rows[0]["payload"]["source"] = {"subagent": "review"}
        write_jsonl(os.path.join(self.home, ".codex/sessions/2026/10/01/r.jsonl"), rows)
        self.assertEqual(self.extract()["c1"]["subagent"], True)

    def test_codex_item_and_function_call_for_one_call_count_once(self):
        rows = codex_rows()
        rows.append(dict(timestamp=T0, type="event_msg", payload=dict(
            type="item_completed", started_at_ms=1790000005000, completed_at_ms=1790000035000,
            item=dict(type="CollabAgentToolCall", id="f1", tool="wait_agent"))))
        write_jsonl(os.path.join(self.home, ".codex/sessions/2026/10/01/r.jsonl"), rows)
        calls = read_jsonl(self.extract_path())
        self.assertEqual([c["timing"] for c in calls if c["id"] == "f1"], ["exact"])

    def test_a_hook_log_and_a_transcript_of_one_call_count_once(self):
        write_jsonl(os.path.join(self.home, ".claude/projects/p/s.jsonl"), claude_rows())
        log = os.path.join(self.home, "hooks.jsonl")
        write_jsonl(log, [dict(t=1790000000000, event="pre", agent="Claude Code", session="s-claude", id="tu1", tool="Bash"),
                          dict(t=1790000009990, event="post", agent="Claude Code", session="s-claude", id="tu1", tool="Bash")])
        calls = read_jsonl(self.extract_path(env=dict(os.environ, AGENT_LATENCY_HOOK_LOG=log)))
        self.assertEqual([c["timing"] for c in calls if c["id"] == "tu1"], ["exact"])

    def test_a_failing_adapter_is_reported_and_the_rest_still_written(self):
        write_jsonl(os.path.join(self.home, ".claude/projects/p/s.jsonl"), claude_rows())
        broken = os.path.join(self.home, "broken.py")
        with open(broken, "w") as fh:
            fh.write("NAME = 'broken'\ndef detect(ctx):\n    return []\ndef records(ctx):\n    raise OSError('no table')\n")
        out = os.path.join(self.home, "calls.jsonl")
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "extract.py"), "--home", self.home, "--since",
                                 "2026-09-01", "--out", out, "--adapter", broken], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("broken         FAILED", result.stderr)
        self.assertEqual(len(read_jsonl(out)), 3)

    def test_one_corrupt_session_file_costs_only_its_own_calls(self):
        write_jsonl(os.path.join(self.home, ".claude/projects/p/s.jsonl"), claude_rows())
        bad = claude_rows(session="s-bad")
        bad[0]["message"]["content"][0]["input"] = "not a dict"
        bad[0]["message"]["content"][0]["name"] = None
        write_jsonl(os.path.join(self.home, ".claude/projects/p/bad.jsonl"), bad[:1] + [
            dict(bad[3], timestamp="garbage")])
        self.assertIn("tu1", self.extract())

    def test_t3_path_claim_leaves_other_agents_alone(self):
        calls = [dict(agent="Cursor", harness="Cursor", session="c", id="1", _cwd="/u/.t3/worktrees/p")]
        extract.apply_claims(calls, [dict(frontend="T3 Code", cwd="/.t3/worktrees/", agents=("Claude Code", "Codex"))])
        self.assertEqual(calls[0]["harness"], "Cursor")

    def test_codex_originator_names_the_frontend(self):
        write_jsonl(os.path.join(self.home, ".codex/sessions/2026/10/01/r.jsonl"), codex_rows("T3 Code"))
        self.assertEqual(self.extract()["c1"]["harness"], "T3 Code → Codex")

    def test_exclude_cwd_drops_benchmark_sessions_and_include_cwd_keeps_only_them(self):
        write_jsonl(os.path.join(self.home, ".claude/projects/p/s.jsonl"), claude_rows(cwd="/tmp/bench-runs/a"))
        write_jsonl(os.path.join(self.home, ".claude/projects/q/s.jsonl"), claude_rows(cwd="/home/u/proj", session="s2"))
        self.assertEqual({c["session"] for c in self.extract("--exclude-cwd", "/bench-runs/").values()}, {"s2"})
        self.assertEqual({c["session"] for c in self.extract("--include-cwd", "/bench-runs/").values()}, {"s-claude"})

    def test_extra_adapter_file_is_loaded(self):
        path = os.path.join(self.home, "my_harness.py")
        with open(path, "w") as fh:
            fh.write("from common import record\nNAME = 'mine'\n"
                     "def detect(ctx):\n    return ['x']\n"
                     "def records(ctx):\n    yield record(agent='Mine', harness='Mine', session='s', id='1',"
                     " ts=1790000000000, dur_ms=5, tool='run', kind='shell', command='ls')\n")
        self.assertEqual(self.extract("--adapter", path, "--only", "mine")["1"]["agent"], "Mine")

    def test_hook_capture_pairs_pre_and_post(self):
        log = os.path.join(self.home, "hooks.jsonl")
        env = dict(os.environ, AGENT_LATENCY_HOOK_LOG=log)
        for event in ("pre", "post"):
            payload = json.dumps(dict(session_id="s", tool_name="Bash", tool_use_id="h1", tool_input=dict(command="ls")))
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "hook_capture.py"), event, "--agent", "X"],
                           input=payload, text=True, env=env, check=True)
        out = os.path.join(self.home, "calls.jsonl")
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "extract.py"), "--home", self.home, "--since",
                        "2026-01-01", "--only", "hooklog", "--out", out], check=True, env=env, capture_output=True)
        (call,) = read_jsonl(out)
        self.assertEqual((call["id"], call["kind"], call["command"], call["timing"]), ("h1", "shell", "ls", "exact"))

    def test_hook_capture_reads_a_nested_error_and_names_the_mcp_server(self):
        log = os.path.join(self.home, "hooks.jsonl")
        env = dict(os.environ, AGENT_LATENCY_HOOK_LOG=log)
        for event, extra in (("pre", {}), ("post", dict(tool_response=dict(is_error=True)))):
            payload = json.dumps(dict(session_id="s", tool_name="mcp__playwright__browser_click", tool_use_id="h2",
                                      cwd="/tmp/agent-latency-bench/x", **extra))
            subprocess.run([sys.executable, os.path.join(SCRIPTS, "hook_capture.py"), event, "--agent", "X"],
                           input=payload, text=True, env=env, check=True)
        out = os.path.join(self.home, "calls.jsonl")
        args = [sys.executable, os.path.join(SCRIPTS, "extract.py"), "--home", self.home, "--since", "2026-01-01",
                "--only", "hooklog", "--out", out]
        subprocess.run(args, check=True, env=env, capture_output=True)
        (call,) = read_jsonl(out)
        self.assertEqual((call["mcp_server"], call["mcp_tool"], call["error"]), ("playwright", "browser_click", True))
        subprocess.run(args + ["--exclude-cwd", "/agent-latency-bench/"], check=True, env=env, capture_output=True)
        self.assertEqual(read_jsonl(out), [])

    def test_hook_capture_never_fails_the_tool(self):
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "hook_capture.py"), "pre"], input="not json",
                                text=True, capture_output=True,
                                env=dict(os.environ, AGENT_LATENCY_HOOK_LOG="/nonexistent/dir/x.jsonl"))
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_validator_rejects_bad_records(self):
        path = os.path.join(self.home, "calls.jsonl")
        write_jsonl(path, [dict(agent="a", harness="h", session="s", id="1", ts=1790000000000, dur_ms=-1,
                                tool="t", kind="nope")])
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "validate_calls.py"), path],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("negative dur_ms", result.stdout)
        self.assertIn("kind 'nope'", result.stdout)


def pb_varint(n):
    out = b""
    while n > 0x7F:
        out += bytes([n & 0x7F | 0x80])
        n >>= 7
    return out + bytes([n])


def pb(num, value):
    """One protobuf field: an int becomes a varint, bytes or str a length-delimited value."""
    if isinstance(value, int):
        return pb_varint(num << 3) + pb_varint(value)
    value = value.encode() if isinstance(value, str) else value
    return pb_varint(num << 3 | 2) + pb_varint(len(value)) + value


def pb_time(ms):
    return pb(1, ms // 1000) + pb(2, ms % 1000 * 1_000_000)


START_MS = 1790000000000


def cursor_db(home, data_dir, bubbles):
    """A Cursor state.vscdb under `data_dir`; bubbles=None leaves out the cursorDiskKV table."""
    path = os.path.join(home, data_dir, "User/globalStorage/state.vscdb")
    os.makedirs(os.path.dirname(path))
    db = sqlite3.connect(path)
    if bubbles is None:
        db.execute("create table ItemTable (key text unique on conflict replace, value blob)")
    else:
        db.execute("create table cursorDiskKV (key text unique on conflict replace, value blob)")
        for key, value in bubbles:
            db.execute("insert into cursorDiskKV values (?, ?)", (key, json.dumps(value)))
    db.commit()
    db.close()


def cursor_bubble(call_id, name, params, duration=1000):
    return dict(startedAtMs=START_MS, completedAtMs=START_MS + duration, toolFormerData=dict(
        name=name, toolCallId=call_id, status="completed", params=json.dumps(params)))


def ag_step(call_id, name, args, end, statuses):
    history = b"".join(pb(1, pb(1, st) + pb(2, pb_time(t))) for st, t in statuses)
    return (pb(1, pb_time(START_MS)) + pb(4, pb(1, call_id) + pb(2, name) + pb(3, json.dumps(args)))
            + pb(6, pb_time(START_MS)) + pb(8, pb_time(end)) + pb(26, history))


def antigravity_db(home, steps):
    """An Antigravity conversation file of (status, metadata) steps; steps=None leaves out the table."""
    path = os.path.join(home, ".gemini/antigravity/conversations/conv-1.db")
    os.makedirs(os.path.dirname(path))
    db = sqlite3.connect(path)
    if steps is None:
        db.execute("create table trajectory (id integer primary key)")
    else:
        db.execute("create table steps (idx integer primary key, step_type integer, status integer, metadata blob)")
        for i, (status, meta) in enumerate(steps, 1):
            db.execute("insert into steps values (?, 132, ?, ?)", (i, status, meta))
    db.commit()
    db.close()


class GuiHarnessAdapters(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()

    def run_extract(self, *extra):
        out = os.path.join(self.home, "calls.jsonl")
        result = subprocess.run([sys.executable, os.path.join(SCRIPTS, "extract.py"), "--home", self.home, "--since",
                                 "2026-09-01", "--out", out, *extra], capture_output=True, text=True,
                                env=dict(os.environ, AGENT_LATENCY_HOOK_LOG=os.path.join(self.home, "no-hooks.jsonl")))
        return result, {c["id"]: c for c in read_jsonl(out)} if os.path.exists(out) else {}

    def extract(self, only, *extra):
        result, calls = self.run_extract("--only", only, *extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        return calls

    def test_cursor_reads_tool_bubbles_and_review_waits(self):
        shell = dict(startedAtMs=START_MS, completedAtMs=START_MS + 3500, toolFormerData=dict(
            name="run_terminal_command_v2", toolCallId="toolu_1", status="completed",
            params=json.dumps(dict(command="pnpm test", requestedSandboxPolicy=dict(additionalReadwritePaths=["/w/app"]))),
            additionalData=dict(status="success")))
        edit = dict(startedAtMs=START_MS + 10_000, completedAtMs=START_MS + 130_000, toolFormerData=dict(
            name="edit_file_v2", toolCallId="toolu_2", status="completed", params="{}",
            additionalData=dict(blockReason="outOfWorkspace", reviewData=dict(selectedOption="accept"))))
        cursor_db(self.home, "Library/Application Support/Cursor",
                  [("bubbleId:c1:b1", shell), ("bubbleId:c1:b1/t:toolu_1", shell), ("bubbleId:c1:b2", edit)])
        calls = self.extract("cursor")
        self.assertEqual(len(calls), 2)
        self.assertEqual((calls["toolu_1"]["kind"], calls["toolu_1"]["dur_ms"], calls["toolu_1"]["project"]),
                         ("shell", 3500, "app"))
        self.assertTrue(calls["toolu_2"]["human_wait"])
        self.assertEqual(calls["toolu_2"]["approval"], "outOfWorkspace")
        self.assertEqual(set(self.extract("cursor", "--exclude-cwd", "/w/app")), {"toolu_2"})
        self.assertEqual(set(self.extract("cursor", "--include-cwd", "/w/app")), {"toolu_1"})

    def test_cursor_takes_mcp_server_and_tool_from_params_on_linux_and_windows(self):
        cursor_db(self.home, ".config/Cursor", [
            ("bubbleId:c1:b1", cursor_bubble("m1", "mcp-context7-resolve-library-id",
                                             dict(tools=[dict(serverName="context7", name="resolve-library-id")]))),
            ("bubbleId:c1:b2", cursor_bubble("m2", "mcp--", dict(tools=[dict(serverName="user-gitlab",
                                                                               name="user-gitlab-create_issue")]))),
            ("bubbleId:c1:b3", cursor_bubble("m3", "mcp_cursor-browser-extension_browser_click", {}))])
        cursor_db(self.home, "AppData/Roaming/Cursor", [("bubbleId:c2:b1", cursor_bubble("w1", "read_file_v2", {}))])
        calls = self.extract("cursor")
        self.assertEqual(set(calls), {"m1", "m2", "m3", "w1"})
        named = {i: (calls[i]["kind"], calls[i].get("mcp_server"), calls[i].get("mcp_tool")) for i in ("m1", "m2", "m3")}
        self.assertEqual(named, {"m1": ("mcp", "context7", "resolve-library-id"),
                                 "m2": ("mcp", "user-gitlab", "create_issue"),
                                 "m3": ("mcp", None, None)})

    def test_antigravity_decodes_steps_and_flags_approval_waits(self):
        antigravity_db(self.home, [
            (3, ag_step("call_1", "run_command", dict(CommandLine="find . -maxdepth 1", Cwd="/w/app"),
                        START_MS + 300_000, [(1, START_MS), (9, START_MS + 100), (3, START_MS + 300_000)])),
            (3, ag_step("call_2", "view_file", {}, START_MS + 20, [(1, START_MS), (3, START_MS + 20)])),
            (3, pb(1, pb_time(START_MS)))])  # a model turn, no tool call
        calls = self.extract("antigravity")
        self.assertEqual(set(calls), {"call_1", "call_2"})
        self.assertEqual((calls["call_1"]["kind"], calls["call_1"]["dur_ms"], calls["call_1"]["command"]),
                         ("shell", 300_000, "find . -maxdepth 1"))
        self.assertTrue(calls["call_1"]["human_wait"])
        self.assertFalse(calls["call_2"].get("human_wait"))
        self.assertEqual(calls["call_2"]["kind"], "read")
        self.assertEqual(set(self.extract("antigravity", "--exclude-cwd", "/w/app")), {"call_2"})
        self.assertEqual(set(self.extract("antigravity", "--include-cwd", "/w/app")), {"call_1"})

    def test_antigravity_skips_steps_whose_wire_types_changed_and_counts_them(self):
        good = ag_step("call_1", "view_file", {}, START_MS + 20, [(3, START_MS + 20)])
        name_as_varint = pb(4, pb(1, "call_2") + pb(2, 7)) + pb(6, pb_time(START_MS)) + pb(8, pb_time(START_MS + 5))
        seconds_as_bytes = pb(4, pb(1, "call_3") + pb(2, "view_file")) + pb(6, pb(1, b"x")) + pb(8, pb_time(START_MS))
        antigravity_db(self.home, [(3, good), (3, name_as_varint), (3, seconds_as_bytes), (3, b"\xff")])
        result, calls = self.run_extract("--only", "antigravity")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(calls), {"call_1"})
        self.assertIn("skipped 3 steps", result.stderr)

    def test_antigravity_mcp_names_are_not_split_on_underscores(self):
        antigravity_db(self.home, [(3, ag_step("call_1", "mcp_claude_ai_Notion_search", {}, START_MS + 20, []))])
        call = self.extract("antigravity")["call_1"]
        self.assertEqual((call["kind"], call.get("mcp_server"), call.get("mcp_tool")), ("mcp", None, None))

    def test_a_database_without_its_table_is_skipped_and_the_run_goes_on(self):
        write_jsonl(os.path.join(self.home, ".claude/projects/p/s.jsonl"), claude_rows())
        cursor_db(self.home, "Library/Application Support/Cursor", None)
        antigravity_db(self.home, None)
        result, calls = self.run_extract()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(calls), {"tu1", "tu2", "tu3"})
        self.assertIn("cursor: skipped", result.stderr)
        self.assertIn("antigravity: skipped", result.stderr)


class Aggregate(unittest.TestCase):
    @staticmethod
    def calls(durations, start_step=60_000, **extra):
        return [dict(ts=1790000000000 + i * start_step, dur_ms=d, **extra) for i, d in enumerate(durations)]

    def test_find_caps_spots_a_timeout_cluster(self):
        self.assertEqual(aggregate.find_caps(self.calls([1000, 70_000, 600_100, 600_400, 601_000])), [(600_100, 3)])
        self.assertEqual(aggregate.find_caps(self.calls([70_000, 200_000, 600_000])), [])

    def test_find_caps_finds_a_default_cap_below_a_longer_one(self):
        durations = [120_000 + i * 50 for i in range(10)] + [300_000, 450_000, 600_000, 600_200, 600_500, 601_000]
        self.assertEqual([cap for cap, _ in aggregate.find_caps(self.calls(durations))], [120_000, 600_000])

    def test_find_caps_ignores_calls_that_end_together_and_user_waits(self):
        self.assertEqual(aggregate.find_caps(self.calls([268_000] * 4, start_step=0)), [])
        queued = [dict(ts=1790000000000 + i * 1000, dur_ms=1_300_000 - i * 1000) for i in range(5)]
        self.assertEqual(aggregate.find_caps(queued), [])
        self.assertEqual(aggregate.find_caps(self.calls([1_708_000] * 5, human_wait=True)), [])

    def test_find_caps_needs_a_spike_above_ordinary_work_of_that_length(self):
        ordinary = [d for d in range(96_000, 146_000, 500) if not 118_000 <= d <= 123_000]
        self.assertEqual(aggregate.find_caps(self.calls(ordinary + [120_000, 120_300, 121_000])), [])
        self.assertEqual([cap for cap, _ in aggregate.find_caps(self.calls(ordinary + [120_000 + i * 40 for i in range(30)]))],
                         [120_000])

    def test_percentiles_use_nearest_rank(self):
        self.assertEqual(aggregate.q(list(range(1, 11)), .9), 9)
        self.assertEqual(aggregate.q([1, 2], .5), 1)

    def test_release_table_compares_within_one_approval_path(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "calls.jsonl")
        rows = []
        for version, approval, dur in [("1.0", "mode", 10), ("1.1", "mode", 12), ("1.2", "mode", 11), ("1.3", "classifier", 800)]:
            rows += [dict(agent="A", harness="H", session="s", id=f"{version}-{i}", ts=1790000000000 + i, dur_ms=dur,
                          tool="Edit", kind="edit", version=version, approval=approval) for i in range(20)]
        write_jsonl(path, rows)
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "aggregate.py"), path, "--out-dir", d], check=True,
                       capture_output=True)
        summary = json.loads(read_text(os.path.join(d, "summary.json")))
        self.assertEqual([r for r in summary["fast_op_by_version"] if r.get("outlier")], [])

    def test_classify_puts_heavy_steps_before_setup(self):
        patterns = [(c, l, aggregate.re.compile(p)) for c, l, p in aggregate.SHELL_PATTERNS]
        call = dict(kind="shell", command="mkdir -p out && blender -b scene.blend")
        self.assertEqual(aggregate.classify(call, patterns), ("Render / 3D", "Blender headless"))
        self.assertEqual(aggregate.classify(dict(kind="shell", command="until curl -s x; do sleep 2; done"), patterns),
                         ("Wait / poll", "until loop"))

    def test_summary_end_to_end(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "calls.jsonl")
        rows = [dict(agent="A", harness="H", session="s", id=str(i), ts=1790000000000 + i * 700_000, dur_ms=600_000 + i,
                     tool="Bash", kind="shell", command="until x; do sleep 5; done") for i in range(4)]
        write_jsonl(path, rows)
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "aggregate.py"), path, "--out-dir", d], check=True,
                       capture_output=True)
        summary = json.loads(read_text(os.path.join(d, "summary.json")))
        self.assertEqual(summary["caps"][0]["n"], 4)
        self.assertIn("## Calls ending at a timeout cap", read_text(os.path.join(d, "summary.md")))


if __name__ == "__main__":
    unittest.main()
