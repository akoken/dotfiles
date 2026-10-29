# Synthetic review input

Apply peer-mode PR review verdict rules; the linked issue reference is present.
Review this offline synthetic first-round change. Do not use gh, run code, edit, or publish.
Base SHA: cccccccccccccccccccccccccccccccccccccccc
Head SHA: dddddddddddddddddddddddddddddddddddddddd
Five new files; all dimensions and required trusted CI are available and passed.
The filesystem is case-sensitive. The unchanged validate_tree() rejects any symlink below
the source root before these functions run. The unchanged uploader calls
manifest.record(path, digest) for every path that files_to_upload returns.

The linked issue adds incremental backup with these requirements:
- The configured source root may itself be a symlink to the data directory.
- Exclude entries may be absolute or relative to the working directory.
- Files already recorded in the manifest are not uploaded again.
- Excluded files are never uploaded.
- Pruning removes manifest entries only for files that no longer exist.

The complete new src/manifest.py:
1 import os
2
3
4 def _key(path):
5     return os.path.realpath(path)
6
7
8 class Manifest:
9     def __init__(self, entries=None):
10         self.entries = dict(entries or {})
11
12     def record(self, path, digest):
13         self.entries[_key(path)] = digest

The complete new src/scan.py:
1 import os
2
3 from src.exclude import is_excluded
4
5
6 def files_to_upload(root, manifest, excluded):
7     pending = []
8     for folder, _, names in os.walk(root):
9         for name in names:
10             path = os.path.join(folder, name)
11             if is_excluded(path, excluded):
12                 continue
13             if os.path.abspath(path) not in manifest.entries:
14                 pending.append(path)
15     return pending

The complete new src/exclude.py:
1 import os
2
3
4 def is_excluded(path, excluded):
5     candidate = os.path.normpath(path)
6     return any(candidate == os.path.normpath(entry) for entry in excluded)

The complete new src/prune.py:
1 import os
2
3
4 def prune_stale(root, manifest):
5     live = set()
6     for folder, _, names in os.walk(root):
7         for name in names:
8             live.add(os.path.abspath(os.path.join(folder, name)))
9     for key in list(manifest.entries):
10         if key not in live:
11             del manifest.entries[key]

The complete new tests/test_manifest.py:
1 from src.manifest import Manifest
2
3
4 def test_record_stores_digest(tmp_path):
5     target = tmp_path / "a.txt"
6     target.write_text("a")
7     manifest = Manifest()
8     manifest.record(str(target), "d1")
9     assert manifest.entries == {str(target.resolve()): "d1"}

PR body: Adds incremental backup: skips recorded files, honors the exclude list and prunes
stale manifest entries.
