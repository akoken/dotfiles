---
name: dependency-resilience
description: Use when designing, reviewing, or changing remote calls, queues, webhooks, caches, brokers, streams, retries, timeouts, idempotency, backpressure, health checks, circuit breakers, or overload behavior.
---

## Core Rule

No remote dependency or queue is production-safe until timeout, retry, idempotency, backpressure, overload behavior, and caller-visible failure signals are defined.

## Workflow

1. Identify every synchronous and asynchronous dependency involved in the requested change.
2. Build a compact dependency matrix:
   - caller
   - callee
   - operation
   - protocol or mechanism
   - criticality
   - user impact if slow, unavailable, rejecting, or ambiguous
3. Set deadline budgets:
   - end-to-end caller deadline
   - per-hop timeout
   - connection timeout
   - cancellation propagation
4. Bound retries:
   - retry count
   - retry location
   - backoff and jitter
   - retryable errors/statuses
   - retry budget
   - overload signals that stop retrying
5. Require idempotency for retryable writes, webhooks, queue consumers, and partial batch retries.
6. Bound queues with max depth, max age, drain-rate alerts, poison-message handling, and DLQ policy.
7. Define overload response:
   - admission control or fail-fast behavior
   - load shedding
   - degraded user behavior
   - visible reject/shed/error-budget metrics
8. Check health probes:
   - liveness must stay local and cheap
   - readiness must not remove all capacity at once because a shared dependency is unhealthy
   - startup behavior must be defined when dependencies are unavailable
9. End with tests or experiments for slow, erroring, overloaded, and unavailable dependencies.

## Output Shape

Use this structure:

```markdown
## Dependency Resilience Review

### Dependency Matrix
| caller | dependency | operation | criticality | failure behavior |
|---|---|---|---|---|

### Deadline Budget
| path | timeout | cancellation | evidence needed |
|---|---:|---|---|

### Retry And Idempotency
| operation | retry policy | idempotency/dedupe | stop signals |
|---|---|---|---|

### Backpressure And Overload
| surface | threshold | behavior | metric |
|---|---|---|---|

### Health And Startup
- Liveness:
- Readiness:
- Startup:

### Failure Tests
- Slow dependency:
- Erroring dependency:
- Overloaded dependency:
- Unavailable dependency:

### Risks / Follow-ups
- ...
```

## Calibration

- Prefer no retry over unsafe retry.
- Prefer one retry layer over stacked retries.
- Do not infer timeout values from average latency; ask for or inspect tail latency and caller deadlines.
- Do not recommend circuit breakers as magic. If used, name open threshold, half-open probe policy, recovery condition, and behavior while open.
- If evidence is missing, mark it as a concrete follow-up instead of claiming readiness.
