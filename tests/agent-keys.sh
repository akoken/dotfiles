#!/usr/bin/env bash

# Controls for the per-command agent key flow (README "Agent keys"):
# bin/secret-get, bin/with-secret, bin/context7-headers, the shell wrappers in
# config/zsh/.zsh_agent_keys and the Context7 MCP configs.
#
# Every case runs against a fake `security` and a fake `op` placed first on a
# private PATH, with synthetic values only. Nothing here reads the real
# Keychain or 1Password.

set -Eeuo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

# Synthetic values, never real credentials.
token="synthetic-sa-token-0001"
xai_value="synthetic-xai-value-42"
ctx_value="synthetic.ctx7.value-7"

fakebin="$work/fakebin"
mkdir -p "$fakebin" "$work/home"
oplog="$work/op.log"

cat >"$fakebin/security" <<EOF
#!/bin/sh
# fake macOS security: only the agent-keys service account token exists
[ "\${FAKE_SECURITY_MODE:-ok}" = fail ] && exit 44
[ "\$1" = find-generic-password ] || exit 2
shift
service="" account="" print=0
while [ "\$#" -gt 0 ]; do
  case "\$1" in
    -s) service="\$2"; shift 2 ;;
    -a) account="\$2"; shift 2 ;;
    -w) print=1; shift ;;
    *) exit 2 ;;
  esac
done
[ "\$service" = op-sa-agent-keys ] && [ -n "\$account" ] && [ "\$print" = 1 ] || exit 44
printf '%s\n' '$token'
EOF

cat >"$fakebin/op" <<EOF
#!/bin/sh
# fake 1Password CLI: records argv and selected environment facts, serves
# synthetic values only when called with the expected token
{
  printf 'argv:%s\n' "\$*"
  printf 'token-match:%s\n' "\$([ "\${OP_SERVICE_ACCOUNT_TOKEN-}" = '$token' ] && echo yes || echo no)"
  printf 'connect-host:%s\n' "\${OP_CONNECT_HOST-unset}"
} >>'$oplog'
case "\${FAKE_OP_MODE:-ok}" in
  fail)
    # A misbehaving op that leaks onto both streams before failing.
    printf '%s' '$xai_value'
    printf 'error %s %s\n' '$xai_value' "\${OP_SERVICE_ACCOUNT_TOKEN-}" >&2
    exit 1 ;;
  empty) exit 0 ;;
esac
[ "\${OP_SERVICE_ACCOUNT_TOKEN-}" = '$token' ] || { echo "bad token" >&2; exit 3; }
[ "\$1 \$2" = "read --no-newline" ] || exit 4
case "\$3" in
  op://agent-keys/xai/credential) printf '%s' '$xai_value' ;;
  op://agent-keys/jira/credential) printf '%s' 'synthetic-jira-value' ;;
  op://agent-keys/context7/credential) printf '%s' "\${FAKE_CTX_VALUE:-$ctx_value}" ;;
  *) exit 5 ;;
esac
EOF

# A consumer stand-in: records which of the five key names it received.
cat >"$fakebin/probe" <<'EOF'
#!/bin/sh
out="$1"
: >"$out"
for name in CONTEXT7_API_KEY OBSS_LLM_API_KEY OPENROUTER_API_KEY XAI_API_KEY JIRA_API_TOKEN OP_SERVICE_ACCOUNT_TOKEN; do
  eval "v=\${$name-}"
  [ -n "$v" ] && printf '%s=%s\n' "$name" "$v" >>"$out"
done
exit 0
EOF
chmod +x "$fakebin/security" "$fakebin/op" "$fakebin/probe"

# Resolve the interpreter before narrowing PATH; the config check needs
# tomllib (Python 3.11+).
py="$(command -v python3)" || fail "python3 not found"
"$py" -c 'import tomllib' 2>/dev/null || fail "python3 with tomllib (3.11+) is required"

# Private PATH: fakes first, then the repo's bin, then the system.
export PATH="$fakebin:$repo/bin:/usr/bin:/bin"
export USER="${USER:-tester}"
unset CONTEXT7_API_KEY OBSS_LLM_API_KEY OPENROUTER_API_KEY XAI_API_KEY JIRA_API_TOKEN OP_SERVICE_ACCOUNT_TOKEN

no_secret_in() { # <file> <label>
  ! grep -q -e "$token" -e "$xai_value" -e "$ctx_value" "$1" || fail "$2 contains a secret or the token"
}

# --- secret-get: success -----------------------------------------------------
: >"$oplog"
out="$(OP_CONNECT_HOST=http://connect.invalid secret-get xai)" || fail "secret-get xai failed"
[ "$out" = "$xai_value" ] || fail "secret-get xai printed the wrong value"
grep -qx 'argv:read --no-newline op://agent-keys/xai/credential' "$oplog" || fail "op not called with the expected read reference"
grep -qx 'token-match:yes' "$oplog" || fail "op did not receive the service account token"
grep -qx 'connect-host:unset' "$oplog" || fail "OP_CONNECT_HOST leaked into op"
! grep -q "argv:.*$token" "$oplog" || fail "token appeared on op's command line"

# --- secret-get: failure paths print no value and no token -------------------
check_failure() { # <label> <expected-status|any> <command...>
  local label="$1" want="$2" status=0
  shift 2
  "$@" >"$work/f.out" 2>"$work/f.err" || status=$?
  [ "$status" -ne 0 ] || fail "$label: exited 0"
  [ "$want" = any ] || [ "$status" -eq "$want" ] || fail "$label: exit $status, want $want"
  [ ! -s "$work/f.out" ] || fail "$label: wrote to stdout"
  no_secret_in "$work/f.err" "$label stderr"
  [ -s "$work/f.err" ] || fail "$label: no error message"
}
check_failure "op failure" 1 env FAKE_OP_MODE=fail secret-get xai
check_failure "empty credential" 1 env FAKE_OP_MODE=empty secret-get xai
check_failure "keychain failure" 1 env FAKE_SECURITY_MODE=fail secret-get xai
check_failure "unknown item" 1 secret-get nosuchitem
check_failure "no args" 2 secret-get
: >"$oplog"
for bad in '../xai' 'xai/credential' '-x' 'a b' 'x?y' ''; do
  check_failure "item name '$bad'" 2 secret-get "$bad"
done
[ ! -s "$oplog" ] || fail "op was called for an invalid item name"

# --- with-secret: only the named variable reaches only the child ------------
with-secret xai XAI_API_KEY probe "$work/child.env" || fail "with-secret failed"
[ "$(cat "$work/child.env")" = "XAI_API_KEY=$xai_value" ] ||
  fail "child env should hold exactly XAI_API_KEY, got: $(cut -d= -f1 "$work/child.env" | tr '\n' ' ')"
check_failure "with-secret bad var" 2 with-secret xai '1BAD' probe "$work/never"
check_failure "with-secret usage" 2 with-secret xai XAI_API_KEY
rm -f "$work/never"
check_failure "with-secret on op failure" 1 env FAKE_OP_MODE=fail with-secret xai XAI_API_KEY probe "$work/never"
[ ! -e "$work/never" ] || fail "with-secret started the command although the secret was unavailable"

# --- shell wrappers: child gets its own key, parent shell gets nothing -------
# Fake consumers named like the real CLIs.
ln -s probe "$fakebin/grok"
ln -s probe "$fakebin/jira"

run_wrappers() { # <shell> [startup-file flags]
  local sh="$1"
  shift
  # Never let the shell read the invoking user's startup files: a real
  # ~/.zshenv could export real keys into this test.
  env -u BASH_ENV -u ENV HOME="$work/home" ZDOTDIR="$work/home" "$sh" "$@" -c '
    set -u
    . "$1/config/zsh/.zsh_agent_keys"
    grok "$2/grok.env" || exit 11
    jira "$2/jira.env" || exit 12
    with-openrouter true; [ $? -ne 0 ] || exit 13   # no such item: fails closed
    for n in CONTEXT7_API_KEY OBSS_LLM_API_KEY OPENROUTER_API_KEY XAI_API_KEY JIRA_API_TOKEN OP_SERVICE_ACCOUNT_TOKEN; do
      eval "v=\${$n-}"
      [ -z "$v" ] || { echo "parent shell holds $n" >&2; exit 14; }
    done
  ' sh "$repo" "$work" 2>"$work/$(basename "$sh").err" || fail "wrappers under $sh exited $?: $(cat "$work/$(basename "$sh").err")"
  [ "$(cat "$work/grok.env")" = "XAI_API_KEY=$xai_value" ] || fail "$sh grok wrapper injected the wrong variables"
  [ "$(cat "$work/jira.env")" = "JIRA_API_TOKEN=synthetic-jira-value" ] || fail "$sh jira wrapper injected the wrong variables"
  no_secret_in "$work/$(basename "$sh").err" "$sh wrapper stderr"
}
run_wrappers bash --norc --noprofile
if command -v zsh >/dev/null 2>&1; then
  run_wrappers "$(command -v zsh)" -f
elif [ -n "${CI:-}" ]; then
  fail "zsh is required in CI to test the wrappers under the real shell"
else
  echo "note: zsh not installed, wrappers tested under bash only" >&2
fi

# No dotfiles shell file may export any of the keys globally again.
if grep -rnE '^[[:space:]]*(export[[:space:]]+)?(CONTEXT7_API_KEY|OBSS_LLM_API_KEY|OPENROUTER_API_KEY|XAI_API_KEY|JIRA_API_TOKEN)=' "$repo/config/zsh"; then
  fail "a shell file assigns an agent key globally"
fi

# --- context7-headers: valid JSON header, fail closed ------------------------
hdr="$(context7-headers)" || fail "context7-headers failed"
"$py" -c '
import json, sys
h = json.loads(sys.argv[1])
assert h == {"Authorization": "Bearer " + sys.argv[2]}, sorted(h)
' "$hdr" "$ctx_value" || fail "context7-headers output is not the expected JSON header object"
check_failure "context7-headers on op failure" 1 env FAKE_OP_MODE=fail context7-headers
check_failure "context7-headers bad chars" 1 env 'FAKE_CTX_VALUE=a"b' context7-headers

# --- Context7 MCP configs carry no literal key and no argv key ---------------
"$py" - "$repo" <<'PY' || fail "a Context7 MCP config carries a key or bypasses with-secret"
import json, re, sys, tomllib
repo = sys.argv[1]

with open(f"{repo}/config/codex/config.toml", "rb") as fh:
    codex = tomllib.load(fh)["mcp_servers"]["context7"]
argv = [codex["command"], *codex.get("args", [])]
joined = " ".join(argv)
assert "--api-key" not in joined, "codex: --api-key on argv"
assert re.search(r'with-secret"? context7 CONTEXT7_API_KEY ', joined), "codex: not launched through with-secret"
assert not codex.get("env") and not codex.get("env_vars"), "codex: key passed through config env"

with open(f"{repo}/config/opencode/opencode.json") as fh:
    oc = json.load(fh)["mcp"]["context7"]
joined = " ".join(oc.get("command", []))
assert "--api-key" not in joined, "opencode: --api-key on argv"
assert re.search(r'with-secret"? context7 CONTEXT7_API_KEY ', joined), "opencode: not launched through with-secret"
assert not oc.get("headers") and not oc.get("environment"), "opencode: key in headers or environment"
PY
if grep -rnE 'ctx7sk-[A-Za-z0-9]|--api-key' "$repo/config/codex/config.toml" "$repo/config/opencode/opencode.json"; then
  fail "literal Context7 key or --api-key in a tracked config"
fi

echo "PASS: agent key flow injects one key into one command and fails closed"
