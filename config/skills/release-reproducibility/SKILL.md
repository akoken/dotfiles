---
name: release-reproducibility
description: Use when cutting releases, tags, version bumps, build artifacts, packages, deployment artifacts, release candidates, artifact promotion, rollback targets, flaky builds, cache trust, or build reproducibility.
---

## Core Rule

No release is reliable unless inputs are pinned, the build is reproducible enough for its risk, the artifact identity is immutable, and promotion is traceable.

## Workflow

1. Separate developer feedback, CI validation, artifact creation, deployment, and user-facing release.
2. Pin every input:
   - source revision
   - dependencies and lockfiles
   - toolchains and SDKs
   - build image or host assumptions
   - generators
   - configuration and environment variables
3. Check hermeticity:
   - undeclared local files
   - ambient credentials
   - network fetches
   - clock-sensitive output
   - machine-specific behavior
4. Stabilize build/test graph:
   - targets
   - generated outputs
   - cache keys
   - invalidation rules
   - cache miss-path check
5. Prefer build-once, promote-many. Do not rebuild separate artifacts per environment unless explicitly justified.
6. Record artifact identity:
   - immutable identifier
   - source revision
   - build metadata
   - storage location
   - checks passed
7. Define release line policy:
   - trunk release
   - release branch
   - train
   - candidate
   - hotfix branch expiry and merge-back rule
8. Define rollback target by artifact identity, not just "previous deployment".
9. Pair release cuts with `staff-production-readiness` when the release affects users, production data, shared infrastructure, or external commitments.

## Output Shape

```markdown
## Release Reproducibility Review

### Pipeline Map
| step | owner/tool | input | output | evidence |
|---|---|---|---|---|

### Pinned Inputs
| input | pinned? | evidence | gap |
|---|---|---|---|

### Hermeticity And Cache Safety
| risk | status | evidence / check |
|---|---|---|

### Artifact Identity
| artifact | immutable id | source revision | metadata | storage |
|---|---|---|---|---|

### Release Policy
- Branch/train/candidate policy:
- Inflight release ordering:
- Supersession rule:
- Emergency branch expiry:

### Checks
| check | required/advisory | command or source | result |
|---|---|---|---|

### Promotion And Rollback
- Promotion path:
- Rollback artifact:
- Latent-change rollback rule:

### Blockers / Follow-ups
- ...
```

## Calibration

- Treat cache speed as irrelevant until cache correctness is proven.
- Treat generated code and generators as build inputs.
- Flaky checks must be quarantined with owner and expiry; do not silently weaken release gates.
- If the user asks to tag, publish, package, or promote, show this review before the release action.
