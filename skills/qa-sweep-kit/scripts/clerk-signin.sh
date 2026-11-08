#!/usr/bin/env bash
# Signs a test user into an agent-browser session with a Clerk sign-in token (ticket strategy); "anon" signs out.
# Usage: clerk-signin.sh <session> <user|anon> [start-path]
# Env: QA_BASE_URL (e.g. http://localhost:3100), CLERK_SECRET_KEY, QA_USERS (JSON file {"qa_owner": "user_…", …})
# The Clerk users need an identifier (username/email) or the ticket is rejected — see references/pitfalls.md.
set -euo pipefail
SESSION="$1"; WHO="$2"; START="${3:-/}"
BASE="${QA_BASE_URL:?set QA_BASE_URL}"
AB="agent-browser --session $SESSION"
$AB open "$BASE/" >/dev/null
$AB wait --load networkidle >/dev/null 2>&1 || true
WAIT_CLERK="for (let i = 0; i < 75 && !(window.Clerk && window.Clerk.loaded); i++) await new Promise(r => setTimeout(r, 200));"
if [ "$WHO" = anon ]; then
  $AB eval "(async () => { $WAIT_CLERK if (window.Clerk.user) await window.Clerk.signOut(); return 'signed-out'; })()" >/dev/null
else
  UID_=$(jq -r --arg u "$WHO" '.[$u] // empty' "${QA_USERS:?set QA_USERS}")
  [ -n "$UID_" ] || { echo "unknown test user: $WHO" >&2; exit 2; }
  TICKET=$(curl -s -X POST -H "Authorization: Bearer ${CLERK_SECRET_KEY:?set CLERK_SECRET_KEY}" -H 'Content-Type: application/json' \
    https://api.clerk.com/v1/sign_in_tokens -d "{\"user_id\":\"$UID_\",\"expires_in_seconds\":600}" | jq -r .token)
  [ -n "$TICKET" ] && [ "$TICKET" != null ] || { echo "could not mint a sign-in token for $WHO" >&2; exit 1; }
  $AB eval "(async () => { $WAIT_CLERK if (window.Clerk.user) await window.Clerk.signOut(); const si = await window.Clerk.client.signIn.create({ strategy: 'ticket', ticket: '$TICKET' }); await window.Clerk.setActive({ session: si.createdSessionId }); return window.Clerk.user.id; })()" >/dev/null
fi
$AB open "$BASE$START" >/dev/null
$AB wait --load networkidle >/dev/null 2>&1 || true
echo "session=$SESSION user=$WHO at $BASE$START"
