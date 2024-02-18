# Applications
alias ls="eza -l --icons --git -a"
alias lt="eza --tree --level=2 --long --icons --git"
alias gg="git-graph"
alias v="nvim"
alias la=tree
alias cat=bat
alias g=git
# Dirs
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
alias .....="cd ../../../.."
alias ......="cd ../../../../.."

alias cl='clear'

export "PATH=$HOME/bin:$PATH"
export "PATH=/opt/homebrew/bin:$PATH"
export EDITOR=/opt/homebrew/bin/nvim

eval "$(starship init zsh)"
export STARSHIP_CONFIG=~/.config/starship/starship.toml
eval "$(zoxide init --cmd cd zsh)"
