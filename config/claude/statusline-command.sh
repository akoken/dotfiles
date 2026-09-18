#!/usr/bin/env bash
# Claude Code statusline: directory, git branch, model, caveman badge.
# Reads the session JSON Claude Code sends on stdin and prints a single line.
set -u

input="$(cat)"

json_field() {
  # $1: jq path. Empty string when jq is missing or the field is absent.
  [ -n "${HAS_JQ:-}" ] || return 0
  printf '%s' "$input" | jq -r "$1 // empty" 2>/dev/null
}

command -v jq >/dev/null 2>&1 && HAS_JQ=1

dim=$'\033[2m'
cyan=$'\033[36m'
green=$'\033[32m'
reset=$'\033[0m'

cwd="$(json_field '.workspace.current_dir')"
[ -n "$cwd" ] || cwd="$PWD"
model="$(json_field '.model.display_name')"

branch=""
if command -v git >/dev/null 2>&1; then
  branch="$(git -C "$cwd" --no-optional-locks symbolic-ref --quiet --short HEAD 2>/dev/null)"
  if [ -n "$branch" ] && [ -n "$(git -C "$cwd" --no-optional-locks status --porcelain 2>/dev/null)" ]; then
    branch="$branch*"
  fi
fi

# Caveman renders its own badge (empty when the mode is off) from the same JSON.
caveman=""
badge_script="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/caveman-statusline.sh"
[ -x "$badge_script" ] && caveman="$(printf '%s' "$input" | bash "$badge_script" 2>/dev/null)"

out="${cyan}$(basename "$cwd")${reset}"
[ -n "$branch" ] && out="$out ${green}${branch}${reset}"
[ -n "$model" ] && out="$out ${dim}${model}${reset}"
[ -n "$caveman" ] && out="$out $caveman"

printf '%s\n' "$out"
