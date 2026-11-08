"""Decision table for bin/agent-env-guard (PreToolUse command guard).

Runs the guard as a subprocess with Claude Code / Codex shaped hook input.
The decision tables never execute their commands. The corpus tests
(agent_env_guard_shell_corpus.py) also run each corpus command under sh,
bash and zsh inside agent_env_guard_harness.Sandbox: a synthetic
environment with a synthetic canary, shims for env/printenv/ps, and no user
startup files. Nothing reads the real environment or /proc.
"""

import ast
import json
import os
import pathlib
import subprocess
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import agent_env_guard_harness as harness  # noqa: E402
from agent_env_guard_shell_corpus import CASES, PROFILES, WHY  # noqa: E402

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


def run_guard(payload):
    proc = subprocess.run(
        [sys.executable, "-I", str(GUARD)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return proc


def decide(command, shape="claude"):
    if shape == "claude":
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    else:
        payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "turn_id": "t", "tool_input": {"command": command}}
    proc = run_guard(json.dumps(payload))
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
                    # An allow is written out and never runs a dump anywhere.
                    self.assertFalse(dumped)
                    self.assertIsNone(case["why"])
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
        cls.profiles = harness.profiles()

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
        # zsh -f still sources the system zshenv; the report names it and
        # every shell must keep PATH, HOME and the canary unchanged.
        report = harness.startup_report(self.box)
        for shell in self.profiles:
            with self.subTest(shell=shell, system_zshenv=report["system_zshenv"]):
                self.assertEqual(report[shell], {
                    "path_unchanged": True, "home_unchanged": True, "canary_unchanged": True,
                })


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
# type-checked, compared with "" and passed on to check_command).
RAW_NAMES = {"main": {"payload", "tool_input", "command"}, "check_command": {"command", "text"}}
RAW_SINKS = {"LogicalSource", "isinstance", "check_command"}


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

    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in {"_text", "_pos"}:
            owner = enclosing(node, ast.ClassDef)
            if owner is None or owner.name != "LogicalSource":
                violations.append(f"line {node.lineno}: .{node.attr} outside LogicalSource")
        if isinstance(node, ast.FunctionDef) and node.name in RAW_NAMES:
            for name in ast.walk(node):
                if (isinstance(name, ast.Name) and isinstance(name.ctx, ast.Load)
                        and name.id in RAW_NAMES[node.name] and not allowed(name)):
                    violations.append(f"line {name.lineno}: raw `{name.id}` used in {node.name}()")
    return violations


SEEDED_RAW_ACCESS = [
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

    def test_moderate_nesting_is_allowed(self):
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
