# Upstream provenance

- Repository: https://github.com/alirezarezvani/claude-skills
- Commit: `19392f7a08264ed00486a251f5b2098321771f94`
- Source directory: `productivity/handoff/skills/handoff`
- Imported as a standalone skill with its bundled scripts, references, and assets.
- Resolve bundled resource paths relative to this skill directory, while keeping the target project as the working directory where required.
- Claude plugin commands, agents, and hooks are not installed by this skill copy.
- Variant: productivity handoff. SessionStart/SessionEnd automation requires the upstream plugin; manual handoff generation works as a standalone skill.
- Local adaptation: a line-specific `gitleaks:allow` comment identifies an upstream synthetic redaction fixture; runtime behavior is unchanged.
