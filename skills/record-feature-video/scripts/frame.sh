#!/usr/bin/env bash
# Usage: frame.sh <session>
# Bring the session's tab to the front and give it a 1920x1080 layout at device pixel ratio 2.
# Exits 1 when the tab is still hidden: a hidden tab records frozen frames.
set -uo pipefail
S="$1"
ab() { agent-browser --session "$S" "$@"; }

# Switching to the session's own tab is what brings it to the front of the shared window.
TAB=$(ab tab list 2>/dev/null | grep '→' | grep -o '\[t[0-9]*\]' | tr -d '[]' | head -1)
[ -n "$TAB" ] && ab tab "$TAB" >/dev/null 2>&1

ab set viewport 1920 1080 2 >/dev/null 2>&1
W=$(ab eval 'innerWidth' | tr -d '"')
if [ "$W" != "1920" ] && [ -n "$W" ]; then
  # The browser keeps a zoom level per host (seen: 125% on localhost, 133% on dev.azure.com).
  # Scale the viewport up and the device scale down by the same factor.
  read -r VW VH SC < <(python3 -c "z=1920/$W; print(round(1920*z), round(1080*z), round(2/z, 4))")
  ab set viewport "$VW" "$VH" "$SC" >/dev/null 2>&1
fi

URL=$(ab get url 2>/dev/null)
case "$URL" in
  chrome-error:*|about:blank|"")
    echo "the tab shows no app page ($URL): is the app or its port-forward up?" >&2; exit 1 ;;
esac

STATE=$(ab eval 'innerWidth+"x"+innerHeight+" dpr "+devicePixelRatio.toFixed(2)+" "+document.visibilityState' | tr -d '"')
echo "$STATE"
case "$STATE" in
  *visible) exit 0 ;;
  *) echo "tab is hidden: bring its browser window to the front, then rerun" >&2; exit 1 ;;
esac
