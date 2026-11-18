#!/usr/bin/env bash
# Usage: press.sh <session> <role> <text>
# Moves the recorded cursor onto the element, then presses it from JavaScript with the full
# pointer sequence. Radix tabs, selects and options act on pointerdown/mousedown, and a CDP
# click on an app button sometimes does not register; this works for both.
# role: button | link | tab | option | combobox | menuitem | checkbox | textbox
set -uo pipefail
S="$1"; ROLE="$2"; TEXT="$3"
ab() { agent-browser --session "$S" "$@"; }
REF=$(ab snapshot -i -c | grep -F "$ROLE \"$TEXT" | head -1 | grep -o 'ref=e[0-9]*' | cut -d= -f2)
if [ -n "$REF" ]; then ab hover "@$REF" >/dev/null 2>&1; sleep 0.7; fi
Q=$(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$TEXT")
R=$(python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$ROLE")
ab eval "(()=>{const sel={button:'button,[role=button]',link:'a,[role=link]',tab:'[role=tab]',option:'[role=option]',combobox:'[role=combobox]',menuitem:'[role=menuitem]',checkbox:'[role=checkbox],input[type=checkbox]',textbox:'input,textarea,[role=textbox]'}[$R]||'*';const t=$Q;const scope=document.querySelector('[role=dialog]')&&$R!=='combobox'?[...document.querySelectorAll('[role=dialog] '+sel.split(',').join(',[role=dialog] '))].concat([...document.querySelectorAll(sel)]):[...document.querySelectorAll(sel)];const el=scope.find(e=>(e.textContent||'').trim()===t||e.getAttribute('aria-label')===t)||scope.find(e=>(e.textContent||'').trim().startsWith(t));if(!el)return 'not found';const o={bubbles:true,cancelable:true,pointerType:'mouse'};el.dispatchEvent(new PointerEvent('pointerdown',o));el.dispatchEvent(new MouseEvent('mousedown',o));el.dispatchEvent(new PointerEvent('pointerup',o));el.dispatchEvent(new MouseEvent('mouseup',o));el.click();return 'pressed'})()" | tr -d '"'
