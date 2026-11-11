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
- [Agent Keys](#agent-keys)
- [Agent Secret Hygiene (partial)](#agent-secret-hygiene-partial)
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

`install.sh link` (and `install.sh skills`) never deletes or overwrites anything inside a home. If a home is a symlink, a real file or directory sits where a link belongs, or an old `~/.config/{claude,codex,copilot}` is still present, the run reports every conflict with the exact path involved, changes nothing there, and exits non-zero; move the named path aside and re-run.

`config/skills/` is the single source for all four harness skill directories. After adding a skill there, run `./install.sh skills` (also part of `link`) to create the `config/<harness>/skills/` links and the `~/.claude/skills/` links; `python3 githooks/skills-lint.py` checks skill metadata, references, portable paths, harness symlinks, and the pr-review2 eval structure (case files, defect class registry, reviewer identity on recorded results), and runs after agent-guard in pre-commit.

#### Fresh-device setup

On a new machine, after cloning the repo, `./install.sh link` alone sets up Claude Code, Codex and Copilot CLI:

```bash
./install.sh link
```

This creates `~/.claude`, `~/.codex` and `~/.copilot` as real directories (if they don't already exist) and, inside each, one symlink per tracked entry of `config/claude`, `config/codex` and `config/copilot` (plus every `~/.claude/skills/<name>` link). It also generates `~/.codex/config.toml` from `config/codex/config.toml` (+ `config/codex/config.local.toml` if present) - see [Codex Configuration](#codex-configuration). Re-running `link` is a no-op once everything is in place.

The one manual, machine-local step: if you keep machine-specific Codex settings (notify path, trusted projects, hook trust), copy `config/codex/config.local.toml.example` to `config/codex/config.local.toml` and fill it in *before* running `link`, so the generated `~/.codex/config.toml` picks it up (or run `./install.sh codex-sync` afterwards to regenerate).

```
dotfiles/
├── Brewfile                  # Homebrew packages, casks, and taps
├── Dockerfile                # Linux test environment
├── install.sh                # Setup & installation script
├── bin/                      # Custom shell scripts (symlinked to ~/bin)
├── mcp/                      # Pinned MCP server manifests (installed by install.sh mcp)
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
./install.sh [--dry-run] [--non-interactive] {backup|clean|link|copy|codex-sync|skills|hooks|mcp|doctor|git|homebrew|shell|macos|all|help}
```

| Command      | Description |
|--------------|-------------|
| `backup`     | Back up existing dotfiles to `~/dotfiles-backup/` |
| `clean`      | Remove symlinks created by `link` (including `~/.zshenv` and `~/bin`) |
| `link`       | Create symlinks from `config/` → `~/.config/`, `bin/` → `~/bin`, `config/git/.gitconfig`, `config/git/.gitignore` and `config/AGENTS.md` → `~/`, and tracked `config/{claude,codex,copilot}` entries → `~/.claude`, `~/.codex`, `~/.copilot` (refuses, without touching anything, when a real file or an old-layout symlink is in the way) |
| `copy`       | Copy configs instead of symlinking (useful for containers) |
| `codex-sync` | Regenerate `~/.codex/config.toml` from `config.toml` + `config.local.toml` |
| `skills`     | Link `config/skills/` into every `config/<harness>/skills/` and `~/.claude/skills/` (also run by `link`) |
| `hooks`      | Install `githooks/pre-commit` via `git config core.hooksPath` |
| `mcp`        | Install the pinned MCP servers from `mcp/*` into `~/.local/share/agent-mcp/` (see [Agent Keys](#agent-keys)) |
| `doctor`     | Read-only check that `~/.claude.json` (and its leftover copies) and `~/.copilot/mcp-config.json` hold no static Context7 credential (see [Agent Keys](#agent-keys)) |
| `git`        | Set up Git identity and credential helper |
| `homebrew`   | Install Homebrew and run `brew bundle` from the [Brewfile](./Brewfile) |
| `shell`      | Set Zsh as the default shell and pre-install Zinit |
| `macos`      | Apply macOS system preferences (Finder, keyboard, Safari, etc.) |
| `all`        | Run `link` → `homebrew` → `mcp` → `shell` → `git` → `macos` |
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

## Agent Keys

API keys that agents and CLIs need (Context7, OBSS LLM, OpenRouter, xAI,
Jira) are never exported into the shell. Each key reaches only the one command
that needs it, at the moment it starts, so an agent session started from an
interactive shell does not inherit any of them.

### How the flow works

1. The keys live in a dedicated 1Password vault, `agent-keys`: one API
   Credential item per key, value in the `credential` field, the env var name
   in a `key name` field. A read-only 1Password service account can see that
   vault and nothing else; its token is in the macOS Keychain as generic
   password service `op-sa-agent-keys`, account `$USER`.
2. `bin/secret-get <item>` reads that token from the Keychain and runs
   `op read op://agent-keys/<item>/credential` with
   `OP_SERVICE_ACCOUNT_TOKEN` set for that one `op` process only. It prints
   the value on stdout for a caller to capture. On failure it prints one short
   line on stderr (never the value, never the token), nothing on stdout, and
   exits non-zero.
3. `bin/with-secret <item> <VAR> <command> [args...]` captures that value,
   removes the other managed keys (`CONTEXT7_API_KEY`, `OBSS_LLM_API_KEY`,
   `OPENROUTER_API_KEY`, `XAI_API_KEY`, `JIRA_API_TOKEN`) and
   `OP_SERVICE_ACCOUNT_TOKEN` from its environment, sets `VAR` and `exec`s
   the command. The command (and its children) is the only process that gets
   the key, and only that key; the calling shell gets nothing. If the key
   cannot be read, the command is not started. All three scripts turn off an
   inherited `xtrace` (`SHELLOPTS=xtrace`, `bash -x`) before reading anything.
4. Consumers:

   | Consumer | Key (item → variable) | How it gets the key |
   |----------|-----------------------|---------------------|
   | `grok` (Grok CLI) | `xai` → `XAI_API_KEY` | shell function in `config/zsh/.zsh_agent_keys` |
   | `jira` (jira-cli) | `jira` → `JIRA_API_TOKEN` | shell function in `config/zsh/.zsh_agent_keys` |
   | `qwen` (Qwen Code, OBSS LLM provider) | `obss-llm` → `OBSS_LLM_API_KEY` | shell function in `config/zsh/.zsh_agent_keys` |
   | `qwen-or` (Qwen Code, OpenRouter provider) | `openrouter` → `OPENROUTER_API_KEY` | shell function in `config/zsh/.zsh_agent_keys`; it selects the key, not the model |
   | `copilot-obss` (Copilot CLI, OBSS LLM provider) | `obss-llm` → `COPILOT_PROVIDER_API_KEY` | shell function in `config/zsh/.zsh_agent_keys`; it also sets `COPILOT_PROVIDER_TYPE=openai` and `COPILOT_PROVIDER_BASE_URL=https://ai.obss.tech/llm/v1` for that one command; it selects the provider and key, not the model |
   | anything needing OpenRouter / OBSS LLM | `openrouter` → `OPENROUTER_API_KEY`, `obss-llm` → `OBSS_LLM_API_KEY` | prefix the one command: `with-openrouter <cmd>`, `with-obss-llm <cmd>` |
   | Codex Context7 MCP | `context7` → `CONTEXT7_API_KEY` | `config/codex/config.toml` runs `bin/context7-mcp`, which starts the pinned server by absolute path through `with-secret`; the key is in that server's environment only, never on argv and never in Codex's own environment |
   | OpenCode Context7 MCP | `context7` → `CONTEXT7_API_KEY` | `config/opencode/opencode.json`, same `bin/context7-mcp` launch as Codex |
   | Claude Code Context7 MCP (HTTP) | `context7` → `Authorization` header | `headersHelper` running `bin/context7-headers`; no static header in `~/.claude.json` |

The stdio Context7 server never runs through `npx`: `npx` prefers a
same-named package from the current project's `node_modules`, so any project
an agent opens could receive the key. `./install.sh mcp` (also part of `all`)
installs the version pinned in `mcp/context7/package.json` with `npm ci
--ignore-scripts` from the tracked lockfile (exact versions, integrity hashes)
into `~/.local/share/agent-mcp/context7/`, and `bin/context7-mcp` starts that
copy by absolute path. Without that install it fails closed. To upgrade, bump
the exact version in `mcp/context7/package.json`, regenerate the lockfile with
`npm install --package-lock-only --ignore-scripts` in that directory, and
re-run `./install.sh mcp`.

Copilot CLI keeps MCP servers in `~/.copilot/mcp-config.json` (not managed
here). Use the same launcher there instead of a header holding the key:

```json
"context7": { "type": "local", "command": "sh", "args": ["-c", "exec \"$HOME/bin/context7-mcp\""], "tools": ["*"] }
```

Copilot CLI does not read `OBSS_LLM_API_KEY`: for a custom (BYOK) provider
it reads `COPILOT_PROVIDER_BASE_URL`, `COPILOT_PROVIDER_TYPE` and
`COPILOT_PROVIDER_API_KEY` (`copilot help environment`). `copilot-obss`
reads the OBSS LLM key once per session into `COPILOT_PROVIDER_API_KEY` and
sets the other two for that one command only, through `env` rather than a
prefix assignment on the function call, which some shells (macOS `/bin/sh`)
keep in the calling shell. It selects the provider and key, not the model:
choose the model at startup (`--model` or `COPILOT_MODEL`). Plain `copilot`
is not wrapped and keeps GitHub Copilot's own model routing.

Claude Code keeps MCP servers in `~/.claude.json`, which this repo does not
manage. Register Context7 there once (the single quotes keep `$HOME` for the
shell Claude Code runs the helper in):

```bash
claude mcp remove context7 -s user
claude mcp add-json -s user context7 \
  '{"type":"http","url":"https://mcp.context7.com/mcp","headersHelper":"\"$HOME/bin/context7-headers\""}'
```

Neither file is managed here, so nothing else stops a static key from
coming back (an old `claude mcp add --header`, a hand edit, a copied
snippet). `./install.sh doctor` (or `bin/context7-config-check`) checks,
read-only:

- `~/.claude.json`, user scope and every project scope, plus the copies
  Claude Code leaves next to it (`~/.claude.json.tmp.*`,
  `~/.claude.json.backup*`, `~/.claude/backups/.claude.json.backup*`);
- `~/.copilot/mcp-config.json`.

It fails when a Context7 entry (name, url, command or args mention
`context7`) has a `headers` or `env` field with entries, a literal or a
`${VAR}` value alike, or an `--api-key` argument, and when any string in
those files contains a Context7-shaped key (`ctx7sk-`). It parses the JSON
and prints file and entry names only, never a value. Exit 0 is clean (a
file that does not exist is fine), 1 is a static credential, 2 is a file it
could not verify, which is never a pass: a file or directory it cannot look
up or read (only a plain "does not exist" counts as absent), invalid JSON,
or a value that is not an object where one belongs (an explicit `null`
included). After removing a static key, rotate
it: it has sat in a plain file.

Qwen Code reads its key from the variable that its provider config names in
`envKey`, so each wrapper hands it only the key of one provider. `qwen-or`
selects the OpenRouter key, not an OpenRouter model: choose the model
explicitly when the session starts. To switch between OBSS LLM and
OpenRouter, restart Qwen Code through the other wrapper; one session never
holds both keys.

`tests/agent-keys.sh` (CI job "Agent key wrappers") checks all of this with a
fake `op`, `security`, `npm` and `npx` and synthetic values: each wrapper
passes exactly its own variable to its child and nothing to the parent shell
(under bash and zsh), even when the starting environment still carries the
other keys and the service account token; the `qwen` and `qwen-or` wrappers also pass their arguments
(including empty ones and ones with spaces) and the child's exit status
through unchanged; `copilot-obss` also gets its provider type and URL,
overrides stale `COPILOT_PROVIDER_*` values, passes its arguments and exit
status through the same way, and leaves none of the three
`COPILOT_PROVIDER_*` variables in the parent shell; every failure path, and every path
under an inherited `xtrace`, prints neither value nor token and starts
nothing; the Codex and OpenCode launches, run inside a project that ships its
own `context7-mcp` package, start only the pinned install; the leak scans
report file names, never the matched text; and `context7-config-check`,
run on synthetic configs in a temp HOME, passes the `headersHelper` and the
launcher, flags static headers, `env` values and key flags in every scope
and leftover copy, refuses unreadable files and directories and `null`
containers, and prints no value.

### Adding a key

1. In 1Password, add an API Credential item to the `agent-keys` vault: value
   in `credential`, the env var name in `key name`. Item names may contain
   only letters, digits, `.`, `_` and `-`.
2. Check it without displaying it:
   `with-secret <item> CHECK sh -c 'test -n "$CHECK"' && echo ok` (prints `ok`
   when the key reads and is not empty; the single quotes keep `$CHECK` for
   the inner shell, so no shell expands the value on a command line and
   nothing prints it). An agent cannot run `secret-get` or `op read` for this:
   the command guard denies them (see "Agent Secret Hygiene"). A human in
   their own terminal, outside an agent, is unaffected and can still run
   `secret-get <item>`.
3. Give its consumer a wrapper in `config/zsh/.zsh_agent_keys`, for example
   `mytool() { with-secret myitem MYTOOL_API_KEY mytool "$@"; }`. If the new
   variable should also be stripped from other consumers, add it to the
   managed list in `bin/with-secret` and `bin/secret-get`. An MCP server gets
   a pinned install under `mcp/<name>/` and a launcher like
   `bin/context7-mcp` that starts it by absolute path through `with-secret`;
   never launch it with `npx` or a bare name a project could shadow.
   Never add an `export` of the key anywhere, and never pass it as a command
   line flag.
4. Extend `tests/agent-keys.sh` for the new consumer.

### Residual risks

- A key inside a running process is readable by other processes of the same
  user (for example through its environment); `with-secret` narrows which
  processes hold a key and for how long, it does not isolate them from one
  another.
- `node` itself is resolved from `PATH` when the pinned server starts, and
  `NODE_OPTIONS` or similar variables in the launching environment still
  apply; only the package location is pinned.
- Qwen Code's own child processes (shell tools, MCP servers) have not been
  measured for key inheritance yet. They may receive the provider key from
  Qwen Code's environment, so protection for Qwen Code is partial until a
  measurement with a sentinel value verifies what they get.
- Copilot CLI keeps `COPILOT_PROVIDER_API_KEY` in its environment for the
  whole session. Its own child processes (shell tools, MCP servers) have not
  been measured for key inheritance yet and may receive it, so protection
  for Copilot CLI is partial until a measurement with a sentinel value
  verifies what they get.
- Long-running consumers, MCP servers in particular, hold their key in their
  environment for as long as they run. Restart them after rotating a key.
- The Claude Code helper's output is held by Claude Code for that connection,
  so the Context7 key is in Claude Code's memory (not its environment) while
  the server is connected.
- Anyone who can run commands as you can run `secret-get` and read every key
  in the `agent-keys` vault (but nothing outside it). The command guard refuses
  `secret-get` to an agent when the command spells the name, and only as a
  tripwire (see "Agent Secret Hygiene"). Keep only agent-usable keys in that
  vault.

## Agent Secret Hygiene (partial)

These settings narrow what agent subprocesses can see. They are **partial
protection**, not a fix:

- **Claude Code MCP servers**: `CLAUDE_CODE_MCP_ALLOWLIST_ENV=1` in
  `config/claude/settings.json` starts each stdio MCP server with a safe
  baseline environment plus only that server's own configured `env`, instead
  of the whole shell environment. Give each server its own secret through its
  own `env` (stdio) or header (HTTP) entry, never on the command line.
- **Codex commands**: `[shell_environment_policy]` in
  `config/codex/config.toml` turns on Codex's built-in exclusion of variable
  names containing `KEY`, `SECRET` or `TOKEN` (this also drops `GH_TOKEN`;
  `gh` keeps working from the keyring) and adds `*PASSWORD*`, `*PASSWD*`,
  `*CREDENTIAL*`, `*_PAT` and `*PRIVATE*`.
- **Command guard**: `bin/agent-env-guard` is a PreToolUse hook for Claude
  Code (`settings.json`) and Codex (`config.toml`) that denies whole-environment
  dumps (`env`, `printenv` with no name, `export -p`, bare `set`,
  `declare -x`/`-p`), `ps` with environment flags (`-E`, BSD `e` as in
  `ps eww`) and reads of `/proc/<pid>/environ`. Ordinary `ps`,
  `printenv NAME`, `env NAME=value command` and `env -u NAME command` still
  run. **It is a best-effort tripwire, not a security boundary**: it blocks
  the dump commands it recognises and refuses forms it cannot read (for
  example zsh glob qualifiers, ANSI-C escapes, a redirection before the
  command name, a command name built from a variable or a glob, an option a
  wrapper table does not know, `env -S`, a shell reading stdin, nesting or
  size over the limits), with a short reason that does not quote the
  command. An allow only means that no recognised pattern matched: the hook
  blocks the patterns it recognises; a command that passes is not evidence
  of security. Everyday
  forms such as `git status && git diff`, `env FOO=1 true` and quoted
  here-documents pass. Codex runs the hook only after it is trusted with
  `/hooks`. Tests: `python3 -m unittest discover -s tests -p 'test_agent_env_guard.py'`
  (needs `sh`, `bash` and `zsh`; the shell corpus runs each case in a
  synthetic environment, never the real one).
- **Secret-read rule**: the same hook refuses an agent command that spells
  the name of a command or setting that prints a stored key. **Scope**: the
  rule examines only inputs whose text spells a guarded name (`secret-get`,
  `op` as a word, `OP_RUN_NO_MASKING`) after quotes and backslashes are
  removed and case is folded; each backslash-newline counts both as a line
  continuation and as a real newline, the two ways a shell can read it.
  Such an input is refused whole, whatever it
  would do, as a command string and as an argument list alike: the rule reads
  no shell syntax and keeps no list of harmless commands, so `secret-get
  <item>`, `op read`, `op item get` and `OP_RUN_NO_MASKING=1 op run` are
  refused by any path and inside any pipeline, substitution, `sh -c` string
  or wrapper, and so is a command that only mentions a name. An input that
  spells no guarded name is not examined by this rule: it gets the env-dump
  decision above, exactly as on `main`. **Access without spelling the name is
  an explicit protection limit** of this rule (see the limits below), not a
  finding. The rule lowers the chance of a mistake; it does not promise that a
  key never reaches tool output or a transcript.
  The refusal has one named reason, which states the guarded name that was
  spelled and never quotes the command. **Mentions are refused too**:
  `rg secret-get README.md`, `cat bin/secret-get`, `git log -- bin/secret-get`,
  `op --version`, `op whoami`, `op vault list`, `op item list`, a commit
  message or a here-document that holds a name, and the word `op` in prose.
  An earlier design read such inputs with a strict grammar and a list of
  read-only commands, and a listed command could still be made to run the
  guarded one (`git show --ext-diff` after a `diff.external` line written by
  the same input), so the list is gone. To read or search a file that
  mentions a name, an agent that has file tools uses them (the hook is
  registered for the shell tool only; whether Codex has a read path outside
  the shell tool was not measured), and it hands over text that holds a
  name from a file (`git commit -F <file>`). Keys stay usable through
  `with-secret <item> <VAR> <command>` and the launchers (`grok`, `jira`,
  `qwen`, `qwen-or`, `copilot-obss`, `with-openrouter`, `with-obss-llm`),
  which hand the value to one command and never print it; a call that spells
  no guarded name is not examined by this rule. Check that a key reads without
  displaying it with
  `with-secret <item> CHECK sh -c 'test -n "$CHECK"' && echo ok`. Why it
  exists: under zsh, `MULTIOS` makes `secret-get obss-llm 2>&1 >/dev/null | cat`
  send the value to the pipe as well as to `/dev/null` (bash prints nothing),
  which is how a key reached a session transcript. Humans running commands in
  their own terminal, outside an agent, are unaffected: the hook only sees what
  an agent types. Same limit as the rest of the guard: a tripwire, not a
  boundary.
- **Known limitations of the guard** (commands that still dump and pass; kept
  as `KNOWN_LIMITS` rows in `tests/agent_env_guard_shell_corpus.py`):
  - ENV-GUARD-11: a function body without braces is not checked, so
    `f() env; f` passes (dumps in zsh and dash).
  - ENV-GUARD-12: one named operand makes a declaration command pass, so
    `typeset -m PATH '*'` and `typeset -pm PATH '*'` (zsh) and
    `export -p PATH`, `export -p UNUSED` and
    `readonly FAKE_TEST_API_KEY; readonly -p PATH` (dash) list everything.
  - ENV-GUARD-13: `env` skips an operand whose value is unknown as if it were
    an assignment, so `env "$(printf env)" -u X` passes.
  - SECRET-LIMIT-01: a guarded command reached by another name is not
    examined, because the name is not spelled: a copy, symlink, alias or
    function (`mykey fake-item`).
  - SECRET-LIMIT-02: a script file is not read. One command can write it and
    another run it: a write that spells the name is refused, but
    `printf '%s-get x\n' secret > s.sh` passes and then `sh s.sh` passes
    (neither spells a name).
  - SECRET-LIMIT-03: a name that is not spelled in the text is not examined,
    whatever builds it: `find . -exec sec*et-get x ';'`, an interpreter string
    such as `python3 -c 'os.system("sec"+"ret-get x")'`, an `env` operand
    (`env "$(printf sec)ret-get" x`, the ENV-GUARD-13 family), or a
    configuration file a tool reads
    (`printf '[diff]\n\texternal = %s-get x\n' secret >> .git/config && git show --ext-diff`).
  - SECRET-LIMIT-04: a command run through `with-secret` or a launcher can
    print its own key, so `with-secret obss-llm KEY printenv KEY` passes.
  - SECRET-LIMIT-05: the spelling test is a test on the text, not on what a
    shell or a filesystem resolves. It removes the quotes of `$''` and `$""`
    and leaves the `$`, so `env secret-$''get x` (bash and zsh) and
    `env secret-$""get x` (bash) run the command and pass. Case is folded with
    `str.casefold()`, so the name written with the long s (`ſ`), which a
    case-insensitive macOS volume resolved to `s` when measured, is refused;
    that covers this one letter and is not a statement about every
    equivalence a filesystem applies. A backslash-newline is read both as a
    continuation and as a real newline (after an escaped backslash or inside
    a comment a shell reads the second), so `true x\\` newline `op item get x`
    is refused; the cost is that a real continuation directly next to `op`
    (`true x\` newline `op ...`, the single word `xop`) is refused as well.
  - ENV-LEXER-01: the lexer reads some forms differently from the shells, so
    inputs that dump the environment pass when they spell no guarded name (for
    example `echo ${x:-'}'$(env)'}'} #'`, `printf 'env\n' | bash /dev/stdin`,
    `{fd}>/dev/null env`, `if [[ -n x ]] env`). This is the defect class of
    issue #24 and is **not fixed** by the secret-read rule.
  - ENV-SUDO-K-01: `sudo -k env` passes (issue #25), **not fixed** here.
  - Anything the guard cannot see: what a started program, script file or
    interpreter does, and variables set outside the command.

What this does **not** solve:

- The global export chain: `config/zsh/.zshenv` sources `~/.zshenv.local`
  for every zsh, and anything exported there reaches every shell an agent
  starts, including the Claude Code Bash tool, whatever the settings above say.
  Secrets must not be exported globally.
- Same-user access to other processes' environments: any program running as
  your user can read them. The guard only inspects the command line the agent
  typed; it cannot see what a test, script or interpreter (node, python, ...)
  does once it runs.
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` is intentionally not set: on Claude Code
  2.1.319 it forces the permission mode to `default` (bypass is ignored), and
  it cannot remove keys that shell startup files export again.

## ZSH Configuration

The shell environment is managed through [Zinit](https://github.com/zdharma-continuum/zinit) and organized across several files in `config/zsh/`:

| File               | Purpose |
|--------------------|---------|
| `.zshenv`          | Sets `XDG_CONFIG_HOME`, `EDITOR`, `DOTFILES`, history, and PATH |
| `.zshrc`           | Loads plugins, completions, key bindings, and tool integrations |
| `.zsh_aliases`     | Shell, git, tmux, and tool aliases |
| `.zsh_functions`   | Helper functions (`g`, `md`, `docker open/close/flush`, etc.) |
| `.zsh_agent_keys`  | Per-command API key wrappers (`grok`, `jira`, `qwen`, `qwen-or`, `copilot-obss`, `with-openrouter`, `with-obss-llm`), see [Agent Keys](#agent-keys) |
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
| `context7-config-check` | Check agent configs for a static Context7 key (`install.sh doctor`), see [Agent Keys](#agent-keys) |
| `context7-headers`   | Claude Code `headersHelper` for Context7, see [Agent Keys](#agent-keys) |
| `context7-mcp`       | Start the pinned Context7 MCP server with its key, see [Agent Keys](#agent-keys) |
| `extract`            | Extract any archive format automatically |
| `git-bare-clone`     | Clone a repo as a bare repository for worktrees |
| `git-create-worktree`| Create a new git worktree |
| `git-graph`          | Visual git log graph |
| `ip`                 | Print your public IP address |
| `jwt`                | Decode a JWT token |
| `sbx-sync`           | Sync Codex/Claude config into a sandbox environment |
| `secret-get`         | Read one key from the 1Password `agent-keys` vault, see [Agent Keys](#agent-keys) |
| `update`             | Update Homebrew packages and Neovim plugins|
| `wgh`                | Clean up ghost windows in AeroSpace |
| `with-secret`        | Run one command with one key in its environment, see [Agent Keys](#agent-keys) |
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
