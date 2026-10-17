# Synthetic review input

Apply the general review verdict rules.
Review this offline synthetic change. No execution, live tools, edits, or publication.
Base aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa; head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.
Linked issue explicitly requires renaming the CLI option --path to --file while keeping --path
as a backwards-compatible alias in this release. PR body says the rename and alias are complete.
Only changed file src/args.py; previous parser.add_argument("--path") was replaced by:
1 import argparse
2 parser = argparse.ArgumentParser()
3 parser.add_argument("--file")
4 args = parser.parse_args()
No other parser/wrapper/aliases. Existing callers still use --path. All required CI passed;
tests cover --file only. Complete changed code is available.
