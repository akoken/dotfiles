. "$HOME/.cargo/env"

export XDG_CONFIG_HOME="$HOME/.config"
#export COPILOT_HOME="$XDG_CONFIG_HOME/copilot"
export CODEX_HOME="$XDG_CONFIG_HOME/codex"

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

# Local LLM API key, persisted so every shell (and an already-running
# llama-server) agrees on the same key instead of each shell minting its own.
_local_api_key_file="${XDG_STATE_HOME:-$HOME/.local/state}/llama/api_key"
if [[ ! -r "$_local_api_key_file" ]]; then
    mkdir -p "${_local_api_key_file:h}"
    (umask 077; openssl rand -hex 32 > "$_local_api_key_file")
fi
export LOCAL_API_KEY="$(<"$_local_api_key_file")"
export LLAMA_API_KEY="$LOCAL_API_KEY"
unset _local_api_key_file

# Copilot CLI (Local)
export COPILOT_PROVIDER_BASE_URL="http://localhost:8080/v1"
export COPILOT_PROVIDER_API_KEY="$LOCAL_API_KEY"

export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
export DISABLE_TELEMETRY=
export OTEL_LOG_USER_PROMPTS=0
export NO_MISTAKES_TELEMETRY=0
