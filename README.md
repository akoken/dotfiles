# My Dotfiles

Personal dotfiles for my macOS development environment.

> [!Note]
>
> This project is still a work in progress! Use at your own risk.

![Preview](/assets/preview.png)

## Table of Contents

- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Install Script](#install-script)
- [ZSH Configuration](#zsh-configuration)
- [Neovim](#neovim)
- [Tmux](#tmux)
- [Terminal Emulators](#terminal-emulators)
- [Utility Scripts](#utility-scripts)
- [Docker](#docker)
- [Preferred Apps and Tools](#preferred-apps-and-tools)

## Quick Start

> [!Note]
>
> Requires the Xcode Command Line Tools.

```bash
xcode-select --install
git clone https://github.com/akoken/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh backup   # optional — backs up existing dotfiles first
./install.sh all
```

## Repository Structure

```
dotfiles/
├── Brewfile                  # Homebrew packages, casks, and VS Code extensions
├── Dockerfile                # Linux test environment
├── install.sh                # Setup & installation script
├── bin/                      # Custom shell scripts (symlinked to ~/bin)
└── config/
    ├── aerospace/            # Tiling window manager
    ├── bat/                  # bat themes
    ├── delta/                # Git diff pager themes
    ├── ghostty/              # Ghostty terminal config + shaders
    ├── git/                  # Global gitconfig, gitignore, commit template
    ├── nvim/                 # Neovim (lazy.nvim + kickstart-based)
    ├── oh-my-posh/           # Prompt theme
    ├── ripgrep/              # ripgrep defaults
    ├── sketchybar/           # macOS menu bar replacement
    ├── starship/             # Starship prompt config
    ├── tmux/                 # Tmux config + plugins + scripts
    ├── wezterm/              # WezTerm terminal config
    └── zsh/                  # Zsh config (zshrc, aliases, functions, env)
```

## Install Script

```bash
./install.sh {backup|clean|link|copy|git|homebrew|shell|macos|all}
```

| Command      | Description |
|--------------|-------------|
| `backup`     | Back up existing dotfiles to `~/dotfiles-backup/` |
| `clean`      | Remove symlinks created by `link` |
| `link`       | Create symlinks from `config/` → `~/.config/` and `bin/` → `~/bin` |
| `copy`       | Copy configs instead of symlinking (useful for containers) |
| `git`        | Set up Git identity and credential helper |
| `homebrew`   | Install Homebrew and run `brew bundle` from the [Brewfile](./Brewfile) |
| `shell`      | Set Zsh as the default shell |
| `macos`      | Apply macOS system preferences (Finder, keyboard, Safari, etc.) |
| `all`        | Run `link` → `homebrew` → `shell` → `git` → `macos` |

> [!Note]
>
> `backup` and `clean` must be run manually — they are not included in `all`.

## ZSH Configuration

The shell environment is managed through [Zinit](https://github.com/zdharma-continuum/zinit) and organized across several files in `config/zsh/`:

| File               | Purpose |
|--------------------|---------|
| `.zshenv`          | Sets `XDG_CONFIG_HOME`, `EDITOR`, `DOTFILES`, history, and PATH |
| `.zshrc`           | Loads plugins, completions, key bindings, and tool integrations |
| `.zsh_aliases`     | Shell, git, tmux, and tool aliases |
| `.zsh_functions`   | Helper functions (`g`, `md`, `docker open/close/flush`, etc.) |
| `.zprofile`        | Homebrew and tool-specific PATH setup |

### Plugins (via Zinit)

- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting)
- [zsh-completions](https://github.com/zsh-users/zsh-completions)
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions)
- [fzf-tab](https://github.com/Aloxaf/fzf-tab)

### Key integrations

- [Oh My Posh](https://ohmyposh.dev) — prompt theme engine (config in `config/oh-my-posh/`)
- [zoxide](https://github.com/ajeetdsouza/zoxide) — smart `cd`
- [fzf](https://github.com/junegunn/fzf) — fuzzy finder with key bindings
- [direnv](https://direnv.net/) — per-directory environment variables

## Neovim

Configuration lives in `config/nvim/` and is symlinked to `~/.config/nvim`. Built on a [kickstart.nvim](https://github.com/nvim-lua/kickstart.nvim) foundation with custom plugins.

> [!Warning]
>
> The first time you run `nvim`, [lazy.nvim](https://github.com/folke/lazy.nvim) will automatically install all plugins. Expect some initial errors until installation completes.

Plugins can be synced headlessly from the command line:

```bash
vu   # alias for: nvim --headless "+Lazy! sync" +qa
```

### Notable plugins

Telescope, Treesitter, LSP (via lspconfig), blink-cmp, conform, nvim-tree, flash, trouble, gitsigns, todo-comments, vim-tmux-navigator, and language-specific setups for Go and Rust.

## Tmux

Configuration is in `config/tmux/tmux.conf` with a Catppuccin theme. Prefix is set to `Ctrl-A`.

### Setup

```bash
# Install the plugin manager
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# Inside tmux, install plugins with:
# prefix + I
```

### Plugins

tmux-sensible, tmux-yank, tmux-resurrect, tmux-continuum, tmux-thumbs, tmux-fzf, tmux-fzf-url, tmux-sessionx, catppuccin-tmux, and vim-tmux-navigator.

![Tmux](/assets/tmux.png)

## Terminal Emulators

### Ghostty

Primary terminal. Config in `config/ghostty/` with custom cursor shaders, Vesper dark / Catppuccin Latte theme, and MonoLisa font.

### WezTerm

Secondary GPU-accelerated terminal. Config in `config/wezterm/wezterm.lua`.

## Utility Scripts

Custom scripts in `bin/` are symlinked to `~/bin` and available on `$PATH`:

| Script               | Description |
|----------------------|-------------|
| `brew-why`           | List installed packages and their dependents |
| `extract`            | Extract any archive format automatically |
| `git-bare-clone`     | Clone a repo as a bare repository for worktrees |
| `git-create-worktree`| Create a new git worktree |
| `git-graph`          | Visual git log graph |
| `ip`                 | Print your public IP address |
| `jwt`                | Decode a JWT token |
| `update`             | Update Homebrew packages |
| `wgh`                | Clean up ghost windows in AeroSpace |
| `wtfport`            | Find which process is listening on a given port |

## Docker

A Dockerfile is provided to test the dotfiles setup in a Linux environment:

```bash
docker build -t dotfiles --force-rm .
docker run -it --rm dotfiles
```

## Preferred Apps and Tools

I almost exclusively work on macOS, but many of these are cross-platform.

| Category | Tool | Description |
|----------|------|-------------|
| Terminal | [Ghostty](https://ghostty.org) | Fast, native terminal emulator |
| Terminal | [WezTerm](https://wezfurlong.org/wezterm/) | GPU-accelerated terminal emulator |
| Shell | [Zsh](https://zsh.org/) | Default shell |
| Prompt | [Oh My Posh](https://ohmyposh.dev) | Cross-platform prompt theme engine |
| Window Manager | [AeroSpace](https://github.com/nikitabobko/AeroSpace) | Tiling window manager for macOS |
| Launcher | [Raycast](https://raycast.com) | Spotlight replacement |
| Fonts | [Nerd Fonts](https://nerdfonts.com) | MonoLisa + [SF Mono Nerd Font](https://github.com/shaunsingh/SFMono-Nerd-Font-Ligaturized) fallback |
| Navigation | [zoxide](https://github.com/ajeetdsouza/zoxide) | Smarter `cd` |
| File Listing | [eza](https://github.com/eza-community/eza) | Modern `ls` replacement |
| File Viewing | [bat](https://github.com/sharkdp/bat) | `cat` with syntax highlighting |
| Search | [ripgrep](https://github.com/BurntSushi/ripgrep) | Fast `grep` replacement |
| Search | [fd](https://github.com/sharkdp/fd) | Fast `find` replacement |
| Filtering | [fzf](https://github.com/junegunn/fzf) | Fuzzy finder |

## License

[MIT](./LICENSE) © Abdurrahman Alp Köken
