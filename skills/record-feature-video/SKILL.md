---
name: record-feature-video
description: Record a captioned demo video of a feature in the agent browser, with caption cards, name patching and a leak check. Use when asked to record, film or make a video of a feature, a demo, or a before/after for a PR.
compatibility: Needs agent-browser, ffmpeg, tesseract and Python 3.
---

# Record a feature video

A video is a list of **scenes**; a scene is caption **cards** and short **clips** in turn. Each clip shows one step and is recorded on its own, so a failed take costs seconds, not the whole video. Everything shown is real: a real build, real data, real accounts.

`<skill>` below is this file's folder: scripts are in `<skill>/scripts/`, examples of every input in `<skill>/examples/`. Work in an output folder such as `~/Movies/<video-name>/` with `raw/` for clips and `cards/` for cards.

## 1. Plan

Write `scenes.json` (format: `examples/scenes.example.json`) and `cards.txt` (format: `examples/cards.example.txt`) before recording. One card before each step says what the viewer is about to see; time or stage hints ("About 8 minutes later") go in the card's sub line.

Prepare off camera whatever the clips need: the build to show, realistic data, the state before each step, sign-ins. Never record setup.

Done when every clip in `scenes.json` names one step whose start state exists or will exist when you reach it.

## 2. Name map

When a screen shows a real person who should not appear (the account an automation runs as, an email, an avatar), write a name map (format: `examples/names.example.json`) and turn it into an init script:

```bash
python3 <skill>/scripts/make-patch.py names.json patch.js
agent-browser --session <s> --init-script patch.js open <url>
```

The init script applies to every page the session opens on the listed hosts. `@Name` mentions and selectors in `keep_selectors` stay as they are. It changes only what the browser shows, never what is sent.

## 3. Record each clip

Use one session for the whole video, in the browser that holds the sign-ins the clips need. For each clip:

```bash
bash <skill>/scripts/rec.sh start <s> raw/<clip>.mp4   # brings the tab to front, sets a 1920x1080 layout at DPR 2
# act: scripts/press.sh <s> <role> <text>, scripts/scroll.sh <s> <px>, agent-browser keyboard type …, sleep between steps
bash <skill>/scripts/rec.sh stop <s> raw/<clip>.mp4    # prints how many seconds show motion
```

- Pause 2–4 s before and after each action so the viewer can read.
- Press buttons, tabs and options with `press.sh`: it moves the visible cursor there, then presses from JavaScript with the full pointer sequence, which also works for Radix-style controls that act on pointerdown.
- For a long wait (a background job), record a few seconds of the live state, stop, then wait off camera with `scripts/wait-for.sh` in the background (it polls a value from the app in its own tab and fails loudly when the app is unreachable), then record the result as a new clip.

Done when every clip of `scenes.json` exists and `rec.sh stop` reported motion for each clip that scrolls or clicks. Look at a contact sheet of any clip you doubt: `bash <skill>/scripts/motion.sh raw/<clip>.mp4 sheet.png`.

## 4. Cards and assembly

```bash
bash <skill>/scripts/cards.sh cards.txt cards/ [logo.svg]
python3 <skill>/scripts/assemble.py scenes.json     # every scene, then the full cut
```

Cards follow `cards/card.html`: an optional logo on top, then the title and the sub line. Change its colours and font there to match a brand.

## 5. Leak check

```bash
bash <skill>/scripts/ocr-check.sh names.json <video>.mp4 ...
```

Done when it reports 0 frames with a real name for every finished video. A hit names the second; re-record that clip.

## Traps

- **Hidden tab**: a tab not in front of its window reports `document.visibilityState = hidden`; its recording freezes, some clicks do not register, and pages that pause in the background stop updating. `frame.sh` switches to the session's tab and refuses to start while it is hidden or showing a browser error page.
- **Per-host zoom**: a browser that keeps a zoom level per site lays a 1920 viewport out narrower (125% zoom gives 1536 CSS pixels). `frame.sh` compensates.
- **Typing into people pickers** shows names and emails while suggestions load; the name map's `hide_typing_in` hides typed text in those inputs.
- **zsh** mangles `$var:r`, `$ARR[a]` and arithmetic on values with commas: put multi-line commands in bash script files.
