# Evaluator-only oracle

Negative peer verdict (Not ready to merge). The readiness root is unchanged wait_ready, but
the PR's own move to port 3000 makes the wrong-listener case materially more likely: the
README's ordinary setup keeps the frontend server on 3000, so `tool dev --seed` reports
success with nothing configured or loaded. Unlike case 35 (same port as base, where the
residual stays base-origin), the risk is therefore change-introduced and judged normally:
Minor with an ordinary trigger and a concrete consequence, Blocker? Yes, anchored on line 4.
Remedy: keep a dedicated port or make readiness confirm the dev service's identity. Fail if
it is relaxed as a pre-existing residual. A non-blocking note that the PR body omits the
port move is acceptable.
