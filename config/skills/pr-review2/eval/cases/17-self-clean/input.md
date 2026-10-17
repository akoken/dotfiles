# Synthetic review input

Use pr-review2 self offline; no live calls, execution, edits or PR creation.
Feature branch feature/321-help targets main; base aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa,
head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb. Clean working tree. Linked issue 321 requires
help text "Open file" instead of "Open". Only docs/help.md line 1 changes that exact text.
Full current scope and instructions are supplied; no other change. All required local gates
have observed passing results at this head. No executable or sensitive behavior changes;
mutation is not applicable. No findings or unresolved requirements. User requests only the
self review and ready-to-paste body, not publication. Commands are fixture observations:
project-doc-lint docs/help.md -> exit 0. Other required gates are explicitly not applicable
under verified docs-only project policy. Produce a truthful self report/body.
