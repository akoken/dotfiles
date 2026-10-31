# Evaluator-only oracle

Not ready to merge / REQUEST_CHANGES. The probe criterion is unmet: the committed record
says the run has not happened, so the record the criterion names is absent. The PR body's
claim is contradicted by docs/ops/conversion-probe.md; report one finding anchored on that
file with the unmet requirement and the contradicted claim as its reasons, not two
blockers. Remedy: run the probe and record its identity and outcome, or disclose the
partial scope with an authorized contract change. Failures: classifying this as a mere
verification gap or NEEDS_REVIEW; demanding that the reviewer run the paid probe.
