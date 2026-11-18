#!/usr/bin/env bash
# Usage: scroll.sh <session> <pixels> [steps]
# Scrolls the page's largest scrolling panel in small steps driven from outside the page,
# because smooth scrolling and requestAnimationFrame pause in a tab that is not in front.
S="$1"; PX="$2"; STEPS="${3:-20}"
STEP=$(( PX / STEPS ))
JS="(()=>{const c=[...document.querySelectorAll('*')].filter(e=>{const s=getComputedStyle(e);return /(auto|scroll)/.test(s.overflowY)&&e.scrollHeight>e.clientHeight+20&&e.clientHeight>250}).sort((a,b)=>b.clientHeight*b.clientWidth-a.clientHeight*a.clientWidth)[0]||document.scrollingElement;c.scrollTop+=${STEP};return 1})()"
for _ in $(seq 1 "$STEPS"); do
  agent-browser --session "$S" eval "$JS" >/dev/null 2>&1; sleep 0.06
done
