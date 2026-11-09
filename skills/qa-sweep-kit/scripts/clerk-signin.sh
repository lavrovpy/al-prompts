#!/usr/bin/env bash
# Signs a test user into an agent-browser session with a Clerk sign-in token (ticket strategy); "anon" signs out.
# Usage: clerk-signin.sh <session> <user|anon> [start-path]   (agents call it through the qa-signin wrapper, SKILL.md step 3)
# Env: QA_BASE_URL (e.g. http://localhost:3100), CLERK_SECRET_KEY, QA_USERS (JSON file {"qa_owner": "user_…", …})
# Exits non-zero with Clerk's or the browser's message unless the session ends signed in as that user (or signed out).
set -euo pipefail
SESSION="$1"; WHO="$2"; START="${3:-/}"
BASE="${QA_BASE_URL:?set QA_BASE_URL}"
AB="agent-browser --session $SESSION"
$AB open "$BASE/" >/dev/null
$AB wait --load networkidle >/dev/null 2>&1 || true
WAIT_CLERK="for (let i = 0; i < 75 && !(window.Clerk && window.Clerk.loaded); i++) await new Promise(r => setTimeout(r, 200)); if (!(window.Clerk && window.Clerk.loaded)) return 'clerk-not-loaded';"
if [ "$WHO" = anon ]; then
  WANT=qa-signed-out
  GOT=$($AB eval "(async () => { $WAIT_CLERK if (window.Clerk.user) await window.Clerk.signOut(); return window.Clerk.user ? 'still signed in as ' + window.Clerk.user.id : 'qa-signed-out'; })()" 2>&1) || true
else
  USER_ID=$(jq -r --arg u "$WHO" '.[$u] // empty' "${QA_USERS:?set QA_USERS}")
  [ -n "$USER_ID" ] || { echo "unknown test user: $WHO" >&2; exit 2; }
  WANT="qa-signed-in:$USER_ID"
  : "${CLERK_SECRET_KEY:?set CLERK_SECRET_KEY}"
  # The key reaches curl on stdin (-H @-) because ps shows every process's arguments.
  RESP=$(printf 'Authorization: Bearer %s\n' "$CLERK_SECRET_KEY" | curl -sS -X POST -H @- -H 'Content-Type: application/json' \
    -w '\n%{http_code}' https://api.clerk.com/v1/sign_in_tokens -d "{\"user_id\":\"$USER_ID\",\"expires_in_seconds\":600}")
  STATUS=${RESP##*$'\n'}; BODY=${RESP%$'\n'*}
  TICKET=$(jq -r '.token // empty' <<<"$BODY" 2>/dev/null || true)
  if [ "$STATUS" != 200 ] || [ -z "$TICKET" ]; then
    MSG=$(jq -r '[.errors[]? | .long_message // .message] | join("; ")' <<<"$BODY" 2>/dev/null || true)
    echo "could not mint a sign-in token for $WHO ($USER_ID): HTTP $STATUS ${MSG:-$BODY}" >&2
    exit 1
  fi
  GOT=$($AB eval "(async () => { $WAIT_CLERK if (window.Clerk.user) await window.Clerk.signOut(); const si = await window.Clerk.client.signIn.create({ strategy: 'ticket', ticket: '$TICKET' }); await window.Clerk.setActive({ session: si.createdSessionId }); return window.Clerk.user ? 'qa-signed-in:' + window.Clerk.user.id : 'no user after setActive'; })()" 2>&1) || true
fi
case "$GOT" in
  *"$WANT"*) ;;
  *) echo "sign-in as $WHO did not take: expected $WANT, the browser returned: $GOT" >&2; exit 1 ;;
esac
$AB open "$BASE$START" >/dev/null
$AB wait --load networkidle >/dev/null 2>&1 || true
echo "session=$SESSION user=$WHO at $BASE$START"
