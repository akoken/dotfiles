---
name: production-readiness
description: Use for launch, migration, traffic shift, release readiness, go/no-go, production impact, customer-impacting changes, recovery, rollback, observability, SLO, ownership, or operational readiness reviews.
---

## Core Rule

Do not claim production readiness without reviewable evidence, explicit blockers, or a dated risk record.

## Workflow

1. Classify the scope:
   - local checkpoint
   - external artifact
   - production/customer-impacting change
2. Classify impact dimensions:
   - external commitment
   - customer criticality
   - data sensitivity
   - state durability
   - blast radius
3. Gather evidence before making readiness claims:
   - architecture map or textual component map
   - dependencies and fault domains
   - rollout and rollback plan
   - SLOs/error budget, dashboards, alerts, runbooks
   - capacity/load-test data
   - backup/restore or DR evidence when stateful
   - threat model, access controls, secrets, vulnerability status
4. Mark each domain as `Pass`, `Blocker`, `Exception`, `Follow-up`, or `Not applicable`.
5. A gap is a blocker when it can violate user, data, security, recovery, or rollback requirements before launch.
6. A gap is a follow-up only when launch risk remains bounded and the action, owner, check path, and due date are explicit.
7. For manual or semi-automated launch paths, name launch owner, rollback owner, responder handoff, watch window, and success/abort checks.
8. For automated paths, name the automation path and its rollback trigger.

## Output Scaling

If scope is ambiguous, state the assumption first:

```text
I am treating this as local-only because it is not being pushed, published, deployed, or exposed to users. If wrong, tell me whether this is public or production/customer-impacting.
```

Use compact output for local or external artifacts; use the full matrix for production/customer-impacting changes.

## Output Shape

```markdown
## Production Readiness Review

### Scope And Impact
| dimension | applies? | evidence / assumption |
|---|---|---|

### Readiness Matrix
| domain | status | evidence | blocker / exception / follow-up |
|---|---|---|---|

### Architecture And Dependencies
- Component map:
- Critical dependencies:
- Fault domains:

### Rollout, Rollback, And Watch
- Launch path:
- Rollback path:
- Owner or automation:
- Watch window:
- Success checks:
- Abort checks:

### Blockers
| blocker | required evidence | owner | due date |
|---|---|---|---|

### Exceptions
| accepted risk | compensating control | expiry | refresh trigger |
|---|---|---|---|

### Advisory Posture
- Ready / not ready / ready with exceptions:
- Highest risk:
- Next check:
```

## Calibration

- The agent gives an advisory posture; the user decides go/no-go.
- Do not mark a checklist green without evidence paths, commands, dashboard names, runbooks, or explicit assumptions.
- Do not use `Not applicable` to skip security, recovery, or incident checks without rationale.
