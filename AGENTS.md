# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Agent-home linking and conflict handling are implemented in `install.sh`; see `README.md` for migration instructions. Sandbox installer checks must set both `HOME` and `XDG_CONFIG_HOME` to throwaway paths.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
