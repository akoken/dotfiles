# Synthetic review input

Apply peer-mode PR review verdict rules; the linked issue reference is present.
Review this offline synthetic first-round change. Do not use gh, run code, edit, or publish.
Base SHA: eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
Head SHA: ffffffffffffffffffffffffffffffffffffffff
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
4 def file_key(path):
5     return os.path.realpath(path)
6
7
8 class Manifest:
9     def __init__(self, entries=None):
10         self.entries = dict(entries or {})
11
12     def record(self, path, digest):
13         self.entries[file_key(path)] = digest

The complete new src/scan.py:
1 import os
2
3 from src.exclude import is_excluded
4 from src.manifest import file_key
5
6
7 def files_to_upload(root, manifest, excluded):
8     pending = []
9     for folder, _, names in os.walk(root):
10         for name in names:
11             path = os.path.join(folder, name)
12             if is_excluded(path, excluded):
13                 continue
14             if file_key(path) not in manifest.entries:
15                 pending.append(path)
16     return pending

The complete new src/exclude.py:
1 from src.manifest import file_key
2
3
4 def is_excluded(path, excluded):
5     candidate = file_key(path)
6     return any(candidate == file_key(entry) for entry in excluded)

The complete new src/prune.py:
1 import os
2
3 from src.manifest import file_key
4
5
6 def prune_stale(root, manifest):
7     live = set()
8     for folder, _, names in os.walk(root):
9         for name in names:
10             live.add(file_key(os.path.join(folder, name)))
11     for key in list(manifest.entries):
12         if key not in live:
13             del manifest.entries[key]

The complete new tests/test_readers.py:
1 import os
2
3 from src.exclude import is_excluded
4 from src.manifest import Manifest
5 from src.prune import prune_stale
6 from src.scan import files_to_upload
7
8
9 def make_tree(tmp_path):
10     data = tmp_path / "data"
11     data.mkdir()
12     (data / "a.txt").write_text("a")
13     (data / "cache.db").write_text("c")
14     root = tmp_path / "root"
15     root.symlink_to(data, target_is_directory=True)
16     return data, root
17
18
19 def test_recorded_file_is_skipped_through_symlinked_root(tmp_path):
20     data, root = make_tree(tmp_path)
21     manifest = Manifest()
22     manifest.record(str(data / "a.txt"), "d1")
23     pending = files_to_upload(str(root), manifest, [str(data / "cache.db")])
24     assert pending == []
25
26
27 def test_relative_exclude_entry_matches(tmp_path, monkeypatch):
28     data, root = make_tree(tmp_path)
29     monkeypatch.chdir(tmp_path)
30     assert is_excluded(str(root / "cache.db"), ["data/cache.db"])
31     assert not is_excluded(str(root / "a.txt"), ["data/cache.db"])
32
33
34 def test_prune_keeps_live_entries_through_symlinked_root(tmp_path):
35     data, root = make_tree(tmp_path)
36     manifest = Manifest()
37     manifest.record(str(root / "a.txt"), "d1")
38     manifest.record(str(data / "gone.txt"), "d2")
39     prune_stale(str(root), manifest)
40     assert manifest.entries == {os.path.realpath(data / "a.txt"): "d1"}

PR body: Adds incremental backup: skips recorded files, honors the exclude list and prunes
stale manifest entries.
