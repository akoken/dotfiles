# My Dotfiles

> Still a WIP! Use at your own risk.

# Homebrew

```bash
# Export packages
brew leaves > leaves.txt

# Install packages
xargs brew install < leaves.txt
```

# Neovim Setup

### Requirements

- Neovim >= **0.9.0** (needs to be built with **LuaJIT**)
- Git >= **2.19.0** (for partial clones support)
- [LazyVim](https://www.lazyvim.org/)
- [Nerd Font](https://www.nerdfonts.com/)(I use Monaspace Neon and CaskaydiaCove NF as fallback)
- a **C** compiler for `nvim-treesitter`. See [here](https://github.com/nvim-treesitter/nvim-treesitter#requirements)
- for [telescope.nvim](https://github.com/nvim-telescope/telescope.nvim) **_(optional)_**
  - **live grep**: [ripgrep](https://github.com/BurntSushi/ripgrep)
  - **find files**: [fd](https://github.com/sharkdp/fd)

### Preview

![alt text](/assets/nvim.png)

# Shell Setup

- [WezTerm](https://wezfurlong.org/wezterm/installation.html)
- [Zsh](https://zsh.org/)
- [Starship](https://starship.rs)
- [Nerd fonts](https://nerdfonts.com)(I use Monaspace Neon and CaskaydiaCove NF as fallback)
- [Eza](https://github.com/eza-community/eza) - `ls` replacement
- [bat](https://github.com/sharkdp/bat) - `cat` replacement
- [ghq](https://github.com/x-motemen/ghq) - Local Git repository organizer
- [fzf](https://github.com/PatrickF1/fzf.fish) - Interactive filtering

# Tmux Setup

### Requirements

- [tpm](https://github.com/tmux-plugins/tpm)
- [fzf](https://github.com/junegunn/fzf) (specifically [fzf-tmux](https://github.com/junegunn/fzf#fzf-tmux-script))
- [bat](https://github.com/sharkdp/bat)
- [icalBuddy](https://formulae.brew.sh/formula/ical-buddy#default) for MacOS calendar
- Optional: [zoxide](https://github.com/ajeetdsouza/zoxide) (Highly recommended)

### Installation

Clone the tmux plugin repo:

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

Then install the plugins with the following command:

```bash
CTRL + I
```

### Preview

![alt text](/assets/tmux.png)

