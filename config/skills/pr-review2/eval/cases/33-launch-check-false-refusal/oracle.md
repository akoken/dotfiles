# Evaluator-only oracle

Negative peer verdict (Not ready to merge). Line 4 matches any basename containing "tool",
so the README's documented `tool gate -- ./scripts/toolchain-check.sh` now exits with the
nested-gate message although it is not a nested gate. This Minor meets the materiality bar:
an ordinary documented trigger and a concrete user-visible consequence (the standard
command fails), introduced by the change. Blocker? Yes through branch 1; it must not be
relaxed as a guard bypass (the input is not contrived) or deferred by the reviewer.
Remedy: match the tool's own launcher exactly (and the gate subcommand), plus a test for
the documented command. The marker logic on line 8 is correct.
