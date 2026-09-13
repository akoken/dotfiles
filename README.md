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

### Agent tool home directories

Every agent tool keeps its own native default directory as a real directory, and the repo only links tracked content into it entry by entry. No environment variable relocates a tool's home: Claude Code honours `CLAUDE_CONFIG_DIR`, but third-party tools (quota-axi, GUI launchers that never source the shell) derive Keychain entry names and paths from the defaults, so a relocated home broke them.

| Tool | Real home | Linked from the repo | Machine state stays in |
|------|-----------|----------------------|------------------------|
| Claude Code | `~/.claude` (plus `~/.claude.json` at its default place) | each tracked entry of `config/claude/` (`CLAUDE.md`, ...) and one link per skill in `~/.claude/skills/` | `~/.claude` (settings, sessions, plugins, history) and the default `Claude Code-credentials` Keychain entry |
| Codex | `~/.codex` | each tracked entry of `config/codex/` (`agents`, `skills`, `.codexignore`, `llama_cpp.config.toml`); `config.toml` is generated there, see [Codex Configuration](#codex-configuration) | `~/.codex` (auth, sessions, sqlite, plugin caches) |
| Copilot CLI | `~/.copilot` | each tracked entry of `config/copilot/` (`agents`, `skills`) | `~/.copilot` |
| OpenCode | `~/.config/opencode` (its native location already) | whole-directory symlink to `config/opencode/`, like every other `config/*` dir | `~/.local/share/opencode` |

`install.sh link` (and `install.sh skills`) never deletes or overwrites anything inside a home. If a home is a symlink, a real file or directory sits where a link belongs, or an old `~/.config/{claude,codex,copilot}` is still present, the run reports every conflict, changes nothing there, and exits non-zero. Resolve them with the migration below and re-run.

`config/skills/` is the single source for all four harness skill directories. After adding a skill there, run `./install.sh skills` (also part of `link`) to create the `config/<harness>/skills/` links and the `~/.claude/skills/` links; `python3 githooks/skills-lint.py` checks skill metadata, references, portable paths, and harness symlinks, and runs after agent-guard in pre-commit.

#### One-time migration from the old layout

The old layout pointed Claude Code at `~/.config/claude` through `CLAUDE_CONFIG_DIR` (with `~/.claude` and `~/.claude.json` as compatibility symlinks), pointed Codex at `~/.config/codex` through `CODEX_HOME` (a whole-directory symlink into the repo, or a real directory with per-entry links), and linked `~/.config/copilot` to the repo while Copilot CLI kept reading `~/.copilot`. Every step below moves data or removes a symlink; nothing is deleted, and each block checks the layout it expects before touching anything.

Before you start: pull the dotfiles, quit Claude Code, Codex (CLI and app) and Copilot, and open a new shell so `CLAUDE_CONFIG_DIR`, `CLAUDE_SECURESTORAGE_CONFIG_DIR` and `CODEX_HOME` are no longer exported (or `unset` them in the current one).

Claude Code:

```bash
( set -e
  [ -L ~/.claude ] && [ -d ~/.config/claude ] && [ ! -L ~/.config/claude ] \
    || { echo "unexpected Claude layout, nothing changed"; exit 1; }
  rm ~/.claude                                   # compatibility symlink only
  mv ~/.config/claude ~/.claude
  [ -L ~/.claude.json ] && rm ~/.claude.json      # compatibility symlink only
  [ -e ~/.claude.json ] || mv ~/.claude/.claude.json ~/.claude.json
  # hooks and the status line were rewritten to ~/.config/claude/ by the old
  # migration; -i.pre-migration keeps a copy of each edited file next to it
  for f in ~/.claude/settings.json ~/.claude/statusline-command.sh; do
    [ -f "$f" ] && sed -i.pre-migration "s#$HOME/\.config/claude/#$HOME/.claude/#g" "$f"
  done
  grep -rls "$HOME/.config/claude" ~/.claude --include='*.json' --include='*.sh' \
    | grep -v '\.pre-migration$' || true       # anything listed still needs the same edit
)
```

The Keychain entry is already the unsuffixed `Claude Code-credentials` (the old layout kept it that way with `CLAUDE_SECURESTORAGE_CONFIG_DIR=""`), so the login survives.

Codex:

```bash
( set -e
  [ -e ~/.config/codex ] || { echo "no old Codex layout, nothing changed"; exit 1; }
  src="$(cd ~/.config/codex && pwd -P)"          # repo dir (old whole-dir symlink) or the real dir
  stamp="$(date +%Y%m%d-%H%M%S)"
  # whatever the GUI app wrote into ~/.codex while the shell used CODEX_HOME is
  # parked, not deleted
  [ -e ~/.codex ] && mv ~/.codex ~/.codex.pre-migration-"$stamp"
  mkdir ~/.codex
  for entry in "$src"/* "$src"/.[!.]*; do
    { [ -e "$entry" ] || [ -L "$entry" ]; } || continue
    name="$(basename "$entry")"
    [ -L "$entry" ] && continue                  # repo links: install.sh recreates them
    case "$name" in config.toml|config.local.toml|config.local.toml.example) continue ;; esac
    git -C "$src" ls-files --error-unmatch -- "$name" >/dev/null 2>&1 && continue   # tracked repo content stays
    mv "$entry" ~/.codex/
  done
  cp "$src/config.toml" ~/.codex/config.toml.pre-migration   # the live file Codex was writing into
  if [ -L ~/.config/codex ]; then rm ~/.config/codex; else mv ~/.config/codex ~/.config/codex.pre-migration-"$stamp"; fi
  echo "state moved into ~/.codex; previous ~/.codex parked as ~/.codex.pre-migration-$stamp"
)
```

Then fix up the config sources in the repo:

```bash
cd "$DOTFILES"
# absolute paths that pointed into the repo's config/codex now live under ~/.codex
sed -i.pre-migration "s#$DOTFILES/config/codex/#$HOME/.codex/#g" config/codex/config.local.toml
# Codex may have written machine-local entries straight into the tracked file:
# move notify, [projects.*], [hooks.state.*] and local marketplaces into
# config.local.toml (a copy of the live file is at ~/.codex/config.toml.pre-migration)
git diff -- config/codex/config.toml
git checkout -- config/codex/config.toml
```

Copilot:

```bash
[ -L ~/.config/copilot ] && rm ~/.config/copilot   # old whole-dir symlink; ~/.copilot already holds Copilot CLI state
# if ~/.copilot/agents or ~/.copilot/skills already exist as real directories,
# move them aside (e.g. ~/.copilot/skills.local) or fold them into config/copilot
```

Finally:

```bash
./install.sh link
readlink ~/.claude/CLAUDE.md ~/.claude/skills/agent-guard ~/.codex/skills ~/.copilot/agents
```

`link` recreates every repo link inside the three homes, prunes links left behind by entries the repo no longer has, and generates `~/.codex/config.toml` from `config.toml` + `config.local.toml`. Once Claude Code, Codex and Copilot all start cleanly, the parked `~/.codex.pre-migration-*`, `~/.config/codex.pre-migration-*` and `*.pre-migration` files can be deleted.

To roll back: check out the previous dotfiles commit (it restores the old `.zshenv` exports), then reverse the moves: `mv ~/.claude ~/.config/claude && ln -s ~/.config/claude ~/.claude`, `mv ~/.claude.json ~/.config/claude/.claude.json && ln -s ~/.config/claude/.claude.json ~/.claude.json`, restore each `*.pre-migration` file over its edited copy, move the entries back out of `~/.codex` into the old Codex directory and rename the parked `~/.codex.pre-migration-*` back to `~/.codex`, and re-run `./install.sh link` from the old commit.

```
dotfiles/
├── Brewfile                  # Homebrew packages, casks, and taps
├── Dockerfile                # Linux test environment
├── install.sh                # Setup & installation script
├── bin/                      # Custom shell scripts (symlinked to ~/bin)
└── config/
    ├── aerospace/  # Tiling window manager
    ├── bat/        # bat themes
    ├── claude/     # Claude Code CLAUDE.md + skills (linked into ~/.claude)
    ├── codex/      # Codex config, agents, skills (linked into ~/.codex, see below)
    ├── copilot/    # Copilot CLI agents and skills (linked into ~/.copilot)
    ├── delta/      # Git diff pager themes
    ├── ghostty/    # Ghostty terminal config + shaders
    ├── git/        # Global gitconfig, gitignore, commit template
    ├── herdr/      # Herdr terminal multiplexer config
    ├── nvim/       # Neovim (lazy.nvim + kickstart-based)
    ├── oh-my-posh/ # Prompt theme
    ├── opencode/   # OpenCode agents, skills, and provider config
    ├── ripgrep/    # ripgrep defaults
    ├── skills/     # Shared agent skills (Claude/Codex/Copilot/OpenCode)
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
./install.sh [--dry-run] [--non-interactive] {backup|clean|link|copy|codex-sync|skills|hooks|git|homebrew|shell|macos|all|help}
```

| Command      | Description |
|--------------|-------------|
| `backup`     | Back up existing dotfiles to `~/dotfiles-backup/` |
| `clean`      | Remove symlinks created by `link` (including `~/.zshenv` and `~/bin`) |
| `link`       | Create symlinks from `config/` → `~/.config/`, `bin/` → `~/bin`, and tracked `config/{claude,codex,copilot}` entries → `~/.claude`, `~/.codex`, `~/.copilot` (refuses, without touching anything, when a real file or an old-layout symlink is in the way) |
| `copy`       | Copy configs instead of symlinking (useful for containers) |
| `codex-sync` | Regenerate `~/.codex/config.toml` from `config.toml` + `config.local.toml` |
| `skills`     | Link `config/skills/` into every `config/<harness>/skills/` and `~/.claude/skills/` (also run by `link`) |
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
- not automatically on every run). So `install.sh link` treats `~/.codex`,
Codex's own home, as a real directory rather than a whole-directory symlink:
the tracked entries of `config/codex` are symlinked into it one by one, and
`~/.codex/config.toml` is generated from `config.toml` + `config.local.toml`.
It's only generated once by `link` (so it won't clobber trusted-project or
hook-trust entries Codex writes back into the live file); run
`./install.sh codex-sync` to force a refresh after editing either source - and
copy anything Codex wrote back into `config.local.toml` first, or `codex-sync`
will drop it. Codex's own state (auth, sessions, sqlite, plugin caches) lives
next to those links in `~/.codex` and never inside the repo.

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
