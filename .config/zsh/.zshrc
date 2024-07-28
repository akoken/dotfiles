if [ -f ~/.config/zsh/docker ]; then
    source ~/.config/zsh/docker
else
    print "404: ~/.config/zsh/docker not found."
fi

# Aliases
alias ls="eza -l --icons --git -a"
alias lt="eza --tree --level=2 --long --icons --git"
alias gg="git-graph"
alias v="nvim"
alias la=tree
alias cat=bat --theme="gruvbox-dark"
alias g=git

alias tc='f() { tmux new -A -s $1 };f'
alias tl='f() { tmux list-sessions };f'
alias ta='f() { tmux attach -t "$1" };f'
alias tk='f() { tmux kill-session -t $1 };f'

# Dirs
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
alias .....="cd ../../../.."
alias ......="cd ../../../../.."

alias cl='clear'

# Environment Variables
export "PATH=$HOME/bin:$PATH"
export "PATH=/opt/homebrew/bin:$PATH"
export EDITOR=/opt/homebrew/bin/nvim
export DOTNET_CLI_TELEMETRY_OPTOUT=1

# Set the directory we want to store zinit and plugins
ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"

# Download Zinit, if it's not there yet
if [ ! -d "$ZINIT_HOME" ]; then
   mkdir -p "$(dirname $ZINIT_HOME)"
   git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
fi

# Source/Load zinit
source "${ZINIT_HOME}/zinit.zsh"

# Load starship theme
#zinit ice as"command" from"gh-r" atclone"./starship init zsh > init.zsh; ./starship completions zsh > _starship" atpull"%atclone" src"init.zsh"
#zinit light starship/starship

# Add in zsh plugins
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions
zinit light Aloxaf/fzf-tab

# Load completions
autoload -Uz compinit && compinit

zinit cdreplay -q

# Keybindings
bindkey -e
bindkey '^p' history-search-backward
bindkey '^n' history-search-forward
bindkey '^[w' kill-region

# History
HISTSIZE=5000
HISTFILE=~/.zsh_history
SAVEHIST=$HISTSIZE
HISTDUP=erase
setopt appendhistory
setopt sharehistory
setopt hist_ignore_space
setopt hist_ignore_all_dups
setopt hist_save_no_dups
setopt hist_ignore_dups
setopt hist_find_no_dups

# Completion styling
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'ls --color $realpath'
zstyle ':fzf-tab:complete:__zoxide_z:*' fzf-preview 'ls --color $realpath'

# Vim mode
echo -ne '\e[5 q' # Use beam shape cursor on startup.

preexec() { echo -ne '\e[5 q' ;} # Use beam shape cursor for each new prompt.

# Shell integrations
eval "$(fzf --zsh)"
eval "$(oh-my-posh init zsh --config $HOME/.config/oh-my-posh/zen.toml)"
#eval "$(starship init zsh)"
#export STARSHIP_CONFIG=~/.config/starship/starship.toml
eval "$(zoxide init --cmd cd zsh)"
