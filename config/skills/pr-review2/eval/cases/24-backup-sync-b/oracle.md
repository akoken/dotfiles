# Evaluator-only oracle

Fixed negative control for class `path.file-identity`, paired with 23-backup-sync-a: the
same feature with one shared identity function used by the writer and every reader, plus
tests that reach files through the symlinked root and a relative exclude entry.

## False blockers

Count every blocking finding; the target is 0. Expected verdict: Ready to merge, because
coverage is complete and required gates passed. Optional suggestions do not count as false
blockers but are scored separately when incorrect or harmful, such as removing the shared
function or the upstream symlink guard. No execution may be claimed.
