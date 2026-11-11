#!/usr/bin/env bash

# Controls for bin/agent-env-tripwire, the Claude Code SessionStart hook that
# warns, by name only, when an agent session inherits credential-like
# environment variables (README "Agent Keys").
#
# Every case runs the tripwire under `env -i` with a minimal PATH and
# synthetic values only, never the invoking environment. Failure messages
# name the case, never the data.

set +x
set -Eeuo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
tripwire="$repo/bin/agent-env-tripwire"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

py="$(command -v python3)" || fail "python3 not found"
# The tripwire's shebang resolves python3 through PATH: keep the one found
# here first, then the system directories.
base_path="$(dirname "$py"):/usr/bin:/bin"

# Synthetic values, never real credentials. None may appear in any output.
m_or="synthetic-tripwire-marker-01"
m_xai="synthetic-tripwire-marker-02"
m_obss="synthetic-tripwire-marker-03"
m_ctx="synthetic-tripwire-marker-04"
m_jira="synthetic-tripwire-marker-05"
m_op="synthetic-tripwire-marker-06"
m_pat="synthetic-tripwire-marker-07"
m_excl="synthetic-tripwire-marker-08"
m_near="synthetic-tripwire-marker-09"
# A value that is itself a credential-like name: if values were ever scanned
# or printed, this name would show up in the report.
m_lookalike="LOOKALIKE_API_KEY"
markers=("$m_or" "$m_xai" "$m_obss" "$m_ctx" "$m_jira" "$m_op" "$m_pat" "$m_excl" "$m_near" "$m_lookalike")

no_marker_in() { # <file> <label>: fixed message only, never the match
  local m
  for m in "${markers[@]}"; do
    if grep -qF -e "$m" "$1"; then fail "$2 contains a secret marker"; fi
  done
}

run() { # <label> <NAME=value...>: runs the tripwire in exactly that env
  local label="$1" status=0
  shift
  env -i PATH="$base_path" "$@" "$tripwire" </dev/null >"$work/out" 2>"$work/err" || status=$?
  [ "$status" -eq 0 ] || fail "$label: exited $status, want 0"
  [ ! -s "$work/err" ] || fail "$label: wrote to stderr"
  no_marker_in "$work/out" "$label stdout"
}

expect_names() { # <label> <expected names, comma-separated, sorted>
  "$py" - "$work/out" "$2" <<'PY' || fail "$1: report is not the expected hook JSON with names '$2'"
import json, sys
path, want = sys.argv[1], sys.argv[2]
with open(path) as fh:
    text = fh.read()
assert text.count("\n") == 1, "want exactly one JSON line"
out = json.loads(text)
assert set(out) == {"systemMessage", "hookSpecificOutput"}, sorted(out)
hso = out["hookSpecificOutput"]
assert hso["hookEventName"] == "SessionStart"
names = want.split(",")
listed = ", ".join(names)
for field in (out["systemMessage"], hso["additionalContext"]):
    assert listed in field, "names missing or out of order"
assert f"holds {len(names)} credential-like" in out["systemMessage"], "wrong count"
PY
}

# --- clean environment: silent, exit 0 ---------------------------------------
run "clean environment"
[ ! -s "$work/out" ] || fail "clean environment: printed a report"

# Ordinary names, near misses and names with a matching word in the middle
# are not credentials by this rule.
run "near misses" HOME=/nonexistent TOKENIZER_PATH="$m_near" KEYBOARD="$m_near" \
  SSH_AUTH_SOCK="$m_near" MY_TOKEN_FILE="$m_near" API_KEY_PATH="$m_near" PASSWORD_STORE_DIR="$m_near" \
  NOTE="$m_lookalike"
[ ! -s "$work/out" ] || fail "near misses: printed a report"

# --- excluded names: silent even with a value --------------------------------
run "excluded names" GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="$m_excl" GIT_CONFIG_VALUE_0="$m_excl" \
  CLAUDE_CODE_MESSAGING_TOKEN="$m_excl" CLAUDE_CODE_SESSION_ID="$m_excl"
[ ! -s "$work/out" ] || fail "excluded names: printed a report"

# --- the five former global keys and the service account token --------------
run "former keys" OPENROUTER_API_KEY="$m_or" XAI_API_KEY="$m_xai" OBSS_LLM_API_KEY="$m_obss" \
  CONTEXT7_API_KEY="$m_ctx" JIRA_API_TOKEN="$m_jira" OP_SERVICE_ACCOUNT_TOKEN="$m_op" \
  GIT_CONFIG_KEY_0="$m_excl" CLAUDE_CODE_MESSAGING_TOKEN="$m_excl"
expect_names "former keys" \
  "CONTEXT7_API_KEY,JIRA_API_TOKEN,OBSS_LLM_API_KEY,OPENROUTER_API_KEY,OP_SERVICE_ACCOUNT_TOKEN,XAI_API_KEY"

# --- conservative suffix pattern, any case; an empty value still counts ------
run "suffix pattern" FOO_API_KEY="$m_pat" BAR_APIKEY="$m_pat" GH_TOKEN="$m_pat" BAZ_SECRET="$m_pat" \
  AWS_SECRET_KEY="$m_pat" DB_PASSWORD="$m_pat" lower_token="$m_pat" EMPTY_TOKEN= \
  CLAUDE_CODE_OAUTH_TOKEN="$m_pat" OTHER="$m_lookalike"
expect_names "suffix pattern" \
  "AWS_SECRET_KEY,BAR_APIKEY,BAZ_SECRET,CLAUDE_CODE_OAUTH_TOKEN,DB_PASSWORD,EMPTY_TOKEN,FOO_API_KEY,GH_TOKEN,lower_token"

# --- a name that is not a shell identifier is skipped, never printed ---------
run "non-identifier name" "odd-name_TOKEN=$m_pat" "x.y_API_KEY=$m_pat"
[ ! -s "$work/out" ] || fail "non-identifier name: printed a report"

# --- the hook as configured: settings.json command, run through sh ----------
# Claude Code runs a command hook through a shell with HOME set; ~/bin links
# to this repo's bin (install.sh link).
"$py" - "$repo/config/claude/settings.json" >"$work/hook.cmd" <<'PY' || fail "settings.json does not register the tripwire as a SessionStart hook"
import json, sys
hooks = json.load(open(sys.argv[1]))["hooks"]["SessionStart"]
cmds = [h for g in hooks if not g.get("matcher") for h in g["hooks"]
        if "agent-env-tripwire" in h.get("command", "")]
assert len(cmds) == 1, "want exactly one unmatched-source registration"
h = cmds[0]
assert h["type"] == "command" and h["command"] == '"$HOME/bin/agent-env-tripwire"', h
assert 0 < h.get("timeout", 0) <= 10, "timeout"
sys.stdout.write(h["command"])
PY
home="$work/home"
mkdir -p "$home"
ln -s "$repo/bin" "$home/bin"
status=0
env -i PATH="$base_path" HOME="$home" XAI_API_KEY="$m_xai" \
  sh -c "$(cat "$work/hook.cmd")" </dev/null >"$work/out" 2>"$work/err" || status=$?
[ "$status" -eq 0 ] || fail "configured hook command: exited $status"
[ ! -s "$work/err" ] || fail "configured hook command: wrote to stderr"
no_marker_in "$work/out" "configured hook command stdout"
expect_names "configured hook command" "XAI_API_KEY"

echo "PASS: agent-env-tripwire reports credential-like names only and always exits 0"
