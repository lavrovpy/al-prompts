---
name: whiteboard
description: Explain code, architecture or a planned change on an Excalidraw+ board (frames, flow diagrams, real code panels), and work on the board with the user. Use when the user asks to show or explain something on a board, whiteboard or Excalidraw, gives an app.excalidraw.com scene link, says "check the board", or wants @claude notes on a board answered or watched.
---

# Whiteboard

A **board** is an Excalidraw+ scene that you and the user both edit. You draw **frames**, one per question, through the official CLI; the user moves, edits and adds things in the browser and calls you with **notes**: text or sticky notes containing `@claude`. You answer each note with a **reply** sticky note next to it.

Everything goes through `npx -y @excalidraw/cli@0.3.0` (pinned; the unscoped `excalidraw-cli` package is unrelated), wrapped by the scripts here. `SKILL_DIR` below is this skill's directory.

## Setup, once per machine

The user runs `npx @excalidraw/cli login --api-key <key>` themselves; a key never goes through chat. `npx -y @excalidraw/cli@0.3.0 whoami` must report `keyType: personal`: workspace keys cannot see Private scenes and return 404 for them.

The scene ID is the last part of the board URL: `app.excalidraw.com/s/<workspaceId>/<sceneId>`. For a new board: `excalidraw scenes create --name "<name>" --collection-id private`.

## Draw a board

1. **Content first.** Read the real code and docs you will quote; code panels show real repo code, trimmed, or say they are a sketch.
2. **Write a board module** in the scratchpad, starting from `SKILL_DIR/examples/hello.mjs`. Import the helpers from `SKILL_DIR/lib/board.mjs` by absolute path. Give every element you may change later a `key`: the key is its identity across reruns.
3. **Pick the origin.** On a scene that already has content, run `node SKILL_DIR/scripts/diff.mjs <sceneId> --keep` and start at `--at <bounds.right + 400>,<bounds.top>`.
4. **Preview.** `node SKILL_DIR/scripts/sync.mjs <sceneId> <board.mjs> --at x,y --dry <dir>` writes nothing and renders every frame to `<dir>/frames/`. Read each new frame's PNG and fix the module until each one passes the layout rules below. Done when you have read every new frame's PNG after the last change.
5. **Sync.** The same command without `--dry`. Then run `diff.mjs <sceneId>` once, so the next check compares against this state.
6. **Watch** (below), and give the user the board link.
7. **Report in chat** what each new frame concludes, one short paragraph per frame, in full sentences (see **Writing**). The user has the board open, so don't list its panels or describe its layout.

## Check the board

Run this when the user says "check the board" or the watcher exits with notes.

1. `node SKILL_DIR/scripts/diff.mjs <sceneId>` lists what changed since the last look (`added`, `changed` with field names, `deleted`), the frames, and `openNotes`. Elements without `customData.owner: "claude"` belong to the user.
2. Render frames that changed, to see them as the user does: `npx -y @excalidraw/cli@0.3.0 scenes render <sceneId> --frame-id <id> --out f.png`.
3. Act on each open note. Changes to your frames go through the board module and `sync.mjs`. Answer with `node SKILL_DIR/scripts/reply.mjs <sceneId> <noteTextId> -` and the reply on stdin. Done when `diff.mjs <sceneId> --keep` shows no `openNotes`.
4. Restart the watcher if it had exited.

## Watch

`python3 -I SKILL_DIR/scripts/watch.py <sceneId>` as a background command with `timeout: 7200000`. It polls every 20 s and exits once a note has kept the same text for 25 s, because Excalidraw saves while the user types. Exit 0: notes on stdout, go to "Check the board". Exit 3: the 110-minute limit, restart it. Exit 2: five failed reads in a row, tell the user. It runs only while this session is open.

## Rules

- **Patch only.** `sync.mjs` and `reply.mjs` send `scenes content patch`. `scenes content put` replaces the whole scene and erases the user's work; use it only to fill a scene created empty for this board.
- **Ownership.** Your elements carry `customData: {owner: "claude", key}`. Change the user's elements only when a note asks for it.
- **Three-way merge.** `sync.mjs` compares the live scene, what it last wrote (`~/.cache/whiteboard/<sceneId>/written.json`) and the new board. A field the user changed keeps the user's value. An element the user deleted stays deleted. An element the board no longer generates is removed, unless the user edited it. Without `written.json`, your elements count as untouched and are overwritten, so keep the cache.
- **Notes.** The watcher matches `@claude` exactly, case aside; a typo does not fire it, and "check the board" still works. Replies start with `claude:` and are marked as yours, so they never wake the watcher. Excalidraw+ comment threads cannot be read through the API; notes on the canvas replace them.
- **API facts the scripts handle.** IDs must be 21-character Excalidraw IDs or the server replaces them (`idFor(key)` derives one). Every element needs an `index` (fractional order key; new ones go after the current top). Arrow bindings must be `{elementId, fixedPoint: [fx, fy], mode: "orbit"}`; the older `{focus, gap}` is rejected. The server drops `lastCommittedPoint`; a field the server drops makes every rerun look like a change.

## Layout

- One frame per question; title it with the answer, under an uppercase eyebrow (`heading()`).
- Flows run left to right, then top to bottom. Label each arrow with what crosses it. Leave at least the label's width plus 60 px between boxes joined by a labelled arrow.
- Dashed `group()` outlines with an uppercase eyebrow show where boxes run (YOUR MAC, CLOUD).
- Neutral boxes with dark text; ember (`C.emberSoft` fill, `C.ember` stroke) on the one element per frame the answer is about.
- Code panels (`code()`) with a caption saying what the panel shows and where the code lives (see **Writing**).
- Fonts: Nunito (`SANS`, 6) for text and Cascadia (`CODE`, 3) for code; Excalidraw has no Geist. Colours: the palette in `C` (warm neutrals, one ember accent); change it there to restyle every board.
- Every element must tell the reader something about the subject; no legends, no notes on how the board was made.

## Writing

Every word on the board and in the chat report follows these rules:

- **Sentences say who does what.** Don't compress a clause into a noun phrase: write "if the measurements don't show that the change would help", not "if baseline evidence does not support the requested improvement".
- **State the claim, not the thing.** Write "`x: str = "?"` lets the key be left out; `x: str | None` lets the value be null", not "a table that separates missing keys from null values". Text that only names a thing makes the reader guess the point.
- **Give a concrete value** when a claim has one: `"yes"` becomes `True`, `"often"` fails.
- **Define before you refer.** Don't write "the X" until you have said what X is, and check every count against what follows it.

On a board they mean:

- **Captions state the claim**, then where the code lives: "Pydantic writes `| None` as anyOf, which the proxy drops (lib/models/analysis.py)", not "what Pydantic writes for `| None`".
- **Box and note text is sentences.** Arrow labels are the exception: they name what crosses the arrow, so a noun is right there.
- **Replies to notes** answer first, then give the reason.
