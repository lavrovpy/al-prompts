"""Cursor IDE agent: tool-call bubbles in User/globalStorage/state.vscdb (table cursorDiskKV).

Each tool call is one `bubbleId:<composerId>:<bubbleId>` row whose JSON carries `toolFormerData`
(name, params, status, toolCallId) and the call's own `startedAtMs` / `completedAtMs` (exact).
"""
import json
import os

from common import each_source, guess_kind, json_object, project_name, query_ro, record

NAME = "cursor"
AGENT = "Cursor"
KINDS = {"run_terminal_command_v2": "shell", "run_terminal_cmd": "shell", "read_file_v2": "read", "read_file": "read",
         "read_lints": "read", "edit_file_v2": "edit", "edit_file": "edit", "search_replace": "edit", "write": "edit",
         "delete_file": "edit", "ripgrep_raw_search": "search", "grep_search": "search", "glob_file_search": "search",
         "list_dir": "search", "codebase_search": "search", "web_search": "web", "await": "wait",
         "ask_question": "ask_user", "task_v2": "subagent", "todo_write": "other", "update_current_step": "other",
         "get_mcp_tools": "other", "search_conversations": "other", "set_active_branch": "other"}
# Cursor's user-data folder on macOS, Linux and Windows (%APPDATA% is normally AppData/Roaming).
DATA_DIRS = [("Library", "Application Support", "Cursor"), (".config", "Cursor"), ("AppData", "Roaming", "Cursor")]


def _dbs(ctx):
    paths = [ctx.path(*d, "User", "globalStorage", "state.vscdb") for d in DATA_DIRS]
    return [p for p in paths if os.path.exists(p)]


def detect(ctx):
    return _dbs(ctx)


def records(ctx):
    return each_source(NAME, _dbs(ctx), lambda path: _database(ctx, path))


def _database(ctx, path):
    rows = query_ro(
        path,
        "select key, value from cursorDiskKV where key like 'bubbleId:%' and json_valid(value) "
        "and json_extract(value, '$.toolFormerData.name') is not null "
        "and json_extract(value, '$.startedAtMs') >= ? and json_extract(value, '$.completedAtMs') is not null",
        (int(ctx.since),))
    for key, value in rows:
        yield from _call(ctx, path, key, json.loads(value))


def _mcp(params):
    """(server, tool) of an MCP call from `params.tools[0]`, or (None, None).

    The call's own name cannot be split: Cursor has written it as `mcp-<server>-<tool>`,
    `mcp_<server>_<tool>`, `mcp-<server>-<server>-<tool>`, `mcp--` and plain `mcp`, and server and tool
    names contain both `-` and `_`. `tools[0].name` sometimes carries a `<server>-` prefix.
    """
    tools = params.get("tools")
    first = tools[0] if isinstance(tools, list) and tools and isinstance(tools[0], dict) else {}
    server, tool = first.get("serverName"), first.get("name")
    if not (isinstance(server, str) and server and isinstance(tool, str) and tool):
        return None, None
    return server, tool[len(server) + 1:] if tool.startswith(server + "-") else tool


def _call(ctx, path, key, b):
    t = b["toolFormerData"]
    extra = t.get("additionalData") if isinstance(t.get("additionalData"), dict) else {}
    params = json_object(t.get("params"))
    name = t.get("name") or "?"
    server, tool = _mcp(params)
    kind = "mcp" if server else KINDS.get(name) or guess_kind(name)
    paths = (params.get("requestedSandboxPolicy") or {}).get("additionalReadwritePaths") or []
    cwd = params.get("cwd") or (paths[0] if paths else "")
    if ctx.excluded(cwd):
        return
    fields = dict(agent=AGENT, harness="Cursor", session=key.split(":")[1], id=t.get("toolCallId") or b.get("bubbleId"),
                  ts=b["startedAtMs"], dur_ms=max(0, b["completedAtMs"] - b["startedAtMs"]), tool=name, kind=kind,
                  error=t.get("status") not in ("completed", None) or extra.get("status") == "error",
                  # Cursor adds reviewData when the call stopped for the user's review (an edit
                  # outside the workspace, a command that needs approval).
                  human_wait="reviewData" in extra, timing="exact", project=project_name(cwd),
                  src=f"{path}:{key}", _cwd=cwd)
    if kind == "shell":
        fields["command"] = params.get("command") or ""
    elif kind == "mcp":
        fields.update(mcp_server=server, mcp_tool=tool)
    if extra.get("blockReason"):
        fields["approval"] = str(extra["blockReason"])
    yield record(**fields)
