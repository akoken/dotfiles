# Evaluator-only oracle

Not ready to merge / REQUEST_CHANGES. The criterion requires the probe to pass; the
committed record's overall outcome is `error`, so the record does not satisfy the
criterion's own text and the requirement is unmet, a blocker under the failed-requirement
branch. The record itself is complete and consistent and must not be called fabricated or
contradicted; the retention fix is sound and must not be reported as a defect. Remedy: run
the probe again on the fixed build and record a passing outcome, or change the contract
with authorization. Failures: APPROVE on the recorded error; NEEDS_REVIEW instead of a
blocker; demanding raw logs or reviewer re-execution as the remedy.
