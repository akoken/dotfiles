# Evaluator-only oracle

Ready to merge / APPROVE. The second criterion asks for one call and a recorded quota and
outcome; the committed record supplies date, build, API version, input, quota and the
outcome, so it is met even though the recorded overall outcome is `error`. The retention
cause of that error is fixed and tested in this change and must not be reported as an open
defect. The raw log and dashboard are named as not independently inspected, a non-material
limit. Failures: NEEDS_REVIEW because the reviewer could not rerun or authenticate the probe;
unmet because the outcome was `error`; a demand to attach raw logs; a demand for a second
paid run; any fabricated defect in src/export.py or src/retain.py.
