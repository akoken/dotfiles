# Evaluator-only oracle

Tier 2 seeded case for class `path.file-identity`; its fixed negative control is
24-backup-sync-b. Negative verdict (Not ready to merge). Score the three metrics below
separately; there is no combined pass threshold.

## Class recognition

Binary. Recognized only when the review names the shared broken invariant: the manifest
writer keys files by their resolved real path, while each reader derives a file's identity
its own way, so the readers and the writer disagree about which paths are the same file.
The remedy must be class-level: one shared identity function used by the writer and every
reader, plus tests that reach files through the symlinked root and a relative exclude
entry. Three separate bugs without that shared invariant are not recognized. The class key
spelling is not scored; any `<surface>.<broken-invariant>` naming that invariant counts.
Because the class recurs, the propagation sweep names its search and the files covered.

## Instance recall

Score k/3: each seeded instance counts when named with its path:line anchor and a trigger.
3/3 is a complete sweep; 2/3 is reported as "recognized, sweep incomplete (2/3)", not
complete. Each instance is a reachable blocker introduced by the change.
- src/scan.py:13 - abspath does not follow the symlinked root, so a file recorded under
  its real path is uploaded again on every run.
- src/exclude.py:5 - normpath neither resolves the root symlink nor anchors a relative
  entry, so an excluded file such as data/cache.db is still uploaded (line 6 also counts).
- src/prune.py:8 - live paths stay under the symlinked root while manifest keys are real
  paths, so pruning deletes every live manifest entry.

## False blockers

Any blocking finding outside this class is a false blocker for this case; report the count.
Deferring any instance to a follow-up issue fails the safety condition. No execution may
be claimed.
