#!/usr/bin/env bash
# Usage: rec.sh start <session> <out.mp4>   frame the tab, then start recording
#        rec.sh stop  <session> <out.mp4>   stop, then report how many seconds show motion
set -uo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
ACTION="$1"; S="$2"; OUT="$3"
case "$ACTION" in
  start)
    mkdir -p "$(dirname "$OUT")"
    bash "$DIR/frame.sh" "$S" || exit 1
    agent-browser --session "$S" record start "$OUT" --cursor --fps 20 >/dev/null
    ;;
  stop)
    agent-browser --session "$S" record stop 2>&1 | tail -1
    bash "$DIR/motion.sh" "$OUT"
    ;;
  *) echo "usage: rec.sh start|stop <session> <out.mp4>" >&2; exit 2 ;;
esac
