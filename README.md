# My Dotfiles
Welcome to my dotfiles repository! This contains the configuration files I use for my daily development workflow.

> [!Note]
>
> This project is still a work in progress! Use at your own risk.
![alt text](/assets/nvim.png)

# Setup

> [!Note]
>
> You need to install the XCode CLI tools for macOS configuration.

```bash
xcode-select --install
```
After cloning the repository, you can set up the dotfiles using the install.sh script. Run the script with one of the following commands:

```bash
./install .sh help
Usage: install.sh {backup|link|homebrew|shell|macos|all}
```
## Available Setup Options

### `backup`

```bash
./install.sh backup
```

This command creates a backup of your current dotfiles (if any) in ~/.dotfiles-backup/. It scans for files that will be symlinked and moves them to the backup directory. It also handles vim/neovim setups, moving related files into the [XDG base directory](http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html), e.g., ~/.config.

- `~/.config/nvim/` - The home of [neovim](https://neovim.io/) configuration
- `~/.vim/` - The home of vim configuration
- `~/.vimrc` - The main init file for vim

### `link`

```bash
./install.sh link
```

This command creates symbolic links from the dotfiles directory to your home directory (`$HOME`). This allows you to keep the configurations in version control while using them in your actual environment.

### `homebrew`

```bash
./install.sh homebrew
```

This command installs `Homebrew` (macOS/Linux package manager) by downloading and running the Homebrew installer script. If the script detects you're on Linux, it will use Linuxbrew instead.

Once Homebrew is installed, it runs brew bundle to install the packages listed in the [Brewfile](./Brewfile).

### `shell`

```bash
./install.sh shell
```

This command sets up your shell configuration. It specifically configures the shell to Zsh using the `chsh` command.

### `macos`

```bash
./install.sh macos
```

This command applies macOS-specific settings using defaults write commands. It modifies various system preferences, including:

* Show all filename extensions in Finder
* Show hidden files by default
* Set UTF-8 encoding in Terminal.app
* Expand save dialogs by default
* Enable full keyboard access for all controls
* Enable subpixel font rendering on non-Apple LCDs
* Show the Path and Status bars in Finder
* Enable Safari’s debug menu

### `all`

```bash
./install.sh all
```

This runs all the installation tasks mentioned above (except for backup, which must be run manually).

## ZSH Configuration

The prompt for ZSH is configured in the `cnofig/zsh/zshrc` file and performs the
following operations.

- Sets `EDITOR` to `nvim`
- Recursively searches the `$DOTFILES/zsh` directory for any `.zsh` files and
  sources them
- Sources a `~/.localrc`, if available for configuration that is
  machine-specific and/or should not ever be checked into git
- Adds `~/bin` and `$DOTFILES/bin` to the `PATH`

## Neovim Setup

To install Neovim, use Homebrew:

```bash
brew install neovim
```

However, it was likely installed already if you ran the `./install.sh brew`
command provided in the dotfiles.

All of the configuration for Neovim starts at `config/nvim/init.lua`, which is
symlinked into the `~/.config/nvim` directory.

> [!Warning]
>
> The first time you run `nvim` with this configuration, it will likely have a
> lot of errors. This is because it is dependent on a number of plugins being
> installed.

### Installing plugins

On the first run, all required plugins should automatically installed by
[lazy.nvim](https://github.com/folke/lazy.nvim), a plugin manager for neovim.

> [!Note]
>
> Plugins can be synced in a headless way from the command line using the `vimu`
> alias.

## Tmux Setup

### Requirements

- [tpm](https://github.com/tmux-plugins/tpm)
- [fzf](https://github.com/junegunn/fzf) (specifically [fzf-tmux](https://github.com/junegunn/fzf#fzf-tmux-script))
- [bat](https://github.com/sharkdp/bat)
- [icalBuddy](https://formulae.brew.sh/formula/ical-buddy#default) for MacOS calendar

### Installation

Clone the tmux plugin repo:

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

Then install the plugins with the following command:

```bash
CTRL^ + I
```

![alt text](/assets/tmux.png)

## Docker Setup

A Dockerfile is provided to help test the dotfiles setup in a Linux environment. To build the Docker image:

```bash
docker build -t dotfiles --force-rm  .
```

This creates a dotfiles image with the repository cloned. To run the container:

```bash
docker run -it --rm dotfiles
```

This opens a Bash shell in the container, allowing you to test the dotfiles installation process.

## Preferred Apps and Tools

I almost exclusively work on macOS, so this list will be specific to that
operating system, but several of these reccomendations are also available,
cross-platform.

- [WezTerm](https://wezfurlong.org/wezterm/index.html) - GPU-accelerated terminal emulator
- [Aerospace](https://github.com/nikitabobko/AeroSpace) - i3-like tiling window manager for macOS
- [Raycast](https://raycast.com) - MacOS productivity app
- [Zsh](https://zsh.org/)
- [Oh My Posh](https://ohmyposh.dev) - Cross-platform prompt theme engine
- [Nerd fonts](https://nerdfonts.com)(I use [SF Mono Nerd Font](https://github.com/shaunsingh/SFMono-Nerd-Font-Ligaturized) and [CaskaydiaCove NF](https://www.nerdfonts.com/font-downloads) as fallback)
- [zoxide](https://github.com/ajeetdsouza/zoxide) (Highly recommended)
- [Eza](https://github.com/eza-community/eza) - `ls` replacement
- [bat](https://github.com/sharkdp/bat) - `cat` replacement
- [fzf](https://github.com/PatrickF1/fzf.fish) - Interactive filtering
- [icalBuddy](https://formulae.brew.sh/formula/ical-buddy#default) for MacOS calendar