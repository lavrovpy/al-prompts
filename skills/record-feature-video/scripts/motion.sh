#!/usr/bin/env bash
# Usage: motion.sh <clip.mp4> [sheet.png]
# Prints how many one-second steps change the picture; 0 on a clip with scrolling or clicks
# means the recording froze. With a second argument, also writes a contact sheet to look at.
set -uo pipefail
CLIP="$1"; SHEET="${2:-}"
ffmpeg -v error -i "$CLIP" -vf "fps=1,scale=64:36,format=gray" -f rawvideo - | python3 -c '
import sys
data = sys.stdin.buffer.read(); n = 64 * 36
frames = [data[i:i + n] for i in range(0, len(data), n)]
changes = sum(1 for a, b in zip(frames, frames[1:]) if sum(abs(x - y) for x, y in zip(a, b)) > 2000)
print(f"{sys.argv[1]}: {len(frames)} s, {changes} changes" + ("  <- FROZEN?" if changes == 0 else ""))
' "$(basename "$CLIP")"
if [ -n "$SHEET" ]; then
  ffmpeg -v error -i "$CLIP" -vf "fps=1/2,scale=640:-1,tile=4x3" -frames:v 1 -y "$SHEET"
  echo "sheet: $SHEET"
fi
