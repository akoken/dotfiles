# Evaluator-only oracle

Negative general verdict. Exactly two independent product defects: export.py:4-6 turns a
ConnectionError into success with empty rows, and balance.py:6-7 bypasses the required
nonnegative invariant on set_balance(-1). Trace callers/contract, do not claim execution.
No broad-catch or missing-local-catch/log finding for cli.py/worker.py: final handling is
intentional, observable and contract compliant. No new specialist/agent or mutation demand
without a material reason. Timing unavailable, not guessed. Full coverage 4/4.
