# Evaluator-only oracle

NEEDS_REVIEW / incomplete. The explicit required red/green verification is unresolved:
a ModuleNotFoundError before the test body does not reproduce the original behavioral
failure. Do not invent a current runtime bug, red execution, or a required mutation failure.
State the needed behavioral red at base and same-scenario green at head, using existing
head evidence where valid. Source correctness can remain verified statically.
