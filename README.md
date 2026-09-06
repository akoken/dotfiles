# My Dotfiles

Personal dotfiles for my macOS development environment.

> [!Note]
>
> This project is still a work in progress! Use at your own risk.

![Preview](https://github.com/user-attachments/assets/d5ab8449-8aa5-45df-9c25-f840b10adf50)

## Table of Contents

- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Install Script](#install-script)
- [Codex Configuration](#codex-configuration)
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
├── Brewfile                  # Homebrew packages, casks, and taps
├── Dockerfile                # Linux test environment
├── install.sh                # Setup & installation script
├── bin/                      # Custom shell scripts (symlinked to ~/bin)
└── config/
    ├── aerospace/  # Tiling window manager
    ├── bat/        # bat themes
    ├── claude/     # Claude Code skills
    ├── codex/      # Codex CLI config, agents, skills (see below)
    ├── copilot/    # Copilot agents and skills
    ├── delta/      # Git diff pager themes
    ├── ghostty/    # Ghostty terminal config + shaders
    ├── git/        # Global gitconfig, gitignore, commit template
    ├── herdr/      # Herdr terminal multiplexer config
    ├── nvim/       # Neovim (lazy.nvim + kickstart-based)
    ├── oh-my-posh/ # Prompt theme
    ├── opencode/   # OpenCode agents, skills, and provider config
    ├── ripgrep/    # ripgrep defaults
    ├── skills/     # Shared agent skills (Codex/OpenCode/Copilot)
    ├── starship/   # Starship prompt config
    ├── tmux/       # Tmux config + plugins + scripts
    ├── wezterm/    # WezTerm terminal config
    └── zsh/        # Zsh config (zshrc, aliases, functions, env)
```

> [!Note]
>
> This Brewfile does not manage Mac App Store apps (no `mas` entries) — App
> Store installs are out of scope and stay manual.

## Install Script

```bash
./install.sh [--dry-run] [--non-interactive] {backup|clean|link|copy|codex-sync|hooks|git|homebrew|shell|macos|all|help}
```

| Command      | Description |
|--------------|-------------|
| `backup`     | Back up existing dotfiles to `~/dotfiles-backup/` |
| `clean`      | Remove symlinks created by `link` (including `~/.zshenv` and `~/bin`) |
| `link`       | Create symlinks from `config/` → `~/.config/` and `bin/` → `~/bin` |
| `copy`       | Copy configs instead of symlinking (useful for containers) |
| `codex-sync` | Regenerate `~/.config/codex/config.toml` from `config.toml` + `config.local.toml` |
| `hooks`      | Install `githooks/pre-commit` via `git config core.hooksPath` |
| `git`        | Set up Git identity and credential helper |
| `homebrew`   | Install Homebrew and run `brew bundle` from the [Brewfile](./Brewfile) |
| `shell`      | Set Zsh as the default shell and pre-install Zinit |
| `macos`      | Apply macOS system preferences (Finder, keyboard, Safari, etc.) |
| `all`        | Run `link` → `homebrew` → `shell` → `git` → `macos` |
| `help`       | Show usage |

| Flag                | Description |
|---------------------|-------------|
| `--dry-run`          | Print what would change without touching the filesystem |
| `--non-interactive`  | Skip prompts (currently: the git identity prompts in `setup_git`) |

> [!Note]
>
> `backup`, `clean`, and `hooks` must be run manually — they are not included in `all`.

## Codex Configuration

`config/codex/config.toml` holds only portable settings. Machine-specific
state — the trusted-project list, hook trust hashes, and the absolute
`notify` path — lives in `config/codex/config.local.toml`, which is
gitignored (see `config/codex/config.local.toml.example` for its shape).

Codex CLI has no native "load a second overlay file automatically" mechanism
for this (its own profile files, like `config/codex/llama_cpp.config.toml`,
only load when explicitly selected with `--profile`, e.g. via a shell alias
— not automatically on every run). So `install.sh link` gives
`config/codex` a real target directory instead of the usual whole-directory
symlink: everything else in `config/codex` is symlinked per-entry, and
`config.toml` at the target is generated from `config.toml` +
`config.local.toml`. It's only generated once by `link` (so it won't clobber
trusted-project/hook-trust entries Codex writes back into the live file);
run `./install.sh codex-sync` to force a refresh after editing either
source — and copy anything Codex wrote back into `config.local.toml` first,
or `codex-sync` will drop it.

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

![Tmux](https://github.com/user-attachments/assets/390cd17c-c7fc-4aba-894f-c88322274881)

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
| `sbx-sync`           | Sync Codex/Claude config into a sandbox environment |
| `update`             | Update Homebrew packages and Neovim plugins|
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
