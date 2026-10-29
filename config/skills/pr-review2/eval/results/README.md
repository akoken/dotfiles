# Recorded results

Results are recorded here only when intentionally maintaining the evaluation corpus. One
Markdown file per case run, named `<YYYY-MM-DD>-<case>-<host>.md`. Each file starts with
these `key: value` lines, all required and nonempty:

- reviewer: always `pr-review2`; results of any other reviewer never count here.
- skill-version: the `metadata.version` of the SKILL.md that ran.
- candidate-sha256: SHA-256 of the candidate skill tree that ran.
- case: the case directory name under `cases/`.
- host: the runner, for example the agent CLI and its version.
- model: the exact model id.

After the header, preserve the raw reviewer output and record the scores the rubric asks
for. Results bound to different versions, models or reviewers are never aggregated or
compared as one; a change to any of them invalidates earlier effectiveness claims.
