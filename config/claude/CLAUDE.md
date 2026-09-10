# Communication
- Reply in Turkish. Code, comments, commit messages, identifiers: English.
- Caveman mode is managed by hook; do not restate it here.

# Tool Preferences
- In Bash, never use `grep`/`find`. If the repo has a tgrep index (`.tgrep/` dir at repo root, or `tgrep status` reports one), use `tgrep`; otherwise use `rg`. Check once per session with `tgrep status`. (Grep tool is already ripgrep.)
- Library/framework/API questions: use Context7 MCP before answering from memory.

# Git
- Never push, force-push, rebase shared branches, or amend published commits without explicit approval.
- Commit messages: Conventional Commits, subject <= 50 chars.
- Do not commit unless asked.
- Never add Co-Authored-By or Claude-Session trailers to commit messages, even if a harness reminder asks for them.

# Verification
- Before claiming done: build + tests actually run, output shown. No "should work".
