export ZSH=$DOTFILES/zsh

source "$ZDOTDIR/.zsh_functions"

########################################################
# Configuration
########################################################

prepend_path /usr/local/opt/grep/libexec/gnubin
prepend_path /usr/local/sbin
prepend_path $DOTFILES/bin
prepend_path $HOME/bin

# display how long all tasks over 10 seconds take
export REPORTTIME=10

setopt NO_BG_NICE
setopt NO_HUP                    # don't kill background jobs when the shell exits
setopt NO_LIST_BEEP
setopt LOCAL_OPTIONS
setopt LOCAL_TRAPS
setopt PROMPT_SUBST

# history
setopt EXTENDED_HISTORY          # write the history file in the ":start:elapsed;command" format.
setopt HIST_REDUCE_BLANKS        # remove superfluous blanks before recording entry.
setopt SHARE_HISTORY             # share history between all sessions.
setopt HIST_IGNORE_ALL_DUPS      # delete old recorded entry if new entry is a duplicate.
setopt appendhistory
setopt hist_ignore_space
setopt hist_save_no_dups
setopt hist_ignore_dups
setopt hist_find_no_dups
setopt COMPLETE_ALIASES

# Aliases
alias ls="eza -l --icons --git -a"
alias lt="eza --tree --level=2 --long --icons --git"
alias gg="git-graph"
alias v="nvim"
alias la=tree
alias cat=bat --theme="Catppuccin Mocha"
alias g=git
alias nf=neofetch
alias sf="fzf --preview='bat --color=always {}'"
alias sft="fzf-tmux --preview='bat --color=always {}'"

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

# Add in zsh plugins
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-autosuggestions
zinit light Aloxaf/fzf-tab

# Load completions
autoload -Uz compinit && compinit

zinit cdreplay -q

# Keybindings
#bindkey "^[[D" beginning-of-line
#bindkey "^[[C" end-of-line
#bindkey -e
#bindkey '^p' history-search-backward
#bindkey '^n' history-search-forward
#bindkey '^[w' kill-region

# make terminal command navigation sane again
bindkey "^[[1;5C" forward-word                      # [Ctrl-right] - forward one word
bindkey "^[[1;5D" backward-word                     # [Ctrl-left] - backward one word
bindkey '^[^[[C' forward-word                       # [Ctrl-right] - forward one word
bindkey '^[^[[D' backward-word                      # [Ctrl-left] - backward one word
bindkey '^[[1;3D' beginning-of-line                 # [Alt-left] - beginning of line
bindkey '^[[1;3C' end-of-line                       # [Alt-right] - end of line
bindkey '^[[5D' beginning-of-line                   # [Alt-left] - beginning of line
bindkey '^[[5C' end-of-line                         # [Alt-right] - end of line
bindkey '^?' backward-delete-char                   # [Backspace] - delete backward

if [[ "${terminfo[kdch1]}" != "" ]]; then
    bindkey "${terminfo[kdch1]}" delete-char        # [Delete] - delete forward
else
    bindkey "^[[3~" delete-char                     # [Delete] - delete forward
    bindkey "^[3;5~" delete-char
    bindkey "\e[3~" delete-char
fi

bindkey "^A" vi-beginning-of-line
bindkey -M viins "^F" vi-forward-word               # [Ctrl-f] - move to next word
bindkey -M viins "^E" vi-add-eol                    # [Ctrl-e] - move to end of line
bindkey "^J" history-beginning-search-forward
bindkey "^K" history-beginning-search-backward

# History
#HISTSIZE=5000
#HISTFILE=~/.zsh_history
#SAVEHIST=$HISTSIZE
#HISTDUP=erase

# Completion styling
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*' menu no
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'ls --color $realpath'
zstyle ':fzf-tab:complete:__zoxide_z:*' fzf-preview 'ls --color $realpath'

# Vim mode
#echo -ne '\e[5 q' # Use beam shape cursor on startup.

#preexec() { echo -ne '\e[5 q' ;} # Use beam shape cursor for each new prompt.

# add color to man pages
export MANROFFOPT='-c'
export LESS_TERMCAP_mb=$(tput bold; tput setaf 2)
export LESS_TERMCAP_md=$(tput bold; tput setaf 6)
export LESS_TERMCAP_me=$(tput sgr0)
export LESS_TERMCAP_so=$(tput bold; tput setaf 3; tput setab 4)
export LESS_TERMCAP_se=$(tput rmso; tput sgr0)
export LESS_TERMCAP_us=$(tput smul; tput bold; tput setaf 7)
export LESS_TERMCAP_ue=$(tput rmul; tput sgr0)
export LESS_TERMCAP_mr=$(tput rev)
export LESS_TERMCAP_mh=$(tput dim)

# Detect which `ls` flavor is in use
if ls --color > /dev/null 2>&1; then # GNU `ls`
    colorflag="--color"
else # macOS `ls`
    colorflag="-G"
fi

# If a ~/.zshrc.local exists, source it
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
# If a ~/.localrc zshrc exists, source it
[[ -a ~/.localrc ]] && source ~/.localrc

# look for all .zsh files and source them
for file in "$ZDOTDIR/.zsh_prompt" "$ZDOTDIR/.zsh_aliases"; do
    if [ -f $file ]; then
        source $file
    fi
done

# Shell integrations
eval "$(fzf --zsh)"
eval "$(oh-my-posh init zsh --config $DOTFILES/oh-my-posh/zen.toml)"

# prefer zoxide over z.sh
if [[ -x "$(command -v zoxide)" ]]; then
    eval "$(zoxide init zsh --hook pwd)"
    #eval "$(zoxide init --cmd cd zsh)"
else
  # source z.sh if it exists
  zpath="$(brew --prefix)/etc/profile.d/z.sh"
  if [ -f "$zpath" ]; then
      source "$zpath"
  fi
fi
