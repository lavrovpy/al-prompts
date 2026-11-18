#!/usr/bin/env bash
# Usage: cards.sh <cards.txt> <out_dir> [logo.svg|png]
# Renders one 1920x1080 PNG per line of cards.txt: name|title|sub (sub optional).
# Cards follow cards/card.html: an optional logo, the title, the sub line.
set -euo pipefail
CARDS="$(cd "$(dirname "$0")/../cards" && pwd)"
MANIFEST="$1"; OUT="$2"; LOGO="${3:-}"; mkdir -p "$OUT"
enc() { python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$1"; }
LOGO_Q=""
[ -n "$LOGO" ] && LOGO_Q="&logo=$(enc "file://$(cd "$(dirname "$LOGO")" && pwd)/$(basename "$LOGO")")"
S=video-cards
while IFS='|' read -r name title sub; do
  case "$name" in ""|"#"*) continue ;; esac
  agent-browser --session $S open "file://$CARDS/card.html?title=$(enc "$title")&sub=$(enc "${sub:-}")$LOGO_Q" >/dev/null 2>&1
  agent-browser --session $S set viewport 1920 1080 >/dev/null 2>&1
  agent-browser --session $S wait --load networkidle >/dev/null 2>&1
  agent-browser --session $S eval 'document.fonts.ready.then(()=>1)' >/dev/null 2>&1
  agent-browser --session $S screenshot "$OUT/$name.png" >/dev/null
  echo "$OUT/$name.png"
done < "$MANIFEST"
agent-browser --session $S tab close >/dev/null 2>&1 || true
agent-browser --session $S close >/dev/null 2>&1 || true
