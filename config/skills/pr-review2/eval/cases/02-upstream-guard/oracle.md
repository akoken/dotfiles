# Evaluator-only oracle

Complete positive verdict and no division-by-zero defect: mean rejects empty input,
and len(values) is positive on the only _divide call. Do not demand an unreachable count=0
guard or weakening/removal of existing validation. Name inspected code/test behavior.
