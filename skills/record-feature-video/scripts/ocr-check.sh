#!/usr/bin/env bash
# Usage: ocr-check.sh <names.json> <clip.mp4>...
# Reads a frame every 0.5 s with tesseract and lists the frames that still show a real name,
# using the "ocr" regex of the name map. Exits 1 when any frame does.
set -uo pipefail
PATTERN=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["ocr"])' "$1"); shift
WORK=$(mktemp -d "${TMPDIR:-/tmp}/ocr-check.XXXXXX")
leaks=0
for clip in "$@"; do
  name=$(basename "$clip" .mp4); dir="$WORK/$name"; mkdir -p "$dir"
  ffmpeg -v error -i "$clip" -vf "fps=2,scale=2880:-1" "$dir/f%05d.png"
  hits=0
  for f in "$dir"/f*.png; do
    if tesseract "$f" - --psm 11 2>/dev/null | grep -i -q -E "$PATTERN"; then
      hits=$((hits + 1)); echo "  leak: $name at $(( (10#$(basename "$f" .png | tr -d f) - 1) / 2 )) s"
    fi
  done
  echo "$name: $(ls "$dir" | wc -l | tr -d ' ') frames, $hits with a real name"
  leaks=$((leaks + hits))
done
rm -rf "$WORK"
[ "$leaks" -eq 0 ]
