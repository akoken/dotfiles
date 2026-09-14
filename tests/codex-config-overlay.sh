#!/usr/bin/env bash

# Regression test for `install.sh codex-sync` / codex_generate_config:
# the generated ~/.codex/config.toml must contain every line of
# config.local.toml exactly once (a missing `next` in the overlay awk used to
# print each table header after the first twice, which is invalid TOML), and
# the overlay's bare top-level keys must land at the document root.
#
# Runs entirely inside a temporary HOME and a temporary copy of the two
# inputs codex_generate_config reads (install.sh and config/codex/config.toml),
# so it never touches the real ~/.codex or the repo's own config.local.toml.

set -Eeuo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

fake_repo="$work/dotfiles"
home="$work/home"
mkdir -p "$fake_repo/config/codex" "$home/.codex"
cp "$repo/install.sh" "$fake_repo/install.sh"
cp "$repo/config/codex/config.toml" "$fake_repo/config/codex/config.toml"

overlay="$fake_repo/config/codex/config.local.toml"
cat >"$overlay" <<'TOML'
# machine-local overlay used by the test
notify = ["/usr/local/bin/notifier", "turn-ended"]

[marketplaces.local-example]
source_type = "local"
source = "/srv/marketplace"

[projects."/srv/project-one"]
trust_level = "trusted"

[projects."/srv/project-two"]
trust_level = "trusted"

[hooks.state."/srv/project-one/.codex/hooks.json:session_start:0:0"]
trusted_hash = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
TOML

HOME="$home" "$fake_repo/install.sh" codex-sync >"$work/codex-sync.log" 2>&1 ||
  { cat "$work/codex-sync.log" >&2; fail "install.sh codex-sync exited non-zero"; }

out="$home/.codex/config.toml"
[ -f "$out" ] || fail "$out was not generated"

# No table header may appear more than once in the whole generated file.
dupes="$(grep '^\[' "$out" | sort | uniq -d || true)"
[ -z "$dupes" ] || fail "duplicate table header(s) in generated config.toml:"$'\n'"$dupes"

# Everything after the overlay marker must be the overlay's table section
# verbatim: from its first table header to end of file, each line exactly once.
sed -n '/^\[/,$p' "$overlay" >"$work/expected-overlay-tail"
sed -n '/^# ---- machine-local overlay: config.local.toml ----$/,$p' "$out" | tail -n +2 >"$work/actual-overlay-tail"
diff -u "$work/expected-overlay-tail" "$work/actual-overlay-tail" ||
  fail "overlay table section was not copied verbatim into generated config.toml"

# The overlay's bare top-level key must precede the first table header.
first_table="$(grep -n -m1 '^\[' "$out" | cut -d: -f1)"
notify_line="$(grep -n -m1 '^notify = ' "$out" | cut -d: -f1)"
[ -n "$notify_line" ] || fail "overlay top-level key 'notify' missing from generated config.toml"
[ "$notify_line" -lt "$first_table" ] || fail "'notify' ended up inside a table instead of at the document root"

# Parse as TOML when a python3 with tomllib (3.11+) is available.
if python3 -c 'import tomllib' >/dev/null 2>&1; then
  python3 - "$out" <<'PY'
import sys, tomllib
with open(sys.argv[1], "rb") as fh:
    data = tomllib.load(fh)
assert data["notify"] == ["/usr/local/bin/notifier", "turn-ended"], data.get("notify")
assert data["marketplaces"]["local-example"]["source"] == "/srv/marketplace"
assert set(data["projects"]) >= {"/srv/project-one", "/srv/project-two"}, sorted(data["projects"])
assert "/srv/project-one/.codex/hooks.json:session_start:0:0" in data["hooks"]["state"]
PY
else
  echo "note: python3 with tomllib not available, skipped TOML parse check" >&2
fi

echo "PASS: generated config.toml contains the overlay exactly once and parses as TOML"
