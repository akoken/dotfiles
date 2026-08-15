---
name: structured-handoff
description: Use when delegating to subagents, receiving subagent results, coordinating multi-agent work, or asking for worker output that must be auditable, resumable, or easy to validate.
---

## Purpose

Use a compact, repeatable handoff shape for subagent and worker outputs. This keeps delegation results concrete enough to resume, review, or validate without rereading the entire conversation.

## Required Handoff Fields

Every worker handoff should include:

- `status`: `completed`, `blocked`, or `failed`
- `summary`: one concise paragraph
- `artifacts`: repository-relative files created or changed, or empty list
- `verification`: commands/checks run with result and details
- `findings`: block/warn/note items with path and line when applicable
- `recommended_next_stage`: next useful owner/action, or `null`

## Markdown Shape

Use this shape in normal conversation:

```markdown
## Handoff

Status: completed | blocked | failed

Summary:
...

Artifacts:
- path/to/file

Verification:
| command | result | details |
|---|---|---|

Findings:
| severity | path | line | summary |
|---|---|---:|---|

Recommended next stage:
...
```

## JSON Shape

Use this when a machine-readable handoff is requested:

```json
{
  "status": "completed",
  "summary": "...",
  "artifacts": [],
  "verification": [
    {
      "command": "...",
      "result": "passed",
      "details": "..."
    }
  ],
  "findings": [
    {
      "severity": "warn",
      "summary": "...",
      "path": null,
      "line": null
    }
  ],
  "recommended_next_stage": null
}
```

## Validation Rules

- `status` must be exactly `completed`, `blocked`, or `failed`.
- `verification.result` must be exactly `passed`, `failed`, or `skipped`.
- `findings.severity` must be exactly `block`, `warn`, or `note`.
- Use repository-relative paths for artifacts and findings when possible.
- If no command was run, include one `verification` row with `result: skipped` and explain why.
- Do not claim completion when verification is absent unless the task is read-only or documentation-only and the skip reason is explicit.
