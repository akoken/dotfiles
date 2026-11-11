"""Decision table for bin/agent-env-guard (PreToolUse command guard).

Runs the guard as a subprocess with Claude Code / Codex shaped hook input.
The decision tables never execute their commands. The corpus tests
(agent_env_guard_shell_corpus.py) also run each corpus command under sh,
bash and zsh inside agent_env_guard_harness.Sandbox: a synthetic
environment with a synthetic canary, shims for env/printenv/ps, and no user
startup files. Nothing reads the real environment or /proc.
"""

import ast
import importlib.machinery
import importlib.util
import io
import json
import os
import pathlib
import random
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import agent_env_guard_contract as contract  # noqa: E402
import agent_env_guard_harness as harness  # noqa: E402
import agent_env_guard_gate_corpus as gate_corpus  # noqa: E402
from agent_env_guard_shell_corpus import CASES, KNOWN_LIMITS, PROFILES, WHY  # noqa: E402

# AGENT_ENV_GUARD_UNDER_TEST runs the same table against another copy of the
# guard (used to show a regression test is red on an older head).
GUARD = pathlib.Path(
    os.environ.get("AGENT_ENV_GUARD_UNDER_TEST")
    or pathlib.Path(__file__).resolve().parent.parent / "bin" / "agent-env-guard"
)
MARKER = "SYNTH-MARKER-guard-7f3c"
CATEGORIES = {"visible", "ran", "none", "parse_error"}
DUMPED = {"visible", "ran"}

DENY = [
    # ps with an environment flag, any spelling or order
    "ps -E",
    "ps -Eww",
    "ps -wwE",
    "ps -axE -o pid,command",
    "ps -A -E",
    "ps eww",
    "ps auxe",
    "ps axe",
    "ps -p 123 eww",
    "/bin/ps eww 1",
    "sudo ps -E",
    "nice -n 5 ps eww",
    "ps -ef | head; ps eww",
    "echo start && ps -Ewwo pid,command",
    "bash -lc 'ps eww'",
    "sh -c \"ps -E\"",
    "watch -n 1 ps eww",
    "echo \"$(ps eww)\"",
    "x=`ps -E`",
    "env FOO=1 ps eww",
    "timeout 5 ps -E",
    # whole-environment dumps
    "env",
    "env | sort",
    "/usr/bin/env",
    "env -u PATH",
    "env FOO=1",
    "printenv",
    "printenv -0",
    "printenv 2>/dev/null",
    "export -p",
    "export",
    "set",
    "set | grep KEY",
    "declare -x",
    "declare -p",
    "typeset -x",
    "readonly -p",
    "command env",
    "eval env",
    "env -S 'ps eww'",
    "cd /tmp\nenv",
    # /proc/<pid>/environ
    "cat /proc/self/environ",
    "tr '\\0' '\\n' < /proc/1/environ",
    "strings /proc/$PID/environ",
    "cat /proc/*/environ",
]

ALLOW = [
    "ps",
    "ps aux",
    "ps -ef",
    "ps -e -o pid,command",
    "ps -A",
    "ps -p 123 -o comm=",
    "ps -o pid,ppid,etime,command -p $$",
    "ps axo pid,state,command",
    "ps -U root",
    "printenv HOME",
    "printenv PATH HOME",
    "env FOO=1 npm test",
    "env -u CONTEXT7_API_KEY node script.js",
    "env -i PATH=/usr/bin /usr/bin/true",
    "env -i",
    "FOO=1 env BAR=2 make test",
    "export FOO=bar",
    "export -n FOO",
    "set -euo pipefail",
    "set -o",
    "set -- a b",
    "declare -p PATH",
    "declare -x FOO=bar",
    "typeset -i n=3",
    "integer n=3",
    "float f=1.5",
    "integer -x COUNT=1",
    "command -v env",
    "git status && git diff",
    "gh auth status",
    "echo env",
    "grep -r environ src/",
    "echo ${#PATH}; ls",
    "cat <<'EOF' > notes.md\nenv\nset\nEOF",
    "xargs -n1 echo",
    "bash script.sh",
]

# Forms the patterns were not written against; kept separate so the table
# shows generalisation, not just recall.
UNSEEN_DENY = [
    "ps -wwwAE",
    "doas ps eww",
    "zsh -c 'export -p | head'",
    "nohup printenv > /tmp/x &",
    "( printenv )",
    "env -0",
    "sudo -u root env",
    "time printenv",
    "xargs -0 printf '%s\\n' < /proc/12/environ",
    "find . -name x | xargs env",
]
UNSEEN_ALLOW = [
    "ps -o user,pid,command -u akoken",
    "pgrep -fl node",
    "printenv -0 HOME",
    "env --unset=FOO python3 -V",
    "nice -n 5 make",
]


# Here-documents (ENV-GUARD-01). With an unquoted delimiter the shell runs
# command substitutions in the body; with any quoting of the delimiter the
# body is literal. Here-document operators inside quotes or comments are not
# operators, so they must not hide the following lines from inspection.
HEREDOC_DENY = [
    "cat <<EOF\n$(env)\nEOF",
    "cat <<EOF\n`env`\nEOF",
    "cat <<-EOF\n\t$(env)\n\tEOF",
    "cat <<EOF\n'$(printenv)'\nEOF",
    "cat <<EOF\nuser: $(echo $(env))\nEOF",
    "cat <<EOF\n$(env | (cat))\nEOF",
    "cat <<A <<B\nfirst\nA\n$(env)\nB",
    "cat <<EOF > out.txt\n$(export -p)\nEOF",
    "cat <<EOF\n$(ps eww)\nEOF",
    "echo '<<EOF'\nenv\nEOF",
    "echo hi # <<EOF\nenv\nEOF",
    "cat <<EOF\n$(env\nEOF",
]
HEREDOC_ALLOW = [
    "cat <<'EOF'\n$(env)\nEOF",
    "cat <<\"EOF\"\n`env`\nEOF",
    "cat <<E'OF'\n$(env)\nEOF",
    "cat <<\\EOF\n$(printenv)\nEOF",
    "cat <<-'EOF'\n\t$(env)\n\tEOF",
    "cat <<EOF\nbuilt $(date) on $(uname -s)\nEOF",
    "cat <<EOF\n$(env FOO=1 date)\nEOF",
    "cat <<EOF\nliteral \\$(env) and \\`env\\`\nEOF",
    "cat <<EOF\nHOME is $HOME\nEOF",
    "cat <<<\"$(date)\"",
    "echo '$(env)'",
]
# ENV-GUARD-01 round 3: here-string operator, and line continuation
# (backslash-newline) in delimiters, bodies, words and arithmetic, per the
# lexing contract in bin/agent-env-guard.
B = "\\"
LEXING_DENY = [
    'cat <<<"$(env)"',
    'cat <<<"`env`"',
    "cat <<<`env`",
    'cat <<<"$(echo $(env))"',
    f"cat <<EO{B}\nF\nEOF\nenv",
    f"cat <<EOF\nEO{B}\nF\nenv\n# EOF",
    f"cat <<-EOF\n\tEO{B}\nF\nenv\n# EOF",
    f"cat <<-EO{B}\nF\n\tEOF\nenv",
    f"cat <<{B}\nEOF\nx\nEOF\nenv",
    f"cat <{B}\n<EOF\nx\nEOF\nenv",
    f"cat <<A <<B\nA\nB{B}\n\nB\nenv",
    f"cat <<EOF\nline {B}\n$(env)\nEOF",
    f"en{B}\nv",
    f"e{B}\nn{B}\nv",
    f"printen{B}\nv",
    f"env {B}\n| cat",
    f'echo "$(en{B}\nv)"',
    "((x = 1 << 2))\nenv\n2",
    "x=$((1<<2)); env",
    'echo "# <<EOF"\nenv\nEOF',
    # Executed, but the output does not reach the terminal: still denied.
    'cat <<A <<"B"\n$(env)\nA\nliteral\nB',
    "echo $(( $(env | grep -c SYNTH) ))",
    f"cat /proc/self/envi{B}\nron",
    # A substitution's value is unknown, so it never counts as a name.
    "printenv $(echo HOME)",
    "env $(true)",
]
LEXING_ALLOW = [
    "cat <<<'$(env)'",
    f"cat <<<{B}`env{B}`",
    f"cat <<'EOF'\nEO{B}\nF\nenv\nEOF",
    f"cat <<'EO'{B}\nF\n$(env)\nEOF",
    f'cat <<"EOF"\nEOF{B}\nenv\nEOF',
    "echo x#<<EOF\nenv\nEOF",
    "echo $((1 << 2))",
    'printf "%s\\n" "$(date)"',
    f'env FOO=1 {B}\n  sh -c "echo ok"',
    "env FOO=1 date",
    "cat <<EOF\n$(date)\nEOF",
    "cat <<'EOF'\n$(env)\n`env`\nEOF",
]


def run_guard(payload, guard=None):
    proc = subprocess.run(
        [sys.executable, "-I", str(guard or GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return proc


def decide(command, shape="claude", guard=None):
    if shape == "claude":
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    else:
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "turn_id": "t", "tool_input": {"command": command}}
    proc = run_guard(json.dumps(payload), guard)
    if proc.returncode != 0:
        raise AssertionError(f"guard exited {proc.returncode}: {proc.stderr}")
    if not proc.stdout.strip():
        return "allow", ""
    out = json.loads(proc.stdout)
    spec = out["hookSpecificOutput"]
    assert spec["hookEventName"] == "PreToolUse"
    return spec["permissionDecision"], spec["permissionDecisionReason"]


class GuardDecisions(unittest.TestCase):
    def check(self, commands, expected):
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(decide(command)[0], expected)

    def test_denied_forms(self):
        self.check(DENY, "deny")

    def test_allowed_forms(self):
        self.check(ALLOW, "allow")

    def test_unseen_denied_forms(self):
        self.check(UNSEEN_DENY, "deny")

    def test_unseen_allowed_forms(self):
        self.check(UNSEEN_ALLOW, "allow")

    def test_heredoc_executable_bodies_denied(self):
        self.check(HEREDOC_DENY, "deny")

    def test_heredoc_literal_bodies_and_safe_expansions_allowed(self):
        self.check(HEREDOC_ALLOW, "allow")

    def test_lexing_executable_forms_denied(self):
        self.check(LEXING_DENY, "deny")

    def test_lexing_literal_and_legitimate_forms_allowed(self):
        self.check(LEXING_ALLOW, "allow")

    def test_codex_shape(self):
        self.assertEqual(decide("ps eww", shape="codex")[0], "deny")
        self.assertEqual(decide("ps aux", shape="codex")[0], "allow")


class CorpusTable(unittest.TestCase):
    """The written corpus is complete and self-consistent (no shell needed)."""

    def test_every_case_states_a_consistent_expectation(self):
        seen = set()
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertNotIn(case["id"], seen)
                seen.add(case["id"])
                self.assertIn(case["decision"], {"allow", "deny"})
                if not case["run"]:
                    self.assertEqual(case["decision"], "deny")
                    continue
                observed = case["observed"]
                self.assertEqual(set(observed), set(PROFILES))
                self.assertLessEqual(set(observed.values()), CATEGORIES)
                dumped = DUMPED & set(observed.values())
                if case["decision"] == "allow":
                    # An allow is written out; one that dumps anywhere must name
                    # its documented known limitation (round 7, decision (c)).
                    self.assertIsNone(case["why"])
                    if dumped:
                        self.assertIn(case["limit"], KNOWN_LIMITS)
                    else:
                        self.assertIsNone(case["limit"])
                elif dumped:
                    self.assertIsNone(case["why"])
                else:
                    # "No dump seen" never implies allow: the deny says why.
                    self.assertIn(case["why"], WHY)

    def test_guard_decision_matches_the_table(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertEqual(decide(case["command"])[0], case["decision"])


class ShellCase(unittest.TestCase):
    """Runs sh, bash and zsh in harness.Sandbox: synthetic env, shims, no
    user startup files, never the real environment or /proc."""

    @classmethod
    def setUpClass(cls):
        cls.box = harness.Sandbox()
        cls.addClassCleanup(cls.box.close)
        cls.profiles = harness.profiles(cls.box)
        # Gate: no shell case runs unless every shell starts with exactly the
        # synthetic surface (system zshenv included, no name exemptions).
        problems = harness.startup_problems(harness.startup_report(cls.box))
        if problems:
            raise AssertionError(f"shell startup is not isolated: {problems}")

    def measure(self, command):
        return {key: self.box.run(shell, command) for shell, key in self.profiles.items()}


class ShellProfiles(ShellCase):
    def test_every_shell_is_a_verified_profile(self):
        # A missing shell or an unmeasured version fails instead of being skipped.
        self.assertEqual(set(self.profiles), set(harness.SHELL_ARGV))
        for shell, key in self.profiles.items():
            with self.subTest(shell=shell):
                self.assertIn(key, PROFILES)

    def test_startup_files_leave_the_synthetic_environment_alone(self):
        # zsh -f still sources the system zshenv (/etc/zshenv or
        # /etc/zsh/zshenv); the report names it, and every shell must start
        # with exactly the synthetic environment, no extra exports, aliases,
        # functions or options.
        report = harness.startup_report(self.box)
        for shell in self.profiles:
            with self.subTest(shell=shell, system_zshenv=report["system_zshenv"]):
                self.assertEqual(report[shell], harness.expected_surface(shell))

    def test_startup_check_detects_a_startup_file(self):
        # Control: a startup file that exports, aliases and defines something
        # (zsh without -f reads $ZDOTDIR/.zshenv) must show up in the report.
        # SHLVL is an integer in zsh: a non-numeric value would read as 0.
        with open(os.path.join(self.box.home, ".zshenv"), "w") as fh:
            fh.write("export SYNTH_STARTUP_EXTRA=1\nexport HOME=/elsewhere\n"
                     "export LOGNAME=SYNTH-STARTUP-MARKER\nexport SHLVL=7\n"
                     "alias zz=true\nzz_fn() { :; }\nsetopt extendedglob\n")
        argv = harness.SHELL_ARGV["zsh"]
        try:
            harness.SHELL_ARGV["zsh"] = ["/bin/zsh", "-c"]
            report = harness.startup_report(self.box)["zsh"]
        finally:
            harness.SHELL_ARGV["zsh"] = argv
            os.remove(os.path.join(self.box.home, ".zshenv"))
        self.assertIn("SYNTH_STARTUP_EXTRA", report["extra_exports"])
        self.assertIn("HOME", report["changed_values"])
        self.assertIn("LOGNAME", report["changed_values"])  # re-review ENV-GUARD-06
        self.assertIn("SHLVL", report["changed_values"])
        self.assertIn("zz=true", report["aliases"])
        self.assertIn("zz_fn", report["functions"])
        self.assertIn("extendedglob", report["options"])
        self.assertTrue(harness.startup_problems({"zsh": report}))

    def test_startup_check_detects_a_removed_export(self):
        # re-review ENV-GUARD-06 (368d4f8): a startup file that unexports or
        # unsets a shell-added name must fail the check, one control each.
        argv = harness.SHELL_ARGV["zsh"]
        for line, name in (("typeset +x OLDPWD", "OLDPWD"), ("typeset +x PWD", "PWD"),
                           ("unset SHLVL", "SHLVL"), ("unset LC_ALL", "LC_ALL")):
            with self.subTest(startup=line):
                with open(os.path.join(self.box.home, ".zshenv"), "w") as fh:
                    fh.write(line + "\n")
                try:
                    harness.SHELL_ARGV["zsh"] = ["/bin/zsh", "-c"]
                    report = harness.startup_report(self.box)["zsh"]
                finally:
                    harness.SHELL_ARGV["zsh"] = argv
                    os.remove(os.path.join(self.box.home, ".zshenv"))
                self.assertIn(name, report["missing_exports"])
                self.assertTrue(harness.startup_problems({"zsh": report}))


class CorpusMatchesShells(ShellCase):
    def test_measured_categories_match_the_table(self):
        for case in CASES:
            if not case["run"]:
                continue
            with self.subTest(case=case["id"]):
                measured = self.measure(case["command"])
                expected = {key: case["observed"][key] for key in measured}
                self.assertEqual(measured, expected)


def continuation_variants(command):
    """`command` with one backslash-newline inserted at every position."""
    for i in range(1, len(command)):
        yield command[:i] + B + "\n" + command[i:]


class ContinuationSweep(ShellCase):
    def test_guard_denies_every_variant_a_shell_dumps(self):
        bases = [case for case in CASES if case["sweep"]]
        self.assertTrue(bases)
        for case in bases:
            for variant in continuation_variants(case["command"]):
                measured = self.measure(variant)
                if DUMPED & set(measured.values()):
                    with self.subTest(case=case["id"], variant=variant, measured=measured):
                        self.assertEqual(decide(variant)[0], "deny")


# Structural rule (lexing contract): only LogicalSource reads the raw text.
# Outside it, the typed command may only be handed to LogicalSource (or
# type-checked, compared with "" and passed on to check_command). The
# secret-read rule is the one other reader (its spelling test, G1): main()
# hands the command to check_gate() and to nothing else.
RAW_NAMES = {"main": {"payload", "tool_input", "command"}, "check_command": {"command", "text"}}
RAW_SINKS = {"LogicalSource", "isinstance", "check_command", "check_gate"}
# Reflection could reach LogicalSource's private text without naming it.
REFLECTION = {"getattr", "setattr", "delattr", "vars", "eval", "exec", "compile",
              "globals", "locals", "__import__", "attrgetter", "methodcaller"}
ALLOWED_DUNDERS = {"__name__", "__new__"}
PRIVATE = {"_text", "_pos"}
# The guard's whole import surface: plain `import name` of these modules, no
# aliases and no `from` imports (an alias such as `attrgetter as reader`
# would hide reflection from a name check), and no module internals.
ALLOWED_IMPORTS = {"contextlib", "fnmatch", "json", "os", "re", "shlex", "sys"}
MODULE_INTERNALS = {"modules", "_getframe", "settrace", "setprofile", "__builtins__"}
# The reader API of LogicalSource; only the lexing layer may call it.
READER_API = {"peek", "at", "take", "take_physical_line", "physical_eof", "_skip"}
LAYER = {"LogicalSource", "Lexer"}


def fold_string(node):
    """The constant string an expression of string literals builds, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = fold_string(node.left), fold_string(node.right)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.JoinedStr):
        parts = [fold_string(v) for v in node.values if isinstance(v, ast.Constant)]
        return "".join(p for p in parts if p is not None)
    return None


def raw_access_violations(source):
    tree = ast.parse(source)
    parent = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}

    def enclosing(node, kind):
        while node in parent:
            node = parent[node]
            if isinstance(node, kind):
                return node
        return None

    def allowed(name):
        up = parent[name]
        if isinstance(up, ast.Call) and name in up.args and isinstance(up.func, ast.Name):
            return up.func.id in RAW_SINKS
        if isinstance(up, ast.Attribute) and up.attr == "get":
            call = parent[up]
            return (isinstance(call, ast.Call) and len(call.args) == 1
                    and isinstance(call.args[0], ast.Constant))
        if isinstance(up, ast.Compare):
            return (up.left is name and len(up.ops) == 1 and isinstance(up.ops[0], ast.Eq)
                    and isinstance(up.comparators[0], ast.Constant) and up.comparators[0].value == "")
        if isinstance(up, ast.comprehension) and up.iter is name:
            call = parent[enclosing(up, ast.GeneratorExp)]
            return (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "join" and getattr(call.func.value, "id", None) == "shlex")
        return False

    def owner(node):
        cls = enclosing(node, ast.ClassDef)
        return cls.name if cls else None

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in PRIVATE and owner(node) != "LogicalSource":
            violations.append(f"line {node.lineno}: .{node.attr} outside LogicalSource")
        if isinstance(node, ast.Constant) and node.value in PRIVATE and owner(node) != "LogicalSource":
            violations.append(f"line {node.lineno}: private name as a string outside LogicalSource")
        if isinstance(node, ast.ImportFrom):
            violations.append(f"line {node.lineno}: `from {node.module} import ...`")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in ALLOWED_IMPORTS or alias.asname:
                    violations.append(f"line {node.lineno}: import of `{alias.name}`")
        if isinstance(node, ast.Attribute) and node.attr in MODULE_INTERNALS:
            violations.append(f"line {node.lineno}: module internals `.{node.attr}`")
        if isinstance(node, (ast.BinOp, ast.JoinedStr)):
            folded = fold_string(node)
            if folded is not None and any(p in folded for p in PRIVATE) and owner(node) != "LogicalSource":
                violations.append(f"line {node.lineno}: private name built from strings")
        if isinstance(node, ast.Name) and node.id in REFLECTION:
            violations.append(f"line {node.lineno}: reflective `{node.id}`")
        if isinstance(node, ast.Attribute) and node.attr in {"attrgetter", "methodcaller"}:
            violations.append(f"line {node.lineno}: reflective `.{node.attr}`")
        if (isinstance(node, ast.Attribute) and node.attr.startswith("__")
                and node.attr not in ALLOWED_DUNDERS):
            violations.append(f"line {node.lineno}: dunder access `.{node.attr}`")
        if isinstance(node, ast.Attribute) and node.attr in READER_API and owner(node) not in LAYER:
            violations.append(f"line {node.lineno}: reader `.{node.attr}` outside the lexing layer")
        if isinstance(node, ast.FunctionDef) and node.name in RAW_NAMES:
            for name in ast.walk(node):
                if (isinstance(name, ast.Name) and isinstance(name.ctx, ast.Load)
                        and name.id in RAW_NAMES[node.name] and not allowed(name)):
                    violations.append(f"line {name.lineno}: raw `{name.id}` used in {node.name}()")
    return violations


SEEDED_RAW_ACCESS = [
    # re-review ENV-GUARD-07 (eb86707): an import-alias reflective read
    ("import contextlib\n", "import contextlib\nfrom operator import attrgetter as field_reader\n"),
    ("        self.src = src\n",
     '        self.src = src\n        self.debug_prefix = field_reader("_te" + "xt")(src)[:80]\n'),
    ("import contextlib\n", "import contextlib\nimport operator as op\n"),
    ("import contextlib\n", "import contextlib\nimport importlib\n"),
    ("        self.src = src\n", "        self.src = src\n        self.mods = sys.modules\n"),
    # re-review ENV-GUARD-07: a reflective read of the private text
    ("        self.src = src\n", '        self.src = src\n        self.debug_prefix = getattr(src, "_text")[:80]\n'),
    ("        self.src = src\n", "        self.src = src\n        self.debug = vars(src)\n"),
    ("        self.src = src\n", "        self.src = src\n        self.debug = src.__dict__\n"),
    # the reader API used outside the lexing layer
    ("    tokens = lexer.lex_code()\n",
     '    if "environ" in lexer.src.take_physical_line():\n        raise Deny("x")\n    tokens = lexer.lex_code()\n'),
    # the pre-lexer guard's whitespace test on the raw command
    ('command == ""', "not command.strip()"),
    # a raw-text /proc belt next to the lexer
    ("    lexer = Lexer(LogicalSource(command), depth)\n",
     '    if "/proc/" in command:\n        raise Deny("proc")\n    lexer = Lexer(LogicalSource(command), depth)\n'),
    # a lexer reaching around LogicalSource
    ("        self.src = src\n", "        self.src = src\n        self.raw = src._text\n"),
]


class StructuralRule(unittest.TestCase):
    def test_guard_reads_raw_text_only_through_logical_source(self):
        self.assertEqual(raw_access_violations(GUARD.read_text()), [])

    def test_seeded_raw_access_is_caught(self):
        source = GUARD.read_text()
        for old, new in SEEDED_RAW_ACCESS:
            with self.subTest(seed=new):
                self.assertIn(old, source)
                self.assertTrue(raw_access_violations(source.replace(old, new, 1)))


PROMISE = ("The hook blocks the patterns it recognises; a command that passes is not "
           "evidence of security.")
# Round-6 wording and absolute rules: wrong in any sentence, negated or not
# (round 8, ENV-GUARD-14).
STALE_CLAIMS = [re.compile(p) for p in (
    r"\bpositive\b.*\ballow\b|\ballow\s+rule\b",
    r"\bevery\s+accepted\s+command\b",
    r"\bmust\s+be\s+denied\b",
    r"\ba\s+command\s+is\s+denied\s+when\s+any\b",
    r"\bthe\s+guarantee\s+covers\b",
)]
# A sentence that states one of these without a negation claims more than the
# promise.
SAFETY_CLAIMS = [re.compile(p) for p in (
    r"\b(allow|allows|allowed|accepted|permitted|passing|passes|passed|pass)\b.*"
    r"\b(is|are|be|stays?|remains?)\s+(safe|secure|harmless)\b",
    r"\bguarantee",
    r"\bevidence\s+of\s+(security|safety)\b",
)]
NEGATION = re.compile(r"\b(not|never|no|nor|cannot)\b|n't\b")
SEEDED_CLAIMS = [
    "All permitted commands are safe.",
    "A command that passes is evidence of security.",
    "The guard guarantees that an allowed command dumps nothing.",
    "Every case a profile marks visible must be denied.",
    "The positive allow rule holds for every case.",
    "No canary is seen, so the positive allow rule passes it.",
    "A command is denied when any shell would run a denied form.",
]


def normalised(text):
    """Lowercased prose with comment markers and line breaks folded away."""
    return re.sub(r"[\s#]+", " ", text).lower()


def safety_claims(text):
    """Sentences that claim more than the limited promise.

    A secondary tripwire only. It is lexical: it matches a fixed vocabulary,
    and it skips every sentence that contains a negation word anywhere, so
    "Allowed commands are safe and do not dump." passes. A clean result is
    not proof that no misleading claim exists; the pinned reference text
    (agent_env_guard_contract.py, PinnedContractText) is what holds the
    promise in place.
    """
    found = []
    for sentence in re.split(r"[.;:!?](?:\s|$)", normalised(text)):
        if any(claim.search(sentence) for claim in STALE_CLAIMS) or (
                not NEGATION.search(sentence)
                and any(claim.search(sentence) for claim in SAFETY_CLAIMS)):
            found.append(sentence.strip())
    return found


class LimitedGuaranteeIsStated(unittest.TestCase):
    """README, the guard (docstring, contract and deny messages) and the
    shell corpus make the same limited promise (round 7 decision (c), round 8
    ENV-GUARD-14): the hook blocks the patterns it recognises; a command that
    passes is not evidence of security."""

    README = pathlib.Path(__file__).resolve().parent.parent / "README.md"
    TESTS = pathlib.Path(__file__).resolve().parent
    CORPUS = TESTS / "agent_env_guard_shell_corpus.py"
    HARNESS = TESTS / "agent_env_guard_harness.py"

    def texts(self):
        return {"README": self.README.read_text(), "guard": GUARD.read_text(),
                "corpus": self.CORPUS.read_text(), "harness": self.HARNESS.read_text()}

    def test_readme_lists_every_known_limitation_by_command(self):
        readme = self.README.read_text()
        self.assertIn("best-effort tripwire, not a security boundary", readme)
        for case in CASES:
            if case["limit"]:
                with self.subTest(case=case["id"]):
                    self.assertTrue(case["limit"] in readme, case["limit"])
                    self.assertTrue(f"`{case['command']}`" in readme, case["command"])

    def test_every_text_states_the_promise(self):
        promise = normalised(PROMISE)
        for name in ("README", "guard", "corpus"):
            with self.subTest(text=name):
                self.assertIn(promise, normalised(self.texts()[name]))
        self.assertIn("tripwire", normalised(self.texts()["README"]))
        self.assertIn("tripwire", normalised(self.texts()["guard"]))

    def test_no_text_claims_more_than_the_promise(self):
        for name, text in self.texts().items():
            with self.subTest(text=name):
                self.assertEqual(safety_claims(text), [])

    def test_seeded_claims_are_caught(self):
        # Each seeded sentence, added to each real text, must be reported:
        # the scan is checked, not assumed.
        for name, text in self.texts().items():
            for seed in SEEDED_CLAIMS:
                with self.subTest(text=name, seed=seed):
                    self.assertTrue(safety_claims(text + "\n# " + seed + "\n"))
        self.assertEqual(safety_claims(PROMISE), [])

    def test_deny_messages_state_the_promise(self):
        for command in ("env", "ps -E", "echo $'a\\tb'"):
            with self.subTest(command=command):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertIn(PROMISE, reason)
                self.assertEqual(safety_claims(reason), [])


SEED_W1 = "Allowed commands are safe and do not dump."

# (surface, where the text lives, regex that opens its paragraph)
PINNED = [
    ("guard docstring", "guard", r"This is a best-effort tripwire"),
    ("guard contract comment", "guard", r"# Read as a tripwire"),
    ("corpus docstring", "corpus", r'"No canary seen"'),
    ("README command guard bullet", "readme", r"- \*\*Command guard\*\*"),
]
END_OF_PROMISE = r"not(?:\s|#)+evidence(?:\s|#)+of(?:\s|#)+security\."


def after_promise(anchor, seed):
    """(pattern, replacement): add `seed` right after the promise sentence of
    the paragraph that starts at `anchor`."""
    return re.compile(r"(" + anchor + r"[\s\S]*?" + END_OF_PROMISE + r")"), r"\1 " + seed


def one_word(anchor):
    """(pattern, replacement): change one word of the paragraph at `anchor`."""
    return re.compile(r"(" + anchor + r"[\s\S]*?)\brecognises\b"), r"\1knows"


class PinnedContractText(unittest.TestCase):
    """The text that states the promise equals its pinned reference (W-1).

    safety_claims() is a vocabulary scan that skips negated sentences, so a
    sentence such as SEED_W1 added to a surface passes it. Each surface
    paragraph (guard docstring and contract comment, corpus docstring, README
    command guard bullet) and the deny message frame (prefix, safe hint and
    PROMISE) must therefore equal agent_env_guard_contract.REFERENCE
    modulo whitespace. Changing the promise means changing the reference in
    the same commit.

    Limit: only the pinned paragraphs and the fixed deny frame are exact. The
    per-form <reason> inside a deny message and any text outside the pinned
    paragraphs are covered only by the secondary vocabulary scan.
    """

    def real(self):
        return {"guard": GUARD.read_text(),
                "corpus": LimitedGuaranteeIsStated.CORPUS.read_text(),
                "readme": LimitedGuaranteeIsStated.README.read_text()}

    def violations(self, sources):
        return contract.pin_violations(sources["guard"], sources["corpus"], sources["readme"])

    def test_current_text_equals_the_reference(self):
        self.assertEqual(self.violations(self.real()), [])

    def test_every_surface_has_a_reference_and_a_seed_target(self):
        self.assertEqual({name for name, _, _ in PINNED}, set(contract.REFERENCE))

    def test_tripwire_alone_misses_a_negated_claim(self):
        # The reason the text is pinned: the scan lets SEED_W1 through.
        self.assertEqual(safety_claims(SEED_W1), [])
        for name, text in self.texts_with_seed().items():
            with self.subTest(text=name):
                self.assertEqual(safety_claims(text), [])

    def texts_with_seed(self):
        out = {}
        for name, kind, anchor in PINNED:
            pattern, repl = after_promise(anchor, SEED_W1)
            out[name] = pattern.sub(repl, self.real()[kind], count=1)
        return out

    def test_seeded_sentence_fails_the_pin_on_every_surface(self):
        for name, kind, anchor in PINNED:
            with self.subTest(surface=name):
                pattern, repl = after_promise(anchor, SEED_W1)
                sources = self.real()
                sources[kind], count = pattern.subn(repl, sources[kind], count=1)
                self.assertEqual(count, 1)
                self.assertEqual(self.violations(sources), [name])

    def test_one_word_edit_fails_the_pin_on_every_surface(self):
        for name, kind, anchor in PINNED:
            with self.subTest(surface=name):
                pattern, repl = one_word(anchor)
                sources = self.real()
                sources[kind], count = pattern.subn(repl, sources[kind], count=1)
                self.assertEqual(count, 1)
                self.assertEqual(self.violations(sources), [name])

    def test_rewrapping_alone_is_not_an_edit(self):
        # Only whitespace is normalised: re-wrapped text still equals the reference.
        for name, kind, anchor in PINNED:
            with self.subTest(surface=name):
                pattern = re.compile(r"(" + anchor + r"[\s\S]*?)\brecognises; a command\b")
                sources = self.real()
                gap = "\n# " if name == "guard contract comment" else "\n  "
                sources[kind], count = pattern.subn(
                    lambda m: m.group(1) + "recognises;" + gap + "a" + gap + "command", sources[kind], count=1)
                self.assertEqual(count, 1)
                self.assertEqual(self.violations(sources), [])

    def test_missing_paragraph_fails_the_pin(self):
        sources = self.real()
        sources["corpus"] = sources["corpus"].replace('"No canary seen"', '"No canary"')
        self.assertTrue(self.violations(sources))

    def test_deny_messages_follow_the_pinned_frame(self):
        for command in ("env", "ps -E", "echo $'a\\tb'", "echo " + "a" * 200_001):
            with self.subTest(command=command[:20]):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertEqual(contract.deny_frame_violations(reason), [])

    def test_seeded_and_edited_deny_wording_fails_the_frame(self):
        guard = GUARD.read_text()
        seeds = {
            "seed in PROMISE": ('"evidence of security."', f'"evidence of security. {SEED_W1}"'),
            "seed after PROMISE in the message": (
                "{hint} {PROMISE}\"", "{hint} {PROMISE} " + SEED_W1 + "\""),
            "seed before PROMISE in the message": (
                "{hint} {PROMISE}\"", "{hint} " + SEED_W1 + " {PROMISE}\""),
            "one word of PROMISE": ('"The hook blocks the patterns it recognises;',
                                    '"The hook blocks the patterns it knows;'),
            "one word of the safe hint": ("Read a single variable", "Read a single value"),
            "message prefix": ('f"agent-env-guard: {reason}.', 'f"env-guard: {reason}.'),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for label, (old, new) in seeds.items():
                with self.subTest(seed=label):
                    self.assertEqual(guard.count(old), 1, old)
                    copy = pathlib.Path(tmp) / "agent-env-guard"
                    copy.write_text(guard.replace(old, new, 1))
                    decision, reason = decide("env", guard=copy)
                    self.assertEqual(decision, "deny")
                    self.assertTrue(contract.deny_frame_violations(reason), reason)
            # the secret-read hint is part of the frame too
            for label, (old, new) in {
                "one word of the secret hint": ("Do not print a stored key", "Do not show a stored key"),
                "secret hint dropped": ("hand the value \"\n    \"to that one command", "hand the value \"\n    \"to one command"),
            }.items():
                with self.subTest(seed=label):
                    self.assertEqual(guard.count(old), 1, old)
                    copy = pathlib.Path(tmp) / "agent-env-guard"
                    copy.write_text(guard.replace(old, new, 1))
                    decision, reason = decide("secret-get fake-item", guard=copy)
                    self.assertEqual(decision, "deny")
                    self.assertTrue(contract.deny_frame_violations(reason), reason)


def guard_module():
    """The guard loaded as a module (honours AGENT_ENV_GUARD_UNDER_TEST)."""
    loader = importlib.machinery.SourceFileLoader("agent_env_guard_under_test", str(GUARD))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def decide_list(argv, guard=None):
    payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": argv}}
    proc = run_guard(json.dumps(payload), guard)
    if proc.returncode != 0:
        raise AssertionError(f"guard exited {proc.returncode}: {proc.stderr}")
    if not proc.stdout.strip():
        return "allow", ""
    spec = json.loads(proc.stdout)["hookSpecificOutput"]
    return spec["permissionDecision"], spec["permissionDecisionReason"]


def hook_decision(module, command):
    """The decision of the guard's main() run in this process on a hook
    payload whose command is a string or an argv list: the code path of the
    hook without a process per input (the sweep and the fuzz need thousands)."""
    payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    stdin, stdout = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = io.StringIO(json.dumps(payload)), io.StringIO()
    try:
        module.main()
        written = sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout = stdin, stdout
    if not written.strip():
        return "allow", ""
    spec = json.loads(written)["hookSpecificOutput"]
    return spec["permissionDecision"], spec["permissionDecisionReason"]


def env_dump_decision(module, text):
    """What the env-dump rule alone decides (the whole of main's decision)."""
    try:
        module.check_command(text)
    except Exception:  # a Deny, or a guard bug that main() reports as a deny
        return "deny"
    return "allow"


def pinned_rows():
    """(table, command, pinned decision) for every row of every table: the
    main-era tables, the shell corpus and the secret-read corpus."""
    rows = []
    for name, commands, expected in (
            ("DENY", DENY, "deny"), ("ALLOW", ALLOW, "allow"),
            ("UNSEEN_DENY", UNSEEN_DENY, "deny"), ("UNSEEN_ALLOW", UNSEEN_ALLOW, "allow"),
            ("HEREDOC_DENY", HEREDOC_DENY, "deny"), ("HEREDOC_ALLOW", HEREDOC_ALLOW, "allow"),
            ("LEXING_DENY", LEXING_DENY, "deny"), ("LEXING_ALLOW", LEXING_ALLOW, "allow"),
            ("SECRET_DENY", gate_corpus.SECRET_DENY, "deny"), ("ROUND_6", gate_corpus.ROUND_6, "deny"),
            ("SR_01", gate_corpus.SR_01, "deny"), ("LONG_S", gate_corpus.LONG_S, "deny"),
            ("MENTIONS", gate_corpus.MENTIONS, "deny"),
            ("SPELLED_HARMLESS", gate_corpus.SPELLED_HARMLESS, "deny"),
            ("RUNS_PROGRAM", gate_corpus.RUNS_PROGRAM, "deny"),
            ("NOT_GATED_ALLOW", gate_corpus.NOT_GATED_ALLOW, "allow")):
        rows += [(name, command, expected) for command in commands]
    rows += [("CASES", case["command"], case["decision"]) for case in CASES]
    rows += [("REVIEW_INPUTS", command, expected) for _, command, expected in gate_corpus.REVIEW_INPUTS]
    for ident, commands in gate_corpus.STATED_LIMITS.items():
        rows += [(ident, command, "allow") for command in commands]
    return rows


# Text inserted by the sweep and the fuzz: shell syntax, quoting, control and
# non-ASCII characters, and whole or partial guarded names.
SYNTAX = ["$", "`", "\\", "*", "?", "[", "]", "{", "}", "(", ")", "<", ">", "|", "&", ";", "'", '"', "~", "#",
          "=", "!", " ", "\t", "\n", "\\\n", "\r", "\x00", "\u00a0", "\u017f", "\u00e9", "$'", '$"', "$(", "${",
          "<<", "<("]
NAME_PARTS = ["secret-get", "SECRET-GET", "Secret-Get", "s''ecret-get", 'sec"ret"-get', "sec\\ret-get",
              "secret-\\\nget", "op", "OP", " op ", "'op'", "o\\p", "OP_RUN_NO_MASKING", "op_run_no_masking",
              "secret", "-get", "_op", "op.", "top", "$''get", '$""get']
SWEEP_BASES = ["rg secret-get README.md", "cat bin/secret-get | wc -l", "git log -- bin/secret-get",
               "op whoami", "echo op && op vault list", "ls bin 2>&1 >/dev/null | rg secret-get",
               "OP_RUN_NO_MASKING=1 true", "git status && printf '%s\\n' ok", "with-secret xai KEY true"]
FUZZ_SEED = 20261111
FUZZ_INPUTS = 4000


def fuzz_inputs(rows):
    """FUZZ_INPUTS mutated corpus rows, the same on every run."""
    rng = random.Random(FUZZ_SEED)
    for _ in range(FUZZ_INPUTS):
        text = rng.choice(rows)
        for _ in range(rng.randint(1, 4)):
            index = rng.randint(0, len(text))
            action = rng.random()
            if action < 0.45:
                text = text[:index] + rng.choice(SYNTAX) + text[index:]
            elif action < 0.75:
                text = text[:index] + rng.choice(NAME_PARTS) + text[index:]
            elif action < 0.9:
                text = text[:index] + text[index + rng.randint(1, 3):]
            else:
                text = text + rng.choice([" && ", " ; ", " | ", "\n", " "]) + rng.choice(rows)
        if text:
            yield text


class SecretReadGate(unittest.TestCase):
    """The secret-read rule: an input that spells a guarded name (G1) is
    refused; an input that spells none is not examined and decides as the
    env-dump rule does. Every decision is made on a string; nothing is
    executed."""

    @classmethod
    def setUpClass(cls):
        cls.module = guard_module()

    def assertRefused(self, reason):
        self.assertEqual(contract.deny_frame_violations(reason), [], reason)
        self.assertIn("secret-read rule", reason)
        self.assertIn("with-secret <item> <VAR> <command>", reason)

    def test_the_2026_11_09_command_is_denied(self):
        command = "/usr/bin/time -p ~/bin/secret-get obss-llm 2>&1 >/dev/null | rg real"
        self.assertEqual(gate_corpus.SECRET_DENY[0], command)
        for shape in ("claude", "codex"):
            with self.subTest(shape=shape):
                decision, reason = decide(command, shape)
                self.assertEqual(decision, "deny")
                self.assertRefused(reason)
                self.assertIn("the guarded name `secret-get`", reason)

    def test_every_row_that_spells_a_name_is_denied_and_the_rest_decide_as_pinned(self):
        """The acceptance property over every row of every table, through the
        real hook: a row that spells a guarded name is denied as text and as a
        list payload, a row that spells none keeps the decision its table
        pins (for the main-era tables: the decision of main)."""
        rows = pinned_rows()
        self.assertEqual(len(gate_corpus.SECRET_DENY), 227)
        self.assertEqual(len(gate_corpus.REVIEW_INPUTS), 43)
        spelled = 0
        for table, command, expected in rows:
            with self.subTest(table=table, command=command):
                decision, reason = decide(command)
                if self.module.spells_guarded_name(command):
                    spelled += 1
                    self.assertEqual(expected, "deny", "a row that spells a name is pinned as an allow")
                    self.assertEqual(decision, "deny")
                    self.assertRefused(reason)
                    decision, reason = decide_list(["bash", "-lc", command])
                    self.assertEqual(decision, "deny")
                    self.assertRefused(reason)
                else:
                    self.assertEqual(decision, expected)
                    self.assertNotIn("secret-read rule", reason)
        self.assertEqual(spelled, 227 + 2 + 2 + 5 + 8 + 89 + 8 + 42)

    def test_tables_hold_the_rows_their_names_say(self):
        spells = self.module.spells_guarded_name
        for name in ("SECRET_DENY", "ROUND_6", "SR_01", "LONG_S", "MENTIONS", "SPELLED_HARMLESS", "RUNS_PROGRAM"):
            for command in getattr(gate_corpus, name):
                with self.subTest(table=name, command=command):
                    self.assertTrue(spells(command))
        for command in gate_corpus.NOT_GATED_ALLOW + [c for rows in gate_corpus.STATED_LIMITS.values() for c in rows]:
            with self.subTest(command=command):
                self.assertFalse(spells(command))
        for ident, command, expected in gate_corpus.REVIEW_INPUTS:
            with self.subTest(id=ident):
                self.assertEqual(spells(command), expected == "deny")
        self.assertEqual(len(gate_corpus.MENTIONS), 8)
        self.assertLessEqual(set(gate_corpus.MENTIONS), set(gate_corpus.SPELLED_HARMLESS))

    def test_long_s_spelling_is_denied_as_text_and_as_list(self):
        """The U+017F spelling of the guarded command, through the real hook.
        The expected decision is the literal "deny": it is not derived from
        the guard's own spelling test."""
        self.assertEqual(len(gate_corpus.LONG_S), 5)
        self.assertEqual(len(gate_corpus.LONG_S_ARGV), 4)
        for command in gate_corpus.LONG_S:
            self.assertIn("\u017f", command)
            for shape in ("claude", "codex"):
                with self.subTest(command=command, shape=shape):
                    decision, reason = decide(command, shape)
                    self.assertEqual(decision, "deny")
                    self.assertRefused(reason)
                    self.assertIn("the guarded name `secret-get`", reason)
            with self.subTest(command=command, shape="list"):
                decision, reason = decide_list(["bash", "-lc", command])
                self.assertEqual(decision, "deny")
                self.assertRefused(reason)
        for argv in gate_corpus.LONG_S_ARGV:
            self.assertTrue(any("\u017f" in word for word in argv))
            with self.subTest(argv=argv):
                decision, reason = decide_list(argv)
                self.assertEqual(decision, "deny")
                self.assertRefused(reason)
                self.assertIn("the guarded name `secret-get`", reason)

    def test_list_payloads(self):
        for argv, expected in gate_corpus.LIST_PAYLOADS:
            with self.subTest(argv=argv):
                self.assertEqual(self.module.spells_guarded_name(shlex.join(argv)), expected == "deny")
                decision, reason = decide_list(argv)
                self.assertEqual(decision, expected)
                if expected == "deny":
                    self.assertRefused(reason)

    def test_in_process_decisions_equal_the_hook(self):
        """hook_decision() (used by the sweep and the fuzz) is the hook."""
        for command in gate_corpus.SR_01 + gate_corpus.MENTIONS + gate_corpus.NOT_GATED_ALLOW[:4] + ["env", "ps aux"]:
            with self.subTest(command=command):
                self.assertEqual(hook_decision(self.module, command), decide(command))
                argv = ["bash", "-lc", command]
                self.assertEqual(hook_decision(self.module, argv), decide_list(argv))

    def check_property(self, text):
        """The acceptance property for one input, as text and as list payload."""
        argv = ["bash", "-lc", text]
        if self.module.spells_guarded_name(text):
            for payload in (text, argv):
                decision, reason = hook_decision(self.module, payload)
                self.assertEqual(decision, "deny")
                self.assertRefused(reason)
            return True
        self.assertEqual(hook_decision(self.module, text)[0], env_dump_decision(self.module, text))
        self.assertEqual(hook_decision(self.module, argv)[0], env_dump_decision(self.module, shlex.join(argv)))
        return False

    def test_sweep_no_inserted_text_gets_a_spelled_input_through(self):
        """Any SYNTAX or NAME_PARTS text inserted anywhere in a base command:
        while the result spells a guarded name it is denied, otherwise the
        env-dump rule alone decides it."""
        spelled = unspelled = 0
        for base in SWEEP_BASES:
            for index in range(len(base) + 1):
                for piece in SYNTAX + NAME_PARTS:
                    mutated = base[:index] + piece + base[index:]
                    with self.subTest(mutated=mutated):
                        if self.check_property(mutated):
                            spelled += 1
                        else:
                            unspelled += 1
        self.assertGreater(spelled, 5000)
        self.assertGreater(unspelled, 1000)

    def test_fuzz_no_mutated_row_gets_a_spelled_input_through(self):
        rows = [command for _, command, _ in pinned_rows()]
        spelled = unspelled = 0
        for text in fuzz_inputs(rows):
            with self.subTest(text=text):
                if self.check_property(text):
                    spelled += 1
                else:
                    unspelled += 1
        self.assertGreater(spelled, 1000)
        self.assertGreater(unspelled, 500)

    def test_the_reason_names_the_spelled_name_and_never_the_command(self):
        for command, name in ((f"secret-get {MARKER}", "secret-get"), (f"echo {MARKER}; OP read x", "op"),
                              (f"Op_Run_No_Masking=1 {MARKER}", "OP_RUN_NO_MASKING"),
                              (f"echo {MARKER} s''ecret-get", "secret-get")):
            with self.subTest(name=name):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertRefused(reason)
                self.assertIn(f"the guarded name `{name}`", reason)
                self.assertNotIn(MARKER, reason)
                self.assertEqual(safety_claims(reason), [])

    def test_a_spelled_input_is_refused_before_the_lexer_reads_it(self):
        """The refusal does not depend on what the env-dump lexer makes of
        the input: its own denials and its limits come second."""
        for command in ("env; echo secret-get", "cat /proc/self/environ secret-get",
                        "echo secret-get " + "a" * 200_001, "echo secret-get " + "$(" * 12 + "date" + ")" * 12,
                        "echo 'secret-get", "echo $'a' secret-get"):
            with self.subTest(command=command[:40]):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertRefused(reason)

    def test_not_spelled_means_not_examined(self):
        for command in ("echo hi", "git status && git diff", "bash script.sh", "echo $(date)", "sh -c 'echo ok'"):
            with self.subTest(command=command):
                self.assertFalse(self.module.spells_guarded_name(command))
                self.module.check_gate(command)  # no refusal, whatever the syntax
                self.assertEqual(decide(command)[0], "allow")

    def test_spelling_ignores_quotes_backslashes_and_case(self):
        for command in ("echo s''ecret-get", 'echo "SECRET"-get', "echo secr\\et-get", "echo OP_run_NO_masking",
                        "echo 'o'p", "echo o\\\np", "/usr/bin/OP read x", "echo x | op",
                        "echo \u017fecret-get", "echo \u017fECRET-GET", "echo OP_RUN_NO_MA\u017fKING"):
            with self.subTest(command=command):
                self.assertTrue(self.module.spells_guarded_name(command))

    def test_op_is_a_word_only(self):
        for command in ("echo top", "echo stop", "echo copy", "echo op2", "echo my-op", "echo op.exe", "echo op_x"):
            with self.subTest(command=command):
                self.assertFalse(self.module.spells_guarded_name(command))

    def test_stated_limits_decide_as_main(self):
        for ident, rows in gate_corpus.STATED_LIMITS.items():
            for command in rows:
                with self.subTest(limit=ident, command=command):
                    self.assertEqual(decide(command)[0], "allow")

    def test_scope_is_stated_in_the_docstring_and_the_readme(self):
        guard = " ".join(GUARD.read_text().split())
        readme = " ".join((GUARD.parent.parent / "README.md").read_text().split())
        for surface, text in (("docstring", guard), ("README", readme)):
            with self.subTest(surface=surface):
                self.assertIn("examines only inputs whose text spells a guarded name", text)
                self.assertIn("is refused whole, whatever it would do", text)
                self.assertIn("is not examined by this rule", text)
                self.assertIn("explicit protection limit", text)
                self.assertNotIn("grammar v1", text)
        self.assertNotIn("value never lands", readme)
        self.assertNotIn("What still passes", readme)

    def test_every_stated_limit_has_a_corpus_row_and_a_readme_entry(self):
        readme = (GUARD.parent.parent / "README.md").read_text()
        named = set(re.findall(r"\b(?:SECRET-LIMIT|ENV-LEXER|ENV-SUDO-K)-\d\d\b", readme))
        self.assertEqual(named, set(gate_corpus.STATED_LIMITS))
        # the two boundary forms of the spelling test are named by their text
        self.assertEqual(gate_corpus.STATED_LIMITS["SECRET-LIMIT-05"],
                         ["env secret-$''get synthitem", 'env secret-$""get synthitem'])
        for form in ("secret-$''get", 'secret-$""get'):
            self.assertIn(form, readme)

    def test_the_gate_holds_no_grammar_and_no_command_table(self):
        """The rule is one spelling test: the strict scanner, the head list
        and the `op` table of the earlier design are gone."""
        for name in ("StrictScanner", "GATE_HEADS", "GATE_GIT", "OP_FORMS", "GATE_REASONS", "check_gate_command"):
            with self.subTest(name=name):
                self.assertFalse(hasattr(self.module, name))


class Limits(unittest.TestCase):
    def test_oversized_command_is_denied_visibly(self):
        decision, reason = decide("echo " + "a" * 200_001)
        self.assertEqual(decision, "deny")
        self.assertIn("too large", reason)

    def test_deep_nesting_is_denied_visibly(self):
        for command in ("echo " + "$(" * 12 + "date" + ")" * 12, "eval " * 12 + "date"):
            with self.subTest(command=command[:40]):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertIn("too deep", reason)

    def test_deep_expression_nesting_is_denied_visibly(self):
        # re-review ENV-GUARD-08: ${...} recursion shares the nesting budget
        for command in ("echo " + "${a:-" * 40 + "ok" + "}" * 40,
                        "echo " + '"$(' * 20 + "date" + ')"' * 20):
            with self.subTest(command=command[:40]):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertIn("too deep", reason)

    def test_moderate_nesting_is_allowed(self):
        self.assertEqual(decide("echo ${a:-${b:-${c:-ok}}}")[0], "allow")
        self.assertEqual(decide("echo $(echo $(echo $(date)))")[0], "allow")
        self.assertEqual(decide("eval eval eval date")[0], "allow")


class GuardOutputCarriesNoMarker(unittest.TestCase):
    def test_deny_message_does_not_echo_command(self):
        for command in (
            f"env FAKE_TEST_API_KEY={MARKER}",
            f"FAKE_TEST_API_KEY={MARKER} printenv",
            f"printenv; echo {MARKER}",
        ):
            with self.subTest(command=command):
                decision, reason = decide(command)
                self.assertEqual(decision, "deny")
                self.assertNotIn(MARKER, reason)
                self.assertIn("printenv NAME", reason)

    def test_malformed_input_fails_closed_without_echo(self):
        proc = run_guard(f'{{"tool_input": {{"command": "{MARKER}')
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertNotIn(MARKER, proc.stdout + proc.stderr)

    def test_non_bash_input_is_ignored(self):
        proc = run_guard(json.dumps({"tool_name": "Read", "tool_input": {"file_path": MARKER}}))
        self.assertEqual((proc.returncode, proc.stdout, proc.stderr), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
