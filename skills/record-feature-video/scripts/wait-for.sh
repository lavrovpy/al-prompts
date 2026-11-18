#!/usr/bin/env bash
# Usage: wait-for.sh <app-url> <js-expression> <done-regex> [max-seconds] [interval]
# Waits off camera for an app state (a run finishing, a draft being written): evaluates the
# expression on a page of the app every interval and prints the value once it matches done-regex.
# Uses its own session and tab, opened here, so closing the recording tab cannot break it.
# Exits 1 on a timeout and 2 when the evaluation keeps failing (app down, tab gone).
# Run it with run_in_background and wait for its notification.
set -uo pipefail
URL="$1"; JS="$2"; DONE="$3"; MAX="${4:-1800}"; EVERY="${5:-20}"
S="wait-for-$$"
agent-browser --session "$S" open "$URL" >/dev/null 2>&1
start=$(date +%s); errors=0
while :; do
  value=$(agent-browser --session "$S" eval "$JS" 2>&1); code=$?
  page=$(agent-browser --session "$S" get url 2>&1)
  # A down app leaves the browser's error page, where page scripts still evaluate.
  if [[ "$page" == chrome-error:* ]]; then
    agent-browser --session "$S" open "$URL" >/dev/null 2>&1; code=1; value="unreachable: $URL"
  fi
  if [ "$code" -ne 0 ] || [[ "$value" == *"✗"* ]]; then
    errors=$((errors + 1))
    if [ "$errors" -ge 3 ]; then echo "evaluation failing: $value" >&2; status=2; break; fi
  else
    errors=0
    if [[ "$value" =~ $DONE ]]; then echo "$(date +%T) $value"; status=0; break; fi
  fi
  if [ $(( $(date +%s) - start )) -ge "$MAX" ]; then echo "timeout, last value: $value" >&2; status=1; break; fi
  sleep "$EVERY"
done
agent-browser --session "$S" tab close >/dev/null 2>&1; agent-browser --session "$S" close >/dev/null 2>&1
exit "$status"
