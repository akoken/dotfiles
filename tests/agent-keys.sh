#!/usr/bin/env bash

# Controls for the per-command agent key flow (README "Agent keys"):
# bin/secret-get, bin/with-secret, bin/context7-headers, bin/context7-mcp,
# the shell wrappers in config/zsh/.zsh_agent_keys, the Context7 MCP configs
# and `install.sh mcp`.
#
# Every case runs against a fake `security`, `op`, `npm` and `npx` placed
# first on a private PATH, with synthetic values only. Nothing here reads the
# real Keychain or 1Password, and no failure message prints a value: failures
# name the case, never the data.

set +x
set -Eeuo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

# Resolve the interpreter before narrowing PATH; the config checks need
# tomllib (Python 3.11+).
py="$(command -v python3)" || fail "python3 not found"
"$py" -c 'import tomllib' 2>/dev/null || fail "python3 with tomllib (3.11+) is required"

# Synthetic values, never real credentials. Every one is a marker that must
# never show up on any stderr or in this script's own failure output.
token="synthetic-sa-token-0001"
xai_value="synthetic-xai-value-42"
jira_value="synthetic-jira-value-43"
ctx_value="synthetic.ctx7.value-7"
other_jira="synthetic-other-jira-44"
other_ctx="synthetic-other-ctx-45"
other_or="synthetic-other-openrouter-46"
other_obss="synthetic-other-obss-47"
stale_xai="synthetic-stale-xai-48"
caller_value="synthetic-caller-value-49"
or_value="synthetic-openrouter-value-50"
obss_value="synthetic-obss-value-51"
stale_copilot="synthetic-stale-copilot-52"
markers=("$token" "$xai_value" "$jira_value" "$ctx_value" "$other_jira" "$other_ctx" "$other_or" "$other_obss" "$stale_xai" "$caller_value" "$or_value" "$obss_value" "$stale_copilot")
key_names=(CONTEXT7_API_KEY OBSS_LLM_API_KEY OPENROUTER_API_KEY XAI_API_KEY JIRA_API_TOKEN OP_SERVICE_ACCOUNT_TOKEN)

fakebin="$work/fakebin"
home="$work/home"
mkdir -p "$fakebin" "$home"
oplog="$work/op.log"

cat >"$fakebin/security" <<EOF
#!/bin/sh
set +x
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
set +x
# fake 1Password CLI: records argv and selected environment facts, serves
# synthetic values only when called with the expected token
{
  printf 'argv:%s\n' "\$*"
  printf 'token-match:%s\n' "\$([ "\${OP_SERVICE_ACCOUNT_TOKEN-}" = '$token' ] && echo yes || echo no)"
  printf 'connect-host:%s\n' "\${OP_CONNECT_HOST-unset}"
  printf 'jira-in-op:%s\n' "\${JIRA_API_TOKEN:+set}"
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
  op://agent-keys/jira/credential) printf '%s' '$jira_value' ;;
  op://agent-keys/context7/credential) printf '%s' "\${FAKE_CTX_VALUE:-$ctx_value}" ;;
  op://agent-keys/openrouter/credential) printf '%s' '$or_value' ;;
  op://agent-keys/obss-llm/credential) printf '%s' '$obss_value' ;;
  *) exit 5 ;;
esac
EOF

# A consumer stand-in: records which managed names it received, and values
# only as "match"/"other" so the record itself never holds a marker.
cat >"$fakebin/probe" <<EOF
#!/bin/sh
set +x
out="\$1"
: >"\$out"
for name in ${key_names[*]}; do
  eval "v=\\\${\$name-}"
  [ -n "\$v" ] || continue
  case "\$name=\$v" in
    XAI_API_KEY='$xai_value' | JIRA_API_TOKEN='$jira_value' | CONTEXT7_API_KEY='$ctx_value' | \\
      OPENROUTER_API_KEY='$or_value' | OBSS_LLM_API_KEY='$obss_value') printf '%s=match\n' "\$name" >>"\$out" ;;
    *) printf '%s=other\n' "\$name" >>"\$out" ;;
  esac
done
exit 0
EOF

# probe-var <name> <out>: records whether one arbitrary variable holds the
# xAI marker ("match"), something else ("other") or nothing ("missing").
cat >"$fakebin/probe-var" <<EOF
#!/bin/sh
set +x
eval "v=\\\${\$1-}"
if [ "\$v" = '$xai_value' ]; then echo match >"\$2"; elif [ -n "\$v" ]; then echo other >"\$2"; else echo missing >"\$2"; fi
EOF
# A Qwen Code stand-in: `qwen <out> [args...]` records its managed keys
# through probe in <out>.env and its argument count and arguments, one per
# line, in <out>.argv, then exits with FAKE_QWEN_EXIT (default 0).
cat >"$fakebin/qwen" <<'EOF'
#!/bin/sh
set +x
out="$1"
shift
probe "$out.env"
{
  printf '%s\n' "$#"
  for a in "$@"; do printf '[%s]\n' "$a"; done
} >"$out.argv"
exit "${FAKE_QWEN_EXIT:-0}"
EOF

# A Copilot CLI stand-in: `copilot <out> [args...]` records its managed keys
# through probe in <out>.env; in <out>.provider whether
# COPILOT_PROVIDER_API_KEY holds the obss-llm marker ("match"), something
# else ("other") or nothing ("missing"), followed by the non-secret
# COPILOT_PROVIDER_TYPE and COPILOT_PROVIDER_BASE_URL; and its argument count
# and arguments, one per line, in <out>.argv. Exits with FAKE_COPILOT_EXIT
# (default 0).
cat >"$fakebin/copilot" <<EOF
#!/bin/sh
set +x
out="\$1"
shift
probe "\$out.env"
if [ "\${COPILOT_PROVIDER_API_KEY-}" = '$obss_value' ]; then k=match
elif [ -n "\${COPILOT_PROVIDER_API_KEY-}" ]; then k=other
else k=missing; fi
printf 'key:%s\ntype:%s\nurl:%s\n' "\$k" "\${COPILOT_PROVIDER_TYPE-unset}" "\${COPILOT_PROVIDER_BASE_URL-unset}" >"\$out.provider"
{
  printf '%s\n' "\$#"
  for a in "\$@"; do printf '[%s]\n' "\$a"; done
} >"\$out.argv"
exit "\${FAKE_COPILOT_EXIT:-0}"
EOF
chmod +x "$fakebin/security" "$fakebin/op" "$fakebin/probe" "$fakebin/probe-var" "$fakebin/qwen" "$fakebin/copilot"

# Private PATH: fakes first, then the repo's bin, then the system.
export PATH="$fakebin:$repo/bin:/usr/bin:/bin"
export USER="${USER:-tester}"
unset "${key_names[@]}" BASH_ENV ENV

no_marker_in() { # <file> <label>: fixed message only, never the match
  local m
  for m in "${markers[@]}"; do
    if grep -qF -e "$m" "$1"; then fail "$2 contains a secret marker"; fi
  done
}

expect_probe() { # <file> <expected-content> <label>
  [ "$(cat "$1")" = "$2" ] ||
    fail "$3: child env should be '$2', got names: $(cut -d= -f1 "$1" | tr '\n' ' ')"
}

# --- secret-get: success -----------------------------------------------------
: >"$oplog"
out="$(OP_CONNECT_HOST=http://connect.invalid JIRA_API_TOKEN="$other_jira" secret-get xai)" || fail "secret-get xai failed"
[ "$out" = "$xai_value" ] || fail "secret-get xai printed the wrong value"
grep -qx 'argv:read --no-newline op://agent-keys/xai/credential' "$oplog" || fail "op not called with the expected read reference"
grep -qx 'token-match:yes' "$oplog" || fail "op did not receive the service account token"
grep -qx 'connect-host:unset' "$oplog" || fail "OP_CONNECT_HOST leaked into op"
grep -qx 'jira-in-op:' "$oplog" || fail "another managed key leaked into op"
! grep '^argv:' "$oplog" | grep -qF "$token" || fail "token appeared on op's command line"

# --- failure paths print no value and no token -------------------------------
check_failure() { # <label> <expected-status|any> <command...>
  local label="$1" want="$2" status=0
  shift 2
  "$@" >"$work/f.out" 2>"$work/f.err" || status=$?
  [ "$status" -ne 0 ] || fail "$label: exited 0"
  [ "$want" = any ] || [ "$status" -eq "$want" ] || fail "$label: exit $status, want $want"
  [ ! -s "$work/f.out" ] || fail "$label: wrote to stdout"
  no_marker_in "$work/f.err" "$label stderr"
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

# --- inherited xtrace never traces a secret ----------------------------------
# bash imports SHELLOPTS from the environment, so a caller running with
# `set -x` exported would otherwise trace every assignment holding the token
# or a key. Success paths included.
xtrace_quiet() { # <label> <command...>: stderr must hold no marker
  local label="$1"
  shift
  env SHELLOPTS=xtrace "$@" >"$work/x.out" 2>"$work/x.err" || true
  no_marker_in "$work/x.err" "xtrace $label stderr"
}
xtrace_quiet "secret-get success" secret-get xai
xtrace_quiet "secret-get op failure" env FAKE_OP_MODE=fail secret-get xai
xtrace_quiet "with-secret success" with-secret xai XAI_API_KEY true
xtrace_quiet "with-secret op failure" env FAKE_OP_MODE=fail with-secret xai XAI_API_KEY true
xtrace_quiet "context7-headers success" context7-headers
xtrace_quiet "context7-headers op failure" env FAKE_OP_MODE=fail context7-headers
env SHELLOPTS=xtrace context7-headers >"$work/x.out" 2>/dev/null || fail "context7-headers failed under inherited xtrace"

# --- with-secret: only the named variable reaches only the child ------------
with-secret xai XAI_API_KEY probe "$work/child.env" || fail "with-secret failed"
expect_probe "$work/child.env" "XAI_API_KEY=match" "with-secret clean env"

# A session that still carries the old global exports (and a stray token)
# must not hand them to the consumer.
env JIRA_API_TOKEN="$other_jira" CONTEXT7_API_KEY="$other_ctx" OPENROUTER_API_KEY="$other_or" \
  OBSS_LLM_API_KEY="$other_obss" XAI_API_KEY="$stale_xai" OP_SERVICE_ACCOUNT_TOKEN="$token" \
  with-secret xai XAI_API_KEY probe "$work/child.env" || fail "with-secret failed with inherited keys"
expect_probe "$work/child.env" "XAI_API_KEY=match" "with-secret inherited keys"

# The target name must not collide with the script's own variables.
for name in value item var here getter; do
  with-secret xai "$name" probe-var "$name" "$work/var.out" || fail "with-secret into '$name' failed"
  [ "$(cat "$work/var.out")" = match ] || fail "with-secret into '$name' did not deliver the value"
done

# A caller that already exports a variable named like the script's temporary
# must not get the key under that name as well, and an explicit target of
# that name must still receive it.
for tmp in value _with_secret_value; do
  env "$tmp=$caller_value" with-secret xai XAI_API_KEY probe-var "$tmp" "$work/var.out" ||
    fail "with-secret with exported '$tmp' failed"
  [ "$(cat "$work/var.out")" != match ] || fail "with-secret leaked the key under the caller's exported '$tmp'"
  env "$tmp=$caller_value" with-secret xai "$tmp" probe-var "$tmp" "$work/var.out" ||
    fail "with-secret into exported '$tmp' failed"
  [ "$(cat "$work/var.out")" = match ] || fail "with-secret into exported '$tmp' did not deliver the value"
done

check_failure "with-secret bad var" 2 with-secret xai '1BAD' probe "$work/never"
check_failure "with-secret usage" 2 with-secret xai XAI_API_KEY
rm -f "$work/never"
check_failure "with-secret on op failure" 1 env FAKE_OP_MODE=fail with-secret xai XAI_API_KEY probe "$work/never"
[ ! -e "$work/never" ] || fail "with-secret started the command although the secret was unavailable"

# --- shell wrappers: child gets its own key, parent shell gets nothing -------
ln -s probe "$fakebin/grok"
ln -s probe "$fakebin/jira"

# Every managed key and the service account token with a value the wrapped
# child must not see, plus stale Copilot provider settings the wrapper must
# override; sourced by the wrapper checks in a subshell only.
cat >"$work/stale.env" <<EOF
export CONTEXT7_API_KEY='$other_ctx' OBSS_LLM_API_KEY='$other_obss' OPENROUTER_API_KEY='$other_or'
export XAI_API_KEY='$stale_xai' JIRA_API_TOKEN='$other_jira' OP_SERVICE_ACCOUNT_TOKEN='$token'
export COPILOT_PROVIDER_API_KEY='$stale_copilot' COPILOT_PROVIDER_TYPE=azure COPILOT_PROVIDER_BASE_URL=https://stale.invalid
EOF

run_wrappers() { # <shell> [startup-file flags]
  local sh="$1" name status=0
  shift
  name="$(basename "$sh")"
  # Never let the shell read the invoking user's startup files: a real
  # ~/.zshenv could export real keys into this test.
  env -u BASH_ENV -u ENV HOME="$home" ZDOTDIR="$home" "$sh" "$@" -c '
    set -u
    . "$1/config/zsh/.zsh_agent_keys"
    grok "$2/grok.env" || exit 11
    jira "$2/jira.env" || exit 12
    (export FAKE_OP_MODE=fail; with-openrouter true); [ $? -ne 0 ] || exit 13   # vault read fails: fails closed

    # qwen / qwen-or: clean and inherited environments, arguments and exit
    # code pass through, and a failed vault read never starts qwen.
    for w in qwen qwen-or; do
      "$w" "$2/$w.clean" "a b" "" "--flag=x y" || exit 15
      (. "$2/stale.env"; "$w" "$2/$w.stale") || exit 16
      (export FAKE_QWEN_EXIT=7; "$w" "$2/$w.exit" one); s=$?
      [ "$s" -eq 7 ] || { echo "$w returned $s, want 7" >&2; exit 17; }
      for mode in fail empty; do
        (export FAKE_OP_MODE=$mode; "$w" "$2/$w.$mode"); s=$?
        [ "$s" -ne 0 ] || { echo "$w exited 0 on vault $mode" >&2; exit 18; }
        [ ! -e "$2/$w.$mode.env" ] || { echo "$w started qwen on vault $mode" >&2; exit 19; }
      done
    done

    # copilot-obss: clean and inherited environments, arguments and exit
    # code pass through, and a failed vault read never starts copilot.
    copilot-obss "$2/copilot.clean" "a b" "" "--flag=x y" || exit 15
    (. "$2/stale.env"; copilot-obss "$2/copilot.stale") || exit 16
    (export FAKE_COPILOT_EXIT=7; copilot-obss "$2/copilot.exit" one); s=$?
    [ "$s" -eq 7 ] || { echo "copilot-obss returned $s, want 7" >&2; exit 17; }
    for mode in fail empty; do
      (export FAKE_OP_MODE=$mode; copilot-obss "$2/copilot.$mode"); s=$?
      [ "$s" -ne 0 ] || { echo "copilot-obss exited 0 on vault $mode" >&2; exit 18; }
      [ ! -e "$2/copilot.$mode.env" ] || { echo "copilot-obss started copilot on vault $mode" >&2; exit 19; }
    done
    for n in CONTEXT7_API_KEY OBSS_LLM_API_KEY OPENROUTER_API_KEY XAI_API_KEY JIRA_API_TOKEN OP_SERVICE_ACCOUNT_TOKEN \
      COPILOT_PROVIDER_API_KEY COPILOT_PROVIDER_TYPE COPILOT_PROVIDER_BASE_URL; do
      eval "v=\${$n-}"
      [ -z "$v" ] || { echo "parent shell holds $n" >&2; exit 14; }
    done
  ' sh "$repo" "$work" 2>"$work/$name.err" || status=$?
  no_marker_in "$work/$name.err" "$sh wrapper stderr"
  [ "$status" -eq 0 ] || fail "wrappers under $sh exited $status"
  expect_probe "$work/grok.env" "XAI_API_KEY=match" "$sh grok wrapper"
  expect_probe "$work/jira.env" "JIRA_API_TOKEN=match" "$sh jira wrapper"
  local w want
  for w in qwen qwen-or; do
    if [ "$w" = qwen ]; then want="OBSS_LLM_API_KEY=match"; else want="OPENROUTER_API_KEY=match"; fi
    expect_probe "$work/$w.clean.env" "$want" "$sh $w wrapper"
    expect_probe "$work/$w.stale.env" "$want" "$sh $w wrapper inherited keys"
    [ "$(cat "$work/$w.clean.argv")" = "$(printf '3\n[a b]\n[]\n[--flag=x y]')" ] ||
      fail "$sh $w wrapper changed its arguments"
    [ "$(cat "$work/$w.exit.argv")" = "$(printf '1\n[one]')" ] || fail "$sh $w wrapper changed its arguments"
  done
  rm -f "$work"/qwen.* "$work"/qwen-or.*
  local run provider
  provider="$(printf 'key:match\ntype:openai\nurl:https://ai.obss.tech/llm/v1')"
  for run in clean stale exit; do
    expect_probe "$work/copilot.$run.env" "" "$sh copilot-obss wrapper ($run)"
    [ "$(cat "$work/copilot.$run.provider")" = "$provider" ] ||
      fail "$sh copilot-obss wrapper ($run): wrong provider key, type or URL"
  done
  [ "$(cat "$work/copilot.clean.argv")" = "$(printf '3\n[a b]\n[]\n[--flag=x y]')" ] ||
    fail "$sh copilot-obss wrapper changed its arguments"
  [ "$(cat "$work/copilot.exit.argv")" = "$(printf '1\n[one]')" ] || fail "$sh copilot-obss wrapper changed its arguments"
  rm -f "$work"/copilot.*
}
run_wrappers bash --norc --noprofile
if command -v zsh >/dev/null 2>&1; then
  run_wrappers "$(command -v zsh)" -f
elif [ -n "${CI:-}" ]; then
  fail "zsh is required in CI to test the wrappers under the real shell"
else
  echo "note: zsh not installed, wrappers tested under bash only" >&2
fi

# --- leak scans: report file names or a fixed message, never the match ------
scan_global_exports() { # <dir>
  local hits
  hits="$(grep -rlE '^[[:space:]]*(export[[:space:]]+)?(CONTEXT7_API_KEY|OBSS_LLM_API_KEY|OPENROUTER_API_KEY|XAI_API_KEY|JIRA_API_TOKEN)=' "$1" || true)"
  [ -z "$hits" ] || fail "a shell file assigns an agent key globally: $(echo "$hits" | tr '\n' ' ')"
}
scan_literal_keys() { # <file...>
  local hits
  hits="$(grep -lE 'ctx7sk-[A-Za-z0-9]|--api-key' "$@" || true)"
  [ -z "$hits" ] || fail "literal Context7 key or key flag in: $(echo "$hits" | tr '\n' ' ')"
}

# The scans themselves must not echo what they find: plant markers and check
# the failure output.
planted="$work/planted"
mkdir -p "$planted"
printf 'export XAI_API_KEY="%s"\n' "$stale_xai" >"$planted/.zshenv"
printf 'args = ["--api-key", "%s"]\n' "$other_ctx" >"$planted/config.toml"
(scan_global_exports "$planted") >"$work/scan.out" 2>&1 && fail "global export scan missed a planted export"
no_marker_in "$work/scan.out" "global export scan output"
(scan_literal_keys "$planted/config.toml") >"$work/scan.out" 2>&1 && fail "literal key scan missed a planted key flag"
no_marker_in "$work/scan.out" "literal key scan output"

scan_global_exports "$repo/config/zsh"
scan_literal_keys "$repo/config/codex/config.toml" "$repo/config/opencode/opencode.json"

# --- context7-headers: valid JSON header, fail closed ------------------------
hdr="$(context7-headers)" || fail "context7-headers failed"
"$py" -c '
import json, sys
h = json.loads(sys.argv[1])
assert h == {"Authorization": "Bearer " + sys.argv[2]}, sorted(h)
' "$hdr" "$ctx_value" 2>/dev/null || fail "context7-headers output is not the expected JSON header object"
check_failure "context7-headers on op failure" 1 env FAKE_OP_MODE=fail context7-headers
check_failure "context7-headers bad chars" 1 env 'FAKE_CTX_VALUE=a"b' context7-headers

# --- Context7 MCP launch: trusted install only, never the project's ---------
# A hostile project ships a same-named package in node_modules; npx (faked
# here with npx's local-first resolution) would run it.
server_log="$work/server.log"
trusted="$home/.local/share/agent-mcp/context7/node_modules/.bin"
proj="$work/project"
mkdir -p "$trusted" "$proj/node_modules/.bin" "$proj/node_modules/@upstash/context7-mcp"
ln -s "$repo/bin" "$home/bin"
cat >"$trusted/context7-mcp" <<EOF
#!/bin/sh
set +x
if [ "\${CONTEXT7_API_KEY-}" = '$ctx_value' ]; then echo trusted:key >>'$server_log'; else echo trusted:nokey >>'$server_log'; fi
EOF
cat >"$proj/node_modules/.bin/context7-mcp" <<EOF
#!/bin/sh
set +x
echo "project:\${CONTEXT7_API_KEY:+key}" >>'$server_log'
EOF
cat >"$fakebin/npx" <<'EOF'
#!/bin/sh
set +x
exec ./node_modules/.bin/context7-mcp
EOF
chmod +x "$trusted/context7-mcp" "$proj/node_modules/.bin/context7-mcp" "$fakebin/npx"

launch_argv() { # <codex|opencode>: the configured argv, NUL-separated
  "$py" - "$repo" "$1" <<'PY'
import json, sys, tomllib
repo, which = sys.argv[1], sys.argv[2]
if which == "codex":
    with open(f"{repo}/config/codex/config.toml", "rb") as fh:
        s = tomllib.load(fh)["mcp_servers"]["context7"]
    assert not s.get("env") and not s.get("env_vars"), "codex: key passed through config env"
    argv = [s["command"], *s.get("args", [])]
else:
    with open(f"{repo}/config/opencode/opencode.json") as fh:
        s = json.load(fh)["mcp"]["context7"]
    assert s.get("type") == "local", "opencode: not a local launch"
    assert not s.get("headers") and not s.get("environment"), "opencode: key in headers or environment"
    argv = s["command"]
assert "--api-key" not in " ".join(argv), f"{which}: key flag on argv"
sys.stdout.write("\0".join(argv) + "\0")
PY
}

for client in codex opencode; do
  launch_argv "$client" >"$work/argv" 2>/dev/null || fail "$client Context7 config failed the static checks"
  argv=()
  while IFS= read -r -d '' a; do argv+=("$a"); done <"$work/argv"
  : >"$server_log"
  (cd "$proj" && env HOME="$home" "${argv[@]}" >/dev/null 2>"$work/launch.err") || fail "$client Context7 launch failed"
  no_marker_in "$work/launch.err" "$client launch stderr"
  [ "$(cat "$server_log")" = "trusted:key" ] || fail "$client launch did not run only the trusted server with its key"

  # No trusted install: fail closed, never fall back to the project copy.
  mv "$home/.local/share/agent-mcp" "$work/agent-mcp.off"
  : >"$server_log"
  if (cd "$proj" && env HOME="$home" "${argv[@]}" >/dev/null 2>"$work/launch.err"); then
    fail "$client launch succeeded without the trusted install"
  fi
  no_marker_in "$work/launch.err" "$client missing-install stderr"
  [ ! -s "$server_log" ] || fail "$client launch ran a server without the trusted install"
  mv "$work/agent-mcp.off" "$home/.local/share/agent-mcp"
done

# --- install.sh mcp: pinned, lockfile-only, no install scripts ---------------
npmlog="$work/npm.log"
cat >"$fakebin/npm" <<EOF
#!/bin/sh
set +x
printf 'cwd:%s argv:%s\n' "\$PWD" "\$*" >>'$npmlog'
[ -f package.json ] && [ -f package-lock.json ] || exit 9
EOF
chmod +x "$fakebin/npm"
env HOME="$home" bash "$repo/install.sh" mcp >"$work/install.log" 2>&1 || fail "install.sh mcp failed"
dest="$home/.local/share/agent-mcp/context7"
cmp -s "$repo/mcp/context7/package-lock.json" "$dest/package-lock.json" || fail "install.sh mcp did not install the tracked lockfile"
grep -qx "cwd:$dest argv:ci --ignore-scripts --omit=dev --no-audit --no-fund" "$npmlog" ||
  fail "install.sh mcp did not run 'npm ci --ignore-scripts' in the install dir"
"$py" - "$repo/mcp/context7" <<'PY' || fail "mcp/context7 manifest is not pinned to an exact version with integrity"
import json, re, sys
d = sys.argv[1]
spec = json.load(open(f"{d}/package.json"))["dependencies"]["@upstash/context7-mcp"]
assert re.fullmatch(r"\d+\.\d+\.\d+", spec), spec
lock = json.load(open(f"{d}/package-lock.json"))
pkg = lock["packages"]["node_modules/@upstash/context7-mcp"]
assert pkg["version"] == spec and pkg.get("integrity", "").startswith("sha512-")
assert all(p.get("integrity") for k, p in lock["packages"].items() if k), "a locked package lacks integrity"
PY

echo "PASS: agent key flow injects one key into one command and fails closed"
