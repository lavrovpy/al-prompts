"""Antigravity (IDE and CLI): one SQLite file per conversation under
~/.gemini/antigravity/conversations/ and ~/.gemini/antigravity-cli/conversations/.

Each row of `steps` holds a protobuf `metadata` blob with no published schema. The field numbers
below were read from real rows on 2026-10-21 and can shift between releases. A step whose fields
no longer have the expected wire types is skipped and counted on stderr: re-read the layout then,
and when the validator warns.
"""
import glob
import os
import sys

from common import each_source, guess_kind, json_object, mcp_names, project_name, query_ro, record

NAME = "antigravity"
AGENT = "Antigravity"
ROOTS = {"antigravity": "Antigravity", "antigravity-cli": "Antigravity CLI"}
KINDS = {"run_command": "shell", "command_status": "wait", "send_command_input": "shell", "view_file": "read",
         "view_file_outline": "read", "view_code_item": "read", "grep_search": "search", "find_by_name": "search",
         "list_dir": "search", "codebase_search": "search", "write_to_file": "edit", "replace_file_content": "edit",
         "multi_replace_file_content": "edit", "read_url_content": "web", "search_web": "web",
         "browser_subagent": "subagent"}

# Step metadata. A step without CALL is a model or user turn.
CALL, STARTED, COMPLETED, STATUS_HISTORY = 4, 6, 8, 26
# Inside CALL.
CALL_ID, TOOL_NAME, ARGUMENTS = 1, 2, 3
# Inside STATUS_HISTORY: repeated CHANGE entries, each with its status (and a Timestamp in field 2).
CHANGE, CHANGE_STATUS = 1, 1
# Inside a Timestamp (STARTED, COMPLETED).
SECONDS, NANOS = 1, 2
# Step statuses, in the `status` column and in STATUS_HISTORY.
DONE = 3                # any other final status, such as 4 (failed), is an error
AWAITING_APPROVAL = 9   # a step that passed through it stopped for the user's approval


def _varint(b, i):
    result = shift = 0
    while b[i] & 0x80:
        result |= (b[i] & 0x7F) << shift
        shift += 7
        i += 1
    return result | b[i] << shift, i + 1


def _fields(b):
    """Top-level protobuf fields as {number: [value, ...]}; length-delimited values stay bytes."""
    if not isinstance(b, bytes):
        raise ValueError(f"expected a protobuf message, got {type(b).__name__}")
    out, i = {}, 0
    while i < len(b):
        key, i = _varint(b, i)
        num, wire = key >> 3, key & 7
        if wire == 0:
            value, i = _varint(b, i)
        elif wire == 2:
            n, i = _varint(b, i)
            value, i = b[i:i + n], i + n
        elif wire == 1:
            value, i = b[i:i + 8], i + 8
        elif wire == 5:
            value, i = b[i:i + 4], i + 4
        else:
            raise ValueError(f"wire type {wire}")
        out.setdefault(num, []).append(value)
    return out


def _field(fields, num, typ, default=None):
    """The first value of field `num`, or `default` when absent. Raises ValueError when the value
    is not of `typ`, which is how a changed wire type shows."""
    value = fields[num][0] if num in fields else default
    if not isinstance(value, typ):
        raise ValueError(f"field {num} is {type(value).__name__}, expected {typ.__name__}")
    return value


def _ms(timestamp):
    f = _fields(timestamp)
    return _field(f, SECONDS, int, 0) * 1000 + _field(f, NANOS, int, 0) // 1_000_000


def _step(meta):
    """(call id, tool name, arguments, start, end, waited for approval) of a tool-call step, or None
    for any other step. Raises ValueError or IndexError when the blob does not match the layout."""
    m = _fields(meta)
    if CALL not in m or STARTED not in m or COMPLETED not in m:
        return None
    call = _fields(_field(m, CALL, bytes))
    history = _fields(_field(m, STATUS_HISTORY, bytes, b""))
    statuses = {_field(_fields(change), CHANGE_STATUS, int, 0) for change in history.get(CHANGE, [])}
    return (_field(call, CALL_ID, bytes, b"").decode(errors="replace"),
            _field(call, TOOL_NAME, bytes, b"?").decode(errors="replace"),
            json_object(_field(call, ARGUMENTS, bytes, b"{}")),
            _ms(_field(m, STARTED, bytes)), _ms(_field(m, COMPLETED, bytes)),
            AWAITING_APPROVAL in statuses)


def _dbs(ctx):
    found = []
    for root in ROOTS:
        found += glob.glob(ctx.path(".gemini", root, "conversations", "*.db"))
    return [p for p in found if os.path.getmtime(p) * 1000 >= ctx.since]


def detect(ctx):
    return _dbs(ctx)


def records(ctx):
    return each_source(NAME, _dbs(ctx), lambda path: _conversation(ctx, path))


def _conversation(ctx, path):
    harness = ROOTS[os.path.basename(os.path.dirname(os.path.dirname(path)))]
    session = os.path.splitext(os.path.basename(path))[0]
    skipped = 0
    for idx, status, meta in query_ro(path, "select idx, status, metadata from steps where metadata is not null"):
        try:
            step = _step(meta)
        except (ValueError, IndexError):
            skipped += 1
            continue
        if step is None:
            continue
        call_id, name, args, start, end, waited = step
        if start < ctx.since:
            continue
        kind = KINDS.get(name) or guess_kind(name)
        cwd = str(args.get("Cwd") or args.get("cwd") or "")
        if ctx.excluded(cwd):
            continue
        fields = dict(agent=AGENT, harness=harness, session=session, id=call_id or f"{session}:{idx}", ts=start,
                      dur_ms=max(0, end - start), tool=name, kind=kind, error=status != DONE, human_wait=waited,
                      timing="exact", project=project_name(cwd), src=f"{path}:steps.idx={idx}", _cwd=cwd)
        if kind == "shell":
            fields["command"] = str(args.get("CommandLine") or args.get("command") or "")
        elif kind == "mcp":
            # Steps hold no server field, so mcp_names() leaves both unset for a name it cannot split.
            fields["mcp_server"], fields["mcp_tool"] = mcp_names(name)
        yield record(**fields)
    if skipped:
        print(f"{NAME}: {path}: skipped {skipped} steps that no longer match the field layout in "
              f"adapters/antigravity.py", file=sys.stderr)
