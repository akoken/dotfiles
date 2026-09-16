[[ -f "$HOME/.cargo/env" ]] && . "$HOME/.cargo/env"

export XDG_CONFIG_HOME="$HOME/.config"
# Agent tools (Claude Code, Codex, Copilot) keep their native homes (~/.claude,
# ~/.codex, ~/.copilot); install.sh links repo content into them. Do not set
# CLAUDE_CONFIG_DIR / CODEX_HOME / COPILOT_HOME here: third-party tools derive
# keychain names and paths from the defaults and break when a home is moved.

export ZDOTDIR="$XDG_CONFIG_HOME/zsh"
# HISTFILE/HISTSIZE/SAVEHIST live in .zshrc: macOS's /etc/zshrc re-assigns all
# three after .zshenv runs, so setting them here has no effect.

export DOTFILES="$(dirname "$(dirname "$(dirname "$(readlink "${(%):-%N}")")")")"

export CACHEDIR="$HOME/.local/share"
export VIM_TMP="$HOME/.vim-tmp"

# add a config file for ripgrep
export RIPGREP_CONFIG_PATH="$HOME/.config/ripgrep/config"

[[ -d "$CACHEDIR" ]] || mkdir -p "$CACHEDIR"
[[ -d "$VIM_TMP" ]] || mkdir -p "$VIM_TMP"

[[ -f ~/.zshenv.local ]] && source ~/.zshenv.local

fpath=(
    $DOTFILES/config/zsh/functions
    /usr/local/share/zsh/functions       # base autoload funcs (is-at-least, colors, add-zsh-hook, compinit)
    /usr/local/share/zsh/site-functions
    $fpath
)
# Drop nonexistent/duplicate entries (e.g. a stale Cellar/zsh/<old-version> path
# left in an inherited $FPATH after a Homebrew zsh upgrade) and dedupe.
fpath=(${^fpath}(N-/))
typeset -aU fpath

typeset -aU path

export EDITOR='nvim'
export GIT_EDITOR='nvim'
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=true

# Claude Code environment is managed in config/claude/settings.json.

# Firstmate
export OTEL_LOG_USER_PROMPTS=0
export NO_MISTAKES_TELEMETRY=0

# Caveman
export CAVEMAN_DEFAULT_MODE=full
